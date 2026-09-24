# Content snapshot for the Biometric Attendance project.
# Does not encrypt archives and excludes local secrets and runtime data by default.
param (
    [string]$Destination,
    [switch]$IncludeSyntheticDemoDatabase
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if ([string]::IsNullOrWhiteSpace($Destination)) {
    $Destination = Join-Path (Split-Path $repoRoot -Parent) 'backups'
}
$Destination = [System.IO.Path]::GetFullPath($Destination)
if (-not (Test-Path -LiteralPath $Destination)) {
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
}

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$targetZip = Join-Path $Destination "biometric-attendance_backup_$timestamp.zip"
$tempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
$stageName = "bio_attendance_stage_$([guid]::NewGuid().ToString('N'))"
$tempStage = Join-Path $tempRoot $stageName
if (-not $tempStage.StartsWith($tempRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Refusing to create staging directory outside the system temporary directory.'
}
New-Item -ItemType Directory -Path $tempStage | Out-Null

try {
    $includeItems = @(
        'README.md', 'LICENSE', 'CONTRIBUTING.md', 'SECURITY.md', '.gitignore',
        '.github', '.obsidian', 'docs', 'diagrams', 'hardware', 'firmware',
        'backend', 'frontend', 'scripts', 'presentation', 'obsidian'
    )
    foreach ($item in $includeItems) {
        $srcPath = Join-Path $repoRoot $item
        if (Test-Path -LiteralPath $srcPath) {
            Copy-Item -LiteralPath $srcPath -Destination $tempStage -Recurse -Force
        }
    }

    # Remove caches, local secrets, SQLite files and journals from the staged copy only.
    foreach ($name in @('.pio', '.venv', 'venv', 'node_modules', '__pycache__', '.pytest_cache')) {
        Get-ChildItem -LiteralPath $tempStage -Directory -Force -Recurse -Filter $name |
            ForEach-Object { Remove-Item -LiteralPath $_.FullName -Recurse -Force }
    }
    Get-ChildItem -LiteralPath $tempStage -File -Force -Recurse | Where-Object {
        ($_.Name -like '.env*' -and $_.Name -ne '.env.example') -or
        $_.Name -eq 'local_config.h' -or $_.Name -match '\.(db|db-shm|db-wal|db-journal)$'
    } | ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force }

    if ($IncludeSyntheticDemoDatabase) {
        Write-Warning 'The archive is unencrypted. Include a database only when it contains synthetic demo data.'
        $dbSource = Join-Path $repoRoot 'backend\data\attendance.db'
        if (Test-Path -LiteralPath $dbSource) {
            $dbTarget = Join-Path $tempStage 'backend\data\attendance.db'
            New-Item -ItemType Directory -Path (Split-Path $dbTarget -Parent) -Force | Out-Null
            $dbPython = Join-Path $repoRoot 'backend\.venv\Scripts\python.exe'
            if (-not (Test-Path -LiteralPath $dbPython)) { $dbPython = (Get-Command python).Source }
            $backupCode = @'
import sqlite3, sys
source = sqlite3.connect(sys.argv[1])
target = sqlite3.connect(sys.argv[2])
try:
    source.backup(target)
finally:
    target.close()
    source.close()
'@
            & $dbPython -c $backupCode $dbSource $dbTarget
            if ($LASTEXITCODE -ne 0) { throw 'SQLite online backup failed.' }
        } else {
            Write-Warning 'No runtime database found; no database was added.'
        }
    }

    $null = git -C $repoRoot rev-parse --verify HEAD 2>$null
    if ($LASTEXITCODE -eq 0) {
        $bundlePath = Join-Path $tempStage 'git-history.bundle'
        git -C $repoRoot bundle create $bundlePath --all
        if ($LASTEXITCODE -ne 0) { throw 'Git bundle creation failed.' }
        git -C $repoRoot bundle verify $bundlePath
        if ($LASTEXITCODE -ne 0) { throw 'Git bundle verification failed.' }
    } else {
        Write-Warning 'No commit exists; this archive will not contain Git history.'
    }

    $manifest = @(
        'Biometric Attendance content backup',
        "Created: $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssK')",
        "Source: $repoRoot",
        "Database included: $([bool]$IncludeSyntheticDemoDatabase)",
        'Secrets and local config excluded. Archive is not encrypted.'
    ) -join [Environment]::NewLine
    Set-Content -LiteralPath (Join-Path $tempStage 'BACKUP-MANIFEST.txt') -Value $manifest -Encoding utf8

    if (Test-Path -LiteralPath $targetZip) { throw "Backup already exists: $targetZip" }
    Compress-Archive -Path (Join-Path $tempStage '*') -DestinationPath $targetZip
    Write-Host "Content snapshot created: $targetZip" -ForegroundColor Green
    Write-Host 'Restore to a new directory and verify it; this ZIP is not encrypted.' -ForegroundColor Yellow
} finally {
    if (Test-Path -LiteralPath $tempStage) {
        Remove-Item -LiteralPath $tempStage -Recurse -Force
    }
}
