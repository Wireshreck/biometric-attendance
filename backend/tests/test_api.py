from __future__ import annotations

import asyncio
import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.database import connect_database
from app.main import create_app
from app.provision_device import provision


DEVICE_UUID = "9d6f13ab-e7c3-4c12-a258-a46c2240d01d"
DEVICE_TOKEN = "device-secret"


@pytest.fixture
def client(tmp_path: Path):
    settings = Settings(
        database_path=tmp_path / "api.db",
        app_timezone="Asia/Kolkata",
        admin_username="demo-admin",
        admin_password="test-password-at-least-16",
    )
    with TestClient(create_app(settings)) as test_client:
        yield test_client


def seed_device(client: TestClient, *, capacity: int | None = 20, device_uuid: str = DEVICE_UUID) -> None:
    connection = asyncio.run(connect_database(client.app.state.settings.database_path))
    try:
        asyncio.run(connection.execute(
            """INSERT INTO devices
               (device_uuid, device_name, location_name, token_hash, status, sensor_capacity, created_at_utc)
               VALUES (?, 'Terminal', 'Lab', ?, 'ACTIVE', ?, ?)""",
            (device_uuid, hashlib.sha256(DEVICE_TOKEN.encode()).hexdigest(), capacity, "2026-09-25T00:00:00Z"),
        ))
    finally:
        asyncio.run(connection.close())


def test_health_and_admin_student_lifecycle(client: TestClient):
    assert client.get("/health").json() == {"status": "ok", "schema_version": 1}
    assert client.get("/api/v1/students").status_code == 401

    seed_device(client)

    admin = ("demo-admin", "test-password-at-least-16")
    created = client.post("/api/v1/students", auth=admin, json={
        "roll_number": "R-001", "first_name": "Test", "last_name": "Student", "grade_class": "A",
    })
    assert created.status_code == 201
    student = created.json()
    assert student["fingerprint_slot_id"] == 1
    assert student["status"] == "PENDING_ENROLLMENT"
    assert client.get(f"/api/v1/students/{student['student_uuid']}", auth=admin).json() == student
    assert client.get("/api/v1/students?limit=101", auth=admin).status_code == 422
    assert client.get(f"/api/v1/students/{uuid.uuid4()}", auth=admin).status_code == 404
    assert client.post("/api/v1/students", auth=admin, json={
        "roll_number": "R-001", "first_name": "Duplicate", "last_name": "Student", "grade_class": "A",
    }).status_code == 409
    deactivated = client.post(f"/api/v1/students/{student['student_uuid']}/deactivate", auth=admin)
    assert deactivated.status_code == 200
    assert deactivated.json() == {
        "student_uuid": student["student_uuid"], "status": "INACTIVE", "template_cleanup_required": False,
    }


def test_device_enrollment_attendance_idempotency_and_duplicate_window(client: TestClient):
    admin = ("demo-admin", "test-password-at-least-16")
    device_uuid = DEVICE_UUID
    bad_auth = client.post("/api/v1/attendance", json={})
    assert bad_auth.status_code == 401

    seed_device(client)
    headers = {"Authorization": f"Bearer {DEVICE_TOKEN}"}
    student = client.post("/api/v1/students", auth=admin, json={
        "roll_number": "R-001", "first_name": "Test", "last_name": "Student", "grade_class": "A",
    }).json()
    path = f"/api/v1/devices/{device_uuid}/enrollment/{student['student_uuid']}"
    assignment = client.get(path, headers=headers)
    assert assignment.status_code == 200
    assert assignment.json() == {"student_uuid": student["student_uuid"], "fingerprint_slot_id": 1, "capacity": 20}
    completed = client.post(path + "/complete", headers=headers, json={"result": "SUCCESS", "fingerprint_slot_id": 1})
    assert completed.status_code == 200
    assert completed.json()["status"] == "ACTIVE"

    captured_base = datetime.now(UTC) - timedelta(seconds=120)

    def submit(event_id: str, offset: int):
        timestamp = (captured_base + timedelta(seconds=offset)).isoformat()
        return client.post("/api/v1/attendance", headers=headers, json={
            "event_uuid": event_id, "fingerprint_slot_id": 1,
            "captured_at": timestamp, "sync_status": "LIVE",
        })

    first_uuid = str(uuid.uuid4())
    first = submit(first_uuid, 0)
    assert first.status_code == 201
    assert first.json()["outcome"] == "RECORDED"
    replay = submit(first_uuid, 10)
    assert replay.status_code == 200
    assert replay.json() == first.json()
    at_sixty = submit(str(uuid.uuid4()), 60)
    assert at_sixty.status_code == 200
    assert at_sixty.json()["outcome"] == "DUPLICATE_SUPPRESSED"
    after_sixty = submit(str(uuid.uuid4()), 61)
    assert after_sixty.status_code == 201
    assert after_sixty.json()["outcome"] == "RECORDED"
    assert client.post("/api/v1/attendance", headers={"Authorization": "Bearer wrong"}, json={}).status_code == 401
    too_far_future = client.post("/api/v1/attendance", headers=headers, json={
        "event_uuid": str(uuid.uuid4()), "fingerprint_slot_id": 1,
        "captured_at": (datetime.now(UTC) + timedelta(minutes=10)).isoformat(),
        "sync_status": "LIVE",
    })
    assert too_far_future.status_code == 422
    assert too_far_future.json()["error"]["code"] == "clock_skew"


def test_invalid_attendance_payload_and_unassigned_slot(client: TestClient):
    seed_device(client)
    headers = {"Authorization": f"Bearer {DEVICE_TOKEN}"}
    response = client.post("/api/v1/attendance", json={
        "event_uuid": str(uuid.uuid4()), "fingerprint_slot_id": 1,
        "captured_at": "2026-09-25T12:00:00", "sync_status": "LIVE",
    }, headers=headers)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    slot = client.post("/api/v1/attendance", headers=headers, json={
        "event_uuid": str(uuid.uuid4()), "fingerprint_slot_id": 1,
        "captured_at": datetime.now(UTC).isoformat(), "sync_status": "LIVE",
    })
    assert slot.status_code == 409
    assert slot.json()["error"]["code"] == "unknown_slot"


def test_local_device_provisioning_stores_only_token_hash(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "provisioned.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    device_uuid, token = asyncio.run(provision("Test terminal", "Lab", 7))
    connection = asyncio.run(connect_database(db_path))
    try:
        cursor = asyncio.run(connection.execute(
            "SELECT device_uuid, token_hash, sensor_capacity FROM devices WHERE device_uuid=?", (device_uuid,)
        ))
        device = asyncio.run(cursor.fetchone())
        assert device[0] == device_uuid
        assert device[1] == hashlib.sha256(token.encode()).hexdigest()
        assert device[1] != token
        assert device[2] == 7
        cursor = asyncio.run(connection.execute(
            "SELECT action, target_id FROM admin_audit_log WHERE action='DEVICE_PROVISIONED'"
        ))
        assert tuple(asyncio.run(cursor.fetchone())) == ("DEVICE_PROVISIONED", device_uuid)
    finally:
        asyncio.run(connection.close())
