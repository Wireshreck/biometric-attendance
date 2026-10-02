---
type: build-manual
status: IN PROGRESS
updated: 2026-09-29
---

# 18 - Complete Build Guide

This is the Obsidian construction/verification index. The step-by-step current procedures are [beginner assembly](../../docs/COMPLETE-BEGINNER-ASSEMBLY-GUIDE.md), [recommended breadboard layout](../../docs/complete-breadboard-layout.md), [final pin map](../../docs/final-pin-map.md), [software setup](../../docs/COMPLETE-SOFTWARE-SETUP.md), and [science fair setup](../../docs/SCIENCE-FAIR-SETUP.md). This remains **not a physically verified build recipe**: exact board/sensor/breakout revisions, electrical measurements and working sensor behavior are unconfirmed. Local HTTP is unencrypted; use synthetic records only.

## 00. Prerequisites

- Windows 10/11 or a current supported developer OS; Python 3.11+ (the checked environment used Python 3.13), Git, PowerShell, PlatformIO Core, and a browser.
- For the physical build: exact ESP32 board/module, fingerprint module (**owner identified as R307S; assembled wiring has returned zero UART bytes; exact PCB mapping/supply/signal levels UNVERIFIED — REQUIRES MULTIMETER / board inspection**), OLED, DS3231 breakout and correct battery, LEDs/resistors, buzzer/driver, USB supply/cable, breadboard and jumpers. Other procurement/delivery and revisions are **UNKNOWN**; see [[16 - Purchase Checklist]] and `docs/purchase-checklist.md`.
- Read `docs/wiring.md`, `hardware/pinout.md`, and `hardware/test-plan.md`. Their assignments are provisional, not authority to connect power.

## 01–03. Inventory, identification, and electrical safety

Record manufacturer/markings/revision, pin labels, supply range, interface logic levels, onboard pull-ups/driver, and source document for every module in `hardware/test-plan.md`. Wire colors are not pin evidence. Identify WROOM vs WROVER and the exact sensor/breakout manuals before using the provisional GPIO map. ESP32 GPIO is 3.3 V and is not 5 V tolerant. Disconnect USB before rewiring. Do not use an RTC coin cell until the board's charge circuit and compatible cell type are confirmed; never charge a primary CR2032. Stop if a pin, voltage, polarity, or logic level is uncertain.

## 04–11. Breadboard, controller, peripherals, and power

Current assignments are in `docs/final-pin-map.md`: reported R307S UART GPIO32/33; shared OLED/RTC I2C GPIO21/22; green/red LEDs GPIO18/19 through series resistors; buzzer GPIO23 if its module is compatible. Peripheral wiring is provisional except owner-reported sensor assembly; exact sensor mapping and voltage remain unverified.

There is no verified total-current budget or final power topology. Do not power an unknown sensor/buzzer from an ESP32 GPIO. Confirm each supply range, signal high level, pull-up rail, resistor/driver, polarity, common-ground need, board regulator capacity, and peak Wi-Fi load using exact datasheets and measurements. Only then create a one-component-at-a-time wiring record in `docs/wiring.md`; keep the laptop USB supply within board/module limits. The exact final breadboard positions and power connections are **UNKNOWN** until those checks are recorded.

## 12. Component-by-component bring-up

Use `hardware/test-plan.md` as the evidence record. For each test: keep other peripherals disconnected; record setup, exact board/module, meter/logic evidence, action, expected result taken from that exact component's documentation, observed result, and recovery. If the expected result cannot be sourced, do not energize the component.

| Component | Safe first check | Pass evidence | Failure/recovery |
| --- | --- | --- | --- |
| ESP32 | USB only; identify serial port and exact board marking | Stable serial enumeration and successful upload of a known minimal sketch | Try known data cable/port and documented driver; stop if board heats or supply collapses |
| R307S | Inspect exact PCB/connector/jumper, safely measure rail and TX level, then run preserved read-only diagnostic | Valid sensor ACK and system parameters; record exact observations. Prior owner-reported diagnostic returned 0 bytes. | Do not infer dead/alive; stop and resolve power/pin uncertainty before additional electrical changes. |
| OLED | Verify supply and pull-up rail first; scan I2C at 100 kHz | Address and test pattern agree with exact module documentation | Power off; inspect SDA/SCL swap/address/pull-ups; do not raise bus to 5 V |
| DS3231 | Verify breakout charge circuit and correct battery type before fitting cell | I2C responds; set/read time and power-cycle persistence logged | Check address, bus voltage and battery circuit; remove incompatible cell immediately |
| LEDs | Identify polarity; use series resistor calculated from verified LED/rail values | Each LED lights only in commanded test with measured safe current | Power off; check polarity/resistor/GPIO mapping |
| Buzzer | Identify active/passive type and driver/current from its exact documentation | Driver-controlled test produces documented output without GPIO overload | Disconnect; never drive an unknown/high-current load directly from GPIO |

No individual physical component test has been run. Results are **NEEDS HARDWARE**.

