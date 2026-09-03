$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 "$ScriptDir\run_transcribe.py" @args
    exit $LASTEXITCODE
}

if (Get-Command python -ErrorAction SilentlyContinue) {
    & python "$ScriptDir\run_transcribe.py" @args
    exit $LASTEXITCODE
}

Write-Error "Python is required to launch the installed runtime."

