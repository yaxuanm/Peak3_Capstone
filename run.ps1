param(
  [Parameter(Mandatory=$true)] [string]$ExcelPath,
  [Parameter(Mandatory=$true)] [string]$ConfigPath,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Prefer venv if present
$venvPython = Join-Path -Path "." -ChildPath ".venv/Scripts/python.exe"
if (Test-Path $venvPython) {
  $python = $venvPython
} else {
  $python = "python"
}

# Install deps if needed (idempotent)
if (-not (Test-Path "requirements.txt")) {
  Write-Host "requirements.txt not found" -ForegroundColor Yellow
} else {
  Write-Host "Installing dependencies..."
  pip install -r requirements.txt | Out-Null
}

$dry = ""
if ($DryRun) { $dry = "-DryRun" }

& $python -m src.convert -ExcelPath "$ExcelPath" -ConfigPath "$ConfigPath" $dry
