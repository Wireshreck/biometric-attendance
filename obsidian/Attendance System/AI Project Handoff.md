---
type: project-handoff
status: IN PROGRESS
updated: 2026-10-02
---

# AI Project Handoff

This repository is an established ESP32 biometric attendance project. Read [[00 - Project Overview]], [[AI Development Guide]], [[TODO]], and [[Architecture.canvas]]. Actual implementation and task status are authoritative in repository source/tests and `docs/`.

## Implemented

- FastAPI/SQLite backend slice: health, admin student lifecycle/slot reservation, device enrollment assignment/completion, and authenticated idempotent attendance ingestion with the 60-second duplicate rule. Backend has 10 passing tests in the repository venv.
- ESP32 production firmware source: sensor match/two-capture serial enrollment, RTC timestamp gate, OLED and indicators, UUIDv4 event creation, LittleFS checksummed journal, bearer-authenticated API client, offline queue replay, sensor and Wi-Fi retry. Production and compatibility builds pass after current modifications; no physical test has passed.
- Independent component and integration test environments from prior phase; all 25 test envs plus production/compatibility env compile after current implementation.
- Beginner docs: `docs/COMPLETE-BEGINNER-ASSEMBLY-GUIDE.md`, `docs/complete-breadboard-layout.md`, `docs/final-pin-map.md`, `docs/COMPLETE-SOFTWARE-SETUP.md`, and `docs/SCIENCE-FAIR-SETUP.md`.
- Read-only R307S diagnostic retained. It uses VerifyPassword/ReadSysPara/template count and sends no destructive enrollment/delete commands.

## Physical state and blockers

- Owner-reported wiring: red/VIN, black/GND, yellow/GPIO32 RX, green/GPIO33 TX, blue/white disconnected. The sensor reported zero valid UART bytes at previously tried rates/routings. This does not prove it is dead.
- R307S rail voltage/current, TX level, exact board/pad mapping/jumper and sensor condition: **UNVERIFIED — REQUIRES MULTIMETER / exact-unit inspection**. Keep the current wiring report; do not tell the owner to reconnect without a specific reason.
- OLED, RTC, LEDs, buzzer, LittleFS reboot/corruption handling, Wi-Fi and API client need physical/integration tests. No firmware was flashed in this task.
- Actual fingerprint sensor capacity is unknown. Do not provision backend device capacity until read from the responding physical sensor.
- Browser dashboard and reports/CSV/SSE remain planned. Complete hardware-to-backend-to-dashboard experience is not yet available.

## Architecture and source of truth

- Pins/wiring: `docs/final-pin-map.md`; electrical gates: `docs/power-and-safety.md`.
- Runtime behavior and privacy limits: `docs/production-firmware.md`; code: `firmware/src/app/`, `hardware/`, `network/`, `storage/` and `include/`.
- Backend API: `backend/app/schemas.py`, `auth.py`, `main.py`, tests, and `docs/api-plan.md`.
- Local configuration: ignored `firmware/include/local_config.h` and `backend/.env`. Never commit secrets.
- Repository/vault plans and tasks: [[AI Development Guide]], [[TODO]], [[Milestones]], [[Decision Log]], and [[Architecture.canvas]].

## Build and test

- Final run: production and compatibility envs built successfully; all 25 standalone/integration test environments built successfully. Backend: 10 tests passed. These are software-only results; no device test was run.

- Firmware: from repo root, `pio run -d firmware -e production`. Isolated environment names and prerequisites: `docs/component-tests.md` and `docs/integration-tests.md`.
- Backend: from `backend/`, `.\.venv\Scripts\python.exe -m pytest tests -q` (10 passed in this task). System Python currently lacks dependencies.
- Physical commands, setup and COM port guidance: `docs/COMPLETE-SOFTWARE-SETUP.md`.
- New blank LittleFS: `pio run -d firmware -t uploadfs --upload-port COMx` only before any pending event exists; this erases the device filesystem. Firmware never auto-formats.

## Privacy and limitations

No raw fingerprint image/template is sent. Events include only slot, UUID, timestamp and sync status. LittleFS is not encrypted. HTTP bearer token is unencrypted on the isolated LAN; synthetic data only, never use public internet/real student data. Device time is manual local time assumed `+05:30`; use `SETTIME` only after checking a trusted clock. Full queue/recovery behavior remains unverified until tested on device.

## Next three actions

1. At the next safe hardware session, identify the exact R307S board/contact/jumper and measure sensor VIN and TX idle high level; record readings before changing wiring. No multimeter is currently available.
2. Run UART1/2 loopback with sensor disconnected, then the read-only R307S diagnostic only after the electrical safety gate; capture exact output.
3. Independently run I2C/OLED/RTC/LED/buzzer tests, then test firmware queue + local synthetic API and outage/reboot/replay. Do not claim end-to-end success until the matched event is found in the local backend after replay.
