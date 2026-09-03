#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODEX_BUNDLED_PYTHON="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"

CANDIDATES=()
if [[ -n "${BAM_INSTALL_PYTHON:-}" ]]; then
  CANDIDATES+=("$BAM_INSTALL_PYTHON")
fi
CANDIDATES+=(
  "$CODEX_BUNDLED_PYTHON"
  "python3.12"
  "python3.11"
  "python3.10"
  "python3"
  "python"
)

for candidate in "${CANDIDATES[@]}"; do
  if [[ "$candidate" == */* ]]; then
    [[ -x "$candidate" ]] || continue
    resolved="$candidate"
  elif command -v "$candidate" >/dev/null 2>&1; then
    resolved="$(command -v "$candidate")"
  else
    continue
  fi
  if "$resolved" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
    exec "$resolved" "$SCRIPT_DIR/install.py" "$@"
  fi
done

echo "Python 3.10 or newer is required. Install Python, then rerun this script." >&2
exit 1
