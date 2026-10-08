"""v1.1.0 dashboard, analytics, export, devices, AI, and migration tests."""

from __future__ import annotations

import asyncio
import hashlib
import sqlite3
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import ai as AI
from app.config import Settings
from app.database import SCHEMA_VERSION, connect_database
from app.events import BUS
from app.main import create_app

DEVICE_UUID = "9d6f13ab-e7c3-4c12-a258-a46c2240d01d"
DEVICE_TOKEN = "device-secret"
ADMIN = ("demo-admin", "test-password-at-least-16")


@pytest.fixture
def client(tmp_path: Path):
    settings = Settings(
        database_path=tmp_path / "dash.db",
        app_timezone="Asia/Kolkata",
        admin_username="demo-admin",
        admin_password="test-password-at-least-16",
    )
    with TestClient(create_app(settings)) as test_client:
        yield test_client


def seed_device(client: TestClient, *, capacity: int | None = 20) -> None:
    async def _seed():
        connection = await connect_database(client.app.state.settings.database_path)
        try:
            await connection.execute(
                """INSERT INTO devices
                   (device_uuid, device_name, location_name, token_hash, status,
                    sensor_capacity, firmware_version, created_at_utc)
                   VALUES (?, 'Terminal', 'Lab', ?, 'ACTIVE', ?, '1.1.0', ?)""",
                (DEVICE_UUID, hashlib.sha256(DEVICE_TOKEN.encode()).hexdigest(),
                 capacity, "2026-10-08T00:00:00Z"),
            )
            await connection.commit()
        finally:
            await connection.close()
    asyncio.run(_seed())


def make_student(client: TestClient, roll: str, first: str, last: str,
                 grade: str, section: str = "") -> dict:
    response = client.post("/api/v1/students", auth=ADMIN, json={
        "roll_number": roll, "first_name": first, "last_name": last,
        "grade_class": grade, "section": section,
    })
    assert response.status_code == 201, response.text
    return response.json()


def activate(client: TestClient, student: dict) -> None:
    headers = {"Authorization": f"Bearer {DEVICE_TOKEN}"}
    path = f"/api/v1/devices/{DEVICE_UUID}/enrollment/{student['student_uuid']}"
    response = client.post(path + "/complete", headers=headers, json={
        "result": "SUCCESS", "fingerprint_slot_id": student["fingerprint_slot_id"]})
    assert response.status_code == 200, response.text


def checkin(client: TestClient, slot: int, when: datetime, live: bool = True) -> dict:
    headers = {"Authorization": f"Bearer {DEVICE_TOKEN}"}
    response = client.post("/api/v1/attendance", headers=headers, json={
        "event_uuid": str(uuid.uuid4()), "fingerprint_slot_id": slot,
        "captured_at": when.isoformat(),
        "sync_status": "LIVE" if live else "REPLAYED_OFFLINE",
    })
    return response


def test_migration_upgrade_preserves_v1_data(tmp_path: Path):
    from app.database import MIGRATIONS_DIR, _migration_files
    db_path = tmp_path / "old.db"
    connection = sqlite3.connect(db_path)
    sql_001 = (MIGRATIONS_DIR / "001_initial_schema.sql").read_text(encoding="utf-8")
    connection.executescript(sql_001)
    connection.execute(
        "INSERT INTO devices (device_uuid, device_name, location_name, token_hash,"
        " status, sensor_capacity, created_at_utc) VALUES (?,?,?,?,?,?,?)",
        (DEVICE_UUID, "T", "L", "h", "ACTIVE", 20, "2026-01-01T00:00:00Z"))
    connection.execute(
        "INSERT INTO students (student_uuid, roll_number, first_name, last_name,"
        " grade_class, enrollment_device_id, fingerprint_slot_id, status,"
        " created_at_utc, updated_at_utc) VALUES (?,?,?,?,?,?,?,?,?,?)",
        ("s-uuid-1", "R-1", "Old", "Student", "10A", 1, 5, "ACTIVE",
         "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"))
    connection.execute("PRAGMA user_version = 1")
    connection.commit()
    connection.close()
    upgraded = asyncio.run(connect_database(db_path))
    try:
        asyncio.run(upgraded.execute("SELECT section FROM students")).close()
    finally:
        asyncio.run(upgraded.close())
    check = sqlite3.connect(db_path)
    try:
        assert check.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION == 2
        row = check.execute("SELECT roll_number, section FROM students").fetchone()
        assert row == ("R-1", "")
    finally:
        check.close()
    assert sorted(_migration_files(MIGRATIONS_DIR)) == [1, 2]


