# MVP HTTP API Contract

**Status:** PLANNED — no API routes exist in the repository.
**Base path:** `/api/v1`; JSON over the isolated local demo network.  
**Frontend transport:** `fetch()` for commands/queries plus authenticated Server-Sent Events for live updates.  
**Canonical data model:** [database design](database-plan.md); [requirements](requirements-traceability.md).

## Authentication and common behavior

- `GET /health` returns process health and schema version only; it exposes no student/device details.
- Device routes require `Authorization: Bearer <device-token>`. Store only a strong token hash in `devices`; compare in constant time and reject revoked devices. Configure/provision tokens locally, never through committed examples.
- Administrative routes require HTTP Basic credentials sourced from local environment variables. This is only acceptable for synthetic demo data on a dedicated, WPA2-protected local network. HTTP does not encrypt these credentials; do not use real student data or deploy this prototype in a school. Production requires TLS, durable identity management, role separation, and security review.
- JSON errors use `{"error":{"code":"...","message":"..."}}`; never include SQL, secrets, stack traces, or biometric payloads. Dates use RFC3339 with an explicit offset; the server normalizes to UTC.
- Use Python `zoneinfo.ZoneInfo(APP_TIMEZONE)` with the pinned `tzdata` fallback on Windows. Default report zone is `Asia/Kolkata`; do not derive local date from server machine locale.
- List endpoints enforce `limit` 1–100 and non-negative `offset`; invalid fields return `422`. Missing resources return `404`, duplicate/invalid state transitions `409`, unauthenticated requests `401`, forbidden operations `403`, and unexpected failures `500` with a correlation ID only.

## Endpoints

| Method and path | Auth | Request | Response / side effect | Statuses |
| --- | --- | --- | --- | --- |
| `GET /health` | None | None | `{"status":"ok","schema_version":1}`; `503` if DB/migrations unavailable. No personal/device detail. | 200, 503 |
| `GET /api/v1/students` | Admin | Optional `grade_class`, `status`, `limit`, `offset` | `{"items":[student...],"limit":50,"offset":0}`; no token/template fields. | 200, 401, 422 |
| `POST /api/v1/students` | Admin | `{roll_number,first_name,last_name,grade_class}`; bounded strings, no extra fields | `201 {student_uuid,roll_number,first_name,last_name,grade_class,status:"PENDING_ENROLLMENT",fingerprint_slot_id}`; atomically reserves a slot on the sole active MVP device and audits creation. | 201, 401, 409 duplicate/no slot/no unique active device, 422 |
| `GET /api/v1/students/{student_uuid}` | Admin | UUID path | Student representation as above. | 200, 401, 404 |
| `POST /api/v1/students/{student_uuid}/deactivate` | Admin | No body | `200 {student_uuid,status:"INACTIVE",template_cleanup_required:true}`; blocks future event resolution and audits action. It does not claim sensor template erasure or free the slot. | 200, 401, 404, 409 |
| `DELETE /api/v1/students/{student_uuid}` | Admin | No body; allowed only after sensor cleanup and retention authorization | `204`; removes identity and nulls its attendance foreign keys in a transaction; audit action does not retain student name/roll. Never delete the DB row while the sensor template remains. | 204, 401, 404, 409 cleanup required |
| `GET /api/v1/devices` | Admin | Optional `status`, pagination | `{"items":[{device_uuid,device_name,location_name,status,sensor_capacity,last_seen_at_utc}]}`; no token hash. | 200, 401, 422 |
| `GET /api/v1/devices/{device_uuid}` | Admin | UUID path | One safe device status representation. | 200, 401, 404 |
| `GET /api/v1/devices/{device_uuid}/enrollment/{student_uuid}` | Device | Device token must match path UUID | `{student_uuid,fingerprint_slot_id,capacity}` only if student is pending and assignment belongs to device. No identity fields/template bytes. | 200, 401, 404, 409 wrong state/device |
| `POST /api/v1/devices/{device_uuid}/enrollment/{student_uuid}/complete` | Device | `{result:"SUCCESS",fingerprint_slot_id}`; device-reported slot must match assignment | `200 {student_uuid,status:"ACTIVE"}`; activate only after device confirms sensor write; audit transition. No image/template payload. | 200, 401, 404, 409 invalid transition/slot, 422 |
| `GET /api/v1/devices/{device_uuid}/cleanup` | Device | Device bearer token | List inactive students on this device with remaining slot assignment; no names. Operator starts clear from serial console. | 200, 401, 404 |
| `POST /api/v1/devices/{device_uuid}/cleanup/{student_uuid}/complete` | Device | `{result:"SUCCESS",fingerprint_slot_id}` | On verified sensor erase and matching inactive assignment, set student slot NULL and audit cleanup; slot becomes reusable only now. | 200, 401, 404, 409 invalid state/slot, 422 |
| `POST /api/v1/devices/{device_uuid}/heartbeat` | Device | `{firmware_version,uptime_s,sensor_ok,rtc_valid,wifi_rssi,sensor_capacity}`; bounded diagnostics only, no secrets | `200 {device_uuid,status:"ACTIVE",last_seen_at_utc}`; update safe status and capacity fields. Do not log request credentials. | 200, 401, 404, 422 |
| `POST /api/v1/attendance` | Device | `{event_uuid,fingerprint_slot_id,captured_at,sync_status}`; RFC3339 offset, slot within detected capacity | `201 {event_uuid,outcome:"RECORDED",captured_at_utc}`; `200 {event_uuid,outcome:"DUPLICATE_SUPPRESSED",captured_at_utc}`; repeated UUID returns saved response. | 201, 200, 401, 409 unknown/inactive slot, 422 |
| `GET /api/v1/attendance` | Admin | Required `from`,`to` local dates; optional `grade_class`,`limit`,`offset` | Paginated accepted (`RECORDED`) events only; no template data. | 200, 401, 422 range/limit |
| `GET /api/v1/events` | Admin | Optional `Last-Event-ID` header (integer row cursor) | `text/event-stream`; `id` is increasing DB row ID, `data` is minimal committed event (event UUID, outcome, timestamp); heartbeat comments. Reconnect resumes after cursor. | 200 stream, 401 before stream, reconnect on network error |
| `GET /api/v1/reports/daily` | Admin | Required `date=YYYY-MM-DD`; optional configured timezone/class | `{date,timezone,active_roster_count,present_count,absent_count,percentage}`; distinct students with a recorded event count once. | 200, 401, 422 |
| `GET /api/v1/reports/export.csv` | Admin | Required bounded `from`,`to`; optional class | RFC4180 attachment; quote/escape fields and neutralize spreadsheet formulas; audit export. | 200, 401, 422 range |

