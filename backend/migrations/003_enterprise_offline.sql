-- v1.5.0 enterprise + offline hardening. Additive only; existing data preserved.
-- Internal column names (students.grade_class, students.roll_number,
-- students.student_uuid) are retained as the durable identifiers so BLE,
-- firmware, and existing integrations keep working. Enterprise aliases
-- (department, employee_code, employee_uuid, team) are resolved at the API
-- layer. This migration adds offline-sync metadata and company settings.

CREATE TABLE IF NOT EXISTS company_settings (
    key TEXT PRIMARY KEY CHECK (length(trim(key)) > 0),
    value TEXT NOT NULL DEFAULT '',
    updated_at_utc TEXT NOT NULL
);

-- Offline-sync robustness on attendance events. event_uuid remains the
-- idempotency key. client_seq preserves source ordering per device queue;
-- clock_uncertain flags events whose source clock may have drifted.
ALTER TABLE attendance_events ADD COLUMN client_seq INTEGER;
ALTER TABLE attendance_events ADD COLUMN clock_uncertain INTEGER NOT NULL DEFAULT 0 CHECK (clock_uncertain IN (0, 1));

CREATE INDEX IF NOT EXISTS idx_attendance_sync
    ON attendance_events(sync_status, captured_at_utc);
CREATE INDEX IF NOT EXISTS idx_attendance_client_seq
    ON attendance_events(device_id, client_seq);

-- Seed default company settings (idempotent for fresh DBs; upgrades keep
-- existing rows because INSERT OR IGNORE is used via a trigger-free seed).
INSERT OR IGNORE INTO company_settings (key, value, updated_at_utc)
VALUES
    ('company_name', 'Acme Company', '2026-01-01T00:00:00Z'),
    ('retention_days', '365', '2026-01-01T00:00:00Z'),
    ('sync_retry_max', '8', '2026-01-01T00:00:00Z');
