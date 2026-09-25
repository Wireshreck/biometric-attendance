---
type: build-manual
status: IN PROGRESS
updated: 2026-09-25
---

# 18 - Complete Build Guide

This is the canonical human build procedure. **It is not yet a verified physical build recipe.** Exact board/sensor/breakout revisions, purchases, electrical measurements, sensor behavior, and all GPIO connections are unconfirmed. Follow the stop gates below; do not energize an unverified wiring plan. The current software can be developed and API-tested without hardware. The API accepts synthetic records only and local HTTP is unencrypted.

## 00. Prerequisites

- Windows 10/11 or a current supported developer OS; Python 3.11+ (the checked environment used Python 3.13), Git, PowerShell, PlatformIO Core, and a browser.
- For the physical build: exact ESP32 board/module, fingerprint module, OLED, DS3231 breakout and correct battery, LEDs/resistors, buzzer/driver, USB supply/cable, breadboard and jumpers. Procurement/delivery and revisions are **UNKNOWN**; see [[16 - Purchase Checklist]] and `docs/purchase-checklist.md`.
- Read `docs/wiring.md`, `hardware/pinout.md`, and `hardware/test-plan.md`. Their assignments are provisional, not authority to connect power.

## 01–03. Inventory, identification, and electrical safety

Record manufacturer/markings/revision, pin labels, supply range, interface logic levels, onboard pull-ups/driver, and source document for every module in `hardware/test-plan.md`. Wire colors are not pin evidence. Identify WROOM vs WROVER and the exact sensor/breakout manuals before using the provisional GPIO map. ESP32 GPIO is 3.3 V and is not 5 V tolerant. Disconnect USB before rewiring. Do not use an RTC coin cell until the board's charge circuit and compatible cell type are confirmed; never charge a primary CR2032. Stop if a pin, voltage, polarity, or logic level is uncertain.

## 04–11. Breadboard, controller, peripherals, and power

The current signal proposal in `docs/wiring.md` is: AS608 UART on GPIO16/17; shared OLED/RTC I2C on GPIO21/22; green/red LEDs on GPIO18/19 through series resistors; active buzzer module input on GPIO23 through a driver. These assignments are **PROVISIONAL / NEEDS HARDWARE**; GPIO16/17 may conflict with PSRAM on some boards. Do not copy this table into firmware or wire it until exact hardware is checked and `hardware/pinout.md` is updated from bench evidence.

There is no verified total-current budget or final power topology. Do not power an unknown sensor/buzzer from an ESP32 GPIO. Confirm each supply range, signal high level, pull-up rail, resistor/driver, polarity, common-ground need, board regulator capacity, and peak Wi-Fi load using exact datasheets and measurements. Only then create a one-component-at-a-time wiring record in `docs/wiring.md`; keep the laptop USB supply within board/module limits. The exact final breadboard positions and power connections are **UNKNOWN** until those checks are recorded.

## 12. Component-by-component bring-up

Use `hardware/test-plan.md` as the evidence record. For each test: keep other peripherals disconnected; record setup, exact board/module, meter/logic evidence, action, expected result taken from that exact component's documentation, observed result, and recovery. If the expected result cannot be sourced, do not energize the component.

| Component | Safe first check | Pass evidence | Failure/recovery |
| --- | --- | --- | --- |
| ESP32 | USB only; identify serial port and exact board marking | Stable serial enumeration and successful upload of a known minimal sketch | Try known data cable/port and documented driver; stop if board heats or supply collapses |
| AS608 | Exact VCC/logic datasheet, then separately powered UART with common ground and measured levels | Sensor responds to documented protocol/baud; exact capacity and commands recorded | Disconnect, recheck pin labels/baud/logic level; no enrollment/matching claims without a controlled test |
| OLED | Verify supply and pull-up rail first; scan I2C at 100 kHz | Address and test pattern agree with exact module documentation | Power off; inspect SDA/SCL swap/address/pull-ups; do not raise bus to 5 V |
| DS3231 | Verify breakout charge circuit and correct battery type before fitting cell | I2C responds; set/read time and power-cycle persistence logged | Check address, bus voltage and battery circuit; remove incompatible cell immediately |
| LEDs | Identify polarity; use series resistor calculated from verified LED/rail values | Each LED lights only in commanded test with measured safe current | Power off; check polarity/resistor/GPIO mapping |
| Buzzer | Identify active/passive type and driver/current from its exact documentation | Driver-controlled test produces documented output without GPIO overload | Disconnect; never drive an unknown/high-current load directly from GPIO |

No individual physical component test has been run. Results are **NEEDS HARDWARE**.

## 13–15. Firmware, flashing, and enrollment

From the repository root, compile with `pio run -d .\firmware`. This compile-only validation sketch passed on 2026-09-25. Flashing requires the identified board: `pio run -d .\firmware -t upload`; serial monitor: `pio device monitor -d .\firmware -b 115200`. Neither upload nor physical firmware behavior is verified. `firmware/include/local_config.example.h` is a template; copy it to ignored `firmware/include/local_config.h` only after the firmware integration is implemented. Do not enter real Wi-Fi credentials.

Attendance firmware, RTC handling, fingerprint enrollment/matching, feedback, Wi-Fi client, and offline queue are not implemented. Do not enroll real or student fingerprints. A future enrollment procedure must use an explicitly consenting adult synthetic identity, allocate a pending slot from the API, perform and verify the exact sensor's two-impression procedure locally, then call the device enrollment completion route only after sensor write/readback succeeds. That device procedure does not exist yet.

## 16–18. Backend installation, database, and API

From PowerShell at the repository root:

