"""Validated HTTP request/response models.

Enterprise aliases: the durable storage columns remain
``roll_number`` / ``grade_class`` / ``section`` / ``student_uuid`` so BLE,
firmware, and existing integrations keep working. Every employee-facing
model ALSO accepts and returns ``employee_code`` / ``department`` /
``team`` / ``employee_uuid``. Clients should prefer the enterprise names;
the legacy names are kept for backward compatibility.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _enterprise_student_dict(row: dict) -> dict:
    """Return a student dict carrying both legacy and enterprise keys."""
    data = dict(row)
    # Drop alias Nones from request dumps so they cannot shadow real values.
    for alias in ("employee_uuid", "employee_code", "department", "team"):
        if data.get(alias) is None:
            data.pop(alias, None)
    # Legacy -> enterprise mirrors (single source of truth: legacy columns).
    data.setdefault("employee_uuid", data.get("student_uuid", ""))
    data.setdefault("employee_code", data.get("roll_number", ""))
    data.setdefault("department", data.get("grade_class", ""))
    data.setdefault("team", data.get("section", ""))
    # Enterprise -> legacy backfill (for dicts built from enterprise input).
    data.setdefault("student_uuid", data.get("employee_uuid", ""))
    data.setdefault("roll_number", data.get("employee_code", ""))
    data.setdefault("grade_class", data.get("department", ""))
    data.setdefault("section", data.get("team", ""))
    # Guarantee strings for response validation.
    for key in ("student_uuid", "roll_number", "grade_class", "section",
                "employee_uuid", "employee_code", "department", "team"):
        if data.get(key) is None:
            data[key] = ""
    return data


class StudentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    roll_number: str | None = Field(default=None, min_length=1, max_length=40)
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    grade_class: str | None = Field(default=None, min_length=1, max_length=40)
    section: str = Field(default="", max_length=40)
    # Enterprise aliases (preferred by new clients).
    employee_code: str | None = Field(default=None, min_length=1, max_length=40)
    department: str | None = Field(default=None, min_length=1, max_length=40)
    team: str | None = Field(default=None, max_length=40)

    @model_validator(mode="after")
    def resolve_aliases(self):
        roll = self.roll_number or self.employee_code
        cls = self.grade_class or self.department
        if not roll:
            raise ValueError("employee_code (or legacy roll_number) is required")
        if not cls:
            raise ValueError("department (or legacy grade_class) is required")
        object.__setattr__(self, "roll_number", roll)
        object.__setattr__(self, "grade_class", cls)
        if self.team not in (None, "") and not self.section:
            object.__setattr__(self, "section", self.team)
        return self


class StudentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    roll_number: str | None = Field(default=None, min_length=1, max_length=40)
    first_name: str | None = Field(default=None, min_length=1, max_length=80)
    last_name: str | None = Field(default=None, min_length=1, max_length=80)
    grade_class: str | None = Field(default=None, min_length=1, max_length=40)
    section: str | None = Field(default=None, max_length=40)
    employee_code: str | None = Field(default=None, min_length=1, max_length=40)
    department: str | None = Field(default=None, min_length=1, max_length=40)
    team: str | None = Field(default=None, max_length=40)

    def resolved(self) -> dict:
        updates: dict = {}
        if self.roll_number or self.employee_code:
            updates["roll_number"] = self.roll_number or self.employee_code
        if self.first_name is not None:
            updates["first_name"] = self.first_name
        if self.last_name is not None:
            updates["last_name"] = self.last_name
        if self.grade_class or self.department:
            updates["grade_class"] = self.grade_class or self.department
        if self.section is not None:
            updates["section"] = self.section
        elif self.team is not None:
            updates["team"] = self.team
            updates["section"] = self.team
        # Drop the alias-only key before SQL generation.
        updates.pop("team", None)
        return updates


class Student(BaseModel):
    student_uuid: str
    roll_number: str
    first_name: str
    last_name: str
    grade_class: str
    section: str = ""
    status: str
    fingerprint_slot_id: int | None
    # Enterprise mirrors (always populated by the API layer).
    employee_uuid: str = ""
    employee_code: str = ""
    department: str = ""
    team: str = ""

    @model_validator(mode="before")
    @classmethod
    def mirror_legacy(cls, data):
        if isinstance(data, dict):
            data = _enterprise_student_dict(data)
        return data


class AIChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    question: str = Field(min_length=1, max_length=500)


class AIChatResponse(BaseModel):
    tool: str
    answer: str
    ai_available: bool
    result: dict | None = None


class AIKeyUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    gemini_api_key: str = Field(default="", max_length=200)


class AssistedCheckin(BaseModel):
    """Admin-authenticated check-in for BLE-matched slots.

    ``event_uuid`` is optional for backward compatibility. Offline-capable
    clients MUST supply a stable UUID so retries and batch replays are
    idempotent instead of creating duplicates.
    """

    model_config = ConfigDict(extra="forbid")
    fingerprint_slot_id: int = Field(ge=1)
    event_uuid: UUID | None = None
    client_seq: int | None = Field(default=None, ge=0)
    clock_uncertain: bool = False



class StudentList(BaseModel):
    items: list[Student]
    limit: int
    offset: int


class AttendanceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_uuid: UUID
    fingerprint_slot_id: int = Field(ge=1)
    captured_at: datetime
    sync_status: Literal["LIVE", "REPLAYED_OFFLINE"]
    client_seq: int | None = Field(default=None, ge=0)
    clock_uncertain: bool = False

    @field_validator("captured_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("captured_at must include a timezone offset")
        return value


class AttendanceBatchItem(BaseModel):
    """One offline-queued event inside a batch sync request."""

    model_config = ConfigDict(extra="forbid")
    event_uuid: UUID
    fingerprint_slot_id: int = Field(ge=1)
    captured_at: datetime
    client_seq: int | None = Field(default=None, ge=0)
    clock_uncertain: bool = False

    @field_validator("captured_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("captured_at must include a timezone offset")
        return value


class AttendanceBatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    events: list[AttendanceBatchItem] = Field(min_length=1, max_length=100)


class AttendanceResult(BaseModel):
    event_uuid: UUID
    outcome: Literal["RECORDED", "DUPLICATE_SUPPRESSED"]
    captured_at_utc: str


class EnrollmentComplete(BaseModel):
    model_config = ConfigDict(extra="forbid")
    result: Literal["SUCCESS"]
    fingerprint_slot_id: int = Field(ge=1)
