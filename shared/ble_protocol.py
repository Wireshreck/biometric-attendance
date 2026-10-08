"""Shared BLE protocol constants. Mirrors firmware/include/ble_protocol.h,
docs/protocol.md, and shared/ble_protocol.js. Desktop, test.exe, and the
installer must import this module instead of redefining commands."""

BLE_SERVICE_UUID = "89ea2240-04cc-4e36-9356-c71647be1c8d"

BLE_CHARS = {
    "DEVICE_INFO": "1101",
    "DEVICE_STATUS": "1102",
    "PING": "1103",
    "RTC": "1104",
    "FINGERPRINT_STATUS": "1105",
    "FINGERPRINT_CONTROL": "1106",
    "DIAGNOSTIC": "1107",
    "ATTENDANCE": "1108",
}

COMMANDS = [
    "DEVICE_INFO", "DEVICE_STATUS", "PING",
    "RTC_GET", "RTC_SET",
    "FINGERPRINT_STATUS", "FINGERPRINT_COUNT", "FINGERPRINT_ENROLL",
    "FINGERPRINT_SEARCH", "FINGERPRINT_DELETE", "FINGERPRINT_DELETE_ALL",
    "BUZZER_TEST", "FULL_DIAGNOSTIC",
    "ATTENDANCE_STATUS", "ATTENDANCE_READ", "ATTENDANCE_CLEAR",
]

CHAR_FOR_COMMAND = {
    "DEVICE_INFO": "DEVICE_INFO",
    "DEVICE_STATUS": "DEVICE_STATUS",
    "PING": "PING",
    "RTC_GET": "RTC",
    "RTC_SET": "RTC",
    "FINGERPRINT_STATUS": "FINGERPRINT_STATUS",
    "FINGERPRINT_COUNT": "FINGERPRINT_STATUS",
    "FINGERPRINT_ENROLL": "FINGERPRINT_CONTROL",
    "FINGERPRINT_SEARCH": "FINGERPRINT_CONTROL",
    "FINGERPRINT_DELETE": "FINGERPRINT_CONTROL",
    "FINGERPRINT_DELETE_ALL": "FINGERPRINT_CONTROL",
    "BUZZER_TEST": "DIAGNOSTIC",
    "FULL_DIAGNOSTIC": "DIAGNOSTIC",
    "ATTENDANCE_STATUS": "ATTENDANCE",
    "ATTENDANCE_READ": "ATTENDANCE",
    "ATTENDANCE_CLEAR": "ATTENDANCE",
}

STATUS_VALUES = ["ok", "error", "busy", "unreachable", "not_supported"]

ERROR_CODES = [
    "UNKNOWN", "SENSOR_UNAVAILABLE", "NO_FINGER", "BAD_IMAGE",
    "IMAGE_MISMATCH", "DUPLICATE", "INVALID_ID", "STORAGE_FULL",
    "TIMEOUT", "COMMUNICATION", "WRITE_FAILED", "RTC_INVALID",
    "RTC_LOST_POWER", "NOT_IMPLEMENTED",
]

ENROLL_STATES = [
    "ENROLL_PLACE_FINGER", "ENROLL_REMOVE_FINGER",
    "ENROLL_PLACE_FINGER_AGAIN", "ENROLL_SUCCESS", "ENROLL_FAILED",
]

DIAG_TESTS = [
    "ESP32", "BLE", "R307S_UART", "R307S_SENSOR", "FINGERPRINT_DB",
    "DS3231", "RTC", "BUZZER", "STORAGE", "ATTENDANCE",
]

DIAG_RESULTS = ["PASS", "FAIL", "WARN", "SKIPPED"]

TIMEOUTS_MS = {"DEFAULT": 20000, "ENROLL": 120000, "SEARCH": 30000}

# Final hardware mapping (authoritative; matches firmware/include/config.h).
PINS = {
    "DS3231_SDA": 25,
    "DS3231_SCL": 26,
    "R307S_RX": 32,
    "R307S_TX": 33,
    "BUZZER": 27,
}

import json


def build_request(cmd, params=None):
    if cmd not in COMMANDS:
        raise ValueError(f"unknown command {cmd}")
    payload = {"cmd": cmd}
    if params:
        payload.update(params)
    return json.dumps(payload)


def parse_response(text):
    msg = json.loads(text)
    if "status" not in msg or not isinstance(msg["status"], str):
        raise ValueError("response missing status")
    return msg


def is_honest_diag_result(entry, connected):
    """PASS is honest only when the device actually ran the test."""
    if not isinstance(entry, dict):
        return False
    if entry.get("test") not in DIAG_TESTS:
        return False
    if entry.get("result") not in DIAG_RESULTS:
        return False
    if (not connected and entry.get("result") == "PASS"
            and entry.get("test") in ("R307S_UART", "R307S_SENSOR",
                                      "FINGERPRINT_DB", "DS3231", "RTC")):
        return False
    return True
