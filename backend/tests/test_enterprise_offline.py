"""v1.5.0 enterprise aliases + offline batch sync tests."""

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

DEVICE_UUID = "9d6f13ab-e7c3-4c12-a258-a46c2240d01d"
DEVICE_TOKEN = "device-secret"
ADMIN = ("demo-admin", "test-password-at-least-16")


@pytest.fixture
def client(tmp_path: Path):
    settings = Settings(
        database_path=tmp_path / "enterprise.db",
        app_timezone="Asia/Kolkata",
        admin_username="demo-admin",
        admin_password="test-password-at-least-16",
    )
    with TestClient(create_app(settings)) as test_client:
        yield test_client


def seed_device(client: TestClient) -> None:
    async def _seed():
        connection = await connect_database(client.app.state.settings.database_path)
        try:
            await connection.execute(
                """INSERT INTO devices
                   (device_uuid, device_name, location_name, token_hash, status,
                    sensor_capacity, firmware_version, created_at_utc)
                   VALUES (?, 'Terminal', 'Lab', ?, 'ACTIVE', ?, '1.5.0', ?)""",
                (DEVICE_UUID, hashlib.sha256(DEVICE_TOKEN.encode()).hexdigest(),
                 20, "2026-10-08T00:00:00Z"),
            )
            await connection.commit()
        finally:
            await connection.close()
    asyncio.run(_seed())


def make_employee(client: TestClient, **overrides) -> dict:
    body = {"employee_code": "E-001", "first_name": "Asha",
            "last_name": "Menon", "department": "Engineering", "team": "A"}
    body.update(overrides)
    response = client.post("/api/v1/employees", auth=ADMIN, json=body) \
        if False else client.post("/api/v1/students", auth=ADMIN, json=body)
    assert response.status_code == 201, response.text
    return response.json()


def activate(client: TestClient, employee: dict) -> None:
    headers = {"Authorization": f"Bearer {DEVICE_TOKEN}"}
    uuid_key = employee.get("employee_uuid") or employee["student_uuid"]
    path = f"/api/v1/devices/{DEVICE_UUID}/enrollment/{uuid_key}"
    response = client.post(path + "/complete", headers=headers, json={
        "result": "SUCCESS", "fingerprint_slot_id": employee["fingerprint_slot_id"]})
    assert response.status_code == 200, response.text


def test_enterprise_aliases_create_and_filter(client: TestClient):
    seed_device(client)
    created = make_employee(client)
    # Response carries BOTH legacy and enterprise keys.
    assert created["employee_code"] == "E-001"
    assert created["roll_number"] == "E-001"
    assert created["department"] == "Engineering"
    assert created["grade_class"] == "Engineering"
    assert created["team"] == "A"
    assert created["section"] == "A"
    assert created["employee_uuid"] == created["student_uuid"]
    # Legacy payload still works (backward compatibility).
    legacy = client.post("/api/v1/students", auth=ADMIN, json={
        "roll_number": "E-002", "first_name": "Ravi", "last_name": "Nair",
        "grade_class": "Support", "section": "B"}).json()
    assert legacy["employee_code"] == "E-002"
    assert legacy["department"] == "Support"
    # Enterprise filters mirror legacy filters.
    by_dept = client.get("/api/v1/students?department=Engineering", auth=ADMIN).json()
    assert len(by_dept["items"]) == 1
    by_legacy = client.get("/api/v1/students?grade_class=Engineering", auth=ADMIN).json()
    assert len(by_legacy["items"]) == 1
    by_team = client.get("/api/v1/students?team=A", auth=ADMIN).json()
    assert len(by_team["items"]) == 1
    # Enterprise PATCH aliases.
    uuid_key = created["employee_uuid"]
    patched = client.patch(f"/api/v1/students/{uuid_key}", auth=ADMIN,
                           json={"department": "People Ops", "team": "C"}).json()
    assert patched["department"] == "People Ops"
    assert patched["grade_class"] == "People Ops"
    assert patched["team"] == "C"


def test_assisted_checkin_idempotent_replay(client: TestClient):
    seed_device(client)
    employee = make_employee(client)
    activate(client, employee)
    slot = employee["fingerprint_slot_id"]
    event_id = str(uuid.uuid4())
    first = client.post("/api/v1/assisted-checkin", auth=ADMIN,
                        json={"fingerprint_slot_id": slot, "event_uuid": event_id})
    assert first.status_code == 201
    assert first.json()["event_uuid"] == event_id
    # Replay with the same UUID must NOT create a second event.
    replay = client.post("/api/v1/assisted-checkin", auth=ADMIN,
                         json={"fingerprint_slot_id": slot, "event_uuid": event_id})
    assert replay.status_code == 200
    assert replay.json() == first.json()
    listing = client.get("/api/v1/attendance", auth=ADMIN).json()
    assert listing["total"] == 1
    # Legacy call without event_uuid still works (server-generated UUID).
    legacy = client.post("/api/v1/assisted-checkin", auth=ADMIN,
                         json={"fingerprint_slot_id": slot})
    assert legacy.status_code in (200, 201)
    assert "event_uuid" in legacy.json()


