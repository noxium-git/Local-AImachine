<#
Build script for Court local installer package.

Usage:
  1. Install PyInstaller if needed:
       pip install pyinstaller
  2. Run this script in PowerShell:
       .\package.ps1

This will build a local one-folder distribution under dist\Court.
#>

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host 'Building Court local package...' -ForegroundColor Cyan

# Ensure PyInstaller is installed
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host 'PyInstaller not found. Installing...' -ForegroundColor Yellow
    python -m pip install pyinstaller
}

$distName = 'Court'
if (-not (Test-Path "storage.json")) {
    Write-Host 'Creating default storage.json...' -ForegroundColor Yellow
    '{}' | Out-File -Encoding utf8 storage.json
}
$specArgs = @(
    '--onefolder',
    '--noconsole',
    "--name=$distName",
    "--add-data=templates;templates",
    "--add-data=static;static",
    "--add-data=storage.json;."
)

Write-Host "Running PyInstaller for launcher.py..." -ForegroundColor Green
pyinstaller @specArgs launcher.py

if (Test-Path "dist\$distName") {
    Write-Host "Build complete: dist\$distName" -ForegroundColor Green
    Write-Host "You can run the bundled app from dist\$distName\$distName.exe" -ForegroundColor White
} else {
    Write-Error "Build failed: dist\$distName not found."
}