```powershell
Push-Location .\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Edit `backend/.env` with a unique synthetic-demo `ADMIN_USERNAME`, an `ADMIN_PASSWORD` at least 16 characters long, `DATABASE_PATH=data/attendance.db`, `APP_TIMEZONE=Asia/Kolkata`, and `MAX_CLOCK_SKEW_SECONDS=300`. Keep `.env` private and ignored. Start the service with `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`. Startup validates settings and applies ordered SQLite migrations. Check `http://127.0.0.1:8000/health` (expected `{"status":"ok","schema_version":1}`) and `/docs`. Run `python -m pytest tests -q` and `python test_env.py`. The DB is `backend/data/attendance.db`; do not commit it. Schema and duplicate policy are canonical in `docs/database-plan.md`.

Create one device locally only after verifying its actual sensor capacity. In PowerShell, set `$verifiedCapacity = Read-Host "Enter the capacity verified for this sensor"`, then run `python -m app.provision_device --name "Demo terminal" --location "Lab" --sensor-capacity $verifiedCapacity`. The CLI prints a random bearer token once; put it only in ignored local firmware config and do not save it in notes/issues. The implemented routes are documented in `docs/api-plan.md`; student creation reserves a slot and requires one active device with reported capacity. API tests exercise a synthetic device seeded directly into a temporary test database. Device provisioning does not verify sensor compatibility.

## 19–21. Dashboard, network, terminal integration

The frontend has no implemented pages or assets; there is no dashboard to start. Do not expose the service to a LAN yet. Current HTTP/Bearer/Basic behavior is acceptable only for synthetic data on an isolated demo LAN; do not port-forward or use live student information. Firmware-to-backend integration is not available. After implementation, bind only to the required LAN interface, scope the host firewall, confirm the laptop's current IP, and test authenticated device requests before connecting a terminal.

## 22–25. Offline, attendance, synchronization, and system test

LittleFS persistence, chronological retry, firmware-generated UUIDs, RTC timestamps, device acknowledgements, dashboard reporting, and full-system sync are **PLANNED**. The API currently implements server-side UUID idempotency and same-student suppression at a 60-second inclusive boundary; later same-day events are allowed. Use the exact API tests for software evidence; do not present those tests as terminal/biometric behavior. End-to-end procedure is blocked until firmware, frontend, and hardware gates pass.

## 26. Troubleshooting

| Symptom | Possible cause | Diagnostic | Recovery |
| --- | --- | --- | --- |
| ESP32 absent/upload fails | Cable, USB driver, port, board mismatch | Check Device Manager, cable data capability, exact board and PlatformIO output | Try known data cable/port and documented driver; do not change board target blindly |
| AS608 absent/UART errors | Wrong pin labels, baud, logic voltage, power or module variant | Recheck exact datasheet and measure idle TX level; use serial diagnostics once implemented | Disconnect; correct verified wiring/config; no 5 V signal to ESP32 GPIO |
| OLED blank / I2C scan empty | Wrong address, SDA/SCL, pull-up rail, supply | Power-off continuity and rail check, then 100 kHz scan | Correct only from module labels/docs; ensure bus pull-ups do not exceed 3.3 V |
| RTC time wrong / lost | Invalid set time, backup cell/charge mismatch, bus fault | Read back after set and power cycle; inspect breakout circuit | Correct time and documented battery configuration; never fit an unverified cell |
| LED/buzzer silent or hot | Polarity, resistor/driver, GPIO or module mismatch | Disconnect load; verify exact module and current path | Recalculate/provide driver from verified specs; never drive load directly if current is unknown |
| API will not start | Missing/short admin secret, invalid timezone, migration failure | Inspect local console; check `.env` and database path without sharing secrets | Set unique 16+ character demo password, valid IANA timezone, preserve DB for diagnosis |
| Attendance returns 401/409/422 | Invalid/revoked token, enrollment state/slot mismatch, malformed or skewed time | Check error code, device status and synthetic DB assignment; never log token | Re-provision/reconcile locally; correct timestamp/assignment; do not bypass checks |
| Dashboard/network/offline sync fails | Not implemented in current repository | Confirm frontend assets/firmware client are still absent | Do not troubleshoot nonexistent features as if they were operational; complete API-03 and firmware/UI milestones first |

## 27–29. Demonstration, backup, and final verification

The demo script is `presentation/demo-script.md`; clearly identify software simulation versus physical evidence. Before a demonstration, create and restore a synthetic-only database backup using `scripts/backup-project.ps1`; the script's ZIP is not encrypted. Never carry real identity or biometric data in backups. Mark each item in this table only after attaching the evidence to the relevant test record.

| Gate | Current state |
| --- | --- |
| Exact components identified, wiring/revisions/voltage verified | NEEDS HARDWARE |
| Individual sensor/OLED/RTC/LED/buzzer tests | NEEDS HARDWARE |
| Firmware compile | VERIFIED (compile only) |
| Firmware upload, enrollment, match, RTC, indicators, offline queue | NEEDS HARDWARE / NOT IMPLEMENTED |
| Backend environment, migrations, API tests | VERIFIED (10 tests, synthetic/temp DB only) |
| Attendance firmware and dashboard | PLANNED |
| Full terminal-to-dashboard sync, duplicate/offline recovery | NEEDS HARDWARE; integration not implemented |
| Backup restore and complete demo rehearsal | NEEDS TESTING |

The build guide is not complete until exact purchased parts and authoritative electrical specifications are recorded, wiring is bench-verified, hardware tests are logged, the firmware/frontend integration exists, and the end-to-end checklist passes. Update this guide from that evidence rather than guessing.
