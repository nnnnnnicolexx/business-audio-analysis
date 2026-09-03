#!/usr/bin/env python3
"""Install the skill and its isolated local-ASR runtime."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import venv
from pathlib import Path


SKILL_NAME = "business-audio-minutes"
MIN_PYTHON = (3, 10)
MAX_TESTED_PYTHON = (3, 12)


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser().resolve()


def runtime_python(runtime_dir: Path) -> Path:
    if os.name == "nt":
        return runtime_dir / ".venv" / "Scripts" / "python.exe"
    return runtime_dir / ".venv" / "bin" / "python"


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, check=True)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read existing config {path}: {exc}") from exc


def copy_skill(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != destination.resolve():
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(
            source,
            destination,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "*.zip"),
        )
    legacy = destination / "scripts" / "transcribe_mlx.py"
    if legacy.exists():
        legacy.unlink()


def install_dependencies(python: Path) -> None:
    run([str(python), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "faster-whisper>=1.1,<2",
            "openpyxl>=3.1,<4",
        ]
    )
    if sys.platform == "darwin" and platform.machine().lower() in {"arm64", "aarch64"}:
        run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "mlx-whisper>=0.4,<1",
                "scipy>=1.11,<2",
            ]
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Install Business Audio Minutes for the current user.")
    parser.add_argument("--codex-home", type=Path, default=default_codex_home())
    parser.add_argument("--runtime-dir", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--publish-dir", type=Path)
    parser.add_argument("--quality", choices=["fast", "balanced", "accurate"], default=None)
    parser.add_argument("--skip-dependencies", action="store_true", help="Copy/configure only; for packaging tests.")
    parser.add_argument("--no-copy", action="store_true", help="Do not copy the skill into CODEX_HOME.")
    args = parser.parse_args()

    if sys.version_info < MIN_PYTHON:
        raise SystemExit("Python 3.10 or newer is required.")
    if sys.version_info[:2] > MAX_TESTED_PYTHON:
        print("Warning: this installer is tested through Python 3.12.")

    source_skill = Path(__file__).resolve().parents[1]
    codex_home = args.codex_home.expanduser().resolve()
    destination_skill = codex_home / "skills" / SKILL_NAME
    runtime_dir = (args.runtime_dir or codex_home / "runtime" / SKILL_NAME).expanduser().resolve()
    python = runtime_python(runtime_dir)

    if not args.no_copy:
        copy_skill(source_skill, destination_skill)
    else:
        destination_skill = source_skill

    if not args.skip_dependencies:
        runtime_dir.mkdir(parents=True, exist_ok=True)
        if not python.exists():
            venv.EnvBuilder(with_pip=True).create(runtime_dir / ".venv")
        install_dependencies(python)

    config_dir = codex_home / SKILL_NAME
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.json"
    config = load_json(config_path)
    config.update(
        {
            "version": 1,
            "backend": config.get("backend", "auto"),
            "quality": args.quality or config.get("quality", "balanced"),
            "language": config.get("language", "zh"),
            "output_root": str(
                (args.output_root or Path(config.get("output_root", Path.home() / "Documents" / "Codex" / SKILL_NAME)))
                .expanduser()
                .resolve()
            ),
            "publish_dir": str(args.publish_dir.expanduser().resolve())
            if args.publish_dir
            else config.get("publish_dir", ""),
            "runtime_python": str(python),
        }
    )
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Skill: {destination_skill}")
    print(f"Runtime: {runtime_dir}")
    print(f"Config: {config_path}")

    if not args.skip_dependencies:
        doctor = destination_skill / "scripts" / "doctor.py"
        run([str(python), str(doctor), "--codex-home", str(codex_home), "--strict"])
        print("Installation complete. Restart Codex to refresh the skill list.")
    else:
        print("Copy/configuration test complete; dependencies were skipped.")


if __name__ == "__main__":
    main()
