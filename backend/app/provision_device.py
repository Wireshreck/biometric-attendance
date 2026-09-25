"""One-time local provisioning: create a device record and print its token once."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import secrets
import uuid
from datetime import UTC, datetime

from app.config import Settings
from app.database import connect_database


async def provision(name: str, location: str, capacity: int) -> tuple[str, str]:
    settings = Settings.from_env()
    device_uuid = str(uuid.uuid4())
    token = secrets.token_urlsafe(32)
    created_at = datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")
    connection = await connect_database(settings.database_path)
    try:
        await connection.execute("BEGIN IMMEDIATE")
        await connection.execute(
            """INSERT INTO devices
               (device_uuid, device_name, location_name, token_hash, status, sensor_capacity, created_at_utc)
               VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?)""",
            (device_uuid, name, location, hashlib.sha256(token.encode()).hexdigest(), capacity, created_at),
        )
        await connection.execute(
            "INSERT INTO admin_audit_log (occurred_at_utc, actor, action, target_type, target_id) VALUES (?, 'local-cli', 'DEVICE_PROVISIONED', 'device', ?)",
            (created_at, device_uuid),
        )
        await connection.commit()
    except Exception:
        await connection.rollback()
        raise
    finally:
        await connection.close()
    return device_uuid, token


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Human-readable terminal name")
    parser.add_argument("--location", required=True, help="Terminal location label")
    parser.add_argument("--sensor-capacity", required=True, type=int, help="Capacity verified for the attached sensor")
    args = parser.parse_args()
    if args.sensor_capacity < 1:
        parser.error("--sensor-capacity must be positive and must be verified for this sensor")
    device_uuid, token = asyncio.run(provision(args.name, args.location, args.sensor_capacity))
    print("Device provisioned. Save the bearer token in ignored local firmware config now; it cannot be shown again.")
    print(f"DEVICE_UUID={device_uuid}")
    print(f"DEVICE_TOKEN={token}")


if __name__ == "__main__":
    main()
