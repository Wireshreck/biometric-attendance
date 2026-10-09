"""Phase-2 failure campaign: offline sync edge cases, auth, conflicts,
concurrency, CORS, and validation. Every test runs against the real app.
"""

from __future__ import annotations

import asyncio
import hashlib
import threading
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
        database_path=tmp_path / "fail.db",
        app_timezone="Asia/Kolkata",
        admin_username="demo-admin",
        admin_password="test-password-at-least-16",
    )
    with TestClient(create_app(settings)) as test_client:
        yield test_client


def seed_device(client: TestClient, device_uuid: str = DEVICE_UUID,
                token: str = DEVICE_TOKEN, capacity: int | None = 20,
                status: str = "ACTIVE") -> None:
    async def _seed():
        connection = await connect_database(client.app.state.settings.database_path)
        try:
            await connection.execute(
                """INSERT INTO devices
                   (device_uuid, device_name, location_name, token_hash, status,
                    sensor_capacity, created_at_utc)
                   VALUES (?, 'Terminal', 'Lab', ?, ?, ?, ?)""",
                (device_uuid, hashlib.sha256(token.encode()).hexdigest(),
                 status, capacity, "2026-10-08T00:00:00Z"),
            )
            await connection.commit()
        finally:
            await connection.close()
    asyncio.run(_seed())


def make_employee(client: TestClient, code: str = "E-001") -> dict:
    response = client.post("/api/v1/students", auth=ADMIN, json={
        "employee_code": code, "first_name": "Asha", "last_name": "Menon",
        "department": "Engineering", "team": "A"})
    assert response.status_code == 201, response.text
    return response.json()


def activate(client: TestClient, employee: dict, token: str = DEVICE_TOKEN) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    uuid_key = employee.get("employee_uuid") or employee["student_uuid"]
    path = f"/api/v1/devices/{DEVICE_UUID}/enrollment/{uuid_key}"
    response = client.post(path + "/complete", headers=headers, json={
        "result": "SUCCESS", "fingerprint_slot_id": employee["fingerprint_slot_id"]})
    assert response.status_code == 200, response.text


def test_batch_auth_and_shape_validation(client: TestClient):
    seed_device(client)
    assert client.post("/api/v1/attendance/batch", json={"events": []}).status_code == 401
    assert client.post("/api/v1/attendance/batch", auth=("demo-admin", "wrong-password-0000"),
                       json={"events": []}).status_code == 401
    # Empty batch rejected; oversized batch rejected; naive datetime rejected.
    assert client.post("/api/v1/attendance/batch", auth=ADMIN, json={"events": []}).status_code == 422
    big = [{"event_uuid": str(uuid.uuid4()), "fingerprint_slot_id": 1,
            "captured_at": datetime.now(UTC).isoformat()} for _ in range(101)]
    assert client.post("/api/v1/attendance/batch", auth=ADMIN, json={"events": big}).status_code == 422
    naive = client.post("/api/v1/attendance/batch", auth=ADMIN, json={"events": [{
        "event_uuid": str(uuid.uuid4()), "fingerprint_slot_id": 1,
        "captured_at": "2026-10-01T12:00:00"}]})
    assert naive.status_code == 422
    # Unknown slot is a per-item error, not a whole-request failure.
    mixed = client.post("/api/v1/attendance/batch", auth=ADMIN, json={"events": [{
        "event_uuid": str(uuid.uuid4()), "fingerprint_slot_id": 4242,
        "captured_at": (datetime.now(UTC) - timedelta(hours=1)).isoformat()}]})
    assert mixed.status_code == 200
    assert mixed.json()["failed"] == 1
    assert mixed.json()["items"][0]["code"] == "unknown_slot"


def test_batch_future_rejected_old_accepted(client: TestClient):
    seed_device(client)
    employee = make_employee(client)
    activate(client, employee)
    slot = employee["fingerprint_slot_id"]
    future = client.post("/api/v1/attendance/batch", auth=ADMIN, json={"events": [{
        "event_uuid": str(uuid.uuid4()), "fingerprint_slot_id": slot,
        "captured_at": (datetime.now(UTC) + timedelta(minutes=10)).isoformat()}]})
    assert future.json()["items"][0]["code"] == "future_timestamp"
    old = client.post("/api/v1/attendance/batch", auth=ADMIN, json={"events": [{
        "event_uuid": str(uuid.uuid4()), "fingerprint_slot_id": slot,
        "captured_at": (datetime.now(UTC) - timedelta(days=9)).isoformat()}]})
    assert old.json()["items"][0]["status"] == "ok"
    assert old.json()["items"][0]["outcome"] == "RECORDED"


def test_batch_debounce_same_employee(client: TestClient):
    seed_device(client)
    employee = make_employee(client)
    activate(client, employee)
    slot = employee["fingerprint_slot_id"]
    base = datetime.now(UTC) - timedelta(hours=2)
    body = {"events": [
        {"event_uuid": str(uuid.uuid4()), "fingerprint_slot_id": slot,
         "captured_at": base.isoformat()},
        {"event_uuid": str(uuid.uuid4()), "fingerprint_slot_id": slot,
         "captured_at": (base + timedelta(seconds=30)).isoformat()},
        {"event_uuid": str(uuid.uuid4()), "fingerprint_slot_id": slot,
         "captured_at": (base + timedelta(seconds=120)).isoformat()},
    ]}
    result = client.post("/api/v1/attendance/batch", auth=ADMIN, json=body).json()
    assert [i["outcome"] for i in result["items"]] == ["RECORDED", "DUPLICATE_SUPPRESSED", "RECORDED"]
    # Default listing counts RECORDED only.
    assert client.get("/api/v1/attendance", auth=ADMIN).json()["total"] == 2


