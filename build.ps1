# Build autocheck/install/uninstall exe into dist\.  Usage: powershell -ExecutionPolicy Bypass -File build.ps1
# Creates .venv and installs requirements.txt on first run.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$py = ".\.venv\Scripts\python.exe"

function Invoke-Step($what, [scriptblock]$cmd) {
    & $cmd
    if ($LASTEXITCODE -ne 0) { throw "$what failed (exit code $LASTEXITCODE)" }
}

if (-not (Test-Path $py)) {
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        throw "Python not found. Install Python 3.10+ from https://www.python.org/downloads/ and check 'Add python.exe to PATH'."
    }
    Write-Host "[1/3] Creating virtual environment (.venv)"
    Invoke-Step "venv" { python -m venv .venv }
}

Write-Host "[2/3] Installing packages (requirements.txt)"
Invoke-Step "pip install" { & $py -m pip install -q --disable-pip-version-check -r requirements.txt }

Write-Host "[3/3] Building exe files (takes about 1 minute)"
Invoke-Step "autocheck build" { & $py -m PyInstaller --noconfirm --log-level WARN --onefile --noconsole --name autocheck autocheck.py }
Invoke-Step "install build" { & $py -m PyInstaller --noconfirm --log-level WARN --onefile --console --name install install.py }
Invoke-Step "uninstall build" { & $py -m PyInstaller --noconfirm --log-level WARN --onefile --console --name uninstall uninstall.py }
Copy-Item .env.example, README.md dist\ -Force

Write-Host "`nBuild done: $PSScriptRoot\dist"