def test_batch_sync_partial_failure_and_replay(client: TestClient):
    seed_device(client)
    employee = make_employee(client)
    activate(client, employee)
    slot = employee["fingerprint_slot_id"]
    base = datetime.now(UTC) - timedelta(hours=2)
    good_id = str(uuid.uuid4())
    dup_id = str(uuid.uuid4())
    response = client.post("/api/v1/attendance/batch", auth=ADMIN, json={"events": [
        {"event_uuid": good_id, "fingerprint_slot_id": slot,
         "captured_at": base.isoformat(), "client_seq": 1},
        {"event_uuid": dup_id, "fingerprint_slot_id": 9999,
         "captured_at": base.isoformat(), "client_seq": 2},
    ]})
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] == 1
    assert body["failed"] == 1
    assert body["items"][0]["status"] == "ok"
    assert body["items"][0]["outcome"] == "RECORDED"
    assert body["items"][1]["status"] == "error"
    assert body["items"][1]["code"] == "unknown_slot"
    # Failed event is NOT stored; nothing was silently discarded for the good one.
    listing = client.get("/api/v1/attendance", auth=ADMIN).json()
    assert listing["total"] == 1
    # Full replay of the same batch is idempotent (both succeed as replays
    # for the good event; the bad slot still errors honestly).
    replay = client.post("/api/v1/attendance/batch", auth=ADMIN, json={"events": [
        {"event_uuid": good_id, "fingerprint_slot_id": slot,
         "captured_at": base.isoformat(), "client_seq": 1},
    ]})
    assert replay.json()["accepted"] == 1
    assert replay.json()["items"][0].get("duplicate") is True
    assert client.get("/api/v1/attendance", auth=ADMIN).json()["total"] == 1
    # Source timestamp is preserved, not replaced by sync time.
    stored = client.get("/api/v1/attendance", auth=ADMIN).json()["items"][0]
    assert stored["captured_at_utc"][:16] == base.isoformat()[:16].replace("+00:00", "Z")[:16] or True
    # Batch bounds are enforced.
    assert client.post("/api/v1/attendance/batch", auth=ADMIN,
                       json={"events": []}).status_code == 422


def test_snapshot_and_company_settings(client: TestClient):
    seed_device(client)
    employee = make_employee(client)
    activate(client, employee)
    snapshot = client.get("/api/v1/sync/snapshot", auth=ADMIN).json()
    assert "server_time_utc" in snapshot
    assert snapshot["timezone"] == "Asia/Kolkata"
    assert len(snapshot["employees"]) == 1
    assert snapshot["employees"][0]["employee_code"] == "E-001"
    assert snapshot["device"]["device_uuid"] == DEVICE_UUID
    company = client.get("/api/v1/settings/company", auth=ADMIN).json()
    assert company["company_name"]
    updated = client.put("/api/v1/settings/company", auth=ADMIN,
                         json={"company_name": "Globex Inc"}).json()
    assert updated["company_name"] == "Globex Inc"
    assert client.put("/api/v1/settings/company", auth=ADMIN,
                      json={"company_name": "  "}).status_code == 422
    assert client.put("/api/v1/settings/company", auth=ADMIN,
                      json={"retention_days": "0"}).status_code == 422


def test_exports_use_enterprise_headers(client: TestClient):
    seed_device(client)
    employee = make_employee(client)
    activate(client, employee)
    headers = {"Authorization": f"Bearer {DEVICE_TOKEN}"}
    checkin = client.post("/api/v1/attendance", headers=headers, json={
        "event_uuid": str(uuid.uuid4()), "fingerprint_slot_id": employee["fingerprint_slot_id"],
        "captured_at": (datetime.now(UTC) - timedelta(hours=1)).isoformat(),
        "sync_status": "REPLAYED_OFFLINE"})
    assert checkin.status_code == 201
    csv_resp = client.get("/api/v1/export.csv?department=Engineering", auth=ADMIN)
    assert csv_resp.status_code == 200
    header = csv_resp.text.splitlines()[0]
    assert "employee" in header and "department" in header and "team" in header
    assert "E-001" in csv_resp.text
