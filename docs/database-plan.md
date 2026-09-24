# Database Design

**Status:** Planned; no application schema or migrations exist yet.  
**Engine:** SQLite, one local writer, WAL for concurrent dashboard reads.  
**File:** `backend/data/attendance.db` (generated at runtime; never commit it).

This design is subordinate to the attendance requirements in [requirements.md](requirements.md). Raw fingerprint images and templates stay on the sensor; the host database stores only the assigned sensor slot.

## Attendance behavior decision

FR-04 is the source of truth: suppress another recognized scan for the same student when an accepted scan occurred within **60 seconds**. A scan after that window may be recorded, including later the same day. The dashboard's daily “present” count is the number of distinct active students with at least one accepted event that local date. There is no one-row-per-student-per-day constraint.

Every device event carries a persistent `event_uuid`. A replay of that UUID returns the original outcome without inserting another row. Distinct UUIDs for same-student scans inside the 60-second window are retained as `DUPLICATE_SUPPRESSED` audit events and do not count as attendance. Use a write transaction (`BEGIN IMMEDIATE`) around the check-and-insert so simultaneous devices cannot both accept the same window.

## Tables

### `students`

| Column | Type / rule | Purpose |
| --- | --- | --- |
| `id` | INTEGER PRIMARY KEY | Internal reference |
| `student_uuid` | TEXT NOT NULL UNIQUE | Random UUID; API identifier |
| `roll_number` | TEXT NOT NULL UNIQUE | School-provided identifier |
| `first_name`, `last_name` | TEXT NOT NULL | Minimum identity needed for the demo |
| `grade_class` | TEXT NOT NULL | Class/section for reports |
| `enrollment_device_id` | INTEGER NOT NULL FK `devices(id)` ON DELETE RESTRICT | MVP terminal holding this student's template |
| `fingerprint_slot_id` | INTEGER NULL or 1..that device's capacity | Sensor slot; NULL before enrollment |
| `status` | TEXT CHECK in `PENDING_ENROLLMENT`, `ACTIVE`, `INACTIVE` | Enrollment/administrative state |
| `created_at_utc`, `updated_at_utc` | TEXT NOT NULL, RFC3339 UTC | Audit timestamps |

Only `ACTIVE` students are resolved for attendance. Add `UNIQUE(enrollment_device_id, fingerprint_slot_id)`; SQLite permits multiple NULL pending slots. Attendance slot resolution is by `(device_id, fingerprint_slot_id)`. Capacity is reported from the exact sensor at bring-up; do not assume every AS608 unit has 300 slots. MVP supports one physical terminal; multi-terminal attendance enrollment requires explicit per-device assignment and is not implied by the `devices` table.

### `devices`

| Column | Type / rule | Purpose |
| --- | --- | --- |
| `id` | INTEGER PRIMARY KEY | Internal reference |
| `device_uuid` | TEXT NOT NULL UNIQUE | Provisioned terminal identifier |
| `device_name` | TEXT NOT NULL | Human-readable label |
| `location_name` | TEXT NOT NULL | Demo location |
| `token_hash` | TEXT NOT NULL | Hash of a high-entropy per-device token; never store or return raw token |
| `status` | TEXT CHECK in `ACTIVE`, `REVOKED` | Authentication state |
| `last_seen_at_utc` | TEXT NULL | Last successful authenticated heartbeat/event |
| `sensor_capacity` | INTEGER NULL CHECK > 0 | Capacity reported by the exact connected sensor |
| `created_at_utc` | TEXT NOT NULL | Provisioning time |

Do not identify or authenticate devices by MAC address; it is not a secret and may be randomized.

### `attendance_events`

