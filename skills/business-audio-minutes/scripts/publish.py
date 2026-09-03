#!/usr/bin/env python3
"""Publish a Markdown file to the configured notes folder and verify its hash."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path


SKILL_NAME = "business-audio-minutes"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish verified Markdown to a configured directory.")
    parser.add_argument("markdown", type=Path)
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--codex-home", type=Path)
    args = parser.parse_args()

    source = args.markdown.expanduser().resolve()
    if not source.is_file() or source.suffix.lower() != ".md":
        raise SystemExit(f"Markdown file not found: {source}")

    home = (args.codex_home or Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))).expanduser().resolve()
    config_path = home / SKILL_NAME / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    destination_value = args.destination or (Path(config["publish_dir"]) if config.get("publish_dir") else None)
    if destination_value is None:
        print(json.dumps({"status": "skipped", "reason": "publish_dir is not configured"}, ensure_ascii=False))
        return

    destination_dir = destination_value.expanduser().resolve()
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / source.name
    shutil.copy2(source, destination)
    source_hash = sha256(source)
    destination_hash = sha256(destination)
    if source_hash != destination_hash:
        raise SystemExit("Published file hash does not match source.")
    print(
        json.dumps(
            {"status": "ok", "source": str(source), "destination": str(destination), "sha256": source_hash},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

