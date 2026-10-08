# Backend server manager: start, stop, restart, status, logs.
# Usage:
#   scripts/server.ps1 start     # start uvicorn detached (backend/.env required)
#   scripts/server.ps1 stop      # stop it
#   scripts/server.ps1 restart   # stop + start (use after editing .env or code)
#   scripts/server.ps1 status    # PID, port, health
#   scripts/server.ps1 logs      # tail the server log
param([string]$Action = "status")

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$pidFile = Join-Path $env:TEMP "biometric-uvicorn.pid"
$logFile = Join-Path $env:TEMP "biometric-uvicorn.log"
$port = 8000

function Get-ServerPid {
    if (Test-Path $pidFile) {
        $saved = Get-Content $pidFile -ErrorAction SilentlyContinue
        if ($saved -and (Get-Process -Id $saved -ErrorAction SilentlyContinue)) { return [int]$saved }
    }
    $found = Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like "*uvicorn*app.main:app*" }
    if ($found) { return $found[0].ProcessId }
    return $null
}

function Test-PortOpen {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $iar = $client.BeginConnect("127.0.0.1", $port, $null, $null)
        if ($iar.AsyncWaitHandle.WaitOne(1500)) { $client.EndConnect($iar); return $true }
        return $false
    } catch { return $false } finally { $client.Close() }
}

function Get-Health {
    try {
        (Invoke-WebRequest -Uri "http://127.0.0.1:$port/health" -UseBasicParsing -TimeoutSec 5).Content
    } catch { $null }
}

switch ($Action) {
    "start" {
        if (Get-ServerPid) { Write-Output "Server already running."; exit 0 }
        if (Test-PortOpen) { Write-Output "Port $port is busy. Stop that first."; exit 1 }
        if (-not (Test-Path (Join-Path $backend ".env"))) {
            Write-Output "backend/.env missing. Copy backend/.env.example first."
            exit 1
        }
        Start-Process python -ArgumentList "-m", "uvicorn", "app.main:app",
            "--host", "127.0.0.1", "--port", "$port", "--access-log" `
            -WorkingDirectory $backend -RedirectStandardOutput $logFile -WindowStyle Hidden
        for ($i = 0; $i -lt 15; $i++) {
            Start-Sleep 1
            $health = Get-Health
            if ($health) {
                Get-ServerPid | Set-Content $pidFile
                Write-Output "Started. Health: $health"
                Write-Output "Console: http://127.0.0.1:$port/"
                exit 0
            }
        }
        Write-Output "Did not become healthy. See: scripts/server.ps1 logs"
        exit 1
    }
    "stop" {
        $srvPid = Get-ServerPid
        if (-not $srvPid) { Write-Output "Not running."; exit 0 }
        Stop-Process -Id $srvPid -Force
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
        Write-Output "Stopped."
    }
    "restart" {
        & $PSCommandPath stop
        Start-Sleep 2
        & $PSCommandPath start
    }
    "status" {
        $srvPid = Get-ServerPid
        if ($srvPid) {
            Write-Output "Running (PID $srvPid). Health: $(Get-Health)"
        } else {
            Write-Output "Not running."
        }
    }
    "logs" {
        if (Test-Path $logFile) { Get-Content $logFile -Tail 30 } else { Write-Output "No log yet." }
    }
    default { Write-Output "Usage: scripts/server.ps1 {start|stop|restart|status|logs}" }
}
