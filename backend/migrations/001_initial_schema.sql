CREATE TABLE devices (
    id INTEGER PRIMARY KEY,
    device_uuid TEXT NOT NULL UNIQUE CHECK (length(trim(device_uuid)) > 0),
    device_name TEXT NOT NULL CHECK (length(trim(device_name)) > 0),
    location_name TEXT NOT NULL CHECK (length(trim(location_name)) > 0),
    token_hash TEXT NOT NULL CHECK (length(trim(token_hash)) > 0),
    status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'REVOKED')),
    last_seen_at_utc TEXT,
    sensor_capacity INTEGER CHECK (sensor_capacity IS NULL OR sensor_capacity > 0),
    created_at_utc TEXT NOT NULL
);

CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    student_uuid TEXT NOT NULL UNIQUE CHECK (length(trim(student_uuid)) > 0),
    roll_number TEXT NOT NULL UNIQUE CHECK (length(trim(roll_number)) > 0),
    first_name TEXT NOT NULL CHECK (length(trim(first_name)) > 0),
    last_name TEXT NOT NULL CHECK (length(trim(last_name)) > 0),
    grade_class TEXT NOT NULL CHECK (length(trim(grade_class)) > 0),
    enrollment_device_id INTEGER NOT NULL
        REFERENCES devices(id) ON DELETE RESTRICT,
    fingerprint_slot_id INTEGER CHECK (
        fingerprint_slot_id IS NULL OR fingerprint_slot_id > 0
    ),
    status TEXT NOT NULL CHECK (
        status IN ('PENDING_ENROLLMENT', 'ACTIVE', 'INACTIVE')
    ),
    created_at_utc TEXT NOT NULL,
    updated_at_utc TEXT NOT NULL,
    UNIQUE (enrollment_device_id, fingerprint_slot_id)
);

CREATE TABLE attendance_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_uuid TEXT NOT NULL UNIQUE CHECK (length(trim(event_uuid)) > 0),
    student_id INTEGER REFERENCES students(id) ON DELETE SET NULL,
    device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE RESTRICT,
    fingerprint_slot_id INTEGER CHECK (
        fingerprint_slot_id IS NULL OR fingerprint_slot_id > 0
    ),
    captured_at_utc TEXT NOT NULL,
    received_at_utc TEXT NOT NULL,
    sync_status TEXT NOT NULL CHECK (
        sync_status IN ('LIVE', 'REPLAYED_OFFLINE')
    ),
    outcome TEXT NOT NULL CHECK (
        outcome IN ('RECORDED', 'DUPLICATE_SUPPRESSED')
    )
);

CREATE TABLE admin_audit_log (
    id INTEGER PRIMARY KEY,
    occurred_at_utc TEXT NOT NULL,
    actor TEXT NOT NULL CHECK (length(trim(actor)) > 0),
    action TEXT NOT NULL CHECK (length(trim(action)) > 0),
    target_type TEXT NOT NULL CHECK (length(trim(target_type)) > 0),
    target_id TEXT,
    details_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX idx_students_status_class
    ON students(status, grade_class, last_name, first_name);
CREATE INDEX idx_students_device_slot
    ON students(enrollment_device_id, fingerprint_slot_id);
CREATE INDEX idx_attendance_student_capture
    ON attendance_events(student_id, captured_at_utc);
CREATE INDEX idx_attendance_capture
    ON attendance_events(captured_at_utc);
CREATE INDEX idx_attendance_device_received
    ON attendance_events(device_id, received_at_utc);
CREATE INDEX idx_attendance_outcome_capture
    ON attendance_events(outcome, captured_at_utc);
