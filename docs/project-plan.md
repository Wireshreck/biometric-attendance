# Master Project Plan

**Project:** Biometric Attendance (school attendance demonstrator)  
**Target event:** 2026-10-09  
**Current phase:** Early implementation; SQLite schema v1 and a software-tested FastAPI vertical slice are verified. Remaining API/application features and physical hardware validation remain incomplete/unconfirmed.

## Objective

Explore a local attendance pipeline with ESP32 + AS608 fingerprint matching, offline event buffering, a laptop-hosted FastAPI/SQLite service, and a vanilla-JS dashboard. The science-fair MVP must use synthetic data and consenting adult testers. It is an educational prototype, not authorized for live institutional attendance.

## MVP scope

- One ESP32 terminal and one fingerprint sensor, exact revisions to be confirmed.
- USB-serial local enrollment/deactivation; backend allocates a slot, firmware marks enrollment active only after physical sensor confirmation.
- Generic OLED/LED/buzzer feedback; no student name on a public terminal.
- DS3231 timestamp with an explicit local timezone offset; invalid clock blocks event creation.
- Stable event UUID, bounded durable LittleFS queue, idempotent chronological replay.
- Local FastAPI service; SQLite WAL/migrations; auth on device/admin APIs; event ingestion and 60-second suppression.
- Static vanilla HTML/CSS/ES-module UI, REST plus SSE, daily aggregates and CSV export.
- Optional read-only local reporting assistant is deferred and cannot affect core operation.

## Out of scope

Production school deployment, cloud synchronization, real student/biometric data, parent notifications, face recognition, multi-terminal slot synchronization, custom PCB, remote template transfer, production PKI/TLS provisioning and AI-driven decisions.

## Work breakdown and dependency order

| Phase | Work | Dependency / exit evidence |
| --- | --- | --- |
| F0 Foundation | Requirements traceability, architecture, BOM, setup, security boundaries, Git baseline | Baseline commit `9bb5801`; continue with focused commits and evidence |
| H1 Procurement/bench | Confirm purchases and exact variants; safe power/I2C/UART/RTC bring-up | Parts received; measured hardware gates pass |
| D1 Data/backend | Schema/migrations, config/health, admin/device auth, student slot reservation/enrollment state implemented; remaining report/query/device lifecycle routes | 10 DB/API/provisioning tests pass for the current slice; API-03 contract tests remain |
| F1 Firmware local | Sensor enrollment/search/delete, RTC, generic feedback and errors | Physical sensor test evidence; no identity/image leak |
| D2 Attendance API | Event UUID, authenticated transactional ingest and 60s suppression implemented; device heartbeat, reports and SSE remain | Tests verify UUID replay and 60/61-second rule; concurrent load, timezone reports and SSE tests remain |
| F2 Offline firmware | LittleFS durable queue, overflow behavior and reconnect replay | Power-loss/outage/replay tests pass |
| W1 Dashboard | Students, today/history, reports, status, SSE, CSV download | UI and authorization/error-state tests pass |
| I1 Integration | Enroll → scan → API → DB → dashboard; duplicate and offline recovery | Repeated synthetic end-to-end evidence |
| V1 Verification | Security/privacy, stress, timing, backup/restore, demo rehearsal | Traceability tests and restore evidence recorded |

## Success evidence

Every functional/non-functional requirement has a verification plan in [requirements traceability](requirements-traceability.md). Acceptance is based on recorded hardware, API, UI and recovery test evidence—not on a diagram, target, compile-only check, or presentation draft.

## Linked plans

- [Requirements](requirements.md) · [Traceability](requirements-traceability.md) · [Architecture](architecture.md)
- [Hardware/BOM](bill-of-materials.md) · [Wiring](wiring.md) · [Procurement](purchase-checklist.md)
- [Firmware](../firmware/README.md) · [Backend/API](../backend/README.md) · [Database](database-plan.md) · [Frontend](../frontend/README.md)
- [Privacy/security](privacy-security.md) · [Testing](testing-plan.md) · [Deployment](deployment-plan.md) · [Backup/recovery](backup-strategy.md)
- [Fair timeline](science-fair-timeline.md) · [Presentation plan](science-fair.md) · [Authoritative tasks](../obsidian/Attendance%20System/TODO.md)
