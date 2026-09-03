#!/usr/bin/env python3
"""Check the installed skill, runtime, and local transcription backends."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path


SKILL_NAME = "business-audio-minutes"


def get_codex_home(value: Path | None) -> Path:
    if value:
        return value.expanduser().resolve()
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser().resolve()


def default_runtime_python(home: Path) -> Path:
    base = home / "runtime" / SKILL_NAME / ".venv"
    return base / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def import_check(python: Path, modules: list[str]) -> tuple[bool, str]:
    command = [str(python), "-c", "; ".join(f"import {name}" for name in modules)]
    result = subprocess.run(command, capture_output=True, text=True)
    detail = (result.stderr or result.stdout).strip()
    return result.returncode == 0, detail


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose Business Audio Minutes.")
    parser.add_argument("--codex-home", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    home = get_codex_home(args.codex_home)
    config_path = home / SKILL_NAME / "config.json"
    config = {}
    errors: list[str] = []
    warnings: list[str] = []

    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid config JSON: {exc}")
    else:
        errors.append(f"Config not found: {config_path}")

    python = Path(config.get("runtime_python", default_runtime_python(home))).expanduser()
    faster_ok = False
    mlx_ok = False
    faster_detail = ""
    mlx_detail = ""
    if not python.exists():
        errors.append(f"Runtime Python not found: {python}")
    else:
        faster_ok, faster_detail = import_check(python, ["faster_whisper", "openpyxl"])
        if sys.platform == "darwin" and platform.machine().lower() in {"arm64", "aarch64"}:
            mlx_ok, mlx_detail = import_check(python, ["mlx_whisper", "scipy"])

    publish_dir = config.get("publish_dir", "")
    if publish_dir and not Path(publish_dir).expanduser().exists():
        warnings.append(f"Configured publish directory does not exist yet: {publish_dir}")

    apple_silicon = sys.platform == "darwin" and platform.machine().lower() in {"arm64", "aarch64"}
    usable = faster_ok or (apple_silicon and mlx_ok)
    if python.exists() and not usable:
        details = "; ".join(item for item in [faster_detail, mlx_detail] if item)
        errors.append(f"No local transcription backend is usable. {details}".strip())
    elif apple_silicon and not mlx_ok:
        warnings.append(f"MLX unavailable; faster-whisper will be used: {mlx_detail}")
    elif not faster_ok:
        warnings.append(f"faster-whisper unavailable; MLX will be used: {faster_detail}")

    report = {
        "status": "ok" if not errors else "error",
        "platform": sys.platform,
        "machine": platform.machine(),
        "system_python": platform.python_version(),
        "codex_home": str(home),
        "config_path": str(config_path),
        "runtime_python": str(python),
        "backends": {"mlx": mlx_ok, "faster": faster_ok},
        "preferred_backend": "mlx" if apple_silicon and mlx_ok else "faster" if faster_ok else None,
        "warnings": warnings,
        "errors": errors,
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for key, value in report.items():
            print(f"{key}: {value}")

    if args.strict and errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
