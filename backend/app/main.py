"""FastAPI application: health, student administration, and device attendance ingest."""

from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import Annotated

import aiosqlite
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.auth import require_admin, require_device
from app.config import Settings
from app.database import SCHEMA_VERSION, connect_database, initialize_database
from app.dependencies import get_connection, get_settings
from app.schemas import AttendanceCreate, AttendanceResult, EnrollmentComplete, Student, StudentCreate, StudentList

logger = logging.getLogger(__name__)


def _utc_text(value: datetime) -> str:
    return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def create_app(settings: Settings | None = None) -> FastAPI:
    actual_settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        actual_settings.validate()
        await initialize_database(actual_settings.database_path)
        yield

    app = FastAPI(
        title="Biometric Attendance API",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.settings = actual_settings

    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, exc: HTTPException):
        detail = exc.detail if isinstance(exc.detail, dict) else {
            "code": "http_error", "message": str(exc.detail)
        }
        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers,
            content={"error": {**detail, "correlation_id": request.headers.get("x-correlation-id", str(uuid.uuid4()))}},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"error": {
                "code": "validation_error",
                "message": "Request did not match the API contract",
                "correlation_id": request.headers.get("x-correlation-id", str(uuid.uuid4())),
            }},
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception):
        correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))
        logger.exception("Unhandled API error correlation_id=%s", correlation_id)
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": "An internal error occurred", "correlation_id": correlation_id}},
        )

    @app.get("/health")
    async def health():
        try:
            connection = await connect_database(actual_settings.database_path)
            await connection.close()
        except Exception as exc:
            logger.warning("Health check could not open database: %s", type(exc).__name__)
            raise HTTPException(503, {"code": "unavailable", "message": "Database is unavailable"}) from exc
        return {"status": "ok", "schema_version": SCHEMA_VERSION}

    @app.get("/api/v1/students", response_model=StudentList)
    async def list_students(
        _actor: Annotated[str, Depends(require_admin)],
        connection: Annotated[aiosqlite.Connection, Depends(get_connection)],
        grade_class: str | None = None,
        status: str | None = None,
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
    ):
        if status is not None and status not in {"PENDING_ENROLLMENT", "ACTIVE", "INACTIVE"}:
            raise HTTPException(422, {"code": "invalid_status", "message": "Unsupported student status"})
        clauses, parameters = [], []
        if grade_class is not None:
            clauses.append("grade_class = ?")
            parameters.append(grade_class)
        if status is not None:
            clauses.append("status = ?")
            parameters.append(status)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        async with connection.execute(
            "SELECT student_uuid, roll_number, first_name, last_name, grade_class, status, fingerprint_slot_id "
            f"FROM students{where} ORDER BY last_name, first_name, student_uuid LIMIT ? OFFSET ?",
            (*parameters, limit, offset),
        ) as cursor:
            rows = await cursor.fetchall()
        return {"items": [dict(row) for row in rows], "limit": limit, "offset": offset}

    @app.post("/api/v1/students", status_code=201, response_model=Student)
    async def create_student(
        body: StudentCreate,
        actor: Annotated[str, Depends(require_admin)],
        connection: Annotated[aiosqlite.Connection, Depends(get_connection)],
    ):
        now = _utc_text(datetime.now(UTC))
        try:
            await connection.execute("BEGIN IMMEDIATE")
            async with connection.execute(
                "SELECT id, sensor_capacity FROM devices WHERE status='ACTIVE' ORDER BY id"
            ) as cursor:
                devices = await cursor.fetchall()
            if len(devices) != 1:
                await connection.rollback()
                raise HTTPException(409, {"code": "device_configuration", "message": "Exactly one active MVP device is required"})
            device_id, capacity = devices[0]["id"], devices[0]["sensor_capacity"]
            if capacity is None:
                await connection.rollback()
                raise HTTPException(409, {"code": "capacity_unknown", "message": "Device sensor capacity must be reported before enrollment"})
            async with connection.execute(
                "SELECT fingerprint_slot_id FROM students WHERE enrollment_device_id=? AND fingerprint_slot_id IS NOT NULL",
                (device_id,),
            ) as cursor:
                used = {int(row[0]) for row in await cursor.fetchall()}
            slot = 1
            for used_slot in sorted(used):
                if used_slot == slot:
                    slot += 1
                elif used_slot > slot:
                    break
            if slot > int(capacity):
                await connection.rollback()
                raise HTTPException(409, {"code": "no_slots", "message": "No unassigned sensor slots remain"})
            student_uuid = str(uuid.uuid4())
            await connection.execute(
                """INSERT INTO students
                   (student_uuid, roll_number, first_name, last_name, grade_class,
                    enrollment_device_id, fingerprint_slot_id, status, created_at_utc, updated_at_utc)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING_ENROLLMENT', ?, ?)""",
                (student_uuid, body.roll_number, body.first_name, body.last_name,
                 body.grade_class, device_id, slot, now, now),
            )
            await connection.execute(
                "INSERT INTO admin_audit_log (occurred_at_utc, actor, action, target_type, target_id) VALUES (?, ?, 'STUDENT_CREATED', 'student', ?)",
                (now, actor, student_uuid),
            )
            await connection.commit()
        except aiosqlite.IntegrityError as exc:
            await connection.rollback()
            raise HTTPException(409, {"code": "student_conflict", "message": "Roll number or slot conflicts with an existing record"}) from exc
        return {**body.model_dump(), "student_uuid": student_uuid, "status": "PENDING_ENROLLMENT", "fingerprint_slot_id": slot}

    @app.get("/api/v1/students/{student_uuid}", response_model=Student)
    async def get_student(
        student_uuid: uuid.UUID,
        _actor: Annotated[str, Depends(require_admin)],
        connection: Annotated[aiosqlite.Connection, Depends(get_connection)],
    ):
        async with connection.execute(
            "SELECT student_uuid, roll_number, first_name, last_name, grade_class, status, fingerprint_slot_id FROM students WHERE student_uuid=?",
            (str(student_uuid),),
        ) as cursor:
            row = await cursor.fetchone()
        if row is None:
            raise HTTPException(404, {"code": "not_found", "message": "Student was not found"})
        return dict(row)

    @app.get("/api/v1/devices/{device_uuid}/enrollment/{student_uuid}")
    async def enrollment_assignment(
        device_uuid: uuid.UUID,
        student_uuid: uuid.UUID,
        device: Annotated[dict[str, object], Depends(require_device)],
        connection: Annotated[aiosqlite.Connection, Depends(get_connection)],
    ):
        if device["device_uuid"] != str(device_uuid):
            raise HTTPException(401, {"code": "device_mismatch", "message": "Credential does not match device path"})
        async with connection.execute(
            """SELECT s.fingerprint_slot_id, s.status, d.sensor_capacity
               FROM students s JOIN devices d ON d.id=s.enrollment_device_id
               WHERE s.student_uuid=? AND d.id=?""",
            (str(student_uuid), device["id"]),
        ) as cursor:
            row = await cursor.fetchone()
        if row is None:
            raise HTTPException(404, {"code": "not_found", "message": "Enrollment assignment was not found"})
        if row["status"] != "PENDING_ENROLLMENT":
            raise HTTPException(409, {"code": "invalid_state", "message": "Student is not pending enrollment"})
        return {"student_uuid": str(student_uuid), "fingerprint_slot_id": row["fingerprint_slot_id"], "capacity": row["sensor_capacity"]}

    @app.post("/api/v1/devices/{device_uuid}/enrollment/{student_uuid}/complete")
    async def complete_enrollment(
        device_uuid: uuid.UUID,
        student_uuid: uuid.UUID,
        body: EnrollmentComplete,
        device: Annotated[dict[str, object], Depends(require_device)],
        connection: Annotated[aiosqlite.Connection, Depends(get_connection)],
    ):
        if device["device_uuid"] != str(device_uuid):
            raise HTTPException(401, {"code": "device_mismatch", "message": "Credential does not match device path"})
        now = _utc_text(datetime.now(UTC))
        await connection.execute("BEGIN IMMEDIATE")
        async with connection.execute(
            """SELECT s.id, s.status, s.fingerprint_slot_id FROM students s
               WHERE s.student_uuid=? AND s.enrollment_device_id=?""",
            (str(student_uuid), device["id"]),
        ) as cursor:
            row = await cursor.fetchone()
        if row is None:
            await connection.rollback()
            raise HTTPException(404, {"code": "not_found", "message": "Enrollment assignment was not found"})
        if row["status"] != "PENDING_ENROLLMENT" or row["fingerprint_slot_id"] != body.fingerprint_slot_id:
            await connection.rollback()
            raise HTTPException(409, {"code": "invalid_enrollment", "message": "Enrollment state or slot does not match"})
        await connection.execute(
            "UPDATE students SET status='ACTIVE', updated_at_utc=? WHERE id=?",
            (now, row["id"]),
        )
        await connection.execute(
            "INSERT INTO admin_audit_log (occurred_at_utc, actor, action, target_type, target_id) VALUES (?, ?, 'ENROLLMENT_COMPLETED', 'student', ?)",
            (now, f"device:{device['device_uuid']}", str(student_uuid)),
        )
        await connection.commit()
        return {"student_uuid": str(student_uuid), "status": "ACTIVE"}

    @app.post("/api/v1/students/{student_uuid}/deactivate")
    async def deactivate_student(
        student_uuid: uuid.UUID,
        actor: Annotated[str, Depends(require_admin)],
        connection: Annotated[aiosqlite.Connection, Depends(get_connection)],
    ):
        now = _utc_text(datetime.now(UTC))
        await connection.execute("BEGIN IMMEDIATE")
        async with connection.execute("SELECT id, status FROM students WHERE student_uuid=?", (str(student_uuid),)) as cursor:
            row = await cursor.fetchone()
        if row is None:
            await connection.rollback()
            raise HTTPException(404, {"code": "not_found", "message": "Student was not found"})
        if row["status"] == "INACTIVE":
            await connection.rollback()
            raise HTTPException(409, {"code": "invalid_state", "message": "Student is already inactive"})
        await connection.execute("UPDATE students SET status='INACTIVE', updated_at_utc=? WHERE id=?", (now, row["id"]))
        await connection.execute(
            "INSERT INTO admin_audit_log (occurred_at_utc, actor, action, target_type, target_id) VALUES (?, ?, 'STUDENT_DEACTIVATED', 'student', ?)",
            (now, actor, str(student_uuid)),
        )
        await connection.commit()
        return {"student_uuid": str(student_uuid), "status": "INACTIVE", "template_cleanup_required": row["status"] == "ACTIVE"}

    @app.post("/api/v1/attendance", response_model=AttendanceResult)
    async def ingest_attendance(
        body: AttendanceCreate,
        device: Annotated[dict[str, object], Depends(require_device)],
        settings: Annotated[Settings, Depends(get_settings)],
        connection: Annotated[aiosqlite.Connection, Depends(get_connection)],
    ):
        captured = body.captured_at.astimezone(UTC)
        now = datetime.now(UTC)
        if body.sync_status == "LIVE" and abs((now - captured).total_seconds()) > settings.max_clock_skew_seconds:
            raise HTTPException(422, {"code": "clock_skew", "message": "Live event timestamp is outside the allowed clock-skew window"})
        if captured - now > timedelta(seconds=settings.max_clock_skew_seconds):
            raise HTTPException(422, {"code": "future_timestamp", "message": "Event timestamp is too far in the future"})
        captured_text, received_text = _utc_text(captured), _utc_text(now)
        event_uuid = str(body.event_uuid)
        try:
            await connection.execute("BEGIN IMMEDIATE")
            async with connection.execute(
                "SELECT event_uuid, device_id, outcome, captured_at_utc FROM attendance_events WHERE event_uuid=?",
                (event_uuid,),
            ) as cursor:
                prior = await cursor.fetchone()
            if prior is not None:
                if prior["device_id"] != device["id"]:
                    await connection.rollback()
                    raise HTTPException(409, {"code": "event_conflict", "message": "Event UUID is already owned by another device"})
                await connection.commit()
                return JSONResponse(status_code=200, content={
                    "event_uuid": prior["event_uuid"], "outcome": prior["outcome"],
                    "captured_at_utc": prior["captured_at_utc"],
                })
            capacity = device["sensor_capacity"]
            slot = body.fingerprint_slot_id
            if capacity is None or slot > int(capacity):
                await connection.rollback()
                raise HTTPException(409, {"code": "invalid_slot", "message": "Slot is outside the reported sensor capacity"})
            async with connection.execute(
                """SELECT s.id FROM students s JOIN devices d ON d.id=s.enrollment_device_id
                   WHERE d.id=? AND s.fingerprint_slot_id=? AND s.status='ACTIVE'""",
                (device["id"], slot),
            ) as cursor:
                student = await cursor.fetchone()
            if student is None:
                await connection.rollback()
                raise HTTPException(409, {"code": "unknown_slot", "message": "Slot has no active student assignment"})
            student_id = student["id"]
            async with connection.execute(
                "SELECT captured_at_utc FROM attendance_events WHERE student_id=? AND outcome='RECORDED'",
                (student_id,),
            ) as cursor:
                accepted_events = await cursor.fetchall()
            # SQLite's julianday() is floating-point and can misclassify the
            # exact 60-second boundary. Compare parsed UTC datetimes instead.
            duplicate = any(
                abs((captured - datetime.fromisoformat(row[0].replace("Z", "+00:00")).astimezone(UTC)).total_seconds()) <= 60
                for row in accepted_events
            )
            outcome = "DUPLICATE_SUPPRESSED" if duplicate else "RECORDED"
            await connection.execute(
                """INSERT INTO attendance_events
                   (event_uuid, student_id, device_id, fingerprint_slot_id, captured_at_utc,
                    received_at_utc, sync_status, outcome)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (event_uuid, student_id, device["id"], slot, captured_text, received_text, body.sync_status, outcome),
            )
            await connection.execute("UPDATE devices SET last_seen_at_utc=? WHERE id=?", (received_text, device["id"]))
            await connection.commit()
        except aiosqlite.IntegrityError as exc:
            await connection.rollback()
            raise HTTPException(409, {"code": "event_conflict", "message": "Attendance event conflicts with stored data"}) from exc
        return JSONResponse(
            status_code=200 if duplicate else 201,
            content={"event_uuid": event_uuid, "outcome": outcome, "captured_at_utc": captured_text},
        )

    return app


app = create_app()
