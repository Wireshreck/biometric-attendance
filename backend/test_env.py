"""
Environment Validation Script for Backend Subsystem
Validates that Python 3.13, FastAPI, Uvicorn, Pydantic, aiosqlite, and SQLite3 are installed and functional.
"""

import sys
import sqlite3
import tempfile
from pathlib import Path
from contextlib import closing

def test_environment():
    print(f"Python Version: {sys.version}")
    assert sys.version_info >= (3, 11), "Python 3.11+ required"

    # Test SQLite
    print(f"SQLite Version: {sqlite3.sqlite_version}")
    with tempfile.TemporaryDirectory(prefix="biometric-attendance-env-") as temp_dir:
        db_path = Path(temp_dir) / "smoke.db"
        with closing(sqlite3.connect(db_path)) as conn:
            journal_mode = conn.execute("PRAGMA journal_mode = WAL;").fetchone()[0]
            assert journal_mode.lower() == "wal", f"Expected WAL mode, got {journal_mode}"
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT);")
            conn.execute("INSERT INTO test (name) VALUES ('bootstrap');")
            conn.commit()
            result = conn.execute("SELECT name FROM test WHERE id = 1;").fetchone()
            assert result and result[0] == "bootstrap", "SQLite basic operations failed"
            assert conn.execute("PRAGMA foreign_keys;").fetchone()[0] == 1
    print("[PASS] SQLite file database, WAL mode, foreign keys, and basic operations verified.")

    # Test Imports
    import fastapi
    print(f"[PASS] FastAPI version {fastapi.__version__} imported successfully.")

    import uvicorn
    print(f"[PASS] Uvicorn version {uvicorn.__version__} imported successfully.")

    import pydantic
    print(f"[PASS] Pydantic version {pydantic.__version__} imported successfully.")

    import aiosqlite
    print(f"[PASS] aiosqlite version {aiosqlite.__version__} imported successfully.")

    import httpx
    print(f"[PASS] HTTPX version {httpx.__version__} imported successfully.")

    import pytest
    print(f"[PASS] Pytest version {pytest.__version__} imported successfully.")

    print("\nALL BACKEND ENVIRONMENT DEPENDENCIES VERIFIED!")

if __name__ == "__main__":
    test_environment()