def test_student_edit_search_section(client: TestClient):
    seed_device(client)
    created = make_student(client, "R-101", "Aarav", "Sharma", "10A", "A")
    assert created["section"] == "A"
    patched = client.patch(f"/api/v1/students/{created['student_uuid']}",
                           auth=ADMIN, json={"section": "B", "grade_class": "10B"})
    assert patched.status_code == 200
    assert patched.json()["section"] == "B"
    assert patched.json()["grade_class"] == "10B"
    assert client.patch(f"/api/v1/students/{created['student_uuid']}",
                        auth=ADMIN, json={}).status_code == 422
    found = client.get("/api/v1/students?q=aarav", auth=ADMIN).json()
    assert len(found["items"]) == 1
    by_section = client.get("/api/v1/students?grade_class=10B&section=B", auth=ADMIN).json()
    assert len(by_section["items"]) == 1
    assert client.get("/api/v1/students?q=nobody-here", auth=ADMIN).json()["items"] == []
    summary = client.get(f"/api/v1/students/{created['student_uuid']}/summary", auth=ADMIN)
    assert summary.status_code == 200
    assert summary.json()["attendance_percentage"] == 0.0


def test_attendance_filters_pagination_sorting(client: TestClient):
    seed_device(client)
    s1 = make_student(client, "R-201", "Diya", "Patel", "10A", "A")
    s2 = make_student(client, "R-202", "Kabir", "Singh", "10B", "B")
    activate(client, s1)
    activate(client, s2)
    base = datetime.now(UTC) - timedelta(hours=3)
    assert checkin(client, s1["fingerprint_slot_id"], base, live=False).status_code == 201
    assert checkin(client, s2["fingerprint_slot_id"], base + timedelta(minutes=30), live=False).status_code == 201
    day = base.astimezone().date().isoformat() if False else None
    listing = client.get("/api/v1/attendance?limit=1&offset=0", auth=ADMIN).json()
    assert listing["total"] == 2
    assert len(listing["items"]) == 1
    second = client.get("/api/v1/attendance?limit=1&offset=1", auth=ADMIN).json()
    assert second["items"][0]["event_uuid"] != listing["items"][0]["event_uuid"]
    by_class = client.get("/api/v1/attendance?grade_class=10A", auth=ADMIN).json()
    assert by_class["total"] == 1
    assert by_class["items"][0]["roll_number"] == "R-201"
    by_name = client.get("/api/v1/attendance?q=kabir", auth=ADMIN).json()
    assert by_name["total"] == 1
    by_slot = client.get(f"/api/v1/attendance?slot={s2['fingerprint_slot_id']}", auth=ADMIN).json()
    assert by_slot["total"] == 1
    asc = client.get("/api/v1/attendance?sort=captured_at_utc&order=asc", auth=ADMIN).json()
    first_ts = asc["items"][0]["captured_at_utc"]
    desc = client.get("/api/v1/attendance?sort=captured_at_utc&order=desc", auth=ADMIN).json()
    assert desc["items"][0]["captured_at_utc"] >= first_ts
    assert client.get("/api/v1/attendance?sort=nope", auth=ADMIN).status_code == 422
    assert client.get("/api/v1/attendance?day=not-a-date", auth=ADMIN).status_code == 422
    assert day is None


def test_statistics_overview_and_devices(client: TestClient):
    seed_device(client)
    s1 = make_student(client, "R-301", "Anaya", "Gupta", "10A", "A")
    s2 = make_student(client, "R-302", "Vivaan", "Rao", "10A", "A")
    activate(client, s1)
    activate(client, s2)
    assert checkin(client, s1["fingerprint_slot_id"], datetime.now(UTC)).status_code == 201
    stats = client.get("/api/v1/statistics/overview", auth=ADMIN).json()
    assert stats["overview"]["total_students"] == 2
    assert stats["overview"]["present_today"] == 1
    assert stats["overview"]["absent_today"] == 1
    assert stats["overview"]["attendance_percentage"] == 50.0
    assert len(stats["trend"]) == 7
    assert stats["trend"][-1]["present"] == 1
    assert any(c["class"] == "10A" for c in stats["classes"])
    assert len(stats["absent"]) == 1
    assert stats["absent"][0]["roll_number"] == "R-302"
    devices = client.get("/api/v1/devices", auth=ADMIN).json()
    assert devices["items"][0]["firmware_version"] == "1.1.0"


def test_exports_respect_filters(client: TestClient):
    seed_device(client)
    s1 = make_student(client, "R-401", "Ishaan", "Nair", "10A", "A")
    activate(client, s1)
    assert checkin(client, s1["fingerprint_slot_id"], datetime.now(UTC)).status_code == 201
    csv_resp = client.get("/api/v1/export.csv?grade_class=10A", auth=ADMIN)
    assert csv_resp.status_code == 200
    assert "R-401" in csv_resp.text
    assert csv_resp.headers["content-type"].startswith("text/csv")
    empty = client.get("/api/v1/export.csv?grade_class=12Z", auth=ADMIN)
    assert empty.status_code == 200
    assert "R-401" not in empty.text
    xlsx_resp = client.get("/api/v1/export.xlsx", auth=ADMIN)
    assert xlsx_resp.status_code == 200
    assert xlsx_resp.headers["content-type"].startswith(
        "application/vnd.openxmlformats")
    assert len(xlsx_resp.content) > 1000