All JSON endpoints use common error envelope `{"error":{"code":"...","message":"...","correlation_id":"..."}}`. In addition to table statuses: malformed JSON/body size errors are 400/413; missing/invalid credentials 401; authenticated wrong role 403; missing resource 404; illegal state/unique conflict 409; field/range validation 422; unavailable dependency 503. No response includes SQL, tracebacks, secrets, or biometric payload.

## Attendance payload and duplicate rules

Example:

```json
{
  "event_uuid": "2c8f2071-16ae-43b3-83af-0fd68edb5788",
  "fingerprint_slot_id": 7,
  "captured_at": "2026-09-24T08:14:22+05:30",
  "sync_status": "REPLAYED_OFFLINE"
}
```

`event_uuid` is generated once at scan time and persisted with the offline queue; it remains unchanged on retries. Slot ID must be within the detected sensor capacity. `captured_at` must be timezone-qualified. For a replay, preserve capture time and set `REPLAYED_OFFLINE`; never replace it with server receipt time. Device authentication determines `device_uuid`, not a caller-supplied MAC address.

Within a serialized write transaction, return the saved outcome if `event_uuid` already exists. Otherwise resolve an active student's slot and compare the capture timestamp to accepted scans for that student; a scan within 60 seconds is stored as `DUPLICATE_SUPPRESSED`, otherwise as `RECORDED`. Distinct events after 60 seconds on the same date may be recorded. Report presence counts each student once per configured local date.

## Deliberately not in MVP

No public registration, parent portal, remote fingerprint image/template endpoint, arbitrary SQL, generic configuration mutation, AI endpoint, or browser-side database access. Settings use environment variables. Enrollment and cleanup start with physical serial access; the browser API does not remotely command the sensor. Initial device provisioning is a local CLI operation that prints a random token once and stores only its hash. No behavior is considered implemented until route code and contract tests exist.
