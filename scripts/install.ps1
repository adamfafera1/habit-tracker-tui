# Install habit-tracker-tui on Windows.

param(
    [switch]$Help
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

function Write-Step {
    param([string]$Message)
    Write-Host "==> $Message"
}

function Write-Warn {
    param([string]$Message)
    Write-Warning $Message
}

function Show-Usage {
    @"
Install habit-tracker-tui on Windows.

Usage: .\scripts\install.ps1

After install, run: habits

Use Windows Terminal for the best experience.
"@
}

function Test-PythonVersion {
    param([string]$PythonCommand)

    $versionCheck = & $PythonCommand -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
    if ($LASTEXITCODE -ne 0) {
        throw "Python 3.11+ is required."
    }
}

function Ensure-Python {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        throw "Python was not found. Install Python 3.11+ from https://www.python.org/downloads/"
    }

    Test-PythonVersion "python"
}

function Ensure-Venv {
    if (-not (Test-Path $VenvPython)) {
        Write-Step "Creating virtual environment"
        python -m venv (Join-Path $RepoRoot ".venv")
    }

    Write-Step "Installing project into .venv"
    & $VenvPython -m pip install --upgrade pip
    & $VenvPython -m pip install -e $RepoRoot
}

function Ensure-Pipx {
    python -m pipx --version 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        return
    }

    Write-Step "pipx not found; installing it"
    python -m pip install --user pipx
}

function Install-GlobalCommand {
    Write-Step "Installing global habits command with pipx"
    python -m pipx ensurepath 2>$null
    python -m pipx install -e $RepoRoot --force
}

function Verify-Install {
    $habits = Get-Command habits -ErrorAction SilentlyContinue
    if ($habits) {
        Write-Step "Success: $($habits.Source)"
        Write-Host ""
        Write-Host "Run habits to start the tracker."
        return
    }

    Write-Warn "Install finished, but habits is not on PATH in this shell yet."
    Write-Warn "Restart PowerShell or Windows Terminal, then run: habits"
}

if ($Help) {
    Show-Usage
    exit 0
}

Write-Step "Installing from $RepoRoot"
Ensure-Python
Ensure-Venv
Ensure-Pipx
Install-GlobalCommand
Verify-Install
