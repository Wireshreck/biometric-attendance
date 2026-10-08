"""Software-only protocol tests. No hardware required."""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
import ble_protocol as P

ROOT = os.path.join(os.path.dirname(__file__), "..")

EXPECTED_COMMANDS = [
    "DEVICE_INFO", "DEVICE_STATUS", "PING",
    "RTC_GET", "RTC_SET",
    "FINGERPRINT_STATUS", "FINGERPRINT_COUNT", "FINGERPRINT_ENROLL",
    "FINGERPRINT_SEARCH", "FINGERPRINT_DELETE", "FINGERPRINT_DELETE_ALL",
    "BUZZER_TEST", "FULL_DIAGNOSTIC",
    "ATTENDANCE_STATUS", "ATTENDANCE_READ", "ATTENDANCE_CLEAR",
]


def test_command_table_complete():
    assert sorted(P.COMMANDS) == sorted(EXPECTED_COMMANDS)
    for cmd in EXPECTED_COMMANDS:
        assert cmd in P.CHAR_FOR_COMMAND, cmd


def test_request_envelope():
    req = json.loads(P.build_request("FINGERPRINT_ENROLL", {"slot": 3}))
    assert req == {"cmd": "FINGERPRINT_ENROLL", "slot": 3}
    try:
        P.build_request("NOPE")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown command accepted")


def test_response_envelope():
    msg = P.parse_response('{"status":"ok","code":"pong"}')
    assert msg["status"] == "ok"
    try:
        P.parse_response('{"code":"x"}')
    except ValueError:
        pass
    else:
        raise AssertionError("status-less response accepted")


def test_codes_and_states():
    for code in ("SENSOR_UNAVAILABLE", "NO_FINGER", "DUPLICATE",
                 "STORAGE_FULL", "TIMEOUT", "RTC_LOST_POWER"):
        assert code in P.ERROR_CODES, code
    for state in ("ENROLL_PLACE_FINGER", "ENROLL_REMOVE_FINGER",
                  "ENROLL_PLACE_FINGER_AGAIN", "ENROLL_SUCCESS", "ENROLL_FAILED"):
        assert state in P.ENROLL_STATES, state
    assert len(P.DIAG_TESTS) == 10
    assert set(P.DIAG_RESULTS) == {"PASS", "FAIL", "WARN", "SKIPPED"}


def test_honesty_rule():
    assert P.is_honest_diag_result({"test": "R307S_UART", "result": "PASS"}, False) is False
    assert P.is_honest_diag_result({"test": "R307S_UART", "result": "FAIL"}, False) is True
    assert P.is_honest_diag_result({"test": "DS3231", "result": "PASS"}, False) is False
    assert P.is_honest_diag_result({"test": "BUZZER", "result": "PASS"}, False) is True
    assert P.is_honest_diag_result({"test": "NOPE", "result": "PASS"}, True) is False


def test_timeouts_and_pins():
    assert P.TIMEOUTS_MS["ENROLL"] == 120000
    assert P.TIMEOUTS_MS["SEARCH"] == 30000
    assert P.PINS == {"DS3231_SDA": 25, "DS3231_SCL": 26,
                      "R307S_RX": 32, "R307S_TX": 33, "BUZZER": 27}
    assert P.BLE_SERVICE_UUID == "89ea2240-04cc-4e36-9356-c71647be1c8d"
    assert len(P.BLE_CHARS) == 8


def _read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def test_firmware_header_mirrors_commands():
    header = _read("firmware/include/ble_protocol.h")
    for cmd in EXPECTED_COMMANDS:
        assert cmd in header, f"ble_protocol.h missing {cmd}"


def test_js_mirror_mirrors_commands():
    js = _read("shared/ble_protocol.js")
    for cmd in EXPECTED_COMMANDS:
        assert f"'{cmd}'" in js or f'"{cmd}"' in js, f"js mirror missing {cmd}"


def test_protocol_doc_lists_commands():
    doc = _read("docs/protocol.md")
    for cmd in EXPECTED_COMMANDS:
        assert cmd in doc, f"protocol.md missing {cmd}"
    assert "89ea2240-04cc-4e36-9356-c71647be1c8d" in doc


def test_firmware_pins_authoritative():
    config = _read("firmware/include/config.h")
    assert "PIN_I2C_SDA     25" in config
    assert "PIN_I2C_SCL     26" in config
    assert "PIN_BUZZER      27" in config
    assert "PIN_R307S_RX    32" in config
    assert "PIN_R307S_TX    33" in config
    assert "FIRMWARE_VERSION" in config
