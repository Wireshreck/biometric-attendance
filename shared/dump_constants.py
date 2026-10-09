"""Helper for web/protocol-mirrors.test.js: dump py mirror constants as JSON."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
import ble_protocol as P  # noqa: E402

print(json.dumps({
    "SERVICE": P.BLE_SERVICE_UUID,
    "CHARS": P.BLE_CHARS,
    "COMMANDS": P.COMMANDS,
    "CHAR_FOR_COMMAND": P.CHAR_FOR_COMMAND,
    "TIMEOUTS": P.TIMEOUTS_MS,
    "PINS": P.PINS,
    "DIAG_TESTS": P.DIAG_TESTS,
    "DIAG_RESULTS": P.DIAG_RESULTS,
    "ERROR_CODES": P.ERROR_CODES,
    "STATUS": list(getattr(P, "STATUS_VALUES", None) or getattr(P, "STATUS", [])),
}))
