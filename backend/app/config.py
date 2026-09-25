"""Environment-backed application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    database_path: Path
    app_timezone: str
    admin_username: str
    admin_password: str
    max_clock_skew_seconds: int = 300

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
        return cls(
            database_path=Path(os.getenv("DATABASE_PATH", "data/attendance.db")),
            app_timezone=os.getenv("APP_TIMEZONE", "Asia/Kolkata"),
            admin_username=os.getenv("ADMIN_USERNAME", ""),
            admin_password=os.getenv("ADMIN_PASSWORD", ""),
            max_clock_skew_seconds=int(os.getenv("MAX_CLOCK_SKEW_SECONDS", "300")),
        )

    def validate(self) -> None:
        if not self.admin_username or not self.admin_password:
            raise ValueError("ADMIN_USERNAME and ADMIN_PASSWORD must be configured")
        if len(self.admin_password) < 16:
            raise ValueError("ADMIN_PASSWORD must be at least 16 characters")
        if self.max_clock_skew_seconds < 0:
            raise ValueError("MAX_CLOCK_SKEW_SECONDS must not be negative")
        try:
            ZoneInfo(self.app_timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("APP_TIMEZONE must be a valid IANA timezone") from exc
