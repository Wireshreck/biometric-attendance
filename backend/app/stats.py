"""Read-only attendance/student analytics. SQLite is the source of truth.

Every helper uses parameterized queries with validation done by callers.
Shared by the HTTP API and the AI tool layer so both report identical numbers.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import aiosqlite

DAY_START = "T00:00:00"
VALID_SORTS = {"captured_at_utc", "student", "class"}


def local_day_bounds(day: date, tz: str) -> tuple[str, str]:
    """UTC ISO bounds for a calendar day in the app timezone."""
    zone = ZoneInfo(tz)
    start = datetime(day.year, day.month, day.day, tzinfo=zone).astimezone(UTC)
    return (
        start.isoformat(timespec="microseconds").replace("+00:00", "Z"),
        (start + timedelta(days=1)).isoformat(timespec="microseconds").replace("+00:00", "Z"),
    )


def utc_day_of(ts: datetime, tz: str) -> date:
    return ts.astimezone(ZoneInfo(tz)).date()


async def attendance_list(
    connection: aiosqlite.Connection,
    *,
    day: date | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    time_from: str | None = None,
    time_to: str | None = None,
    student_query: str | None = None,
    grade_class: str | None = None,
    department: str | None = None,
    section: str | None = None,
    team: str | None = None,
    fingerprint_slot_id: int | None = None,
    outcome: str | None = None,
    sort: str = "captured_at_utc",
    order: str = "desc",
    limit: int = 50,
    offset: int = 0,
    tz: str = "Asia/Kolkata",
) -> tuple[list[dict], int]:
    clauses = ["e.outcome = 'RECORDED'"]
    params: list[object] = []
    resolved_class = grade_class if grade_class is not None else department
    resolved_section = section if section is not None else team
    if day is not None:
        start, end = local_day_bounds(day, tz)
        clauses.append("e.captured_at_utc >= ? AND e.captured_at_utc < ?")
        params.extend([start, end])
    if date_from is not None:
        start, _ = local_day_bounds(date_from, tz)
        clauses.append("e.captured_at_utc >= ?")
        params.append(start)
    if date_to is not None:
        _, end = local_day_bounds(date_to, tz)
        clauses.append("e.captured_at_utc < ?")
        params.append(end)
    if student_query:
        like = f"%{student_query.strip()}%"
        clauses.append(
            "(s.first_name LIKE ? OR s.last_name LIKE ? OR s.roll_number LIKE ?"
            " OR (s.first_name || ' ' || s.last_name) LIKE ?)"
        )
        params.extend([like, like, like, like])
    if resolved_class:
        clauses.append("s.grade_class = ?")
        params.append(resolved_class)
    if resolved_section:
        clauses.append("s.section = ?")
        params.append(resolved_section)
    if time_from:
        clauses.append("substr(e.captured_at_utc, 12, 5) >= ?")
        params.append(time_from)
    if time_to:
        clauses.append("substr(e.captured_at_utc, 12, 5) <= ?")
        params.append(time_to)
    if fingerprint_slot_id is not None:
        clauses.append("e.fingerprint_slot_id = ?")
        params.append(fingerprint_slot_id)
    if outcome:
        clauses = [c for c in clauses if not c.startswith("e.outcome")]
        clauses.append("e.outcome = ?")
        params.append(outcome)
    where = " AND ".join(clauses)
    order_col = {
        "captured_at_utc": "e.captured_at_utc",
        "student": "s.last_name, s.first_name",
        "class": "s.grade_class, s.section, e.captured_at_utc",
    }[sort]
    direction = "DESC" if order == "desc" else "ASC"
    base = (
        "FROM attendance_events e LEFT JOIN students s ON s.id = e.student_id "
        f"WHERE {where}"
    )
    async with connection.execute(f"SELECT COUNT(*) {base}", params) as cursor:
        total = int((await cursor.fetchone())[0])
    query = (
        "SELECT e.event_uuid, e.captured_at_utc, e.fingerprint_slot_id, e.outcome,"
        " s.student_uuid, s.roll_number, s.first_name, s.last_name, s.grade_class, s.section "
        f"{base} ORDER BY {order_col} {direction} LIMIT ? OFFSET ?"
    )
    async with connection.execute(query, (*params, limit, offset)) as cursor:
        rows = [dict(r) for r in await cursor.fetchall()]
    # Enterprise mirrors: keep legacy keys AND expose department/team and
    # employee_code/employee_uuid so new clients never need school terms.
    for row in rows:
        row["employee_uuid"] = row.get("student_uuid")
        row["employee_code"] = row.get("roll_number")
        row["department"] = row.get("grade_class")
        row["team"] = row.get("section", "")
        row["employee_name"] = f"{row.get('first_name') or ''} {row.get('last_name') or ''}".strip()
    return rows, total


async def overview(
    connection: aiosqlite.Connection, *, today: date, tz: str
) -> dict:
    start, end = local_day_bounds(today, tz)
    async with connection.execute(
        "SELECT COUNT(*) FROM students WHERE status = 'ACTIVE'"
    ) as cursor:
        total_active = int((await cursor.fetchone())[0])
    async with connection.execute(
        """SELECT COUNT(DISTINCT e.student_id)
           FROM attendance_events e JOIN students s ON s.id = e.student_id
           WHERE e.outcome = 'RECORDED' AND s.status = 'ACTIVE'
             AND e.captured_at_utc >= ? AND e.captured_at_utc < ?""",
        (start, end),
    ) as cursor:
        present = int((await cursor.fetchone())[0])
    async with connection.execute(
        """SELECT e.captured_at_utc FROM attendance_events e
           WHERE e.outcome = 'RECORDED'
             AND e.captured_at_utc >= ? AND e.captured_at_utc < ?
           ORDER BY e.captured_at_utc""",
        (start, end),
    ) as cursor:
        times = [r[0] for r in await cursor.fetchall()]
    pct = round(100.0 * present / total_active, 1) if total_active else 0.0
    return {
        "date": today.isoformat(),
        "total_students": total_active,
        "total_employees": total_active,
        "present_today": present,
        "absent_today": max(total_active - present, 0),
        "attendance_percentage": pct,
        "checkins_today": len(times),
        "first_checkin": times[0] if times else None,
        "last_checkin": times[-1] if times else None,
    }


async def daily_trend(
    connection: aiosqlite.Connection, *, days: int, today: date, tz: str
) -> list[dict]:
    out = []
    for back in range(days - 1, -1, -1):
        day = today - timedelta(days=back)
        start, end = local_day_bounds(day, tz)
        async with connection.execute(
            """SELECT COUNT(DISTINCT e.student_id) FROM attendance_events e
               WHERE e.outcome = 'RECORDED'
                 AND e.captured_at_utc >= ? AND e.captured_at_utc < ?""",
            (start, end),
        ) as cursor:
            present = int((await cursor.fetchone())[0])
        out.append({"date": day.isoformat(), "present": present})
    return out


async def class_comparison(
    connection: aiosqlite.Connection, *, day: date, tz: str
) -> list[dict]:
    start, end = local_day_bounds(day, tz)
    async with connection.execute(
        """SELECT s.grade_class, s.section, COUNT(*) AS total,
                  SUM(CASE WHEN s.status = 'ACTIVE' THEN 1 ELSE 0 END) AS active
           FROM students s GROUP BY s.grade_class, s.section"""
    ) as cursor:
        classes = [dict(r) for r in await cursor.fetchall()]
    async with connection.execute(
        """SELECT s.grade_class, s.section, COUNT(DISTINCT e.student_id) AS present
           FROM attendance_events e JOIN students s ON s.id = e.student_id
           WHERE e.outcome = 'RECORDED'
             AND e.captured_at_utc >= ? AND e.captured_at_utc < ?
           GROUP BY s.grade_class, s.section""",
        (start, end),
    ) as cursor:
        present_map = {(r[0], r[1]): r[2] for r in await cursor.fetchall()}
    result = []
    for row in classes:
        key = (row["grade_class"], row["section"])
        present = present_map.get(key, 0)
        active = row["active"] or 0
        result.append({
            "class": row["grade_class"], "section": row["section"],
            "department": row["grade_class"], "team": row["section"],
            "total": row["total"], "active": active, "present": present,
            "percentage": round(100.0 * present / active, 1) if active else 0.0,
        })
    return result


async def busy_times(
    connection: aiosqlite.Connection, *, day: date, tz: str
) -> list[dict]:
    start, end = local_day_bounds(day, tz)
    async with connection.execute(
        """SELECT substr(e.captured_at_utc, 12, 2) AS hour, COUNT(*)
           FROM attendance_events e
           WHERE e.outcome = 'RECORDED'
             AND e.captured_at_utc >= ? AND e.captured_at_utc < ?
           GROUP BY hour ORDER BY hour""",
        (start, end),
    ) as cursor:
        return [{"hour": r[0], "checkins": r[1]} for r in await cursor.fetchall()]


async def student_summary(
    connection: aiosqlite.Connection, *, student_uuid: str, days: int = 30,
    today: date | None = None, tz: str = "Asia/Kolkata",
) -> dict | None:
    async with connection.execute(
        "SELECT id, student_uuid, roll_number, first_name, last_name,"
        " grade_class, section, status, fingerprint_slot_id,"
        " created_at_utc, updated_at_utc FROM students WHERE student_uuid = ?",
        (student_uuid,),
    ) as cursor:
        row = await cursor.fetchone()
    if row is None:
        return None
    student = dict(row)
    ref = today or utc_day_of(datetime.now(UTC), tz)
    start, _ = local_day_bounds(ref - timedelta(days=days - 1), tz)
    async with connection.execute(
        """SELECT captured_at_utc FROM attendance_events
           WHERE student_id = ? AND outcome = 'RECORDED' AND captured_at_utc >= ?
           ORDER BY captured_at_utc""",
        (student["id"], start),
    ) as cursor:
        times = [r[0] for r in await cursor.fetchall()]
    pct = round(100.0 * len({t[:10] for t in times}) / days, 1)
    return {
        **student,
        "employee_uuid": student.get("student_uuid"),
        "employee_code": student.get("roll_number"),
        "department": student.get("grade_class"),
        "team": student.get("section", ""),
        "days_present": len({t[:10] for t in times}),
        "window_days": days, "attendance_percentage": pct,
        "recent": times[-10:], "first": times[0] if times else None,
        "last": times[-1] if times else None,
    }


async def absent_students(
    connection: aiosqlite.Connection, *, day: date, tz: str
) -> list[dict]:
    start, end = local_day_bounds(day, tz)
    async with connection.execute(
        """SELECT s.student_uuid, s.roll_number, s.first_name, s.last_name,
                  s.grade_class, s.section
           FROM students s
           WHERE s.status = 'ACTIVE' AND NOT EXISTS (
               SELECT 1 FROM attendance_events e
               WHERE e.student_id = s.id AND e.outcome = 'RECORDED'
                 AND e.captured_at_utc >= ? AND e.captured_at_utc < ?
           )
           ORDER BY s.grade_class, s.section, s.last_name, s.first_name""",
        (start, end),
    ) as cursor:
        rows = [dict(r) for r in await cursor.fetchall()]
    for row in rows:
        row["employee_uuid"] = row.get("student_uuid")
        row["employee_code"] = row.get("roll_number")
        row["department"] = row.get("grade_class")
        row["team"] = row.get("section", "")
    return rows
