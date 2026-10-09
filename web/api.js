/* Backend REST client (same origin). Credentials live only in
 * sessionStorage for the tab lifetime, entered via the sign-in dialog. */
(() => {
  const KEY = 'att-console-auth';
  const state = { user: '', pass: '' };
  try {
    const saved = JSON.parse(sessionStorage.getItem(KEY) || 'null');
    if (saved) { state.user = saved.u || ''; state.pass = saved.p || ''; }
  } catch (e) {}

  let dialogShow = null;
  function ensureAuth() {
    if (state.user) return Promise.resolve();
    if (!dialogShow) dialogShow = window.AuthDialog
      ? window.AuthDialog.open()
      : Promise.reject(new Error('auth cancelled'));
    return dialogShow.then((creds) => {
      dialogShow = null;
      if (!creds) throw new Error('auth cancelled');
      state.user = creds.u; state.pass = creds.p || '';
      try { sessionStorage.setItem(KEY, JSON.stringify({ u: state.user, p: state.pass })); } catch (e) {}
    }, () => { dialogShow = null; throw new Error('auth cancelled'); });
  }
  function forget() {
    state.user = ''; state.pass = '';
    try { sessionStorage.removeItem(KEY); } catch (e) {}
  }

  async function req(path, opts = {}, silent = false) {
    if (!state.user) {
      if (silent) throw new Error('signed out');
      await ensureAuth();
    }
    const ctrl = new AbortController();
    const timeoutMs = opts.timeoutMs || 15000;
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    const send = () => fetch(path, {
      ...opts,
      signal: ctrl.signal,
      headers: { ...(opts.headers || {}), Authorization: 'Basic ' + btoa(state.user + ':' + state.pass) },
    });
    let res;
    try { res = await send(); }
    catch (e) {
      if (e.name === 'AbortError') throw new Error('backend unreachable: request timed out');
      throw new Error('backend unreachable: ' + e.message);
    }
    finally { clearTimeout(timer); }
    if (res.status === 401) {
      if (silent) throw new Error('unauthorized');
      forget();
      throw new Error('unauthorized — check admin credentials');
    }
    if (!res.ok) {
      let detail = res.statusText;
      try { const j = await res.json(); detail = j.error?.message || detail; } catch (e) {}
      throw new Error(`API ${res.status}: ${detail}`);
    }
    const ct = res.headers.get('content-type') || '';
    return ct.includes('json') ? res.json() : res.blob();
  }

  const get = (path, silent = false) => req(path, {}, silent);
  const post = (path, body) => req(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}) });
  const put = (path, body) => req(path, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  const del = (path) => req(path, { method: 'DELETE' });
  const patch = (path, body) => req(path, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  const download = (path, name) => req(path).then((blob) => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = name; a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 5000);
  });

  // RFC4122 UUIDv4 for idempotent check-ins. crypto.randomUUID needs a
  // secure context; the Math.random fallback is uniqueness-only (not a
  // secret), which is all an idempotency key requires. NEVER invent
  // non-UUID placeholders ('scan-…', 'auto-…'): the server validates
  // event_uuid as UUID and such rows would fail sync forever.
  const newEventUuid = () => {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID();
    const rnd = (typeof crypto !== 'undefined' && crypto.getRandomValues)
      ? crypto.getRandomValues(new Uint8Array(16))
      : Array.from({ length: 16 }, () => Math.floor(Math.random() * 256));
    rnd[6] = (rnd[6] & 0x0f) | 0x40;
    rnd[8] = (rnd[8] & 0x3f) | 0x80;
    const h = [...rnd].map((b) => b.toString(16).padStart(2, '0')).join('');
    return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
  };
  // Unauthenticated liveness probe (no credentials needed, never pops auth).
  const ping = async () => {
    const ctrl = new AbortController();    const timer = setTimeout(() => ctrl.abort(), 8000);
    try {
      const res = await fetch('/health', { signal: ctrl.signal, cache: 'no-store' });
      if (!res.ok) throw new Error('health ' + res.status);
      return res.json();
    } catch (e) {
      throw new Error('backend unreachable: ' + (e.name === 'AbortError' ? 'timed out' : e.message));
    } finally { clearTimeout(timer); }
  };

  // Offline-queue flush: bounded batches of client-UUID events. The server
  // applies per-event idempotency + debounce, so replays are safe.
  const batchSync = (events) => post('/api/v1/attendance/batch', {
    events: events.map((e) => ({
      event_uuid: e.event_uuid,
      fingerprint_slot_id: e.fingerprint_slot_id,
      captured_at: new Date(e.captured_at_utc).toISOString(),
      client_seq: e.client_seq ?? null,
      clock_uncertain: !!e.clock_uncertain,
    })),
  });

  // EventSource cannot send Authorization headers, so the web UI polls
  // the recent-attendance endpoint every few seconds instead (the SSE
  // /api/v1/events stream is used by first-party clients that can set
  // headers, e.g. the desktop app). Polling stops when the tab hides.
  function pollRecent(onMsg, ms = 3000) {
    let last = '';
    const tick = async () => {
      if (document.hidden) return;
      try {
        const r = await get('/api/v1/attendance?limit=1&offset=0', true);
        const cur = r.items[0]?.event_uuid || '';
        if (cur && cur !== last) { last = cur; onMsg({ type: 'attendance.recorded', data: r.items[0] }); }
      } catch (e) {} // silent: background refresh must never pop sign-in or wipe creds
    };
    tick();
    const id = setInterval(tick, ms);
    return () => clearInterval(id);
  }

  const isBrowserOffline = () => typeof navigator !== 'undefined' && navigator.onLine === false;

  window.API = { get, post, put, del, patch, download, pollRecent, ping, batchSync, isBrowserOffline, newEventUuid, state, forget };
})();
