-- v1.1.0 dashboard/analytics: section split, device firmware tracking,
-- search and filter indexes. Additive only; existing data preserved.

ALTER TABLE students ADD COLUMN section TEXT NOT NULL DEFAULT '';

ALTER TABLE devices ADD COLUMN firmware_version TEXT;

CREATE INDEX IF NOT EXISTS idx_students_name
    ON students(last_name, first_name, student_uuid);
CREATE INDEX IF NOT EXISTS idx_students_roll
    ON students(roll_number);
CREATE INDEX IF NOT EXISTS idx_students_class_section
    ON students(status, grade_class, section, last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_students_slot
    ON students(fingerprint_slot_id);
CREATE INDEX IF NOT EXISTS idx_attendance_student_outcome_capture
    ON attendance_events(student_id, outcome, captured_at_utc);
CREATE INDEX IF NOT EXISTS idx_attendance_device_capture
    ON attendance_events(device_id, captured_at_utc);
