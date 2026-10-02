---
type: backend
area: backend
status: verified
tags:
  - backend
  - fastapi
  - sqlite
  - api
---

# 04 - Backend Server Room

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[03 - Firmware Lab]] [[05 - Testing Lab]] [[08 - Documentation Library]] · **CANVAS** [[04 - Backend Server Room/04 - Backend Server Room.canvas]]

The local service. FastAPI over SQLite, single-host, on a laptop, on an isolated LAN.

**Status: VERIFIED (software).** 10/10 tests pass in the repository virtual environment against synthetic fixtures. **No physical terminal has ever talked to it.**

---

## The path of one event

```text
ESP32 → Wi-Fi → HTTP POST +/api/v1/attendance
     → Bearer token  ─▶ devices.token_hash (SHA-256, constant-time compare)
     → BEGIN IMMEDIATE
         ├─ event_uuid already seen?  → return stored outcome, no insert
         ├─ slot > reported capacity? → 409 invalid_slot
         ├─ no ACTIVE student in slot? → 409 unknown_slot
         ├─ accepted scan within 60 s? → DUPLICATE_SUPPRESSED
         └─ otherwise                 → RECORDED
     → COMMIT → 201 / 200
```

Every decision above happens inside one serialised write transaction. That is what makes the offline-replay guarantee hold.

---

## Implemented routes

All seven are real code in `backend/app/main.py` and are listed `VERIFIED` in [[docs/api-plan.md]].

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/health` | none | Opens + migrates the DB, returns `schema_version`; `503` if unavailable |
| `GET` | `/api/v1/students` | Admin Basic | Filters `grade_class`/`status`, bounded pagination 1–100 |
| `POST` | `/api/v1/students` | Admin Basic | Reserves the lowest free slot on the **sole** active device; `PENDING_ENROLLMENT`; audited |
| `GET` | `/api/v1/students/{uuid}` | Admin Basic | One student; no token or template fields |
| `POST` | `/api/v1/students/{uuid}/deactivate` | Admin Basic | Blocks future slot resolution; `template_cleanup_required` flag; slot **not** freed |
| `GET` | `/api/v1/devices/{uuid}/enrollment/{student}` | Device Bearer | The reserved slot, pending students only |
| `POST` | `/api/v1/devices/{uuid}/enrollment/{student}/complete` | Device Bearer | Idempotent activation; an exact retry returns the same status without a second audit write |
| `POST` | `/api/v1/attendance` | Device Bearer | The ingest path above |

**Planned, no code:** device list, device detail, cleanup, heartbeat, attendance query, daily report, CSV export, SSE, static dashboard.

---

## Database

`backend/migrations/001_initial_schema.sql` · version 1 · `SCHEMA_VERSION = 1`

```text
devices ──1:N──▶ students ──1:N──▶ attendance_events
   │
   └──────────1:N───────────────────────────▶ (device_id)
                    admin_audit_log  (append-only trail)
```

| Table | Holds | Notable constraint |
|---|---|---|
| `devices` | `device_uuid`, `token_hash`, `status`, `sensor_capacity`, `last_seen_at_utc` | token is stored **hashed**, never in the clear |
| `students` | identity, `grade_class`, `status`, `fingerprint_slot_id` | `UNIQUE (enrollment_device_id, fingerprint_slot_id)` |
| `attendance_events` | `event_uuid`, `student_id`, `device_id`, `captured_at_utc`, `received_at_utc`, `sync_status`, `outcome` | `event_uuid` unique → server-side idempotency |
| `admin_audit_log` | actor, action, target | no names or biometric content |

Durability: WAL, `synchronous = FULL`, `foreign_keys = ON`, `busy_timeout = 5000`. Migrations are contiguous from `001`, applied under `BEGIN IMMEDIATE` with the schema version re-read *after* the write lock, so two processes starting together cannot both apply the same migration.

The database stores **slot references, never templates or images**. `student_id` and `fingerprint_slot_id` are nullable so a student can be erased while attendance history survives.

---

## Authentication

| Role | Mechanism | Source |
|---|---|---|
| Admin | HTTP Basic against env credentials, `hmac.compare_digest` | `ADMIN_USERNAME` / `ADMIN_PASSWORD` (≥16 chars, fail-fast at startup) |
| Device | HTTP Bearer, SHA-256 hash compared in the `devices` table | printed **once** by `python -m app.provision_device` |

`sensor_capacity` must be a *verified* number. The CLI refuses a non-positive value but cannot verify physics — do not invent a capacity to make provisioning succeed.

Errors use one envelope everywhere: `{"error":{"code","message","correlation_id"}}`. No SQL, no traceback, no secret, no biometric payload ever crosses the boundary.

---

## Running it

```bash
cd backend
.venv/Scripts/python.exe -m pytest tests -q            # 10 passed
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Configuration lives in `backend/.env` (ignored; `.env.example` is tracked): `DATABASE_PATH`, `APP_TIMEZONE` (IANA, default `Asia/Kolkata`), `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `MAX_CLOCK_SKEW_SECONDS` (default 300).

---

## Documents

[[docs/api-plan.md]] · [[docs/database-plan.md]] · [[docs/privacy-security.md]] · `backend/README.md` · [[diagrams/database.mmd]] · [[diagrams/data-flow.mmd]]

**HOME** [[00 - Vault Hub]] · **UP** [[00 - Vault Hub]] · **RELATED** [[03 - Firmware Lab]] [[05 - Testing Lab]] [[08 - Documentation Library]] · **CANVAS** [[04 - Backend Server Room/04 - Backend Server Room.canvas]]
