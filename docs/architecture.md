# System Architecture

**Status:** Architecture selected; application behavior remains planned. Source diagrams: [architecture](../diagrams/architecture.mmd), [data flow](../diagrams/data-flow.mmd), [attendance](../diagrams/attendance-flow.mmd), [enrollment](../diagrams/enrollment-flow.mmd), [hardware](../diagrams/hardware.mmd), [database](../diagrams/database.mmd).

## What and why

A low-cost, local-network school attendance demonstrator pairs an ESP32 terminal with an AS608 fingerprint module and a laptop-hosted FastAPI/SQLite service. It aims to explore edge-side biometric matching, durable offline event delivery, and simple local reporting. Use synthetic identities at the fair. The prototype is not suitable for operational school attendance.

## Components and status

| Component | Intended responsibility | Actual repository state |
| --- | --- | --- |
| ESP32-WROOM-32 + AS608 | Capture/match locally; expose slot result only; RTC and display feedback | PlatformIO toolchain-check sketch and pin config only; no attendance firmware |
| LittleFS queue | Persist event UUID and capture metadata offline; replay in order | Filesystem configured; queue not implemented |
| FastAPI | Device auth, enrollment status, event processing, reports, static files | No application entry point or routes |
| SQLite WAL | Student/device metadata, event outcomes, audit | Design only; no migration or generated database in source |
| Vanilla dashboard | Student registration, attendance/report views, device/system status | Architecture decision only; no UI source |
| Optional local LLM | Explain authorized read-only report results | Deferred; no code/dependency |

## Data and trust boundaries

1. Finger image and matching remain inside the sensor by design; verify exact module behavior. No fingerprint/template bytes are sent to the ESP32 host protocol, backend, logs, database, CSV, or optional AI.
2. The sensor returns a slot ID on a match. The ESP32 combines it with an event UUID, sensor timestamp, and sync status.
3. Device sends a timezone-qualified RFC3339 JSON event to FastAPI over an isolated demo WLAN. Current plan is HTTP; this is not encrypted end-to-end and is permitted only with synthetic data. WPA2 on Wi-Fi does not remove this risk.
4. FastAPI validates device identity, slot/state, idempotency, timestamp, and duplicate window. SQLite commits the event and outcome transactionally.
5. Dashboard calls authenticated REST endpoints; an authenticated SSE stream carries committed attendance events for a <=500ms visibility target. Daily presence is distinct active students with at least one accepted event.
6. Optional AI may call approved read-only report endpoints only and returns model-generated explanation clearly separated from database facts. It is not part of normal operation.

## Enrollment flow

Admin creates a student in the dashboard; API allocates a free sensor slot and marks `PENDING_ENROLLMENT`. An operator with physical USB serial access starts enrollment for that student. Firmware asks the device-authenticated API for the assigned slot, captures two impressions, stores the model in that sensor slot, then confirms completion. API marks the student `ACTIVE`. Only success/failure metadata crosses the network. Deactivation blocks future scans; physical template deletion must be confirmed before slot reuse.

## Attendance and duplicate behavior

Each scan event receives one persistent `event_uuid`, retained across retries and offline replay. API returns the prior outcome for a repeated UUID. A different event for the same student is `DUPLICATE_SUPPRESSED` if captured within 60 seconds of an accepted scan; later same-day scans may be accepted. This matches FR-04. See [database design](database-plan.md) and [API contract](api-plan.md).

## Failure, recovery, and observability

- Sensor no-match: generic local prompt; do not identify the matched student on the public terminal.
- RTC absent/invalid: signal unavailable time and do not create an event with a fabricated timestamp. Recovery requires operator time-setting through USB serial.
- Wi-Fi/API unavailable: append the event durably to LittleFS; acknowledge “saved offline” only after persistence; retry oldest first with the same UUID; delete only after server confirms a stored result. Queue capacity and overflow policy must be implemented; never silently discard.
- Queue full/flash write error: visible error and no false success indication; operator must recover network/storage.
- Backend/SQLite unavailable: health endpoint reports unavailable; device retains queued event. Migration failure stops startup rather than serving partial schema.
- Browser/API unavailable: show explicit offline/error state and retry; do not imply attendance was not recorded if API commit already occurred.
- Logs contain event UUID/correlation ID and result only; no names, tokens, or biometric content. Audit records are not tamper-proof against the laptop administrator.

## Deployment boundary

One Windows laptop hosts API, SQLite, and static dashboard; ESP32 and browser connect on an isolated 2.4 GHz Wi-Fi network. Keep firewall scope to the demo network, do not port-forward, and stop service after use. Detailed setup is [environment](environment.md) and [deployment plan](deployment-plan.md). The optional assistant remains off by default.
