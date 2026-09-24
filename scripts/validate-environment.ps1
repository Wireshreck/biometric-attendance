# Preflight checks for tools and the current bootstrap artifacts; not product tests.
$ErrorActionPreference = 'Continue'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$passed = $true

Write-Host 'Biometric Attendance environment preflight' -ForegroundColor Cyan

foreach ($tool in @('git', 'python', 'pio', 'gh')) {
    $found = Get-Command $tool -ErrorAction SilentlyContinue
    if ($found) {
        $version = & $tool --version 2>&1 | Select-Object -First 1
        Write-Host "[FOUND] $tool : $version" -ForegroundColor Green
    } else {
        Write-Host "[MISSING] $tool is not on PATH" -ForegroundColor Yellow
        if ($tool -in @('python', 'pio')) { $passed = $false }
    }
}

$venvPython = Join-Path $repoRoot 'backend\.venv\Scripts\python.exe'
if (Test-Path -LiteralPath $venvPython) {
    & $venvPython (Join-Path $repoRoot 'backend\test_env.py')
    if ($LASTEXITCODE -eq 0) {
        Write-Host '[PASS] Backend dependency and temporary SQLite/WAL smoke check' -ForegroundColor Green
    } else {
        Write-Host '[FAIL] Backend environment smoke check' -ForegroundColor Red
        $passed = $false
    }
} else {
    Write-Host '[NOT RUN] Create backend/.venv and install requirements-dev.txt first' -ForegroundColor Yellow
}

$firmwareDir = Join-Path $repoRoot 'firmware'
if (Get-Command pio -ErrorAction SilentlyContinue) {
    Push-Location $firmwareDir
    try {
        & pio run
        if ($LASTEXITCODE -ne 0) { $passed = $false }
    } finally { Pop-Location }
} else {
    $passed = $false
}

$ports = [System.IO.Ports.SerialPort]::GetPortNames()
Write-Host "[INFO] Serial ports: $($ports -join ', ')" -ForegroundColor Cyan
if (-not (Test-Path -LiteralPath (Join-Path $repoRoot '.git'))) {
    Write-Host '[INFO] Git metadata is not initialized.' -ForegroundColor Yellow
} else {
    git -C $repoRoot status --short
    if (-not (git -C $repoRoot config --get user.name)) { Write-Host '[INFO] Git author name not configured.' -ForegroundColor Yellow }
    if (-not (git -C $repoRoot config --get user.email)) { Write-Host '[INFO] Git author email not configured.' -ForegroundColor Yellow }
}

if ($passed) { Write-Host 'Preflight checks completed.' -ForegroundColor Green }
else { Write-Host 'One or more required local checks need attention.' -ForegroundColor Red; exit 1 }
