# Build the Windows executables with PyInstaller.
# Produces dist/BiometricDesktop.exe, dist/test.exe, dist/install.exe.
# Firmware (.bin) is built separately with PlatformIO; see docs/setup.md.
param(
  [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

& $Python -m pip install --quiet pyinstaller bleak pyserial
& $Python -m PyInstaller --noconfirm --onefile --windowed `
  --name BiometricDesktop `
  --paths shared `
  desktop/app.py
& $Python -m PyInstaller --noconfirm --onefile --windowed `
  --name test `
  --paths shared `
  tools/test_app/test_app.py
& $Python -m PyInstaller --noconfirm --onefile --windowed `
  --name install `
  --paths shared `
  tools/installer/install_app.py

Get-ChildItem dist/BiometricDesktop.exe, dist/test.exe, dist/install.exe |
  Select-Object Name, Length, LastWriteTime