## 13–15. Firmware, flashing, and enrollment

Build production with `pio run -d firmware -e production`; component and integration builds are listed in `docs/component-tests.md` and `docs/integration-tests.md`. Upload only after the test safety gate: `pio run -d firmware -e production -t upload --upload-port COMx`; serial monitor: `pio device monitor -d firmware --port COMx --baud 115200`. Build is not hardware verification. Copy `firmware/include/local_config.example.h` to ignored `local_config.h` only for an isolated synthetic demo.

Firmware implements RTC-gated events, enrollment/matching, local feedback, Wi-Fi client and offline journal/replay. These are source/build capabilities, not verified on the physical assembly. Do not enroll real or student fingerprints. Enrollment is an explicit USB serial `ENROLL <student-uuid>` workflow requiring a pending backend assignment and two captures; the current sensor's zero-byte report blocks physical validation.

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

The frontend has no implemented pages/assets; there is no dashboard to start. Keep the API on a private demo LAN only when an ESP32 needs it; never port-forward or use live student information. Firmware has a bearer-authenticated client that sends only after local queue write; actual device/backend integration is not tested.

## 22–25. Offline, attendance, synchronization, and system test

Firmware source implements bounded LittleFS persistence/replay, UUIDv4, RTC timestamps and API acknowledgement. The backend implements UUID idempotency and same-student suppression within 60 seconds; later same-day events are allowed. Queue power-loss/network replay and full end-to-end procedure remain NEEDS HARDWARE. Dashboard reporting remains planned. API tests are software evidence, not terminal/biometric evidence.

## 26. Troubleshooting

| Symptom | Possible cause | Diagnostic | Recovery |
| --- | --- | --- | --- |
| ESP32 absent/upload fails | Cable, USB driver, port, board mismatch | Check Device Manager, cable data capability, exact board and PlatformIO output | Try known data cable/port and documented driver; do not change board target blindly |
| R307S absent/UART errors | Unverified exact pin mapping, rail, jumper, UART level, address, module state, or library compatibility | Follow `docs/next-steps.md`, then run the preserved read-only diagnostic after the electrical safety gate | Do not assume failed or powered; no 5 V signal to ESP32 GPIO |
| OLED blank / I2C scan empty | Wrong address, SDA/SCL, pull-up rail, supply | Power-off continuity and rail check, then 100 kHz scan | Correct only from module labels/docs; ensure bus pull-ups do not exceed 3.3 V |
| RTC time wrong / lost | Invalid set time, backup cell/charge mismatch, bus fault | Read back after set and power cycle; inspect breakout circuit | Correct time and documented battery configuration; never fit an unverified cell |
| LED/buzzer silent or hot | Polarity, resistor/driver, GPIO or module mismatch | Disconnect load; verify exact module and current path | Recalculate/provide driver from verified specs; never drive load directly if current is unknown |
| API will not start | Missing/short admin secret, invalid timezone, migration failure | Inspect local console; check `.env` and database path without sharing secrets | Set unique 16+ character demo password, valid IANA timezone, preserve DB for diagnosis |
| Attendance returns 401/409/422 | Invalid/revoked token, enrollment state/slot mismatch, malformed or skewed time | Check error code, device status and synthetic DB assignment; never log token | Re-provision/reconcile locally; correct timestamp/assignment; do not bypass checks |
| Dashboard/network/offline sync fails | Dashboard is absent; firmware client exists but has no physical integration pass | Check `/health`, LAN/IP, local config and queue status; preserve event UUIDs | Keep synthetic data, inspect HTTP status, and never format LittleFS if pending records may exist |

## 27–29. Demonstration, backup, and final verification

The demo script is `presentation/demo-script.md`; clearly identify software simulation versus physical evidence. Before a demonstration, create and restore a synthetic-only database backup using `scripts/backup-project.ps1`; the script's ZIP is not encrypted. Never carry real identity or biometric data in backups. Mark each item in this table only after attaching the evidence to the relevant test record.

| Gate | Current state |
| --- | --- |
| Exact components identified, wiring/revisions/voltage verified | NEEDS HARDWARE |
| Individual sensor/OLED/RTC/LED/buzzer tests | NEEDS HARDWARE |
| Firmware compile | VERIFIED (compile only) |
| Firmware upload, enrollment, match, RTC, indicators, offline queue | IMPLEMENTED in source; NEEDS HARDWARE |
| Backend environment, migrations, API tests | VERIFIED (10 tests, synthetic/temp DB only) |
| Attendance firmware | IMPLEMENTED; physical workflow NEEDS HARDWARE |
| Dashboard | PLANNED |
| Full terminal-to-dashboard sync, duplicate/offline recovery | NEEDS HARDWARE; no browser dashboard |
| Backup restore and complete demo rehearsal | NEEDS TESTING |

The build guide is not complete until exact purchased parts and authoritative electrical specifications are recorded, wiring is bench-verified, hardware tests are logged, the firmware/frontend integration exists, and the end-to-end checklist passes. Update this guide from that evidence rather than guessing.
