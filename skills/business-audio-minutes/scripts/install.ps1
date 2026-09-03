$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$InstallerArgs = @($args)
$Candidates = @(
    @{ Command = "py"; Prefix = @("-3.12") },
    @{ Command = "py"; Prefix = @("-3.11") },
    @{ Command = "py"; Prefix = @("-3.10") },
    @{ Command = "py"; Prefix = @("-3") },
    @{ Command = "python"; Prefix = @() },
    @{ Command = "python3"; Prefix = @() }
)

foreach ($Candidate in $Candidates) {
    if (-not (Get-Command $Candidate.Command -ErrorAction SilentlyContinue)) {
        continue
    }
    & $Candidate.Command @($Candidate.Prefix) -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        & $Candidate.Command @($Candidate.Prefix) "$ScriptDir\install.py" @InstallerArgs
        exit $LASTEXITCODE
    }
}

Write-Error "Python 3.10 or newer is required. Install Python, reopen PowerShell, and rerun this script."
