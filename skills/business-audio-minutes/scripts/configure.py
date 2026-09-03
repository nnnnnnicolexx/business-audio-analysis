#!/usr/bin/env python3
"""Read or update per-user Business Audio Minutes configuration."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


SKILL_NAME = "business-audio-minutes"


def codex_home(value: Path | None) -> Path:
    if value:
        return value.expanduser().resolve()
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser().resolve()


def read_config(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Configure Business Audio Minutes.")
    parser.add_argument("--codex-home", type=Path)
    parser.add_argument("--output-root", type=str)
    parser.add_argument("--publish-dir", type=str, help="Use an empty string to disable publishing.")
    parser.add_argument("--quality", choices=["fast", "balanced", "accurate"])
    parser.add_argument("--backend", choices=["auto", "mlx", "faster"])
    parser.add_argument("--language", type=str)
    parser.add_argument("--runtime-python", type=str)
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()

    home = codex_home(args.codex_home)
    path = home / SKILL_NAME / "config.json"
    config = read_config(path)

    if args.output_root is not None:
        config["output_root"] = str(Path(args.output_root).expanduser().resolve())
    if args.publish_dir is not None:
        config["publish_dir"] = "" if args.publish_dir == "" else str(Path(args.publish_dir).expanduser().resolve())
    if args.quality is not None:
        config["quality"] = args.quality
    if args.backend is not None:
        config["backend"] = args.backend
    if args.language is not None:
        config["language"] = args.language
    if args.runtime_python is not None:
        config["runtime_python"] = str(Path(args.runtime_python).expanduser().resolve())

    changed = any(
        value is not None
        for value in [
            args.output_root,
            args.publish_dir,
            args.quality,
            args.backend,
            args.language,
            args.runtime_python,
        ]
    )
    if changed:
        path.parent.mkdir(parents=True, exist_ok=True)
        config.setdefault("version", 1)
        path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.show or not changed:
        print(json.dumps({"config_path": str(path), "config": config}, ensure_ascii=False, indent=2))
    else:
        print(f"Updated {path}")


if __name__ == "__main__":
    main()

