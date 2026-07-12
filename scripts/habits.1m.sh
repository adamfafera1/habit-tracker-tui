#!/bin/bash
# <swiftbar.hideFromHistory>true</swiftbar.hideFromHistory>

resolve_path() {
  local source="$1"
  while [[ -L "$source" ]]; do
    local dir
    dir="$(cd -P "$(dirname "$source")" && pwd)"
    source="$(readlink "$source")"
    [[ "$source" != /* ]] && source="$dir/$source"
  done
  cd -P "$(dirname "$source")" && pwd
}

SCRIPT_DIR="$(resolve_path "${BASH_SOURCE[0]}")"
REPO_ROOT="${HABITS_REPO:-$(cd "$SCRIPT_DIR/.." && pwd)}"
PYTHON="${HABITS_PYTHON:-$REPO_ROOT/.venv/bin/python3}"

if [[ ! -x "$PYTHON" ]]; then
  PYTHON="$(command -v python3)"
fi

exec "$PYTHON" "$REPO_ROOT/scripts/swiftbar_habits.py" "$@"
