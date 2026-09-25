from __future__ import annotations

import sqlite3
from pathlib import Path

import aiosqlite
import pytest

from app.database import (
    DatabaseMigrationError,
    SCHEMA_VERSION,
    connect_database,
    initialize_database,
)


pytestmark = pytest.mark.asyncio


async def _seed_device(connection: aiosqlite.Connection) -> int:
    cursor = await connection.execute(
        """INSERT INTO devices
           (device_uuid, device_name, location_name, token_hash, status, created_at_utc)
           VALUES (?, ?, ?, ?, 'ACTIVE', ?)""",
        ("device-test-001", "Test terminal", "Lab", "hash-only", "2026-09-25T00:00:00Z"),
    )
    return int(cursor.lastrowid)


async def test_file_database_pragmas_and_versioned_schema(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "attendance.db"
    connection = await connect_database(db_path)
    try:
        async with connection.execute("PRAGMA journal_mode") as cursor:
            assert (await cursor.fetchone())[0].lower() == "wal"
        async with connection.execute("PRAGMA foreign_keys") as cursor:
            assert (await cursor.fetchone())[0] == 1
        async with connection.execute("PRAGMA busy_timeout") as cursor:
            assert (await cursor.fetchone())[0] == 5000
        async with connection.execute("PRAGMA user_version") as cursor:
            assert (await cursor.fetchone())[0] == SCHEMA_VERSION
        async with connection.execute("PRAGMA foreign_key_check") as cursor:
            assert await cursor.fetchall() == []
    finally:
        await connection.close()


async def test_slot_constraints_allow_pending_null_but_prevent_reuse(tmp_path: Path) -> None:
    connection = await connect_database(tmp_path / "attendance.db")
    try:
        device_id = await _seed_device(connection)
        student_values = (
            "PENDING_ENROLLMENT", "2026-09-25T00:00:00Z", "2026-09-25T00:00:00Z"
        )
        for number in (1, 2):
            await connection.execute(
                """INSERT INTO students
                   (student_uuid, roll_number, first_name, last_name, grade_class,
                    enrollment_device_id, fingerprint_slot_id, status,
                    created_at_utc, updated_at_utc)
                   VALUES (?, ?, 'Test', 'Student', 'A', ?, NULL, ?, ?, ?)""",
                (f"student-{number}", f"R{number}", device_id, *student_values),
            )

        values = (
            "student-3", "R3", "Test", "Student", "A", device_id, 7,
            "PENDING_ENROLLMENT", "2026-09-25T00:00:00Z", "2026-09-25T00:00:00Z",
        )
        await connection.execute(
            """INSERT INTO students
               (student_uuid, roll_number, first_name, last_name, grade_class,
                enrollment_device_id, fingerprint_slot_id, status, created_at_utc, updated_at_utc)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            values,
        )
        with pytest.raises(sqlite3.IntegrityError):
            await connection.execute(
                """INSERT INTO students
                   (student_uuid, roll_number, first_name, last_name, grade_class,
                    enrollment_device_id, fingerprint_slot_id, status, created_at_utc, updated_at_utc)
                   VALUES ('student-4', 'R4', 'Test', 'Student', 'A', ?, 7,
                           'PENDING_ENROLLMENT', '2026-09-25T00:00:00Z', '2026-09-25T00:00:00Z')""",
                (device_id,),
            )
    finally:
        await connection.close()


async def test_attendance_event_uuid_and_foreign_keys(tmp_path: Path) -> None:
    connection = await connect_database(tmp_path / "attendance.db")
    try:
        device_id = await _seed_device(connection)
        await connection.execute(
            """INSERT INTO attendance_events
               (event_uuid, student_id, device_id, fingerprint_slot_id,
                captured_at_utc, received_at_utc, sync_status, outcome)
               VALUES ('event-1', NULL, ?, 4, '2026-09-25T00:00:00Z',
                       '2026-09-25T00:00:01Z', 'LIVE', 'RECORDED')""",
            (device_id,),
        )
        with pytest.raises(sqlite3.IntegrityError):
            await connection.execute(
                """INSERT INTO attendance_events
                   (event_uuid, student_id, device_id, fingerprint_slot_id,
                    captured_at_utc, received_at_utc, sync_status, outcome)
                   VALUES ('event-1', NULL, ?, 4, '2026-09-25T00:00:00Z',
                           '2026-09-25T00:00:01Z', 'LIVE', 'RECORDED')""",
                (device_id,),
            )
        with pytest.raises(sqlite3.IntegrityError):
            await connection.execute(
                """INSERT INTO attendance_events
                   (event_uuid, student_id, device_id, fingerprint_slot_id,
                    captured_at_utc, received_at_utc, sync_status, outcome)
                   VALUES ('event-2', NULL, 999, 4, '2026-09-25T00:00:00Z',
                           '2026-09-25T00:00:01Z', 'LIVE', 'RECORDED')"""
            )
    finally:
        await connection.close()


async def test_migration_failure_rolls_back_schema_and_version(tmp_path: Path) -> None:
    migrations = tmp_path / "bad-migrations"
    migrations.mkdir()
    (migrations / "001_broken.sql").write_text(
        "CREATE TABLE should_rollback (id INTEGER PRIMARY KEY);\nINVALID SQL;\n",
        encoding="utf-8",
    )
    db_path = tmp_path / "broken.db"
    with pytest.raises(DatabaseMigrationError, match="rolled back"):
        await connect_database(db_path, migrations_dir=migrations)

    with sqlite3.connect(db_path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 0
        assert connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='should_rollback'"
        ).fetchone() is None


async def test_migration_is_idempotent_and_future_version_fails_closed(tmp_path: Path) -> None:
    db_path = tmp_path / "attendance.db"
    await initialize_database(db_path)
    await initialize_database(db_path)

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA user_version = 99")

    with pytest.raises(DatabaseMigrationError, match="newer than supported"):
        await connect_database(db_path)


async def test_concurrent_first_open_applies_migration_once(tmp_path: Path) -> None:
    import asyncio

    db_path = tmp_path / "concurrent.db"
    await asyncio.gather(
        initialize_database(db_path),
        initialize_database(db_path),
    )
    connection = await connect_database(db_path)
    try:
        async with connection.execute("PRAGMA user_version") as cursor:
            assert (await cursor.fetchone())[0] == SCHEMA_VERSION
        async with connection.execute("PRAGMA foreign_key_check") as cursor:
            assert await cursor.fetchall() == []
    finally:
        await connection.close()
