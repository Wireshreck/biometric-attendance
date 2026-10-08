"""Validated HTTP request/response models."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StudentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    roll_number: str = Field(min_length=1, max_length=40)
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    grade_class: str = Field(min_length=1, max_length=40)
    section: str = Field(default="", max_length=40)


class StudentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    roll_number: str | None = Field(default=None, min_length=1, max_length=40)
    first_name: str | None = Field(default=None, min_length=1, max_length=80)
    last_name: str | None = Field(default=None, min_length=1, max_length=80)
    grade_class: str | None = Field(default=None, min_length=1, max_length=40)
    section: str | None = Field(default=None, max_length=40)


class Student(BaseModel):
    student_uuid: str
    roll_number: str
    first_name: str
    last_name: str
    grade_class: str
    section: str = ""
    status: str
    fingerprint_slot_id: int | None


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

    @field_validator("captured_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("captured_at must include a timezone offset")
        return value


class AttendanceResult(BaseModel):
    event_uuid: UUID
    outcome: Literal["RECORDED", "DUPLICATE_SUPPRESSED"]
    captured_at_utc: str


class EnrollmentComplete(BaseModel):
    model_config = ConfigDict(extra="forbid")
    result: Literal["SUCCESS"]
    fingerprint_slot_id: int = Field(ge=1)
