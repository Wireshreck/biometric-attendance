# Offline-first operation (v1.5.0)

The system keeps recording attendance locally when the server, LAN, or
internet is unavailable, as long as the local app and hardware run.

## What works offline

- **Web console** (this is the primary offline client): an open tab keeps
  working when the backend stops or the network drops. Fingerprint matches
  from BLE (SCAN button, auto-scan) are queued in the browser and synced
  later. Dashboard, Attendance, and Employees render from the last cached
  directory plus the visible queue.
- **ESP32 firmware**: autonomous scanning → RTC timestamp → LittleFS record
  → Wi-Fi sync when configured (offline queue keyed by the same event UUID,
  so reconnects never duplicate). Unchanged in v1.5.0.
- **Mobile**: scan flows now send idempotent `event_uuid`s, so BLE
  match → check-in retries are safe. Full on-device queue is not yet
  implemented on mobile (see Limitations).

## Architecture (no new infrastructure)

```
BLE match ──► assisted-checkin (online) ──► SQLite (LIVE)
     │                     │
     │ offline             │ offline (web)
     ▼                     ▼
 LittleFS queue      IndexedDB `attendance-offline-v1`
 (firmware)          queue / employees / meta
                           │ reconnect
                           ▼
                 POST /api/v1/attendance/batch (≤100/batch)
                 per-event idempotency + 60s debounce
```

## Event model (queue entry / batch item)

| Field | Meaning |
|---|---|
| `event_uuid` | Client-generated UUIDv4. **Idempotency key** — replays return the stored outcome, never a duplicate row. |
| `fingerprint_slot_id` | Sensor slot matched over BLE. |
| `captured_at_utc` | **Source** timestamp. The server preserves it verbatim; sync time is stored separately as `received_at_utc` and never overwrites it. |
| `timezone` | Browser IANA zone at capture (provenance only; storage is UTC). |
| `client_seq` | Monotonic per-browser sequence for stable ordering. |
| `clock_uncertain` | 1 when the source clock may have drifted (offline browser clock). Reviewers can treat these as provisional. |
| `sync_state` | `pending` → `syncing` → (deleted on ack) or `failed` with `attempts`, `last_attempt_utc`, `last_error`. |
| `employee` snapshot | Name/code/department at capture for offline display. Minimal PII only. |

Raw fingerprint images/templates are **never** stored in events (sensor
slots only). Passwords and tokens are never stored in IndexedDB.

## Sync contract (`POST /api/v1/attendance/batch`, admin auth)

- Bounded: 1–100 events per request; the web client sends ≤20 per batch.
- Per-event results: `{"accepted", "failed", "items": [{event_uuid,
  status: ok|error, outcome?, code?, message?}]}`. HTTP 200 unless the whole
  request is malformed (422) or unauthorized (401).
- Individual commit per event: one unknown slot does not roll back the rest
  (partial-batch failure handling). Failures stay queued with reasons.
- Same 60 s debounce per employee as live ingest.
- Offline replays use `sync_status='REPLAYED_OFFLINE'`; future timestamps
  beyond `MAX_CLOCK_SKEW_SECONDS` are rejected as `future_timestamp`
  (clock-drift guard). Old timestamps are accepted — age alone never drops
  evidence.
- `POST /api/v1/assisted-checkin` accepts an optional client `event_uuid`
  with the same replay semantics for single-event flows.
- `GET /api/v1/sync/snapshot` returns server time + active employees +
  device for directory caching.

## Retry policy

- Automatic sync: on `online` events, tab refocus, every 30 s, and after
  every enqueue. Manual **Sync now** / **Retry failed** buttons included.
- Backoff per event: 5 s × 2^attempts, capped at ~2.7 min
  (`5000 * 2^min(attempts,5)`); the queue view shows pending/failed counts
  and last-sync time. Nothing is silently discarded or marked synced while
  records fail.
- `sync_retry_max` (company setting, default 8) caps *automatic* retries:
  exhausted failures stay queued and visible but wait for manual **Retry
  failed** (which resets the counter). No event is ever auto-deleted for
  retrying too often.
- Conflict rule: `event_uuid` owned by another device → `event_conflict`
  (409); evidence preserved, admin resolves. Debounce duplicates return
  `DUPLICATE_SUPPRESSED`, counted once in reports.

## Retention & recovery

- Browser queue capped at 2000 events. `retention_days` (company setting,
  default 30) is enforced by `prune()`, which drops **only** events that
  already failed, exhausted `sync_retry_max` automatic retries, **and** are
  older than the window. Pending or recently-failed events are never pruned —
  unsynchronized evidence is not silently destroyed. If the queue is full,
  the UI refuses new offline check-ins with an explicit error (fail loud,
  never silently drop).
- Queue survives restarts/power loss (IndexedDB; localStorage fallback;
  in-memory last resort — the banner shows which storage is active).
- Crash during write: IndexedDB transactions are atomic; a half-written
  event is either fully present (retried) or absent (recreated on next
  scan). Replays are idempotent either way.
- Device loss: queued PII is limited to name/code/department; clear site
  data or revoke credentials. Server remains authoritative — wipe and
  re-cache from `/api/v1/sync/snapshot`.
- SQLite backup unchanged: copy `backend/data/attendance.db*` while stopped.

## Limitations (honest)

- First visit requires the server (it serves the console). A service worker
  (`web/sw.js`) caches the app shell so an **already-visited** console
  renders while the backend is down; API data is never served stale.
- Mobile has idempotent retries but no full on-device queue yet.
- Browser-clock drift is flagged, not corrected — compare
  `captured_at_utc` vs `received_at_utc` for audit.
- No database encryption at rest in this architecture; OS-level disk
  encryption is recommended (see `docs/privacy-security.md`).
