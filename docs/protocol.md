# BLE Device-Management Protocol

**Status:** defined for implementation
**Transport:** BLE GATT, characteristics defined in `firmware/include/config.h`
**Message format:** UTF-8 JSON text exchanged on the documented characteristics

This protocol is the single documented contract between the ESP32 device and every client:
- web management UI
- mobile app
- Windows desktop app
- `test.exe`
- firmware

Do not invent alternate command names, response shapes, or status codes in a client.

## General rules

- Every request and response is UTF-8 JSON.
- The device echoes command-specific responses on the matching characteristic.
- Diagnostic and status indications may also be pushed from the device to connected clients.
- Unknown commands are never silently treated as success.
- Commands that cannot be completed honestly report an error with a documented code rather than pretending the action succeeded.
- Hardware results are reported only after the device actually attempted the operation; a client may not assume a device is alive or healthy just because it is connected.

## BLE service and characteristics

Service UUID: `89ea2240-04cc-4e36-9356-c71647be1c8d`

Characteristic UUIDs are 16-bit forms registered under the custom service
(firmware `BLE_CHAR_*_UUID`, `firmware/include/config.h`): `1101`–`1108`
(i.e. 0x1101–0x1108 on the Bluetooth base UUID). Clients address them in
numeric 16-bit form (Web Bluetooth integer, ble-plx/bleak base-UUID
expansion); all three client stacks resolve to the same GATT table.

Characteristics are defined in `firmware/include/config.h`:

- `BLE_CHAR_DEVICE_INFO_UUID` — device identification
- `BLE_CHAR_DEVICE_STATUS_UUID` — runtime status and health
- `BLE_CHAR_PING_UUID` — liveness check
- `BLE_CHAR_RTC_UUID` — real-time clock read/set
- `BLE_CHAR_FINGERPRINT_STATUS_UUID` — fingerprint subsystem status/count
- `BLE_CHAR_FINGERPRINT_CONTROL_UUID` — enrollment, search, delete operations
- `BLE_CHAR_DIAGNOSTIC_UUID` — test execution and results
- `BLE_CHAR_ATTENDANCE_UUID` — attendance records

## Message envelope

Request fields:

```json
{
  "cmd": "<command>",
  "...": "<command-specific fields>"
}
```

Response fields:

```json
{
  "status": "ok",
  "code": "<result code>",
  "message": "<human-readable note>",
  "data": { "...": "..." }
}
```

Error response fields:

```json
{
  "status": "error",
  "code": "<error code>",
  "message": "<explanation>"
}
```

`status` values:

- `"ok"` — command executed successfully
- `"error"` — command failed
- `"busy"` — device is busy
- `"unreachable"` — requested subsystem is unavailable
- `"not_supported"` — command or feature is not implemented or not available on this build

## Device commands

### DEVICE_INFO

Request:

```json
{ "cmd": "DEVICE_INFO" }
```

Response data:

```json
{
  "device": "biometric-attendance-esp32",
  "firmware": "<version>",
  "hardware": "ESP32-WROOM-32",
  "uptime_seconds": 12345,
  "ble_service": "89ea2240-04cc-4e36-9356-c71647be1c8d"
}
```

`uptime_seconds` is the device uptime since boot.

### DEVICE_STATUS

Request:

```json
{ "cmd": "DEVICE_STATUS" }
```

Response data:

```json
{
  "rtc_ok": true,
  "rtc_lost_power": false,
  "rtc_valid": true,
  "rtc_time": "2026-10-07T21:57:00+05:30",
  "sensor_ready": false,
  "sensor_connected": false,
  "template_count": 0,
  "template_capacity": 1000,
  "storage_ok": true,
  "storage_used_bytes": 0,
  "buzzer_pin": 27,
  "i2c_bus": "GPIO25/GPIO26",
  "r307s_uart": "GPIO32/GPIO33 @ 57600 8N1"
}
```

If the DS3231 is not present or invalid, the RTC fields must honestly reflect that instead of inventing a time.

### PING

Request:

```json
{ "cmd": "PING" }
```

Response:

```json
{ "status": "ok", "code": "pong" }
```

## RTC commands

### RTC_GET

Request:

```json
{ "cmd": "RTC_GET" }
```

Response data:

```json
{
  "time": "2026-10-07T21:57:00+05:30",
  "valid": true,
  "lost_power": false
}
```

