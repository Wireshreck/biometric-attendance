"""Small authentication dependencies for the isolated synthetic-data MVP."""

from __future__ import annotations

import hashlib
import hmac

import aiosqlite
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer

from app.config import Settings
from app.dependencies import get_connection, get_settings

basic_auth = HTTPBasic(auto_error=False)
bearer_auth = HTTPBearer(auto_error=False)


async def require_admin(
    credentials: HTTPBasicCredentials | None = Depends(basic_auth),
    settings: Settings = Depends(get_settings),
) -> str:
    valid_user = credentials and hmac.compare_digest(
        credentials.username.encode(), settings.admin_username.encode()
    )
    valid_password = credentials and hmac.compare_digest(
        credentials.password.encode(), settings.admin_password.encode()
    )
    if not valid_user or not valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "unauthorized", "message": "Valid admin credentials are required"},
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


async def require_device(
    credentials=Depends(bearer_auth),
    connection: aiosqlite.Connection = Depends(get_connection),
) -> dict[str, object]:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail={"code": "unauthorized", "message": "Device bearer token is required"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest()
    async with connection.execute(
        "SELECT id, device_uuid, sensor_capacity FROM devices "
        "WHERE token_hash = ? AND status = 'ACTIVE'",
        (token_hash,),
    ) as cursor:
        row = await cursor.fetchone()
    if row is None:
        raise HTTPException(
            status_code=401,
            detail={"code": "unauthorized", "message": "Device credential is invalid or revoked"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"id": row[0], "device_uuid": row[1], "sensor_capacity": row[2]}