| Column | Type / rule | Purpose |
| --- | --- | --- |
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | Stable ordered row cursor for SSE/recovery |
| `event_uuid` | TEXT NOT NULL UNIQUE | Device-generated idempotency key, stable across retry/replay |
| `student_id` | INTEGER NULL FK `students(id)` ON DELETE SET NULL | Matched student; nullable after data erasure |
| `device_id` | INTEGER NOT NULL FK `devices(id)` ON DELETE RESTRICT | Reporting/authenticated source |
| `fingerprint_slot_id` | INTEGER NULL or positive integer | Slot seen at scan time; set NULL if identity is erased |
| `captured_at_utc` | TEXT NOT NULL RFC3339 UTC | Normalized from the device's RFC3339 timestamp with offset |
| `received_at_utc` | TEXT NOT NULL RFC3339 UTC | Server ingestion time |
| `sync_status` | TEXT CHECK in `LIVE`, `REPLAYED_OFFLINE` | Transport history |
| `outcome` | TEXT CHECK in `RECORDED`, `DUPLICATE_SUPPRESSED` | Whether this event contributes to attendance |

Indexes: `(student_id, captured_at_utc)`, `(captured_at_utc)`, `(device_id, received_at_utc)`, and `(outcome, captured_at_utc)`. There is deliberately no per-day uniqueness constraint.

### `admin_audit_log`

`id INTEGER PRIMARY KEY`, `occurred_at_utc TEXT NOT NULL`, `actor TEXT NOT NULL`, `action TEXT NOT NULL`, `target_type TEXT NOT NULL`, `target_id TEXT NULL`, `details_json TEXT NOT NULL DEFAULT '{}'`. Record enrollment, deactivation/deletion, export, and configuration actions. Redact names, tokens, credentials, and biometric content. Treat it as append-only application behavior, not tamper-proof storage: a host administrator can edit the SQLite file.

No `configuration` table is needed for the MVP. Operational configuration comes from environment variables; secrets are never seeded into SQLite.

## Constraints and processing rules

- Enable `PRAGMA foreign_keys=ON`, `journal_mode=WAL`, `busy_timeout=5000`; use `synchronous=FULL` for durability unless measured hardware behavior justifies a documented change.
- Normalize accepted timestamps to UTC in the backend. The device sends a timezone-qualified RFC3339 timestamp; the configured IANA timezone (default `Asia/Kolkata`) determines the local attendance date. Never append `Z` to a local time.
- Reject timestamps outside a configured clock-skew bound for live events. Replayed events may be older; retain their original capture time and expose replay status.
- Under one write transaction: look up `event_uuid`; if present return its stored outcome. Resolve active student by `(device_id, fingerprint_slot_id)`; query accepted events for that student where `abs(captured_at_utc - incoming_time) <= 60 seconds`; insert `DUPLICATE_SUPPRESSED` if found, otherwise `RECORDED`. SQLite timestamps should be compared as integer epoch milliseconds in application code or consistently normalized lexicographic UTC strings.
- Reports count only `RECORDED` rows and distinct active students for presence. Sort attendance by capture time, then event UUID for stable ordering.
- If a student is deactivated, preserve records for the configured retention period and block matching. On approved erasure, clear the sensor slot physically, then transactionally set historical `student_id` and `fingerprint_slot_id` to NULL and delete identity. Never reuse a slot until sensor deletion is confirmed.
- Revoke a device by setting `REVOKED`; do not delete it while its attendance rows reference it.

## Migrations, fixtures, recovery

Use checked-in, ordered SQL migrations and `PRAGMA user_version`; migrations run transactionally at startup and fail closed on errors. Back up via SQLite's online backup API before migration. Test migration from an empty database and every supported prior schema version.

Tests use temporary databases and synthetic fixture names/IDs only. Do not ship real student records as seeds. Back up the SQLite database with its backup API (not by copying only the main file while WAL is active), retain documented encrypted copies only when real sensitive records are permitted, and periodically restore into a separate temporary path and run `PRAGMA integrity_check`.

Retention duration is an institution decision, not a default suitable for live deployment. The demo uses synthetic data and deletes it after the project unless the owner explicitly sets another policy.
