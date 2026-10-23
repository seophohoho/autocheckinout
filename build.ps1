# Build autocheck/install/uninstall exe into dist\.  Usage: powershell -ExecutionPolicy Bypass -File build.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$py = ".\.venv\Scripts\python.exe"

& $py -m PyInstaller --noconfirm --onefile --noconsole --name autocheck autocheck.py
& $py -m PyInstaller --noconfirm --onefile --console --name install install.py
& $py -m PyInstaller --noconfirm --onefile --console --name uninstall uninstall.py
Copy-Item .env.example, README.md dist\ -Force

Write-Host "`nBuild done: $PSScriptRoot\dist"
