"""Gemini-powered attendance assistant, server-side only.

Architecture: user question -> local intent router -> one controlled,
parameterized database tool -> structured rows -> Gemini explains ->
UI renders text plus structured tables. Gemini never sees credentials,
never receives the API key client-side, and never executes SQL.

Without GEMINI_API_KEY configured, tool results are still returned with a
deterministic local summary and `ai_available: false`.
"""

from __future__ import annotations

import json
import re
import urllib.request
from datetime import UTC, date, datetime, timedelta

import aiosqlite

from app import stats

GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

MAX_QUESTION = 500


class AIUnavailable(RuntimeError):
    """Gemini is not configured or not reachable; local data still served."""


def _parse_date(text: str) -> date | None:
    text = text.strip().lower()
    today = datetime.now(UTC).date()
    if "today" in text:
        return today
    if "yesterday" in text:
        return today - timedelta(days=1)
    match = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if match:
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return None
    match = re.search(r"(\w+)\s+(\d{1,2})(?:st|nd|rd|th)?", text)
    if match:
        try:
            parsed = datetime.strptime(f"{match.group(1)} {match.group(2)} 2026", "%B %d %Y")
            return parsed.date()
        except ValueError:
            try:
                parsed = datetime.strptime(f"{match.group(1)} {match.group(2)}", "%b %d")
                return date(today.year, parsed.month, parsed.day)
            except ValueError:
                return None
    return None


async def run_tool(
    connection: aiosqlite.Connection, name: str, args: dict, tz: str
) -> dict:
    """Execute one controlled tool. Unknown tools and bad inputs are rejected."""
    today = datetime.now(UTC).date()
    if name == "get_today_attendance":
        day = _parse_date(args.get("date", "today")) or today
        rows, total = await stats.attendance_list(connection, day=day, limit=200, offset=0, tz=tz)
        return {"date": day.isoformat(), "total": total, "records": rows}
    if name == "get_attendance_by_date":
        day = _parse_date(args.get("date", ""))
        if day is None:
            raise ValueError("Provide a date like 2026-10-03 or 'yesterday'")
        rows, total = await stats.attendance_list(connection, day=day, limit=200, offset=0, tz=tz)
        return {"date": day.isoformat(), "total": total, "records": rows}
    if name == "get_attendance_by_date_range":
        start = _parse_date(args.get("from", ""))
        end = _parse_date(args.get("to", ""))
        if start is None or end is None or end < start or (end - start).days > 93:
            raise ValueError("Provide a valid range up to 93 days")
        rows, total = await stats.attendance_list(
            connection, date_from=start, date_to=end, limit=500, offset=0, tz=tz)
        return {"from": start.isoformat(), "to": end.isoformat(), "total": total, "records": rows}
    if name == "get_attendance_by_time_range":
        time_from = str(args.get("from", "00:00"))[:5]
        time_to = str(args.get("to", "23:59"))[:5]
        if not re.fullmatch(r"\d{2}:\d{2}", time_from) or not re.fullmatch(r"\d{2}:\d{2}", time_to):
            raise ValueError("Time range must be HH:MM")
        day = _parse_date(args.get("date", "today")) or today
        rows, total = await stats.attendance_list(
            connection, day=day, time_from=time_from, time_to=time_to,
            limit=500, offset=0, tz=tz)
        return {"date": day.isoformat(), "from": time_from, "to": time_to,
                "total": total, "records": rows}
    if name == "search_students":
        query = str(args.get("query", "")).strip()[:80]
        if not query:
            raise ValueError("Provide a search query")
        rows, total = await stats.attendance_list(connection, limit=0, offset=0, tz=tz)
        del rows, total
        like = f"%{query}%"
        async with connection.execute(
            "SELECT student_uuid, roll_number, first_name, last_name,"
            " grade_class, section, status, fingerprint_slot_id FROM students"
            " WHERE first_name LIKE ? OR last_name LIKE ? OR roll_number LIKE ?"
            " OR (first_name || ' ' || last_name) LIKE ? LIMIT 20",
            (like, like, like, like),
        ) as cursor:
            return {"query": query, "students": [dict(r) for r in await cursor.fetchall()]}
    if name == "get_student":
        ident = str(args.get("student", "")).strip()[:80]
        like = f"%{ident}%"
        async with connection.execute(
            "SELECT student_uuid FROM students WHERE student_uuid = ?"
            " OR roll_number = ? OR (first_name || ' ' || last_name) LIKE ? LIMIT 2",
            (ident, ident, like),
        ) as cursor:
            matches = [r[0] for r in await cursor.fetchall()]
        if len(matches) != 1:
            raise ValueError("Student not found or ambiguous; be more specific")
        summary = await stats.student_summary(connection, student_uuid=matches[0], tz=tz)
        return {"student": summary}
    if name == "get_student_attendance":
        out = await run_tool(connection, "get_student", args, tz)
        if out["student"] is None:
            raise ValueError("Student not found")
        return out
    if name == "get_class_attendance":
        grade_class = str(args.get("class", "")).strip()[:40]
        if not grade_class:
            raise ValueError("Provide a class like 10A")
        day = _parse_date(args.get("date", "today")) or today
        rows, total = await stats.attendance_list(
            connection, day=day, grade_class=grade_class, limit=200, offset=0, tz=tz)
        absent = [s for s in await stats.absent_students(connection, day=day, tz=tz)
                  if s["grade_class"] == grade_class]
        return {"class": grade_class, "date": day.isoformat(),
                "present": total, "absent": absent}
    if name == "get_absent_students":
        day = _parse_date(args.get("date", "today")) or today
        absent = await stats.absent_students(connection, day=day, tz=tz)
        return {"date": day.isoformat(), "count": len(absent), "absent": absent}
    if name == "get_attendance_statistics":
        day = _parse_date(args.get("date", "today")) or today
        return await stats.overview(connection, today=day, tz=tz)
    if name == "get_recent_attendance":
        rows, total = await stats.attendance_list(connection, limit=20, offset=0, tz=tz)
        return {"total": total, "records": rows}
    raise ValueError(f"Unknown tool: {name}")


