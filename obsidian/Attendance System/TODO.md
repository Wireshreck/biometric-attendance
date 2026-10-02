---
type: task-tracker
status: IN PROGRESS
updated: 2026-10-02
---

# Authoritative Project Task Tracker

[[00 - Project Overview|Project home]] · [[Milestones]] · [[AI Project Handoff]] · [[Architecture.canvas]]

This is the single task list. Component designs and acceptance criteria remain in their canonical repository documents. Status reflects evidence, not intention.

Status vocabulary: **PLANNED**, **IN PROGRESS**, **IMPLEMENTED**, **VERIFIED**, **BLOCKED**, **DEPRECATED**, **NEEDS HARDWARE**, **NEEDS TESTING**, **DEFERRED**.

| ID | Task | Subsystem | Priority | Status | Dependency / blocker | Verification method |
|---|---|---|---|---|---|---|
| FND-01 | Audit repository, history, implementation, docs and vault | Foundation | P0 | VERIFIED | — | `docs/firmware-audit.md` |
| FND-02 | Keep requirements/API/duplicate policy traceable | Foundation | P0 | VERIFIED (backend scope) | — | `docs/requirements-traceability.md`, `docs/api-plan.md`, backend tests |
| GIT-01 | Preserve current history/branch; use focused commits only when owner requests | Development | P0 | VERIFIED | — | Audit began clean on main tracking origin/main; no commit/push made |
| HW-00 | Verify exact R307S PCB identity, connector mapping, jumper, rail and UART voltage | Hardware | P0 | BLOCKED | Multimeter / physical markings | Record exact markings, ground continuity, rail and TX readings in `hardware/test-plan.md` |
| HW-01 | Run read-only R307S diagnostic and isolate ESP32 UART with loopback | Hardware/Firmware | P0 | NEEDS TESTING | Safe sensor electrical checks; loopback jumper | `r307s`, `uart1_loopback`, `uart2_loopback`; capture complete serial output |
| HW-02 | Run I2C scanner, OLED, DS3231, LEDs and buzzer separately | Hardware | P0 | NEEDS HARDWARE | Physical peripherals and safe wiring | `i2c_scan`, `oled`, `rtc`, `green_led`, `red_led`, `buzzer`; record visible/observed results |
| HW-03 | Measure rails/reset behavior under sensor/Wi-Fi loads | Hardware/Power | P0 | BLOCKED | Suitable multimeter; safe test setup | `power_reset` plus measured voltage/current evidence; software telemetry alone is insufficient |
| FW-00 | Preserve bounded read-only R307S diagnostic | Firmware | P0 | VERIFIED (software build) | — | `firmware/src/r307s_uart_diag.cpp`; no destructive commands |
| FW-01 | Add independent component and integration PlatformIO environments | Firmware | P0 | VERIFIED (builds only) | Physical tests remain separate | 25 component/integration environments compile/link; production and `esp32dev` compatibility environment build; see `docs/component-tests.md`, `docs/integration-tests.md` |
| FW-02 | Production driver, explicit enrollment/matching, RTC and generic UX | Firmware | P0 | IMPLEMENTED | HW-00/HW-01/HW-02 | Production build; physically test sensor, display, RTC and no-match/enrollment flows |
| FW-03 | Stable UUID, bounded LittleFS journal and replay | Firmware/Storage | P0 | IMPLEMENTED | Local filesystem initialization | Validate append/reboot/corruption/full/outage/replay on device; compare UUID/idempotency |
| FW-04 | Authenticated device API client for attendance contract | Firmware/Backend | P0 | IMPLEMENTED | Local synthetic test device requires verified capacity | Isolated backend integration: 201/200, auth failure, invalid slot and offline retry; no real records |
| API-01 | Implement health, admin student lifecycle, enrollment assignment/completion | Backend/API | P0 | VERIFIED (software tests) | DB-01 | Existing backend API tests; no physical enrollment proof |
| API-02 | Implement authenticated attendance ingest, idempotency, timestamp validation and 60-second duplicate rule | Backend/API | P0 | VERIFIED (software tests) | API-01 | Existing synthetic API tests; queue replay remains unverified |
| API-03 | Add reports, CSV, SSE, device status/heartbeat and cleanup/deletion routes | Backend/API | P0 | PLANNED | API-01/API-02 | Contract tests for timezone, CSV escaping, SSE resume, auth and lifecycle |
| UI-01 | Build accessible student, event, daily report and CSV views | Frontend | P0 | PLANNED | API-03 | Empty/loading/error/auth/export and accessibility tests |
| UI-02 | Add authenticated SSE reconnect/resume and deduplicated live updates | Frontend/API | P1 | PLANNED | UI-01, API-03 | Cursor/event UUID and measured latency tests |
| INT-01 | Complete synthetic end-to-end scan-to-dashboard and offline recovery scenario | Integration | P0 | NEEDS HARDWARE | Firmware, API, UI, safe hardware | Full trace including duplicate and outage/recovery evidence |
| SEC-01 | Review credential, network, retention, deletion, backup and biometric threat controls | Security | P0 | PLANNED | Implemented product flows | Negative auth/leak/deletion/restore checks; synthetic data only |
| BUILD-01 | Complete reproducible assembly/software setup guide and record physical evidence | Documentation/Hardware | P0 | IN PROGRESS | HW-00/02; product integration | Docs created; actual board/module mapping and readings still need bench evidence |
| DEMO-01 | Prepare evidence-led demo, backup restore, fallback and rehearsal | Delivery | P1 | PLANNED | INT-01 | Restore test and script aligned to verified behavior |
| AI-01 | Consider local read-only aggregate reporting only after core MVP verification | Optional | P2 | DEFERRED | Explicit future privacy/architecture decision | No AI dependency or write access to core attendance |

## Current blockers

- R307S returns no valid UART response in the previous reported diagnostic. The current assembly is owner-reported; sensor rail/TX level, exact PCB mapping/jumper and sensor health are **UNVERIFIED — REQUIRES MULTIMETER / board inspection**.
- OLED, RTC, indicators, Wi-Fi and HTTP have test builds but no physical pass evidence in this audit.
- Production firmware implements the attendance/enrollment workflows, network client and offline queue, but physical operation and event replay are unverified.
- Prototype uses plain HTTP bearer tokens; only synthetic data on an isolated local network is permitted.

## Current software evidence

- `pio run -d firmware -e production`, `esp32dev`, and all 25 component/integration environments compile/link; hardware execution is separate. Final run completed 2026-10-02: all 27 firmware environments built successfully.
- `backend/.venv/Scripts/python.exe -m pytest tests -q` from `backend/`: 10 tests passed on this audit date.
- Firmware implementation and documentation milestones are ready for the explicitly requested focused commits and push.
