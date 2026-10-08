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
    const send = () => fetch(path, {
      ...opts,
      headers: { ...(opts.headers || {}), Authorization: 'Basic ' + btoa(state.user + ':' + state.pass) },
    });
    let res;
    try { res = await send(); }
    catch (e) { throw new Error('backend unreachable: ' + e.message); }
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
  const patch = (path, body) => req(path, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  const download = (path, name) => req(path).then((blob) => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = name; a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 5000);
  });

  // EventSource cannot send Authorization headers, so the web UI polls
  // the recent-attendance endpoint every few seconds instead (the SSE
  // /api/v1/events stream is used by first-party clients that can set
  // headers, e.g. the desktop app). Polling stops when the tab hides.
  function pollRecent(onMsg, ms = 5000) {
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

  window.API = { get, post, put, patch, download, pollRecent, state, forget };
})();