def test_cors_explicit_origins_only():
    from app.main import create_app
    base = Settings(
        database_path=":memory:",
        app_timezone="Asia/Kolkata",
        admin_username="u",
        admin_password="p" * 16,
    )
    closed = create_app(base)
    with TestClient(closed) as client:
        response = client.options(
            "/api/v1/students",
            headers={"Origin": "http://lan:8000", "Access-Control-Request-Method": "GET"},
        )
        assert "access-control-allow-origin" not in {k.lower() for k in response.headers}
    opened_settings = Settings(
        database_path=":memory:",
        app_timezone="Asia/Kolkata",
        admin_username="u",
        admin_password="p" * 16,
        allowed_origins="http://lan:8000",
    )
    with TestClient(create_app(opened_settings)) as client:
        response = client.options(
            "/api/v1/students",
            headers={"Origin": "http://lan:8000", "Access-Control-Request-Method": "GET"},
        )
        assert response.headers.get("access-control-allow-origin") == "http://lan:8000"


def test_event_bus_and_ai_without_key(client: TestClient):
    seed_device(client)
    queue = BUS.subscribe()
    try:
        BUS.publish("attendance.recorded", {"event_uuid": "x"})
        message = queue.get_nowait()
        assert "attendance.recorded" in message
    finally:
        BUS.unsubscribe(queue)
    assert AI.TOOLS and "get_today_attendance" in AI.TOOLS
    tool, _ = AI.route("Who was absent today?")
    assert tool == "get_absent_students"
    tool, _ = AI.route("What is attendance for Class 10A?")
    assert tool == "get_class_attendance"
    chat = client.post("/api/v1/ai/chat", auth=ADMIN, json={"question": "Summarize today's attendance."})
    assert chat.status_code == 200
    body = chat.json()
    assert body["ai_available"] is False
    assert "GEMINI_API_KEY" in body["answer"]
    assert client.post("/api/v1/ai/chat", auth=ADMIN, json={"question": ""}).status_code == 422
    assert client.post("/api/v1/ai/chat", auth=ADMIN, json={"question": "x" * 501}).status_code == 422


def test_duplicate_protection_counts_once(client: TestClient):
    seed_device(client)
    student = make_student(client, "R-501", "Meera", "Iyer", "10A", "A")
    activate(client, student)
    moment = datetime.now(UTC) - timedelta(seconds=60)
    first = checkin(client, student["fingerprint_slot_id"], moment)
    assert first.status_code == 201
    dup = checkin(client, student["fingerprint_slot_id"], moment + timedelta(seconds=30))
    assert dup.json()["outcome"] == "DUPLICATE_SUPPRESSED"
    listing = client.get("/api/v1/attendance", auth=ADMIN).json()
    assert listing["total"] == 1


def test_time_filter_applies_before_pagination(client: TestClient):
    seed_device(client)
    student = make_student(client, "R-701", "Time", "Filter", "10A", "A")
    activate(client, student)
    slot = student["fingerprint_slot_id"]
    early_ts = (datetime.now(UTC) - timedelta(hours=3)).replace(minute=5, second=0, microsecond=0)
    late_ts = (datetime.now(UTC) - timedelta(hours=1)).replace(minute=45, second=0, microsecond=0)
    assert checkin(client, slot, early_ts, live=False).status_code == 201
    assert checkin(client, slot, late_ts, live=False).status_code == 201
    lo = (late_ts - timedelta(minutes=10)).strftime("%H:%M")
    hi = (late_ts + timedelta(minutes=10)).strftime("%H:%M")
    window = client.get(f"/api/v1/attendance?time_from={lo}&time_to={hi}", auth=ADMIN).json()
    assert window["total"] == 1
    assert window["items"][0]["captured_at_utc"][11:16] == late_ts.strftime("%H:%M")
    early = client.get("/api/v1/attendance?time_from=00:00&time_to=00:01", auth=ADMIN).json()
    assert early["total"] == 0


def test_admin_activate_enrollment(client: TestClient):
    seed_device(client)
    student = make_student(client, "R-601", "Asha", "Menon", "10A", "A")
    assert student["status"] == "PENDING_ENROLLMENT"
    activated = client.post(f"/api/v1/students/{student['student_uuid']}/activate", auth=ADMIN)
    assert activated.status_code == 200
    assert activated.json() == {"student_uuid": student["student_uuid"], "status": "ACTIVE"}
    again = client.post(f"/api/v1/students/{student['student_uuid']}/activate", auth=ADMIN)
    assert again.status_code == 200
    assert again.json()["status"] == "ACTIVE"
    assert client.post("/api/v1/students/00000000-0000-0000-0000-000000000000/activate", auth=ADMIN).status_code == 404
    assert client.post(f"/api/v1/students/{student['student_uuid']}/activate").status_code == 401
