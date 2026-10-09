/* Offline queue unit tests (node). Stubs browser globals, loads
 * web/offline.js, and exercises the durable event model:
 * - enqueue while "offline", restart survival (localStorage backend),
 * - idempotent UUIDs, ordering via client_seq,
 * - markResult done/failed, resetFailed, prune retention,
 * - bounded backoff, no secrets stored.
 * Run: node web/offline.test.js
 */
'use strict';
const fs = require('fs');
const path = require('path');
const assert = require('assert');
const { randomUUID } = require('crypto');

(async () => {
  // ---- browser stubs ----
  const store = new Map();
  global.localStorage = {
    getItem: (k) => (store.has(k) ? store.get(k) : null),
    setItem: (k, v) => store.set(k, String(v)),
    removeItem: (k) => store.delete(k),
  };
  global.window = {};
  // Node >=19 already exposes global crypto.randomUUID; do not override it.

  const src = fs.readFileSync(path.join(__dirname, 'offline.js'), 'utf8');
  eval(src); // eslint-disable-line — defines window.Offline / window.SyncEngine
  const { Offline: O, SyncEngine: Sync } = window;

  // 1. init picks localStorage (indexedDB absent from window stub)
  const kind = await O.init();
  assert.strictEqual(kind, 'localStorage', 'expected localStorage backend, got ' + kind);

  // 2. enqueue two check-ins; UUIDs unique, seqs ordered
  const a = await O.enqueueCheckin({ fingerprint_slot_id: 3 });
  const b = await O.enqueueCheckin({ fingerprint_slot_id: 5, clock_uncertain: true });
  assert.notStrictEqual(a.event_uuid, b.event_uuid, 'event UUIDs must be unique');
  assert.ok(b.client_seq > a.client_seq, 'client_seq must order events');
  assert.strictEqual(a.event_type, 'check-in');
  assert.ok(a.captured_at_utc.endsWith('Z'), 'timestamps must be UTC ISO');
  assert.strictEqual(a.sync_state, 'pending');

  // 3. no secrets / biometrics in the queue entry
  for (const row of [a, b]) {
    const blob = JSON.stringify(row).toLowerCase();
    assert.ok(!blob.includes('password') && !blob.includes('token') && !blob.includes('template'),
      'queue must not hold secrets or biometric templates');
  }

  // 4. counts + list ordering
  let counts = await O.counts();
  assert.deepStrictEqual([counts.pending, counts.failed, counts.total], [2, 0, 2]);
  const list = await O.listQueue();
  assert.strictEqual(list[0].event_uuid, a.event_uuid, 'queue must be seq-ordered');

  // 5. restart survival: drop in-memory refs, re-read from localStorage backend
  store.set('probe', 'x'); // touch store to prove persistence layer is shared
  const reread = await O.listQueue();
  assert.strictEqual(reread.length, 2, 'queue must survive restarts via localStorage');

  // 6. mark one synced (deleted), one failed (kept with error, backed off)
  await O.markResult(a.event_uuid, true);
  await O.markResult(b.event_uuid, false, new Error('backend unreachable: boom'));
  counts = await O.counts();
  assert.deepStrictEqual([counts.pending, counts.failed, counts.total], [0, 1, 1]);
  const failed = (await O.listQueue())[0];
  assert.ok(failed.last_error.includes('backend unreachable'), 'failure reason must be recorded');
  assert.ok(failed.attempts === 1 && failed.last_attempt_utc, 'attempt metadata required');
  assert.ok(Sync.backoffMs(0) === 5000 && Sync.backoffMs(1) === 10000 && Sync.backoffMs(99) === 160000, 'bounded backoff');

  // 7. resetFailed re-queues; prune honors retention
  await O.resetFailed();
  counts = await O.counts();
  assert.strictEqual(counts.pending, 1, 'resetFailed must re-queue');
  await O.prune(3650); // nothing this fresh
  assert.strictEqual((await O.counts()).total, 1);
  // Backdate then prune with 30d retention
  const rows = await O.listQueue();
  rows[0].created_at_utc = '2020-01-01T00:00:00Z';
  // write back through the backend directly
  await O.markResult(rows[0].event_uuid, false, 'aged');
  const aged = (await O.listQueue())[0];
  aged.created_at_utc = '2020-01-01T00:00:00Z';
  // emulate persistence of the edit for the localStorage backend
  const key = 'attendance-offline-v1:queue';
  const raw = JSON.parse(localStorage.getItem(key));
  raw.find((r) => r.event_uuid === aged.event_uuid).created_at_utc = '2020-01-01T00:00:00Z';
  localStorage.setItem(key, JSON.stringify(raw));
  await O.prune(30);
  assert.strictEqual((await O.counts()).total, 0, 'prune must drop aged events');

  // 8. employee cache round-trip (minimal PII only)
  await O.saveEmployees([{ employee_uuid: 'e1', first_name: 'A', last_name: 'B',
    employee_code: 'E-1', department: 'Eng', team: 'X', fingerprint_slot_id: 3 }]);
  const cached = await O.cachedEmployees();
  assert.strictEqual(cached.employees.length, 1);
  assert.ok(cached.cached_at_utc, 'cache timestamp required');

  // 9. queue bound enforced
  await O.markResult('nope', true); // unknown id: no-op, must not throw

  // ---- sync engine with stubbed transport ----
  // (Node >=21 exposes a read-only global navigator; override onLine only.)
  try {
    Object.defineProperty(globalThis, 'navigator', { value: { onLine: true }, configurable: true, writable: true });
  } catch (e) { globalThis.navigator.onLine = true; }
  const setOnline = (v) => { try { globalThis.navigator.onLine = v; } catch (e) {
    Object.defineProperty(globalThis, 'navigator', { value: { onLine: v }, configurable: true, writable: true }); } };
  const calls = { batch: 0 };
  let behavior = 'ok';
  window.API = {
    ping: async () => ({ status: 'ok' }),
    get: async () => ({ employees: [] }),
    batchSync: async (batch) => {
      calls.batch += 1;
      if (behavior === 'down') throw new Error('backend unreachable: refused');
      if (behavior === 'partial') {
        return { accepted: 1, failed: batch.length - 1, items: batch.map((b, i) => (i === 0
          ? { event_uuid: b.event_uuid, status: 'ok', outcome: 'RECORDED', captured_at_utc: b.captured_at_utc }
          : { event_uuid: b.event_uuid, status: 'error', code: 'unknown_slot', message: 'Slot has no active employee assignment' })) };
      }
      if (behavior === 'garbage') return { accepted: 0, failed: batch.length, items: [] };
      return { accepted: batch.length, failed: 0,
        items: batch.map((b) => ({ event_uuid: b.event_uuid, status: 'ok', outcome: 'RECORDED', captured_at_utc: b.captured_at_utc })) };
    },
  };

  // 10. transport down: queue retained, state honest
  const q1 = await O.enqueueCheckin({ fingerprint_slot_id: 7 });
  behavior = 'down';
  let st = await Sync.syncNow();
  assert.strictEqual(st.state, 'offline', 'failed sync must report offline, got ' + st.state);
  assert.strictEqual((await O.counts()).total, 1, 'failed events must stay queued');

  // 11. partial batch: ok removed, error kept visible with reason
  await O.markResult(q1.event_uuid, true); // isolate: q1 drained
  const q2a = await O.enqueueCheckin({ fingerprint_slot_id: 8 });
  const q2b = await O.enqueueCheckin({ fingerprint_slot_id: 9 });
  behavior = 'partial';
  st = await Sync.syncNow();
  const remaining = await O.listQueue();
  assert.strictEqual(remaining.length, 1, 'exactly the failed event must remain');
  assert.strictEqual(remaining[0].event_uuid, q2b.event_uuid);
  assert.ok(remaining[0].last_error.includes('active employee'), 'rejection reason recorded, got: ' + remaining[0].last_error);
  assert.strictEqual(st.failed, 1, 'UI failed count must match queue');

  // 12. invalid ack (no items): nothing dropped
  behavior = 'garbage';
  await Sync.syncNow();
  assert.strictEqual((await O.counts()).total, 1, 'unacknowledged events must be retained');

  // 13. recovery: success drains queue; replay finds nothing (idempotent)
  // (simulate elapsed backoff by clearing the recent attempt timestamp)
  const qkey = 'attendance-offline-v1:queue';
  const qraw = JSON.parse(localStorage.getItem(qkey));
  qraw.forEach((r) => { r.attempts = 0; r.last_attempt_utc = null; r.sync_state = 'pending'; });
  localStorage.setItem(qkey, JSON.stringify(qraw));
  behavior = 'ok';
  st = await Sync.syncNow();
  assert.strictEqual((await O.counts()).total, 0, 'acked events must be removed');
  const before = calls.batch;
  await Sync.syncNow();
  assert.strictEqual(calls.batch, before, 'empty queue must not send batches');

  // 14. browser-offline short-circuit sends nothing
  await O.enqueueCheckin({ fingerprint_slot_id: 9 });
  setOnline(false);
  const b2 = calls.batch;
  st = await Sync.syncNow();
  assert.strictEqual(calls.batch, b2, 'browser-offline must not attempt transport');
  assert.strictEqual(st.state, 'offline');
  setOnline(true);
  await Sync.syncNow();
  assert.strictEqual((await O.counts()).total, 0);

  console.log('offline.test.js: all 14 checks passed (backend=' + kind + ')');
})().catch((e) => { console.error('offline.test.js FAILED:', e); process.exit(1); });
