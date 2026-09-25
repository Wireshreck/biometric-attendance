"""Request-scoped access to app configuration and database connections."""

from collections.abc import AsyncIterator

import aiosqlite
from fastapi import Request

from app.config import Settings


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


async def get_connection(request: Request) -> AsyncIterator[aiosqlite.Connection]:
    connection = await aiosqlite.connect(request.app.state.settings.database_path)
    connection.row_factory = aiosqlite.Row
    await connection.execute("PRAGMA foreign_keys = ON")
    await connection.execute("PRAGMA busy_timeout = 5000")
    try:
        yield connection
    finally:
        await connection.close()
