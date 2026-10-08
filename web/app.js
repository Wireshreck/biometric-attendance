/* Dashboard views over the backend REST API, with the motion system:
 * count-up metrics, animated canvas charts, skeleton placeholders,
 * staged list entrances, toasts, command palette, theme toggle. */
(() => {
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---- auth dialog ----
  window.AuthDialog = {
    open() {
      return new Promise((resolve) => {
        const dlg = $('authDlg');
        const done = (v) => { dlg.close(); resolve(v); };
        $('authForm').onsubmit = () => { done({ u: $('authUser').value.trim(), p: $('authPass').value.trim() }); };
        $('authCancel').onclick = () => done(null);
        dlg.onclose = () => resolve(null);
        dlg.showModal();
        setTimeout(() => $('authUser').focus(), 50);
      });
    },
  };

  // ---- theme ----
  $('btnTheme').onclick = () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('att-theme', next); } catch (e) {}
    drawLast();
  };

  // ---- clock ----
  setInterval(() => {
    const n = new Date();
    $('clock').textContent = n.toLocaleTimeString();
    $('dateLine').textContent = n.toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' });
  }, 1000);

  // ---- nav ----
  function goto(view) {
    document.querySelectorAll('#nav button').forEach((x) => { x.classList.remove('on'); x.removeAttribute('aria-current'); });
    document.querySelectorAll('.view').forEach((v) => v.classList.remove('on'));
    const b = document.querySelector(`#nav button[data-view="${view}"]`);
    if (b) { b.classList.add('on'); b.setAttribute('aria-current', 'page'); }
    $('view-' + view).classList.add('on');
    if (view === 'dash') loadDash();
    if (view === 'att') loadAtt();
    if (view === 'stu') loadStu();
    if (view === 'ana') loadAnalytics();
    if (view === 'devs') loadDevices();
  }
  document.querySelectorAll('#nav button').forEach((b) => { b.onclick = () => goto(b.dataset.view); });

  function setApi(ok, msg) {
    $('apiTxt').textContent = ok ? 'API: connected' : 'API: ' + msg;
    $('apiDot').className = 'dot ' + (ok ? 'ok' : 'bad');
  }

  // ---- toasts ----
  function toast(msg, kind = '') {
    const box = $('toasts');
    while (box.children.length >= 3) box.firstChild.remove();
    const t = document.createElement('div');
    t.className = 'toast ' + kind;
    t.innerHTML = esc(msg) + '<span class="bar"></span>';
    box.appendChild(t);
    setTimeout(() => { t.classList.add('out'); setTimeout(() => t.remove(), 220); }, 3400);
  }
  window.toast = toast;

  // ---- count-up ----
  function countUp(el, target, suffix = '') {
    const end = parseFloat(target);
    const fmt = (v) => (Number.isInteger(end) ? Math.round(v) : v.toFixed(1)) + suffix;
    el.textContent = fmt(end); // final value first: correct even if rAF stalls
    if (reduced() || !isFinite(end) || !window.requestAnimationFrame) return;
    const t0 = performance.now(), dur = 600;
    const step = (t) => {
      const k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      el.textContent = fmt(end * e);
      if (k < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  // ---- charts ----
  let lastDraw = null;
  function drawLast() { if (lastDraw) lastDraw(); }
  function animateCanvas(canvas, draw, dur = 700) {
    if (reduced()) { draw(1); lastDraw = () => draw(1); return; }
    const t0 = performance.now();
    lastDraw = () => draw(1);
    const step = (t) => {
      const k = Math.min(1, (t - t0) / dur);
      draw(1 - Math.pow(1 - k, 3));
      if (k < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }
  function cssVar(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
  function bars(canvas, labels, values) {
    animateCanvas(canvas, (k) => {
      const ctx = canvas.getContext('2d'), W = canvas.width, H = canvas.height;
      ctx.clearRect(0, 0, W, H);
      const max = Math.max(1, ...values), n = values.length, bw = W / Math.max(1, n);
      values.forEach((v, i) => {
        const h = (H - 30) * (v / max) * k;
        ctx.fillStyle = cssVar('--accent') || '#2f5fd0';
        ctx.fillRect(i * bw + bw * 0.22, H - 22 - h, bw * 0.56, h);
        ctx.fillStyle = cssVar('--muted') || '#5b6b82'; ctx.font = '11px sans-serif';
        ctx.fillText(String(labels[i]).slice(5), i * bw + 4, H - 6);
      });
    });
  }
  function line(canvas, labels, values) {
    animateCanvas(canvas, (k) => {
      const ctx = canvas.getContext('2d'), W = canvas.width, H = canvas.height;
      ctx.clearRect(0, 0, W, H);
      const max = Math.max(1, ...values), n = values.length;
      if (!n) return;
      const px = (i) => (i / Math.max(1, n - 1)) * (W - 16) + 8;
      const py = (v) => H - 26 - (H - 46) * (v / max);
      ctx.strokeStyle = cssVar('--accent') || '#2f5fd0'; ctx.lineWidth = 2.5; ctx.lineJoin = 'round';
      ctx.beginPath();
      const upto = Math.max(2, Math.ceil(n * k));
      ctx.moveTo(px(0), py(values[0]));
      for (let i = 1; i < upto && i < n; i++) ctx.lineTo(px(i), py(values[i]));
      ctx.stroke();
      ctx.fillStyle = cssVar('--accent') || '#2f5fd0';
      for (let i = 0; i < upto && i < n; i++) { ctx.beginPath(); ctx.arc(px(i), py(values[i]), 3, 0, 7); ctx.fill(); }
      ctx.fillStyle = cssVar('--muted'); ctx.font = '11px sans-serif';
      labels.forEach((l, i) => { if (i < upto) ctx.fillText(String(l).slice(5), px(i) - 10, H - 6); });
    });
  }

  function skeleton(el, rows = 3) {
    el.innerHTML = Array.from({ length: rows }, () => '<div class="skel" style="height:18px;margin:6px 0">&nbsp;</div>').join('');
  }

  // ---- dashboard (home) ----
  let dashFirst = true;
  async function loadDash() {
    if (dashFirst) skeleton($('statCards'), 1);
    try {
      const s = await API.get('/api/v1/statistics/overview?trend_days=7');
      setApi(true);
      const o = s.overview;
      $('heroPct').textContent = '';
      countUp($('heroPct'), o.attendance_percentage, '%');
      $('heroCount').textContent = `${o.present_today}/${o.total_students} students`;
      $('devDot').className = 'dot ok'; $('devTxt').textContent = 'live';
      const cards = [[o.present_today, 'present today'], [o.absent_today, 'absent today'],
        [o.attendance_percentage + '%', 'attendance'], [o.total_students, 'students'], [o.checkins_today, 'check-ins']];
      $('statCards').innerHTML = cards.map(([n, l]) => `<div class="card"><div class="num" data-n="${n}"></div><div class="lbl">${l}</div></div>`).join('');
      $('statCards').querySelectorAll('.num').forEach((el) => {
        const raw = el.dataset.n;
        if (String(raw).endsWith('%')) countUp(el, parseFloat(raw), '%');
        else countUp(el, parseFloat(raw));
      });
      const recent = await API.get('/api/v1/attendance?limit=8&offset=0');
      $('recentList').innerHTML = recent.items.length ? recent.items.map((r) =>
        `<div>${esc(r.captured_at_utc.slice(11, 16))} — ${esc(r.first_name)} ${esc(r.last_name)} <span style="color:var(--muted)">(${esc(r.grade_class)}${esc(r.section)})</span></div>`).join('')
        : '<div class="empty"><span class="glyph">○</span>No check-ins yet today.</div>';
      $('absentList').innerHTML = s.absent.length ? s.absent.slice(0, 8).map((a) =>
        `<div>${esc(a.first_name)} ${esc(a.last_name)} <span style="color:var(--muted)">(${esc(a.grade_class)}${esc(a.section)})</span></div>`).join('')
        : '<div class="empty"><span class="glyph">✓</span>Everyone present.</div>';
      dashFirst = false;
    } catch (e) {
      setApi(false, e.message);
      $('statCards').innerHTML = `<div class="errorbox">Dashboard unavailable: ${esc(e.message)}</div>`;
      $('devDot').className = 'dot bad'; $('devTxt').textContent = 'unreachable';
    }
  }
  $('btnDashRefresh').onclick = (e) => { busy(e.target, loadDash)(); };
  API.pollRecent((ev) => {
    showOverlay(ev.data, ev.data.outcome === 'RECORDED' ? 'match' : 'duplicate');
    if ($('view-dash').classList.contains('on')) loadDash();
    if ($('view-att').classList.contains('on')) loadAtt();
  });
  async function busy(btn, fn) {
    return async () => { btn.classList.add('btn-busy'); try { await fn(); } finally { btn.classList.remove('btn-busy'); } };
  }

  // ---- analytics ----
  let anaFirst = true;
  async function loadAnalytics() {
    try {
      const s = await API.get('/api/v1/statistics/overview?trend_days=30');
      line($('chTrend'), s.trend.map((t) => t.date), s.trend.map((t) => t.present));
      $('classTable').innerHTML = s.classes.length ? '<table><thead><tr><th>Class</th><th>Sec</th><th>Present</th><th>Active</th><th>%</th></tr></thead><tbody>' +
        s.classes.map((c) => `<tr><td>${esc(c.class)}</td><td>${esc(c.section)}</td><td>${c.present}</td><td>${c.active}</td><td>${c.percentage}%</td></tr>`).join('') + '</tbody></table>'
        : '<div class="empty"><span class="glyph">▦</span>No classes yet — add students first.</div>';
      bars($('chBusy'), s.busy_times.map((t) => 'xx' + t.hour), s.busy_times.map((t) => t.checkins));
      const month = s.trend.reduce((a, t) => a + t.present, 0);
      $('monthTable').innerHTML = `<table><tbody><tr><td>Check-ins (30d)</td><td><b>${month}</b></td></tr><tr><td>Active days</td><td><b>${s.trend.filter((t) => t.present > 0).length}</b></td></tr></tbody></table>`;
      anaFirst = false;
    } catch (e) { toast(e.message, 'err'); }
  }
  $('btnAnaRefresh').onclick = (e) => { busy(e.target, loadAnalytics)(); };

  // ---- devices ----
  async function loadDevices() {
    try {
      const r = await API.get('/api/v1/devices');
      $('devsTable').querySelector('tbody').innerHTML = r.items.map((d) =>
        `<tr><td>${esc(d.device_name)}</td><td>${esc(d.location_name)}</td><td>${d.status}</td><td>${esc(d.firmware_version || '—')}</td><td>${d.sensor_capacity ?? '—'}</td><td>${esc(d.last_seen_at_utc || 'never')}</td></tr>`).join('')
        || '<tr><td colspan="6"><div class="empty">No devices provisioned.</div></td></tr>';
      $('bleLinkInfo').innerHTML = `<dt>BLE</dt><dd>${window.BLE && window.BLE.connected ? 'connected' : 'disconnected'}</dd>`;
    } catch (e) { toast(e.message, 'err'); }
  }
  $('btnDevsRefresh').onclick = (e) => { busy(e.target, loadDevices)(); };
  $('btnBle2').onclick = () => { goto('dev'); $('btnBle').click(); };

  // ---- big overlay ----
  let overlayTimer = null;
  function showOverlay(rec, kind) {
    const ov = $('overlay');
    const name = `${rec.first_name || ''} ${rec.last_name || ''}`.trim() || 'Unknown fingerprint';
    $('ovName').textContent = name;
    $('ovClass').textContent = rec.grade_class ? `Class ${rec.grade_class}${rec.section || ''}` : `Slot ${rec.fingerprint_slot_id ?? '—'}`;
    const dup = rec.outcome === 'DUPLICATE_SUPPRESSED' || kind === 'duplicate';
    $('ovKicker').textContent = kind === 'nomatch' ? 'NO MATCH' : kind === 'error' ? 'SENSOR' : 'ATTENDANCE';
    $('ovCheck').textContent = kind === 'nomatch' ? '?' : dup ? '⧗' : '✓';
    $('ovStatus').textContent = kind === 'nomatch' ? 'NOT ENROLLED' : dup ? 'ALREADY RECORDED' : 'PRESENT';
    $('ovStatus').className = 'ov-status ' + (kind === 'nomatch' || kind === 'error' ? 'bad' : dup ? 'warn' : 'ok');
    const ts = rec.captured_at_utc || rec.captured_at || '';
    $('ovTime').textContent = ts ? ts.slice(0, 10) + '  ' + ts.slice(11, 16) + ' UTC' : new Date().toLocaleString();
    $('ovFp').textContent = `Fingerprint #${rec.fingerprint_slot_id ?? '—'}` + (rec.confidence != null ? ` · confidence ${rec.confidence}` : '');
    ov.hidden = false;
    ov.classList.remove('show');
    void ov.offsetWidth;
    ov.classList.add('show');
    clearTimeout(overlayTimer);
    overlayTimer = setTimeout(() => { ov.classList.remove('show'); setTimeout(() => { ov.hidden = true; }, 300); }, 6000);
  }
  window.showOverlay = showOverlay;
  $('overlay').addEventListener('click', () => { clearTimeout(overlayTimer); $('overlay').classList.remove('show'); $('overlay').hidden = true; });

  // ---- hero scan ----
  $('btnHeroScan').onclick = async (e) => {
    if (!window.BLE || !window.BLE.connected) {
      toast('Connect BLE first (Devices page)', 'warn');
      goto('dev');
      return;
    }
    e.target.classList.add('btn-busy');
    ScanUI.set('SCANNING', 'Place your finger on the sensor…');
    try {
      const r = await window.BLE.send('FINGERPRINT_SEARCH', {}, 30000);
      if (r.code === 'match') {
        showOverlay({ ...r, first_name: '', last_name: '' }, 'match');
        try {
          const a = await API.post('/api/v1/assisted-checkin', { fingerprint_slot_id: r.slot });
          showOverlay({ ...a, confidence: r.confidence }, a.outcome === 'RECORDED' ? 'match' : 'duplicate');
          loadDash();
        } catch (err) { toast('Check-in: ' + err.message, 'err'); }
      } else if (r.code === 'no_match') {
        showOverlay({ fingerprint_slot_id: null }, 'nomatch');
      } else {
        showOverlay({}, 'error');
      }
    } catch (err) { toast('Scan: ' + err.message, 'err'); }
    finally { e.target.classList.remove('btn-busy'); }
  };
  setInterval(() => {
    const ok = window.BLE && window.BLE.connected;
    $('scanReady').textContent = ok ? 'READY FOR SCAN' : 'not connected';
    $('scanReady').style.color = ok ? 'var(--ok)' : 'var(--muted)';
  }, 2000);

  // ---- attendance ----
  let attPage = 0; const attLimit = 25;
  function attParams() {
    const p = new URLSearchParams({ limit: attLimit, offset: attPage * attLimit, sort: $('fSort').value });
    const v = (id) => $(id).value.trim();
    if (v('fQ')) p.set('q', v('fQ'));
    if (v('fDay')) p.set('day', v('fDay'));
    if (v('fFrom')) p.set('date_from', v('fFrom'));
    if (v('fTo')) p.set('date_to', v('fTo'));
    if (v('fTFrom')) p.set('time_from', v('fTFrom'));
    if (v('fTTo')) p.set('time_to', v('fTTo'));
    if (v('fClass')) p.set('grade_class', v('fClass'));
    if (v('fSection')) p.set('section', v('fSection'));
    if (v('fSlot')) p.set('slot', v('fSlot'));
    if (v('fOutcome')) p.set('outcome', v('fOutcome'));
    return p;
  }
  async function loadAtt() {
    const tb = $('attTable').querySelector('tbody');
    tb.classList.add('fading');
    try {
      const r = await API.get('/api/v1/attendance?' + attParams());
      $('attErr').innerHTML = '';
      $('attMeta').textContent = `${r.total} record(s)`;
      tb.innerHTML = r.items.map((x, i) =>
        `<tr class="${i === 0 && attPage === 0 ? 'fresh' : ''}"><td>${esc(x.captured_at_utc.slice(0, 10))}</td><td>${esc(x.captured_at_utc.slice(11, 16))}</td><td>${esc(x.first_name)} ${esc(x.last_name)}</td><td>${esc(x.roll_number)}</td><td>${esc(x.grade_class)}</td><td>${esc(x.section)}</td><td>${x.fingerprint_slot_id}</td><td>${x.outcome}</td></tr>`).join('')
        || '<tr><td colspan="8"><div class="empty"><span class="glyph">∅</span>No records match these filters.</div></td></tr>';
      $('pgInfo').textContent = `Page ${attPage + 1} of ${Math.max(1, Math.ceil(r.total / attLimit))}`;
    } catch (e) { $('attErr').innerHTML = `<div class="errorbox">Attendance unavailable: ${esc(e.message)}</div>`; }
    requestAnimationFrame(() => tb.classList.remove('fading'));
  }
  $('flt').onsubmit = (e) => { e.preventDefault(); attPage = 0; loadAtt(); };
  let deb = null;
  $('fQ').oninput = () => { clearTimeout(deb); deb = setTimeout(() => { attPage = 0; loadAtt(); }, 350); };
  $('pgPrev').onclick = () => { if (attPage > 0) { attPage--; loadAtt(); } };
  $('pgNext').onclick = () => { attPage++; loadAtt(); };
  $('btnCsv').onclick = (e) => busy(e.target, () => API.download('/api/v1/export.csv?' + attParams(), 'attendance.csv').then(() => toast('Export complete', 'ok')).catch((err) => toast(err.message, 'err')))();
  $('btnXlsx').onclick = (e) => busy(e.target, () => API.download('/api/v1/export.xlsx?' + attParams(), 'attendance.xlsx').then(() => toast('Export complete', 'ok')).catch((err) => toast(err.message, 'err')))();

  // ---- students ----
  let editing = null;
  async function loadStu() {
    try {
      const devs = await API.get('/api/v1/devices');
      if (!devs.items.length) {
        toast('No active device: provision one first — see Help → Setup step 5', 'warn');
      }
    } catch (e) {}
    try {
      const p = new URLSearchParams({ limit: 100, offset: 0 });
      if ($('sQ').value.trim()) p.set('q', $('sQ').value.trim());
      if ($('sClass').value.trim()) p.set('grade_class', $('sClass').value.trim());
      if ($('sStatus').value) p.set('status', $('sStatus').value);
      const r = await API.get('/api/v1/students?' + p);
      $('stuTable').querySelector('tbody').innerHTML = r.items.map((s) =>
        `<tr><td>${esc(s.first_name)} ${esc(s.last_name)}</td><td>${esc(s.roll_number)}</td><td>${esc(s.grade_class)}</td><td>${esc(s.section)}</td><td>${s.status}</td><td>${s.fingerprint_slot_id ?? '—'}</td><td><button data-act="view" data-id="${s.student_uuid}">Open</button></td></tr>`).join('')
        || '<tr><td colspan="7"><div class="empty"><span class="glyph">○</span>No students found. Add one to begin enrollment.</div></td></tr>';
      $('stuTable').querySelectorAll('button').forEach((b) => { b.onclick = () => openStudent(b.dataset.id); });
    } catch (e) { toast(e.message, 'err'); }
  }
  $('stuFlt').onsubmit = (e) => { e.preventDefault(); loadStu(); };
  $('btnStuNew').onclick = () => { editing = null; $('stuDlgTitle').textContent = 'Add student'; $('stuForm').reset(); $('stuDlg').showModal(); };
  $('stuCancel').onclick = () => $('stuDlg').close();
  $('stuForm').onsubmit = async (e) => {
    const body = { roll_number: $('stuRoll').value.trim(), first_name: $('stuFirst').value.trim(), last_name: $('stuLast').value.trim(), grade_class: $('stuClass').value.trim(), section: $('stuSection').value.trim() };
    try {
      if (editing) { await API.patch('/api/v1/students/' + editing, body); }
      else { await API.post('/api/v1/students', body); }
      $('stuDlg').close(); loadStu(); toast('Saved', 'ok');
    } catch (err) {
      e.preventDefault();
      toast(/one active.*device/i.test(err.message)
        ? 'No provisioned device yet — run the provision command in Help → Setup, then retry.'
        : err.message, 'err');
    }
  };
  async function openStudent(id) {
    try {
      const s = await API.get('/api/v1/students/' + id + '/summary?days=30');
      const d = $('stuDetail'); d.hidden = false;
      d.innerHTML = `<h2>${esc(s.first_name)} ${esc(s.last_name)} <span style="color:var(--muted)">(${esc(s.roll_number)} · ${esc(s.grade_class)}${esc(s.section)} · ${s.status})</span></h2>
        <div class="progress"><i style="width:${s.attendance_percentage}%"></i></div>
        <p>30-day attendance: <b>${s.attendance_percentage}%</b> · days present: ${s.days_present}/${s.window_days} · first: ${s.first || '—'} · last: ${s.last || '—'}</p>
        <div class="row"><button id="btnStuEdit">Edit</button>${s.status === 'PENDING_ENROLLMENT' ? '<button id="btnStuActivate">Mark enrolled</button>' : ''}<button id="btnStuDeact">Deactivate</button><button id="btnStuDel">Delete</button></div>`;
      $('btnStuEdit').onclick = () => { editing = id; $('stuDlgTitle').textContent = 'Edit student'; $('stuRoll').value = s.roll_number; $('stuFirst').value = s.first_name; $('stuLast').value = s.last_name; $('stuClass').value = s.grade_class; $('stuSection').value = s.section; $('stuDlg').showModal(); };
      $('btnStuDeact').onclick = async () => { if (confirm('Deactivate this student?')) { await API.post(`/api/v1/students/${id}/deactivate`); toast('Deactivated', 'ok'); loadStu(); d.hidden = true; } };
      $('btnStuDel').onclick = async () => {
        if (!confirm(`Permanently DELETE ${s.first_name} ${s.last_name}? Their attendance rows stay but lose the name link.`)) return;
        try {
          const r = await API.del(`/api/v1/students/${id}`);
          toast(`Deleted (${r.orphaned_attendance_records} orphaned record(s))`, 'ok');
          loadStu(); d.hidden = true;
        } catch (err) { toast(err.message, 'err'); }
      };
      const act = $('btnStuActivate');
      if (act) act.onclick = async () => {
        if (!confirm(`Confirm the finger template is stored in slot ${s.fingerprint_slot_id}, then activate?`)) return;
        try { await API.post(`/api/v1/students/${id}/activate`); toast('Student activated', 'ok'); loadStu(); openStudent(id); }
        catch (err) { toast(err.message, 'err'); }
      };
      d.scrollIntoView({ block: 'nearest' });
    } catch (e) { toast(e.message, 'err'); }
  }

  // ---- scan state machine (driven by ble.js) ----
  window.ScanUI = {
    set(stage, sub = '') {
      const svg = $('fpSvg');
      svg.classList.remove('scanning', 'done', 'fail');
      $('scanStage').textContent = stage;
      $('scanSub').textContent = sub;
      if (stage === 'SCANNING' || stage === 'PROCESSING') svg.classList.add('scanning');
      if (stage === 'MATCH FOUND' || stage === 'ENROLLED') svg.classList.add('done');
      if (stage === 'NO MATCH' || stage === 'FAILED') svg.classList.add('fail');
    },
  };

  // ---- AI ----
  async function refreshKey() {
    try {
      const s = await API.get('/api/v1/settings/ai');
      $('keyState').textContent = s.gemini_configured ? 'configured ✓' : 'not set';
    } catch (e) { $('keyState').textContent = ''; }
  }
  $('btnKeySave').onclick = async (e) => {
    const key = $('aiKey').value.trim();
    if (!key) { toast('Paste a key first', 'warn'); return; }
    try {
      await API.put('/api/v1/settings/ai', { gemini_api_key: key });
      $('aiKey').value = '';
      toast('Key saved on server', 'ok');
      refreshKey();
    } catch (err) { toast(err.message, 'err'); }
  };
  const chips = ['How many students attended today?', 'Who was absent today?', 'What is attendance for Class 10A?', 'Summarize today’s attendance.'];
  chips.forEach((c) => { const b = document.createElement('button'); b.textContent = c; b.onclick = () => { $('aiQ').value = c; $('aiForm').requestSubmit(); }; $('aiChips').appendChild(b); });
  function bubble(cls, html) { const d = document.createElement('div'); d.className = 'msg ' + cls; d.innerHTML = html; $('aiLog').appendChild(d); d.scrollIntoView({ block: 'nearest' }); return d; }
  $('aiForm').onsubmit = async (e) => {
    e.preventDefault();
    const q = $('aiQ').value.trim(); if (!q) return;
    $('aiQ').value = '';
    bubble('q', esc(q));
    const t = bubble('', '<span class="typing"><i></i><i></i><i></i></span>');
    try {
      const r = await API.post('/api/v1/ai/chat', { question: q });
      let html = esc(r.answer);
      const rows = r.result?.records || r.result?.absent || r.result?.students;
      if (r.tool === 'get_attendance_statistics' && r.result?.present_today !== undefined) {
        const o = r.result;
        html = `<div class="cards"><div class="card"><div class="num">${o.present_today}</div><div class="lbl">present</div></div><div class="card"><div class="num">${o.attendance_percentage}%</div><div class="lbl">attendance</div></div></div>` + html;
      }
      if (Array.isArray(rows) && rows.length) {
        html += '<table><tbody>' + rows.slice(0, 12).map((x) =>
          `<tr><td>${esc(x.first_name || '')} ${esc(x.last_name || '')}</td><td>${esc(x.roll_number || '')}</td><td>${esc((x.captured_at_utc || '').slice(0, 16))}</td></tr>`).join('') + '</tbody></table>';
      }
      t.innerHTML = html + (r.ai_available ? '' : ' <span style="color:var(--muted)">(local data; set GEMINI_API_KEY for AI summaries)</span>');
    } catch (err) { t.innerHTML = 'Error: ' + esc(err.message); }
  };

  // ---- command palette ----
  const CMDS = [
    ['Go to Home', 'nav', () => goto('dash')], ['Go to Attendance', 'nav', () => goto('att')],
    ['Go to Students', 'nav', () => goto('stu')], ['Go to Analytics', 'nav', () => goto('ana')],
    ['Go to Devices', 'nav', () => goto('devs')], ['Go to Fingerprints', 'nav', () => goto('dev')],
    ['Go to AI Assistant', 'nav', () => goto('ai')], ['Refresh dashboard', 'data', () => loadDash()],
    ['Export attendance CSV', 'data', () => $('btnCsv').click()], ['Connect BLE device', 'device', () => $('btnBle').click()],
    ['Run full diagnostic', 'device', () => { goto('dev'); $('btnDiag').click(); }],
    ['Toggle dark mode', 'ui', () => $('btnTheme').click()],
  ];
  let palSel = 0;
  function renderPal(filter = '') {
    const list = CMDS.filter(([n]) => n.toLowerCase().includes(filter.toLowerCase()));
    palSel = Math.min(palSel, Math.max(0, list.length - 1));
    $('palList').innerHTML = list.map(([n, c], i) => `<li class="${i === palSel ? 'sel' : ''}" data-i="${i}">${esc(n)}<span class="cat">${c}</span></li>`).join('')
      || '<li>No matching command.</li>';
    $('palList').querySelectorAll('li[data-i]').forEach((li) => {
      li.onclick = () => { closePal(); list[+li.dataset.i][2](); };
      li.onmousemove = () => { palSel = +li.dataset.i; renderPal(filter); };
    });
    return list;
  }
  function openPal() { $('palette').classList.add('open'); $('palInput').value = ''; palSel = 0; renderPal(); setTimeout(() => $('palInput').focus(), 30); }
  function closePal() { $('palette').classList.remove('open'); }
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); $('palette').classList.contains('open') ? closePal() : openPal(); }
    if (e.key === 'Escape') closePal();
    if ($('palette').classList.contains('open') && (e.key === 'ArrowDown' || e.key === 'ArrowUp' || e.key === 'Enter')) {
      e.preventDefault();
      const list = renderPal($('palInput').value);
      if (e.key === 'ArrowDown') palSel = Math.min(palSel + 1, list.length - 1);
      if (e.key === 'ArrowUp') palSel = Math.max(palSel - 1, 0);
      if (e.key === 'Enter' && list[palSel]) { closePal(); list[palSel][2](); return; }
      renderPal($('palInput').value);
    }
  });
  $('palInput').oninput = () => { palSel = 0; renderPal($('palInput').value); };
  $('palette').addEventListener('click', (e) => { if (e.target.id === 'palette') closePal(); });

  loadDash();
})();
