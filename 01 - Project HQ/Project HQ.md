---
type: project
area: project-hq
status: active
tags:
  - project
  - navigation
---

# 01 - Project HQ

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[02 - Hardware Lab]] [[03 - Firmware Lab]] [[09 - Decision Room]] · **CANVAS** [[01 - Project HQ/01 - Project HQ.canvas]]

The front office. What the project is, what it must do, and what it must never do.

---

## Mission

A **local-first biometric attendance demonstrator** for schools, cheap enough for a school in India to actually buy, and open-source enough to hand to anyone.

The engineering question:

> Can a low-cost ESP32 terminal record attendance with biometric **matching kept on the sensor**, send only *event metadata* to a local service, and recover from a network outage — without ever transmitting a fingerprint image or template?

Canonical: [[docs/requirements.md]] · [[docs/architecture.md]] · [[docs/project-plan.md]]

---

## System shape

```text
┌─────────────────────────────────┐
│  EDGE TERMINAL — ESP32          │
│  R307S ──UART── ESP32 ── OLED   │
│                DS3231 RTC       │
│      green/red LED  ·  buzzer   │
│      LittleFS offline journal   │
└──────────────┬──────────────────┘
               │ Wi-Fi 2.4 GHz, local LAN
               ▼
┌─────────────────────────────────┐
│  LOCAL HOST — Python            │
│  FastAPI ──► SQLite (WAL)       │
│  Dashboard (planned)            │
└─────────────────────────────────┘
```

Two halves, one boundary. The sensor never leaves the edge. The service never touches a biometric.

---

## The four non-negotiables

These come from [[docs/privacy-security.md]] and [[SECURITY.md]], and they constrain the design more than any feature does.

1. **Matching happens on the sensor.** The fingerprint module captures, matches and stores templates internally. Only a *slot number* leaves it. Firmware never receives an image.
2. **The database holds no biometric.** Events carry `event_uuid`, `fingerprint_slot_id`, `captured_at`, `sync_status`. Nothing else. Verified in `backend/app/schemas.py`.
3. **Everything runs on a local, isolated network.** No cloud, no public exposure, no port forwarding. HTTP is unencrypted — which is exactly why it is demo-only.
4. **Synthetic data and consenting adults only.** Not now, not at the fair, not in a demo.

---

## Scope: what exists vs what is planned

| Layer | Built | Not built |
|---|---|---|
| Firmware runtime | State machine, enrollment, matching, RTC gate, journal/replay, network client, recovery | — (physical validation is the gap, not code) |
| Backend API | Health, students, enrollment, attendance ingest | Reports, CSV, SSE, device lifecycle, cleanup, heartbeat |
| Database | Schema v1, migrations, constraints, WAL | Retention/deletion execution |
| Frontend | **Nothing** | Every view. `frontend/` is a design note |
| AI assistant | **Nothing** | Deferred by decision; must stay read-only and non-essential |

---

## Current position

Software is further along than the hardware, which is the unusual part of this project.

- `production` firmware **builds** (RAM 13.3%, Flash 66.0%).
- Backend **10/10 tests pass** against synthetic fixtures.
- **Zero** physical test results exist for any peripheral.
- The R307S is silent and its supply rail is unmeasured: **R307S = UNVERIFIED — REQUIRES MULTIMETER**.

> The gap is not missing code. It is missing evidence.

---

## The facility

| Room | Holds |
|---|---|
| [[02 - Hardware Lab]] | Parts, pin map, breadboard, power, safety |
| [[03 - Firmware Lab]] | The terminal runtime |
| [[04 - Backend Server Room]] | The API and database |
| [[05 - Testing Lab]] | Every environment and what it proves |
| [[06 - Research Archive]] | Sensor protocol and hardware research |
| [[07 - Science Fair]] | Demo, presentation, judges |
| [[08 - Documentation Library]] | Which file is authoritative |
| [[09 - Decision Room]] | ADR-001…ADR-014 |
| [[10 - Workshop]] | Tasks, milestones, the blocker |

**Map:** [[00 - Master Canvas.canvas]] · **Area map:** [[01 - Project HQ/01 - Project HQ.canvas]]

---

## Legacy architecture canvas

[[Legacy Architecture Canvas.canvas|Legacy Architecture Canvas]] is the previous subsystem map, kept for history. It predates the production firmware and is superseded by [[00 - Master Canvas.canvas]] and the area canvases.

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[02 - Hardware Lab]] [[03 - Firmware Lab]] [[09 - Decision Room]] · **CANVAS** [[01 - Project HQ/01 - Project HQ.canvas]]