TOOLS = (
    "get_today_attendance", "get_attendance_by_date",
    "get_attendance_by_date_range", "get_attendance_by_time_range",
    "search_students", "get_student", "get_student_attendance",
    "get_class_attendance", "get_absent_students",
    "get_attendance_statistics", "get_recent_attendance",
)


def route(question: str) -> tuple[str, dict]:
    """Rule-based intent router: deterministic, no model call needed."""
    text = question.strip().lower()
    if not text:
        raise ValueError("Ask an attendance question")
    if any(word in text for word in ("absent", "missing", "not here", "didn't come")):
        match = re.search(r"class\s+([0-9]+\s?[a-z]?)", text)
        if match:
            return "get_class_attendance", {"class": match.group(1).replace(" ", "").upper(), "date": text}
        return "get_absent_students", {"date": text}
    if "class" in text:
        match = re.search(r"class\s+([0-9]+\s?[a-z]?)", text)
        if match:
            return "get_class_attendance", {"class": match.group(1).replace(" ", "").upper(), "date": text}
    if any(word in text for word in ("below 75", "most absences", "defaulter", "low attendance", "%")):
        return "get_attendance_statistics", {"date": text}
    if any(word in text for word in ("earliest", "first", "latest", "last check")):
        return "get_recent_attendance", {}
    if any(word in text for word in ("report", "summar")):
        return "get_attendance_statistics", {"date": text}
    if re.search(r"\d{4}-\d{2}-\d{2}|yesterday|october|january|february|march|april|may|june|july|august|september|november|december", text):
        match = re.search(r"(\d{1,2}):(\d{2})", text)
        if match or "between" in text:
            return "get_attendance_by_time_range", {"date": text, "from": "00:00", "to": "23:59"}
        return "get_attendance_by_date", {"date": text}
    if any(word in text for word in ("today", "how many", "present", "attendance")):
        return "get_today_attendance", {"date": text}
    match = re.search(r"(?:student|who is|about)\s+([a-zA-Z0-9 .'-]+)", text)
    if match or "rahul" in text:
        candidate = match.group(1).strip() if match else text
        return "get_student", {"student": candidate[:80]}
    return "get_recent_attendance", {}


def local_summary(tool: str, result: dict) -> str:
    if tool in ("get_today_attendance", "get_attendance_by_date"):
        return f"{result['total']} check-in(s) on {result['date']}."
    if tool == "get_absent_students":
        return f"{result['count']} student(s) absent on {result['date']}."
    if tool == "get_class_attendance":
        return (f"Class {result['class']} on {result['date']}: "
                f"{result['present']} present, {len(result['absent'])} absent.")
    if tool == "get_attendance_statistics":
        r = result
        return (f"{r['date']}: {r['present_today']}/{r['total_students']} present "
                f"({r['attendance_percentage']}%).")
    if tool == "get_student":
        s = result["student"]
        if s is None:
            return "Student not found."
        return (f"{s['first_name']} {s['last_name']} ({s['roll_number']}): "
                f"{s['attendance_percentage']}% over {s['window_days']} days.")
    return "Here are the latest records."


def gemini_explain(api_key: str, question: str, tool: str, result: dict) -> str:
    """Single Gemini call. Raises AIUnavailable on any failure. Key stays here."""
    body = json.dumps({
        "contents": [{
            "parts": [{
                "text": (
                    "You are a school attendance assistant. Answer briefly in plain text, "
                    f"no invented numbers. Question: {question}\n"
                    f"Database result ({tool}): {json.dumps(result)[:4000]}"
                ),
            }],
        }],
        "generationConfig": {"maxOutputTokens": 300},
    }).encode()
    request = urllib.request.Request(
        GEMINI_URL,
        data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode())
    except Exception as exc:
        raise AIUnavailable(f"Gemini request failed: {type(exc).__name__}") from exc
    try:
        return payload["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise AIUnavailable("Gemini returned an unusable response") from exc


async def answer(
    connection: aiosqlite.Connection, question: str, api_key: str, tz: str
) -> dict:
    if len(question.strip()) > MAX_QUESTION:
        raise ValueError("Question is too long")
    tool, args = route(question)
    try:
        result = await run_tool(connection, tool, args, tz)
    except ValueError as exc:
        return {"tool": tool, "result": None, "answer": str(exc),
                "ai_available": False}
    if not api_key:
        return {"tool": tool, "result": result,
                "answer": local_summary(tool, result)
                + " (AI summary unavailable: GEMINI_API_KEY is not configured.)",
                "ai_available": False}
    try:
        text = await _run_blocking(gemini_explain, api_key, question, tool, result)
    except AIUnavailable as exc:
        return {"tool": tool, "result": result,
                "answer": local_summary(tool, result) + f" (AI unavailable: {exc})",
                "ai_available": False}
    return {"tool": tool, "result": result, "answer": text, "ai_available": True}


async def _run_blocking(func, *args):
    import asyncio as _asyncio
    return await _asyncio.get_running_loop().run_in_executor(None, func, *args)
