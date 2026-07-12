#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PYTHON="$REPO_ROOT/.venv/bin/python3"
WITH_SWIFTBAR=false
SWIFTBAR_PLUGIN_DIR="${HOME}/Desktop/swiftbarplugins"

usage() {
  cat <<EOF
Install habit-tracker-tui on this machine.

Usage: $(basename "$0") [options]

Options:
  --swiftbar [DIR]   Also install the macOS menu bar plugin (default: ~/Desktop/swiftbarplugins)
  -h, --help         Show this help

After install, run: habits
EOF
}

log() {
  printf '==> %s\n' "$*"
}

warn() {
  printf '!!> %s\n' "$*" >&2
}

need_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    warn "Missing required command: $1"
    exit 1
  fi
}

python_version_ok() {
  "$1" - <<'PY'
import sys
raise SystemExit(0 if sys.version_info >= (3, 11) else 1)
PY
}

ensure_python() {
  need_command python3
  if ! python_version_ok python3; then
    warn "Python 3.11+ is required."
    exit 1
  fi
}

ensure_venv() {
  if [[ ! -x "$VENV_PYTHON" ]]; then
    log "Creating virtual environment"
    python3 -m venv "$REPO_ROOT/.venv"
  fi

  log "Installing project into .venv"
  "$VENV_PYTHON" -m pip install --upgrade pip
  "$VENV_PYTHON" -m pip install -e "$REPO_ROOT"
}

ensure_pipx() {
  if command -v pipx >/dev/null 2>&1; then
    return
  fi

  log "pipx not found; installing it"
  if command -v brew >/dev/null 2>&1; then
    brew install pipx
  else
    python3 -m pip install --user pipx
    export PATH="${HOME}/.local/bin:${PATH}"
  fi
}

ensure_pipx_path() {
  if command -v pipx >/dev/null 2>&1; then
    pipx ensurepath >/dev/null 2>&1 || true
  fi

  if ! command -v pipx >/dev/null 2>&1; then
    export PATH="${HOME}/.local/bin:${PATH}"
  fi

  if ! command -v pipx >/dev/null 2>&1; then
    warn "pipx is installed but not on PATH yet."
    warn "Restart your terminal, then run: pipx install -e \"$REPO_ROOT\""
    exit 1
  fi
}

install_global_command() {
  log "Installing global habits command with pipx"
  pipx install -e "$REPO_ROOT" --force
}

install_swiftbar_plugin() {
  if [[ "$(uname -s)" != "Darwin" ]]; then
    warn "SwiftBar setup is macOS only; skipping."
    return
  fi

  mkdir -p "$SWIFTBAR_PLUGIN_DIR"

  log "Installing SwiftBar plugin to $SWIFTBAR_PLUGIN_DIR"
  cat > "$SWIFTBAR_PLUGIN_DIR/habits.1m.sh" <<EOF
#!/bin/bash
# <swiftbar.hideFromHistory>true</swiftbar.hideFromHistory>

REPO_ROOT="$REPO_ROOT"
PYTHON="\${HABITS_PYTHON:-\$REPO_ROOT/.venv/bin/python3}"

if [[ ! -x "\$PYTHON" ]]; then
  PYTHON="\$(command -v python3)"
fi

exec "\$PYTHON" "\$REPO_ROOT/scripts/swiftbar_habits.py" "\$@"
EOF
  chmod +x "$SWIFTBAR_PLUGIN_DIR/habits.1m.sh"

  if command -v brew >/dev/null 2>&1 && [[ ! -d "/Applications/SwiftBar.app" ]]; then
    log "Installing SwiftBar"
    brew install --cask swiftbar
  fi

  if [[ -d "/Applications/SwiftBar.app" ]]; then
    log "Launching SwiftBar"
    open -a SwiftBar || true
    warn "In SwiftBar, set the plugin folder to: $SWIFTBAR_PLUGIN_DIR"
  else
    warn "SwiftBar is not installed. Install it, then point it at: $SWIFTBAR_PLUGIN_DIR"
  fi
}

verify_install() {
  if command -v habits >/dev/null 2>&1; then
    log "Success: $(command -v habits)"
    printf '\nRun habits to start the tracker.\n'
    return
  fi

  warn "Install finished, but habits is not on PATH in this shell yet."
  warn "Restart your terminal, then run: habits"
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --swiftbar)
        WITH_SWIFTBAR=true
        if [[ $# -gt 1 && "$2" != --* ]]; then
          SWIFTBAR_PLUGIN_DIR="$2"
          shift
        fi
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        warn "Unknown option: $1"
        usage
        exit 1
        ;;
    esac
    shift
  done
}

main() {
  parse_args "$@"

  log "Installing from $REPO_ROOT"
  ensure_python
  ensure_venv
  ensure_pipx
  ensure_pipx_path
  install_global_command

  if [[ "$WITH_SWIFTBAR" == true ]]; then
    install_swiftbar_plugin
  fi

  verify_install
}

main "$@"