def test_cross_device_uuid_conflict(client: TestClient):
    seed_device(client)
    employee = make_employee(client)
    activate(client, employee)
    # Second device joins AFTER enrollment (fleet ambiguity is the point).
    seed_device(client, device_uuid="11111111-1111-4111-8111-111111111111",
                token="second-device-secret")
    headers1 = {"Authorization": f"Bearer {DEVICE_TOKEN}"}
    headers2 = {"Authorization": "Bearer second-device-secret"}
    captured = (datetime.now(UTC) - timedelta(minutes=2)).isoformat()
    event_id = str(uuid.uuid4())
    first = client.post("/api/v1/attendance", headers=headers1, json={
        "event_uuid": event_id, "fingerprint_slot_id": 1,
        "captured_at": captured, "sync_status": "LIVE"})
    assert first.status_code == 201
    # Same UUID from another device must conflict, never overwrite.
    # (slot 1 is unassigned on device 2, so use the raw conflict path: the
    # UUID check runs before slot resolution.)
    clash = client.post("/api/v1/attendance", headers=headers2, json={
        "event_uuid": event_id, "fingerprint_slot_id": 1,
        "captured_at": captured, "sync_status": "LIVE"})
    assert clash.status_code == 409
    assert clash.json()["error"]["code"] == "event_conflict"
    # Batch endpoint refuses ambiguous multi-device fleets honestly.
    batch = client.post("/api/v1/attendance/batch", auth=ADMIN, json={"events": [{
        "event_uuid": str(uuid.uuid4()), "fingerprint_slot_id": 1,
        "captured_at": captured}]})
    assert batch.status_code == 409
    assert batch.json()["error"]["code"] == "device_configuration"


def test_concurrent_same_uuid_single_row(client: TestClient):
    seed_device(client)
    employee = make_employee(client)
    activate(client, employee)
    slot = employee["fingerprint_slot_id"]
    captured = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
    event_id = str(uuid.uuid4())
    errors: list = []

    def fire():
        try:
            from fastapi.testclient import TestClient as TC
            # Each thread needs its own client (httpx clients are not thread-safe).
            with TC(create_app(client.app.state.settings)) as thread_client:
                response = thread_client.post("/api/v1/attendance/batch", auth=ADMIN, json={"events": [{
                    "event_uuid": event_id, "fingerprint_slot_id": slot, "captured_at": captured}]})
                assert response.status_code == 200
                assert response.json()["accepted"] == 1
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=fire) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors, errors[:1]
    assert client.get("/api/v1/attendance", auth=ADMIN).json()["total"] == 1


def test_snapshot_and_company_auth_and_cors(client: TestClient):
    seed_device(client)
    assert client.get("/api/v1/sync/snapshot").status_code == 401
    assert client.get("/api/v1/settings/company").status_code == 401
    # Snapshot exposes only the required fields (no token hashes, ever).
    snapshot = client.get("/api/v1/sync/snapshot", auth=ADMIN).json()
    blob = str(snapshot)
    assert "token_hash" not in blob and "device-secret" not in blob
    # Unknown settings keys alone are rejected, not silently stored.
    assert client.put("/api/v1/settings/company", auth=ADMIN,
                      json={"hacker_field": "x"}).status_code == 422
    # CORS preflight covers the methods the console actually uses.
    settings = Settings(database_path=":memory:", app_timezone="Asia/Kolkata",
                        admin_username="u", admin_password="p" * 16,
                        allowed_origins="http://lan:8000")
    with TestClient(create_app(settings)) as cors_client:
        for method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
            response = cors_client.options(
                "/api/v1/students",
                headers={"Origin": "http://lan:8000", "Access-Control-Request-Method": method})
            allow = response.headers.get("access-control-allow-methods", "")
            assert method in allow, (method, allow)


def test_attendance_department_team_filters_and_exports(client: TestClient):
    seed_device(client)
    employee = make_employee(client)
    activate(client, employee)
    headers = {"Authorization": f"Bearer {DEVICE_TOKEN}"}
    moment = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
    assert client.post("/api/v1/attendance", headers=headers, json={
        "event_uuid": str(uuid.uuid4()),
        "fingerprint_slot_id": employee["fingerprint_slot_id"],
        "captured_at": moment, "sync_status": "REPLAYED_OFFLINE"}).status_code == 201
    assert client.get("/api/v1/attendance?department=Engineering", auth=ADMIN).json()["total"] == 1
    assert client.get("/api/v1/attendance?department=Nowhere", auth=ADMIN).json()["total"] == 0
    assert client.get("/api/v1/attendance?team=A", auth=ADMIN).json()["total"] == 1
    csv_resp = client.get("/api/v1/export.csv?team=A", auth=ADMIN)
    assert csv_resp.status_code == 200 and "E-001" in csv_resp.text
    assert client.get("/api/v1/attendance?sort=employee&order=asc", auth=ADMIN).status_code == 200
    assert client.get("/api/v1/attendance?sort=department&order=asc", auth=ADMIN).status_code == 200
