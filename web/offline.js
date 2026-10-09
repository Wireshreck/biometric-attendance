/* Offline-first store + sync engine for the Employee Attendance Console.
 *
 * Problem: the console is served by the backend itself, so "offline" almost
 * always means "this tab is already open and the server just became
 * unreachable" (backend stopped, LAN dropped, isolated network). The app
 * must keep recording attendance locally and sync later — not just show a
 * banner over a dead UI.
 *
 * Design (no new infrastructure):
 * - IndexedDB `attendance-offline-v1` holds:
 *     queue     — pending check-in events (survives restarts/power loss)
 *     employees — last-known active employee directory (for offline display
 *                 and name resolution)
 *     meta      — client sequence counter, last sync timestamps
 * - localStorage fallback when IndexedDB is unavailable (private mode).
 * - Each queued event carries a client-generated UUIDv4 so server replays
 *   are idempotent (POST /api/v1/attendance/batch + assisted-checkin).
 * - Source timestamps are preserved verbatim; sync time never overwrites
 *   captured_at_utc. Device-clock drift is flagged via clock_uncertain.
 * - No fingerprint templates, images, passwords, or tokens are stored here.
 */
(() => {
  'use strict';

  const DB_NAME = 'attendance-offline-v1';
  const RETENTION_DAYS_DEFAULT = 30;
  const MAX_QUEUE = 2000;

  const nowISO = () => new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
  const uuid4 = () => (crypto.randomUUID
    ? crypto.randomUUID()
    : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
    }));

  /* ---------- storage backends ---------- */
  function memoryBackend() {
    const tables = { queue: new Map(), employees: new Map(), meta: new Map() };
    return {
      kind: 'memory',
      async get(table, key) { return tables[table].get(key) || null; },
      async put(table, value, key) {
        const k = key || value.event_uuid || value.employee_uuid || value.student_uuid || value.key;
        tables[table].set(k, value);
      },
      async all(table) { return [...tables[table].values()]; },
      async del(table, key) { tables[table].delete(key); },
      async clear(table) { tables[table].clear(); },
    };
  }

  function localStorageBackend() {
    const read = (table) => {
      try { return JSON.parse(localStorage.getItem(DB_NAME + ':' + table) || '[]'); }
      catch (e) { return []; }
    };
    const write = (table, rows) => {
      try { localStorage.setItem(DB_NAME + ':' + table, JSON.stringify(rows)); } catch (e) {}
    };
    const keyOf = (v) => v.event_uuid || v.employee_uuid || v.student_uuid || v.key;
    return {
      kind: 'localStorage',
      async get(table, key) { return read(table).find((r) => keyOf(r) === key) || null; },
      async put(table, value, key) {
        const rows = read(table).filter((r) => keyOf(r) !== (key || keyOf(value)));
        rows.push(value);
        write(table, rows.slice(-MAX_QUEUE));
      },
      async all(table) { return read(table); },
      async del(table, key) { write(table, read(table).filter((r) => keyOf(r) !== key)); },
      async clear(table) { write(table, []); },
    };
  }

  function indexedDBBackend() {
    if (!('indexedDB' in window)) return null;
    let db = null;
    const open = () => new Promise((resolve, reject) => {
      try {
        const req = indexedDB.open(DB_NAME, 1);
        req.onupgradeneeded = () => {
          const d = req.result;
          if (!d.objectStoreNames.contains('queue')) d.createObjectStore('queue', { keyPath: 'event_uuid' });
          if (!d.objectStoreNames.contains('employees')) d.createObjectStore('employees', { keyPath: 'eid' });
          if (!d.objectStoreNames.contains('meta')) d.createObjectStore('meta', { keyPath: 'key' });
        };
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => reject(req.error);
      } catch (e) { reject(e); }
    });
    const tx = async (table, mode, fn) => {
      if (!db) db = await open();
      return new Promise((resolve, reject) => {
        const t = db.transaction(table, mode);
        const store = t.objectStore(table);
        const out = fn(store);
        t.oncomplete = () => resolve(out && out.result !== undefined ? out.result : out);
        t.onerror = () => reject(t.error);
      });
    };
    const reqToPromise = (req) => new Promise((resolve, reject) => {
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
    return {
      kind: 'indexedDB',
      async get(table, key) {
        if (!db) db = await open();
        return reqToPromise(db.transaction(table, 'readonly').objectStore(table).get(key));
      },
      async put(table, value) {
        if (!db) db = await open();
        return reqToPromise(db.transaction(table, 'readwrite').objectStore(table).put(value));
      },
      async all(table) {
        if (!db) db = await open();
        return reqToPromise(db.transaction(table, 'readonly').objectStore(table).getAll());
      },
      async del(table, key) {
        if (!db) db = await open();
        return reqToPromise(db.transaction(table, 'readwrite').objectStore(table).delete(key));
      },
      async clear(table) {
        if (!db) db = await open();
        return reqToPromise(db.transaction(table, 'readwrite').objectStore(table).clear());
      },
    };
  }

  /* ---------- store ---------- */
  const Store = {
    backend: memoryBackend(),
    ready: null,
    async init() {
      if (this.ready) return this.ready;
      this.ready = (async () => {
        const idb = indexedDBBackend();
        if (idb) {
          try { await idb.all('meta'); this.backend = idb; return idb.kind; }
          catch (e) { /* fall through to localStorage */ }
        }
        try {
          localStorage.setItem(DB_NAME + ':probe', '1');
          localStorage.removeItem(DB_NAME + ':probe');
          this.backend = localStorageBackend();
          return 'localStorage';
        } catch (e) { this.backend = memoryBackend(); return 'memory'; }
      })();
      return this.ready;
    },
    get kind() { return this.backend.kind; },
  };

  async function nextSeq() {
    await Store.init();
    const cur = (await Store.backend.get('meta', 'client_seq')) || { key: 'client_seq', value: 0 };
    cur.value = (cur.value || 0) + 1;
    await Store.backend.put('meta', cur);
    return cur.value;
  }

  function normalizeEmployee(e) {
    return {
      eid: e.employee_uuid || e.student_uuid,
      employee_uuid: e.employee_uuid || e.student_uuid,
      student_uuid: e.student_uuid || e.employee_uuid,
      name: e.employee_name || `${e.first_name || ''} ${e.last_name || ''}`.trim(),
      first_name: e.first_name || '', last_name: e.last_name || '',
      employee_code: e.employee_code || e.roll_number || '',
      roll_number: e.roll_number || e.employee_code || '',
      department: e.department || e.grade_class || '',
      grade_class: e.grade_class || e.department || '',
      team: e.team || e.section || '', section: e.section || e.team || '',
      fingerprint_slot_id: e.fingerprint_slot_id ?? null,
      cached_at_utc: nowISO(),
    };
  }

  const Offline = {
    RETENTION_DAYS_DEFAULT,

    async init() { return Store.init(); },
    get storageKind() { return Store.kind; },

    /* ----- queue ----- */
    async enqueueCheckin({ fingerprint_slot_id, captured_at_utc, employee, clock_uncertain }) {
      await Store.init();
      const existing = await Store.backend.all('queue');
      if (existing.length >= MAX_QUEUE) {
        throw new Error(`offline queue full (${MAX_QUEUE}); sync before recording more`);
      }
      const event = {
        event_uuid: uuid4(),
        event_type: 'check-in',
        fingerprint_slot_id,
        captured_at_utc: captured_at_utc || nowISO(),
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
        client_seq: await nextSeq(),
        clock_uncertain: clock_uncertain ? 1 : 0,
        employee: employee ? {
          name: employee.name || `${employee.first_name || ''} ${employee.last_name || ''}`.trim(),
          employee_code: employee.employee_code || employee.roll_number || '',
          department: employee.department || employee.grade_class || '',
        } : null,
        sync_state: 'pending',
        attempts: 0,
        created_at_utc: nowISO(),
        last_attempt_utc: null,
        last_error: null,
      };
      await Store.backend.put('queue', event);
      Sync.kick();
      return event;
    },

    async listQueue() {
      await Store.init();
      const rows = await Store.backend.all('queue');
      return rows.sort((a, b) => (a.client_seq || 0) - (b.client_seq || 0));
    },

    async counts() {
      const rows = await this.listQueue();
      const pending = rows.filter((r) => r.sync_state === 'pending').length;
      const failed = rows.filter((r) => r.sync_state === 'failed').length;
      const syncing = rows.filter((r) => r.sync_state === 'syncing').length;
      return { pending, failed, syncing, total: rows.length };
    },

    async markResult(event_uuid, ok, error) {
      await Store.init();
      if (ok) { await Store.backend.del('queue', event_uuid); return; }
      const row = await Store.backend.get('queue', event_uuid);
      if (!row) return;
      row.attempts = (row.attempts || 0) + 1;
      row.last_attempt_utc = nowISO();
      row.last_error = String((error && error.message) || error || 'sync failed').slice(0, 300);
      row.sync_state = 'failed';
      await Store.backend.put('queue', row);
    },

    async markSyncing(event_uuids) {
      await Store.init();
      for (const id of event_uuids) {
        const row = await Store.backend.get('queue', id);
        if (row) { row.sync_state = 'syncing'; await Store.backend.put('queue', row); }
      }
    },

    async resetFailed() {
      await Store.init();
      const rows = await Store.backend.all('queue');
      for (const row of rows) {
        if (row.sync_state === 'failed') { row.sync_state = 'pending'; await Store.backend.put('queue', row); }
      }
    },

    async prune(days = RETENTION_DAYS_DEFAULT) {
      await Store.init();
      const cutoff = Date.now() - days * 864e5;
      const rows = await Store.backend.all('queue');
      for (const row of rows) {
        if (Date.parse(row.created_at_utc) < cutoff) await Store.backend.del('queue', row.event_uuid);
      }
    },

    /* ----- employee directory cache ----- */
    async saveEmployees(employees) {
      await Store.init();
      await Store.backend.clear('employees');
      for (const e of employees.slice(0, 2000)) {
        try { await Store.backend.put('employees', normalizeEmployee(e)); } catch (err) {}
      }
      await Store.backend.put('meta', { key: 'employees_cached_at', value: nowISO() });
    },

    async cachedEmployees() {
      await Store.init();
      const rows = await Store.backend.all('employees');
      const meta = await Store.backend.get('meta', 'employees_cached_at');
      return { employees: rows, cached_at_utc: (meta && meta.value) || null };
    },

    async setLastSync(value) {
      await Store.init();
      await Store.backend.put('meta', { key: 'last_sync', value });
    },

    async getLastSync() {
      await Store.init();
      const meta = await Store.backend.get('meta', 'last_sync');
      return (meta && meta.value) || null;
    },
  };

  /* ---------- sync engine ---------- */
  const listeners = new Set();
  const Sync = {
    state: 'online', // online | offline | syncing
    timer: null,
    syncing: false,

    onStatus(fn) { listeners.add(fn); return () => listeners.delete(fn); },

    async status() {
      const counts = await Offline.counts().catch(() => ({ pending: 0, failed: 0, syncing: 0, total: 0 }));
      return {
        state: this.state, ...counts,
        lastSync: await Offline.getLastSync().catch(() => null),
        storage: Store.kind,
      };
    },

    async emit() {
      const s = await this.status();
      listeners.forEach((fn) => { try { fn(s); } catch (e) {} });
      return s;
    },

    backoffMs(attempts) {
      return Math.min(5000 * 2 ** Math.min(attempts || 0, 5), 5 * 60 * 1000);
    },

    shouldRetry(row) {
      if (!row.last_attempt_utc) return true;
      return Date.now() - Date.parse(row.last_attempt_utc) >= this.backoffMs(row.attempts);
    },

    kick() { this.emit(); this.autoSoon(3000); },
    autoSoon(ms) {
      if (this.timer) return;
      this.timer = setTimeout(() => { this.timer = null; this.syncNow().catch(() => {}); }, ms || 15000);
    },

    isBrowserOffline() {
      return typeof navigator !== 'undefined' && navigator.onLine === false;
    },

    async syncNow() {
      await Offline.init();
      if (this.syncing) return this.status();
      if (this.isBrowserOffline()) { this.state = 'offline'; return this.emit(); }
      const rows = (await Offline.listQueue()).filter((r) => r.sync_state !== 'syncing');
      const due = rows.filter((r) => this.shouldRetry(r));
      if (!due.length) {
        // Still probe the server so the banner reflects reality.
        try { await window.API.ping(); this.state = 'online'; }
        catch (e) { this.state = 'offline'; }
        return this.emit();
      }
      this.syncing = true;
      this.state = 'syncing';
      await this.emit();
      try {
        // Small bounded batches: never send the whole queue at once.
        for (let i = 0; i < due.length; i += 20) {
          const batch = due.slice(i, i + 20);
          await Offline.markSyncing(batch.map((b) => b.event_uuid));
          let result;
          try {
            result = await window.API.batchSync(batch);
          } catch (err) {
            // Transport/server failure: keep everything queued, back off.
            for (const b of batch) await Offline.markResult(b.event_uuid, false, err);
            this.state = 'offline';
            break;
          }
          const byId = new Map((result.items || []).map((x) => [x.event_uuid, x]));
          for (const b of batch) {
            const r = byId.get(b.event_uuid);
            if (r && r.status === 'ok') await Offline.markResult(b.event_uuid, true);
            else await Offline.markResult(b.event_uuid, false, (r && (r.message || r.code)) || 'rejected');
          }
          this.state = 'online';
        }
        await Offline.setLastSync(nowISO());
        await Offline.prune();
      } finally {
        this.syncing = false;
        if (this.state === 'syncing') this.state = 'online';
      }
      // Cache the directory while we are online so offline views stay useful.
      try {
        const snap = await window.API.get('/api/v1/sync/snapshot');
        if (snap && snap.employees) await Offline.saveEmployees(snap.employees);
      } catch (e) {}
      return this.emit();
    },

    start() {
      if (typeof window !== 'undefined' && window.addEventListener) {
        window.addEventListener('online', () => { this.state = 'online'; this.syncNow().catch(() => {}); });
        window.addEventListener('offline', () => { this.state = 'offline'; this.emit(); });
        document.addEventListener('visibilitychange', () => {
          if (!document.hidden) this.syncNow().catch(() => {});
        });
      }
      setInterval(() => this.syncNow().catch(() => {}), 30000);
      this.syncNow().catch(() => {});
    },
  };

  window.Offline = Offline;
  window.SyncEngine = Sync;
})();