If the RTC is invalid or missing, `valid` must be `false`.

### RTC_SET

Request:

```json
{
  "cmd": "RTC_SET",
  "year": 2026,
  "month": 10,
  "day": 7,
  "hour": 21,
  "minute": 57,
  "second": 0
}
```

Response:

```json
{ "status": "ok", "code": "rtc_set" }
```

The device must reject impossible dates/times instead of accepting them blindly.

## Fingerprint commands

### FINGERPRINT_STATUS

Request:

```json
{ "cmd": "FINGERPRINT_STATUS" }
```

Response data:

```json
{
  "ready": false,
  "connected": false,
  "capacity": 1000,
  "used": 0,
  "note": "sensor did not respond"
}
```

If the sensor is unavailable, the response must say so; it must not report a successful sensor connection that was never confirmed.

### FINGERPRINT_COUNT

Request:

```json
{ "cmd": "FINGERPRINT_COUNT" }
```

Response data:

```json
{ "capacity": 1000, "used": 0 }
```

### FINGERPRINT_ENROLL

Request:

```json
{
  "cmd": "FINGERPRINT_ENROLL",
  "slot": 1
}
```

The device controls the enrollment workflow and reports the current enrollment state on the fingerprint control channel when needed.

Possible device-initiated enrollment states:

- `ENROLL_PLACE_FINGER`
- `ENROLL_REMOVE_FINGER`
- `ENROLL_PLACE_FINGER_AGAIN`
- `ENROLL_SUCCESS`
- `ENROLL_FAILED`

Final response:

```json
{ "status": "ok", "code": "enroll_success", "slot": 1 }
```

Failure response examples:

```json
{ "status": "error", "code": "NO_FINGER", "message": "No finger detected within timeout" }
```

```json
{ "status": "error", "code": "IMAGE_MISMATCH", "message": "Second impression did not match first" }
```

```json
{ "status": "error", "code": "DUPLICATE", "message": "Fingerprint already enrolled" }
```

```json
{ "status": "error", "code": "SENSOR_UNAVAILABLE", "message": "Fingerprint sensor not connected" }
```

```json
{ "status": "error", "code": "INVALID_ID", "message": "Invalid enrollment slot" }
```

```json
{ "status": "error", "code": "STORAGE_FULL", "message": "Fingerprint database is full" }
```

Enrollment must never fake a successful capture or a successful enrollment.

### FINGERPRINT_SEARCH

Request:

```json
{ "cmd": "FINGERPRINT_SEARCH" }
```

The device may report intermediate states such as waiting for a finger. Final response:

Match:

```json
{
  "status": "ok",
  "code": "match",
  "slot": 3,
  "confidence": 85
}
```

No match:

```json
{ "status": "ok", "code": "no_match" }
```

Failures:

```json
{ "status": "error", "code": "NO_FINGER", "message": "No finger detected" }
```

```json
{ "status": "error", "code": "SENSOR_UNAVAILABLE", "message": "Fingerprint sensor not connected" }
```

### FINGERPRINT_DELETE

Request:

```json
{
  "cmd": "FINGERPRINT_DELETE",
  "slot": 1
}
```

Response:

```json
{ "status": "ok", "code": "deleted", "slot": 1 }
```

### FINGERPRINT_DELETE_ALL

Request:

```json
{ "cmd": "FINGERPRINT_DELETE_ALL" }
```

Response:

```json
{ "status": "ok", "code": "deleted_all", "deleted": 5 }
```

Deleting an unknown slot or all templates when none exist must still be reported honestly.

## Buzzer

### BUZZER_TEST

Request:

```json
{ "cmd": "BUZZER_TEST" }
```

Response:

```json
{ "status": "ok", "code": "buzzer_test", "pin": 27 }
```

The buzzer pin is `27` in the current firmware configuration.

## Diagnostics

### FULL_DIAGNOSTIC

Request:

```json
{ "cmd": "FULL_DIAGNOSTIC" }
```

Response data:

