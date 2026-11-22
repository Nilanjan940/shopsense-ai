$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Venv = Join-Path $Root ".venv"

Write-Host "`n=== ShopSense AI Environment Setup ===" -ForegroundColor Cyan

# Check Python
$Python = Get-Command python -ErrorAction SilentlyContinue

if (-not $Python) {
    throw "Python is not installed or not available in PATH."
}

python --version

# Validate Python version
$Version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$Parts = $Version.Split(".")
$Major = [int]$Parts[0]
$Minor = [int]$Parts[1]

if ($Major -lt 3 -or ($Major -eq 3 -and $Minor -lt 9)) {
    throw "Python 3.9 or later is required."
}

Write-Host "[OK] Python version verified." -ForegroundColor Green

# Create virtual environment
if (-not (Test-Path $Venv)) {
    Write-Host "Creating virtual environment..."
    python -m venv $Venv
}
else {
    Write-Host "Virtual environment already exists."
}

# Verify virtual environment
$VenvPython = Join-Path $Venv "Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    throw "Virtual environment Python executable was not created."
}

& $VenvPython --version

# Verify standard-library modules
& $VenvPython -c "import csv, json, re, pathlib, logging, unittest; print('Standard library checks passed.')"

Write-Host "`n[OK] Environment setup complete." -ForegroundColor Green
Write-Host "Environment: $Venv"
Write-Host "`nActivate it using:"
Write-Host ".\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
