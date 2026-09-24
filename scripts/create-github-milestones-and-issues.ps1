# GitHub Milestone and Issue Provisioning Script
# Legacy filename. This script creates Milestones M0 through M13 only; it does NOT create issues.
# Requires: gh CLI authenticated ('gh auth login')

$ErrorActionPreference = 'Stop'

$origin = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($origin)) {
    Write-Host '[ERROR] Configure and verify the intended GitHub origin before provisioning milestones.' -ForegroundColor Red
    exit 1
}

Write-Host "Checking GitHub CLI authentication..." -ForegroundColor Cyan
$authStatus = gh auth status 2>&1 | Out-String
if ($authStatus -notmatch "Logged in to") {
    Write-Host "[ERROR] GitHub CLI is not authenticated. Please run 'gh auth login' first." -ForegroundColor Red
    Write-Host "Refer to docs/github-setup.md for step-by-step instructions." -ForegroundColor Yellow
    exit 1
}

# Define Milestones with Due Dates (Science Fair: 2026-10-09)
$milestones = @(
    @{ Title = "M0 - Preparation"; Due = "2026-09-24T23:59:59Z"; Desc = "Project bootstrap, environment audit, BOM, wiring, and architectural documentation." },
    @{ Title = "M1 - Hardware Bring-up"; Due = "2026-09-28T23:59:59Z"; Desc = "Bench validation of ESP32, AS608, SSD1306 OLED, DS3231 RTC, and audio-visual indicators." },
    @{ Title = "M2 - Fingerprint Enrollment"; Due = "2026-09-29T23:59:59Z"; Desc = "Implement and validate consented sensor enrollment, bounded capture flow, and slot mapping. Template internals are sensor-managed and unverified." },
    @{ Title = "M3 - Fingerprint Recognition"; Due = "2026-09-30T23:59:59Z"; Desc = "Implement sensor match-result handling and local feedback; do not claim confidence metrics unless exposed and validated." },
    @{ Title = "M4 - Attendance Engine"; Due = "2026-10-01T23:59:59Z"; Desc = "Hardware DS3231 RTC timestamping, duplicate scan suppression, and local LittleFS offline buffering." },
    @{ Title = "M5 - Networking"; Due = "2026-10-02T23:59:59Z"; Desc = "ESP32 Wi-Fi station connectivity, reconnection state machine, and HTTP client sync." },
    @{ Title = "M6 - Backend"; Due = "2026-10-03T23:59:59Z"; Desc = "Python FastAPI application scaffolding, configuration, and event processing service." },
    @{ Title = "M7 - Database"; Due = "2026-10-03T23:59:59Z"; Desc = "SQLite3 relational schema, WAL mode, foreign keys, and indexes for students and attendance." },
    @{ Title = "M8 - REST API"; Due = "2026-10-04T23:59:59Z"; Desc = "Implement documented authenticated /api/v1 endpoints for students, devices, attendance, events, and reports." },
    @{ Title = "M9 - Web Dashboard"; Due = "2026-10-04T23:59:59Z"; Desc = "Responsive HTML5/CSS/JS dashboard displaying live attendance feed and daily metrics." },
    @{ Title = "M10 - Testing"; Due = "2026-10-06T23:59:59Z"; Desc = "Comprehensive end-to-end integration testing, offline recovery verification, and 50-scan stress run." },
    @{ Title = "M11 - Privacy/Security"; Due = "2026-10-07T23:59:59Z"; Desc = "Review access control, retention/deletion, audit events, transport limits, and biometric-data minimization; no unverified template privacy claims." },
    @{ Title = "M12 - Science Fair"; Due = "2026-10-08T23:59:59Z"; Desc = "Demonstration rehearsals, physical acrylic rig mounting, and 3-2-1 backup freeze." },
    @{ Title = "M13 - Optional AI"; Due = "2026-10-08T23:59:59Z"; Desc = "Optional local Ollama read-only tool-calling conversational reporting adapter." }
)

$existingTitles = gh api repos/:owner/:repo/milestones -f state=all --paginate --jq '.[].title' 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host '[ERROR] Could not read milestones for the configured repository.' -ForegroundColor Red
    exit 1
}

Write-Host "Creating missing milestones (no issues are created)..." -ForegroundColor Cyan
foreach ($m in $milestones) {
    if ($existingTitles -contains $m.Title) {
        Write-Host "Already exists: $($m.Title)"
        continue
    }
    Write-Host "Creating Milestone: $($m.Title)"
    gh api repos/:owner/:repo/milestones -f title="$($m.Title)" -f due_on="$($m.Due)" -f description="$($m.Desc)" | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Failed to create milestone: $($m.Title)" }
}

Write-Host "Milestones checked/provisioned successfully. No issues were created." -ForegroundColor Green
