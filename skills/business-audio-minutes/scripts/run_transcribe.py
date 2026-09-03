#!/usr/bin/env python3
"""Launch the transcription worker with the isolated skill runtime."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


SKILL_NAME = "business-audio-minutes"


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser().resolve()


def main() -> None:
    home = codex_home()
    config_path = home / SKILL_NAME / "config.json"
    config = {}
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))

    override = os.environ.get("BAM_RUNTIME_PYTHON")
    if override:
        python = Path(override).expanduser().resolve()
    elif config.get("runtime_python"):
        python = Path(config["runtime_python"]).expanduser()
    else:
        venv_dir = home / "runtime" / SKILL_NAME / ".venv"
        python = venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

    if not python.exists():
        raise SystemExit(
            f"Business Audio Minutes runtime not found: {python}\n"
            "Run scripts/install.sh on macOS/Linux or scripts/install.ps1 on Windows."
        )

    worker = Path(__file__).resolve().with_name("transcribe.py")
    result = subprocess.run([str(python), str(worker), *sys.argv[1:]])
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()