```json
{
  "results": [
    { "test": "ESP32",       "result": "PASS" },
    { "test": "BLE",         "result": "PASS" },
    { "test": "R307S_UART",  "result": "FAIL", "reason": "No sensor response" },
    { "test": "R307S_SENSOR","result": "SKIPPED", "reason": "UART check failed" },
    { "test": "FINGERPRINT_DB","result": "SKIPPED" },
    { "test": "DS3231",      "result": "FAIL", "reason": "No I2C device at 0x68" },
    { "test": "RTC",         "result": "SKIPPED" },
    { "test": "BUZZER",      "result": "PASS" },
    { "test": "STORAGE",     "result": "PASS" },
    { "test": "ATTENDANCE",  "result": "PASS" }
  ]
}
```

Diagnostic result values:

- `PASS`
- `FAIL`
- `WARN`
- `SKIPPED`

A test may only be `PASS` when the device actually performed it and got a real result. `SKIPPED` is used when a prerequisite failed or the subsystem is not available. `FAIL` includes a reason when known.

## Attendance commands

### ATTENDANCE_STATUS

Request:

```json
{ "cmd": "ATTENDANCE_STATUS" }
```

Response data:

```json
{
  "records": 3,
  "storage_ok": true
}
```

### ATTENDANCE_READ

Request:

```json
{ "cmd": "ATTENDANCE_READ", "limit": 10, "offset": 0 }
```

`limit` (1–50, default 5) and `offset` keep each BLE response small
enough for reliable GATT reads; `total` reports the full record count.
If there are no records, the device returns an empty list rather than
inventing data.

Response data:

```json
{
  "records": [
    {
      "slot": 1,
      "captured_at": "2026-10-07T08:12:33+05:30",
      "status": "recorded"
    }
  ],
  "total": 1
}
```

If there are no records, the device returns an empty list rather than inventing data.

### ATTENDANCE_CLEAR

Request:

```json
{ "cmd": "ATTENDANCE_CLEAR" }
```

Response:

```json
{ "status": "ok", "code": "cleared", "records": 0 }
```

## Timeouts and status codes

Client timeouts: default 20 s; `FINGERPRINT_SEARCH` 30 s;
`FINGERPRINT_ENROLL` 300 s (up to 3 attempts per capture plus messaging).
Firmware timeouts: `BLE_TIMEOUT_DEFAULT_MS 20000`, `BLE_TIMEOUT_SEARCH_MS
30000`, `BLE_TIMEOUT_ENROLL_MS 300000` (`firmware/include/config.h`).

Write-then-read flow: the client writes the request JSON, waits ~400 ms,
then reads. The device stages each request and executes it on its main
loop, so the first reads may return
`{"status":"busy","code":"processing"}` — keep reading until `status`
is not `busy` (or the command timeout expires). A `busy` envelope is
never a result; disconnected/unreachable hardware is reported with the
documented error codes, never as success.

`status` values: `ok`, `error`, `busy`, `unreachable`, `not_supported`
(see Message envelope). Diagnostic `result` values: `PASS`, `FAIL`,
`WARN`, `SKIPPED` — PASS only when the device actually ran the test.

## Error codes summary
- `UNKNOWN`
- `SENSOR_UNAVAILABLE`
- `NO_FINGER`
- `BAD_IMAGE`
- `IMAGE_MISMATCH`
- `DUPLICATE`
- `INVALID_ID`
- `STORAGE_FULL`
- `TIMEOUT`
- `COMMUNICATION`
- `WRITE_FAILED`
- `RTC_INVALID`
- `RTC_LOST_POWER`
- `NOT_IMPLEMENTED`

## Enrollment workflow summary

Enrollment is a staged workflow, not a single magic request:

1. Client requests `FINGERPRINT_ENROLL` for a slot.
2. Device asks for the first finger placement.
3. Device captures the first impression.
4. Device asks the user to remove the finger.
5. Device asks for the same finger again.
6. Device combines the impressions and stores the template.
7. Device returns the final result.

If images are bad, the two impressions do not match, the sensor fails, or the slot is invalid/full/duplicate, the device reports the corresponding error instead of pretending enrollment succeeded.

## Demo flow in protocol terms

1. `PING`
2. `DEVICE_INFO`
3. `DEVICE_STATUS`
4. `RTC_GET`
5. `FINGERPRINT_COUNT`
6. `FINGERPRINT_ENROLL`
7. `FINGERPRINT_SEARCH`
8. `RTC_GET` (for the attendance timestamp)
9. `ATTENDANCE_READ`
10. `FULL_DIAGNOSTIC`
