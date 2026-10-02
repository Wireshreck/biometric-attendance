---
type: reference
area: documentation
status: active
tags:
  - agent
  - context
  - entry-point
---
# AI Context — Biometric Attendance

**Updated:** 2026-10-02
**Repository:** `fair/biometric-attendance`
**Working rule:** inspect source, tests, and Git diff before acting. Preserve history and working-tree changes. This owner-requested task explicitly authorizes committing and pushing its completed work to `origin/main`.

## Current project state

- Local-first prototype: ESP32/R307S firmware, FastAPI and SQLite. Backend supports health, admin student lifecycle, enrollment assignment/completion, and authenticated attendance ingestion. A browser dashboard is not implemented.
- Production firmware implements two-capture explicit serial enrollment, fingerprint matching, DS3231 timestamp gating, OLED/indicators, durable LittleFS journal, Wi-Fi reconnect, bearer-authenticated attendance requests, and oldest-first replay with stable event UUIDs. These compile but have no full hardware/integration pass evidence.
- The owner reports R307S red→VIN, black→GND, yellow sensor TX→GPIO32/RX, green GPIO33/TX→sensor RX, blue/white disconnected. Previous read-only diagnostics returned 0 bytes across attempted baud/routing options. This does not prove sensor failure.
- Sensor rail, TX logic level, exact PCB pin mapping/jumper, and sensor health are **UNVERIFIED — REQUIRES MULTIMETER / exact board inspection**. OLED, RTC, indicators, buzzer, storage power-loss behavior, Wi-Fi and backend device requests also need physical testing.
- Pin map source of truth: `docs/final-pin-map.md`; retained earlier audit map at `docs/esp32-pin-map.md` redirects to it. Configure in `firmware/include/config.h` and ignored `firmware/include/local_config.h`.
- Backend API contract source of truth: `backend/app/schemas.py`, `backend/app/auth.py`, `backend/app/main.py`, and `docs/api-plan.md`.

## Evidence

- Current owner/task report says the ESP32 previously uploaded and ran diagnostic firmware. No firmware was flashed or peripheral physically exercised in the current task.
- Backend suite: 10 tests pass using `backend/.venv/Scripts/python.exe -m pytest tests -q`.
- PlatformIO's 27 production/compatibility/component/integration environments compiled in the prior phase. Rebuild production after current implementation; a compile is not a physical pass.
- System Python does not contain backend dependencies; use the ignored repository virtual environment.

## Important limits

- HTTP carries a bearer token in plaintext. Use synthetic data on a private isolated LAN; do not expose publicly or use real student records.
- The firmware queue stores fingerprint slot IDs, UUIDs and timestamps, not images/templates or names. LittleFS data is not encrypted.
- RTC values are local wall time assumed to be India Standard Time (+05:30); no NTP or timezone database exists in firmware. Confirm manual `SETTIME` against a trusted clock.
- Actual R307S capacity is unknown until its exact unit responds. Do not provision a backend sensor capacity by copying an unverified example.
- The first `uploadfs` formats/replaces the device filesystem; never use it if any pending event could exist.

## Start here

Open the repository root as the Obsidian vault and start at [00 - Vault Hub](00%20-%20Vault%20Hub.md). Then read the [AI development guide](08%20-%20Documentation%20Library/AI%20Development%20Guide.md), [project handoff](10%20-%20Workshop/AI%20Project%20Handoff.md), [task tracker](10%20-%20Workshop/TODO.md), [production behavior](docs/production-firmware.md), and [hardware gates](docs/power-and-safety.md). Build with `pio run -d firmware -e production`; run backend tests from `backend/` using `.venv`. Use the isolated component tests before combining hardware.

## Safety and privacy

- No raw fingerprint images/templates leave the sensor or enter logs/backend/exports/AI.
- `.env` and `firmware/include/local_config.h` remain untracked; only blank examples belong in Git.
- Do not use CR2032 as sensor supply; do not touch unknown solder/USB pads or short arbitrary GPIOs.
- Record only tests actually executed. Hardware-dependent checks remain **NOT EXECUTED**, **UNVERIFIED**, or **BLOCKED** until evidence exists.
