"""SQLite connection setup and transactional schema migrations."""

from __future__ import annotations

import asyncio
import re
import sqlite3
from pathlib import Path

import aiosqlite


SCHEMA_VERSION = 1
MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "migrations"
_MIGRATION_NAME = re.compile(r"^(?P<version>[0-9]{3,})_[a-z0-9_]+\.sql$")


class DatabaseMigrationError(RuntimeError):
    """Raised when schema history cannot be safely migrated."""


def _migration_files(directory: Path) -> dict[int, Path]:
    migrations: dict[int, Path] = {}
    if not directory.is_dir():
        raise DatabaseMigrationError(f"Migration directory does not exist: {directory}")

    for path in directory.iterdir():
        match = _MIGRATION_NAME.match(path.name)
        if not match:
            continue
        version = int(match.group("version"))
        if version in migrations:
            raise DatabaseMigrationError(f"Duplicate migration version: {version}")
        migrations[version] = path

    expected = list(range(1, max(migrations, default=0) + 1))
    if sorted(migrations) != expected:
        raise DatabaseMigrationError("Migration versions must be contiguous starting at 001")
    return migrations


def _split_sql_statements(script: str) -> list[str]:
    """Split migration SQL without breaking trigger bodies or quoted semicolons."""
    statements: list[str] = []
    pending = ""
    for line in script.splitlines():
        pending += line + "\n"
        if sqlite3.complete_statement(pending):
            statement = pending.strip()
            if statement:
                statements.append(statement)
            pending = ""
    if pending.strip():
        raise DatabaseMigrationError("Migration contains an incomplete SQL statement")
    return statements


async def _apply_migrations(
    connection: aiosqlite.Connection,
    migrations_dir: Path,
) -> None:
    migrations = _migration_files(migrations_dir)
    cursor = await connection.execute("PRAGMA user_version")
    current_version = int((await cursor.fetchone())[0])
    await cursor.close()

    latest_version = max(migrations, default=0)
    if latest_version != SCHEMA_VERSION:
        raise DatabaseMigrationError(
            f"Migration files end at {latest_version}, but SCHEMA_VERSION is {SCHEMA_VERSION}"
        )
    if current_version > latest_version:
        raise DatabaseMigrationError(
            f"Database schema {current_version} is newer than supported schema {latest_version}"
        )

    for version in range(current_version + 1, latest_version + 1):
        try:
            # Re-read the schema version after acquiring the write lock so two
            # processes starting together cannot both apply the same migration.
            await connection.execute("BEGIN IMMEDIATE")
            cursor = await connection.execute("PRAGMA user_version")
            locked_version = int((await cursor.fetchone())[0])
            await cursor.close()

            if locked_version >= version:
                await connection.commit()
                continue
            if locked_version != version - 1:
                raise DatabaseMigrationError(
                    f"Cannot apply migration {version:03d} after schema {locked_version}"
                )

            sql = migrations[version].read_text(encoding="utf-8")
            for statement in _split_sql_statements(sql):
                await connection.execute(statement)
            await connection.execute(f"PRAGMA user_version = {version}")
            await connection.commit()
        except Exception as exc:
            try:
                await connection.rollback()
            except aiosqlite.Error:
                pass
            if isinstance(exc, DatabaseMigrationError):
                raise
            raise DatabaseMigrationError(
                f"Migration {version:03d} failed; transaction rolled back"
            ) from exc


async def _enable_wal(connection: aiosqlite.Connection) -> str:
    """Enable persistent WAL mode, retrying transient concurrent-open locks."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + 5
    delay = 0.01
    while True:
        try:
            cursor = await connection.execute("PRAGMA journal_mode = WAL")
            mode = str((await cursor.fetchone())[0]).lower()
            await cursor.close()
            return mode
        except sqlite3.OperationalError as exc:
            if not any(word in str(exc).lower() for word in ("locked", "busy")) or loop.time() >= deadline:
                raise
            await asyncio.sleep(delay)
            delay = min(delay * 2, 0.2)


async def connect_database(
    db_path: str | Path,
    *,
    migrations_dir: str | Path = MIGRATIONS_DIR,
) -> aiosqlite.Connection:
    """Open a configured connection and apply pending migrations.

    File-backed databases use WAL. Callers own and must close the returned
    connection. A failed setup closes the connection before raising.
    """
    path_text = str(db_path)
    if path_text != ":memory:":
        path = Path(path_text)
        path.parent.mkdir(parents=True, exist_ok=True)

    connection = await aiosqlite.connect(path_text, isolation_level=None)
    try:
        await connection.execute("PRAGMA foreign_keys = ON")
        await connection.execute("PRAGMA busy_timeout = 5000")
        await connection.execute("PRAGMA synchronous = FULL")

        if path_text != ":memory:":
            journal_mode = await _enable_wal(connection)
            if journal_mode != "wal":
                raise DatabaseMigrationError(
                    f"SQLite refused WAL mode for file database (got {journal_mode})"
                )

        await _apply_migrations(connection, Path(migrations_dir))
        return connection
    except Exception:
        await connection.close()
        raise


async def initialize_database(
    db_path: str | Path,
    *,
    migrations_dir: str | Path = MIGRATIONS_DIR,
) -> None:
    """Initialize or upgrade a database, then close the connection."""
    connection = await connect_database(db_path, migrations_dir=migrations_dir)
    await connection.close()
