---
type: task-tracker
status: IN PROGRESS
updated: 2026-09-25
---

# Authoritative Project Task Tracker

[[00 - Project Overview|Project home]] · [[Milestones]] · [[AI Project Handoff]] · [[Architecture.canvas]]

This is the single project task tracker. Component designs and acceptance criteria stay in the canonical files listed in [[AI Development Guide]]. **Status describes actual work/evidence, not the presence of a plan.**

Status vocabulary: **PLANNED**, **IN PROGRESS**, **IMPLEMENTED**, **VERIFIED**, **BLOCKED**, **DEPRECATED**, **NEEDS HARDWARE**, **NEEDS TESTING**, **DEFERRED**. Use `DECIDED` or `PROVISIONAL` only in the decision log.

| ID | Task | Subsystem | Priority | Status | Dependency / blocker | Verification method |
| --- | --- | --- | --- | --- | --- | --- |
| FND-01 | Inventory source, docs, environment, Git and vault; identify product implementation boundary | Foundation | P0 | VERIFIED | — | File inventory, source review, Git status/history, ignored-artifact review |
| FND-02 | Align requirements, duplicate policy and requirement/test traceability | Foundation | P0 | VERIFIED | FND-01 | `docs/requirements-traceability.md`; cross-check FR-04 with schema/API plans |
| FND-03 | Exclude credentials, runtime databases, venv and PlatformIO output | Security/Git | P0 | VERIFIED | FND-01 | `.gitignore`, `git check-ignore`, tracked-file secret scan |
| FND-04 | Make repository root the vault; connect project notes to canonical files via file-backed Canvas | Obsidian | P0 | VERIFIED | FND-01 | Canvas JSON and file targets validated; Markdown/Obsidian links checked |
| FND-05 | Add AI guide, current handoff, decision log and milestone index | Obsidian | P0 | VERIFIED | FND-04 | Source-of-truth map, workflow, status vocabulary, commands and current Git/app state reviewed |
| GIT-01 | Preserve baseline branch/remote/history and use focused milestone commits | Development | P0 | VERIFIED | — | `git status`, `git log`, `git remote`, author identity; no force-push |
| DB-01 | Implement schema v1 and transactional migration/connection setup | Backend/DB | P0 | VERIFIED | FND-02 | `backend/tests/test_database.py`; temporary file DB, constraints, rollback, version, pragmas; 6 passed |
| API-01 | Implement config, health, admin/device authentication and student/enrollment routes | Backend/API | P0 | PLANNED | DB-01 | Contract tests; health/schema readiness, auth failures, state transitions |
| API-02 | Implement authenticated attendance ingest, idempotency, duplicate window, timezone and reports/SSE/CSV | Backend/API | P0 | PLANNED | API-01 | Contract/concurrency tests for 59/60/61 seconds, replay, timezone, export safety |
| HW-01 | Confirm purchase/order/delivery and exact board/sensor/module revisions | Procurement | P0 | BLOCKED | Owner confirmation | Record actual variant, seller, paid total, receipt/order and expected/actual arrival |
| HW-02 | Bench-test safe power, I2C, outputs, sensor UART, RTC and combined load | Hardware | P0 | NEEDS HARDWARE | HW-01, exact parts in hand | Record board IDs, meter/logic evidence and pass/fail in `hardware/test-plan.md` |
| FW-00 | Compile toolchain validation sketch for pinned `esp32dev` target | Firmware | P0 | VERIFIED | — | `pio run -d firmware` passed 2026-09-25; compile only |
| FW-01 | Add diagnostic environments and pass peripheral/board checks | Firmware | P0 | NEEDS HARDWARE | HW-02 | I2C/UART/output/RTC tests with physical measurements in `hardware/test-plan.md` |
| FW-02 | Implement enrollment, matching, RTC, safe feedback/errors and device event client | Firmware | P0 | NEEDS HARDWARE | HW-02, API-01/API-02 | Synthetic consenting tester; timeout, privacy and latency tests |
| FW-03 | Implement bounded crash-safe LittleFS queue and acknowledged chronological replay | Firmware | P0 | PLANNED | FW-02, API-02 | Reboot/power-cut/outage/full-queue/replay tests with stable UUIDs |
| UI-01 | Build accessible student, event, daily report, device and CSV views | Frontend | P0 | PLANNED | API-01/API-02 | UI tests for empty/loading/error/auth/export states and accessibility |
| UI-02 | Add authenticated SSE reconnect/resume and deduplicated live updates | Frontend/API | P1 | PLANNED | UI-01, API-02 | `Last-Event-ID`, event UUID and measured latency tests |
| INT-01 | Repeat synthetic enrollment-to-dashboard and offline recovery scenario | Integration | P0 | NEEDS HARDWARE | API, firmware, UI and hardware gates | Full trace with event/outcome evidence; duplicate and recovery paths |
| SEC-01 | Review secrets, auth, network exposure, retention/deletion, backup and threat model | Security | P0 | PLANNED | API/firmware implementation | Review checklist plus negative auth, leak, deletion and restore tests |
| DEMO-01 | Prepare evidence-led demo, backup restore, fallback and rehearsal | Delivery | P1 | PLANNED | INT-01 | Restore test; demo script matches verified implementation only |
| AI-01 | Evaluate local read-only aggregate reporting after tested core MVP | Optional | P2 | DEFERRED | Separate future decision/privacy review | No AI dependency or write access in core path |

## Current blockers and limitations

- Hardware purchase/arrival and exact revisions remain unconfirmed; no electrical or biometric bench result exists.
- Firmware sketch compile passes. Flashing, sensor/RTC/display behavior, and electrical validation require physical hardware.
- There is no FastAPI application/API, attendance firmware, frontend source, or end-to-end product suite. The DB migration tests do not verify attendance business behavior.
- Prototype transport is planned local HTTP and is unencrypted; synthetic data only, isolated demo LAN only. No production/school deployment.

## Evidence from current milestone

- `backend/.venv/Scripts/python.exe -m pytest tests -q` from `backend/`: 6 database migration/constraint tests passed on 2026-09-25.
- `pio run -d firmware`: passed on 2026-09-25 (compile only; framework warning noted in [[AI Project Handoff]]).
- Backend environment smoke check previously passed; rerun after dependency changes.
- Git baseline at start of milestone: `9bb5801`; commit current coherent changes after reviewing staged diff. Do not push unless requested.

## Schedule

The event target is 2026-10-09. Dates are targets, not proof or guarantees. Procurement target status is unknown as of 2026-09-25. Replan the critical path using actual delivery; see `docs/science-fair-timeline.md`.
