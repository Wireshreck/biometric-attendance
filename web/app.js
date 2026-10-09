/* Dashboard views over the backend REST API, with the motion system:
 * count-up metrics, animated canvas charts, skeleton placeholders,
 * staged list entrances, toasts, command palette, theme toggle. */
(() => {
  const $id = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---- auth dialog ----
  window.AuthDialog = {
    open() {
      return new Promise((resolve) => {
        const dlg = $id('authDlg');
        const done = (v) => { dlg.close(); resolve(v); };
        $id('authForm').onsubmit = () => { done({ u: $id('authUser').value.trim(), p: $id('authPass').value.trim() }); };
        $id('authCancel').onclick = () => done(null);
        dlg.onclose = () => resolve(null);
        dlg.showModal();
        setTimeout(() => $id('authUser').focus(), 50);
      });
    },
  };

  // ---- theme ----
  $id('btnTheme').onclick = () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('att-theme', next); } catch (e) {}
    drawLast();
  };

  // ---- clock ----
  setInterval(() => {
    const n = new Date();
    $id('clock').textContent = n.toLocaleTimeString();
    $id('dateLine').textContent = n.toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' });
  }, 1000);

  // ---- nav ----
  function goto(view) {
    document.querySelectorAll('#nav button').forEach((x) => { x.classList.remove('on'); x.removeAttribute('aria-current'); });
    document.querySelectorAll('.view').forEach((v) => v.classList.remove('on'));
    const b = document.querySelector(`#nav button[data-view="${view}"]`);
    if (b) { b.classList.add('on'); b.setAttribute('aria-current', 'page'); }
    $id('view-' + view).classList.add('on');
    if (view === 'dash') loadDash();
    if (view === 'att') loadAtt();
    if (view === 'stu') loadStu();
    if (view === 'ana') loadAnalytics();
    if (view === 'devs') loadDevices();
  }
  document.querySelectorAll('#nav button').forEach((b) => { b.onclick = () => goto(b.dataset.view); });

  function setApi(ok, msg) {
    $id('apiTxt').textContent = ok ? 'API: connected' : 'API: ' + msg;
    $id('apiDot').className = 'dot ' + (ok ? 'ok' : 'bad');
  }

  // ---- toasts ----
  function toast(msg, kind = '') {
    const box = $id('toasts');
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
  const empName = (r) => r.employee_name || `${r.first_name || ''} ${r.last_name || ''}`.trim() || 'Unknown';
  const empCode = (r) => r.employee_code || r.roll_number || '—';
  const empDept = (r) => r.department || r.grade_class || '—';
  const empTeam = (r) => r.team ?? r.section ?? '';
  async function loadDash() {
    if (dashFirst) skeleton($id('statCards'), 1);
    try {
      const s = await API.get('/api/v1/statistics/overview?trend_days=7');
      setApi(true);
      try { if (s.employees || s.overview) await Offline.saveEmployees((await API.get('/api/v1/sync/snapshot')).employees || []); } catch (e) {}
      const o = s.overview;
      const total = o.total_employees ?? o.total_students ?? 0;
      $id('heroPct').textContent = '';
      countUp($id('heroPct'), o.attendance_percentage, '%');
      $id('heroCount').textContent = `${o.present_today}/${total} employees`;
      $id('devDot').className = 'dot ok'; $id('devTxt').textContent = 'live';
      const cards = [[o.present_today, 'present today'], [o.absent_today, 'absent today'],
        [o.attendance_percentage + '%', 'attendance'], [total, 'employees'], [o.checkins_today, 'check-ins']];
      $id('statCards').innerHTML = cards.map(([n, l]) => `<div class="card"><div class="num" data-n="${n}"></div><div class="lbl">${l}</div></div>`).join('');
      $id('statCards').querySelectorAll('.num').forEach((el) => {
        const raw = el.dataset.n;
        if (String(raw).endsWith('%')) countUp(el, parseFloat(raw), '%');
        else countUp(el, parseFloat(raw));
      });
      const recent = await API.get('/api/v1/attendance?limit=8&offset=0');
      $id('recentList').innerHTML = recent.items.length ? recent.items.map((r) =>
        `<div>${esc(r.captured_at_utc.slice(11, 16))} — ${esc(empName(r))} <span style="color:var(--muted)">(${esc(empDept(r))}${esc(empTeam(r))})</span></div>`).join('')
        : '<div class="empty"><span class="glyph">○</span>No check-ins yet today.</div>';
      $id('absentList').innerHTML = s.absent.length ? s.absent.slice(0, 8).map((a) =>
        `<div>${esc(empName(a))} <span style="color:var(--muted)">(${esc(empDept(a))}${esc(empTeam(a))})</span></div>`).join('')
        : '<div class="empty"><span class="glyph">✓</span>Everyone present.</div>';
      dashFirst = false;
    } catch (e) {
      setApi(false, e.message);
      // Offline fallback: render from the cached directory + queued events.
      try {
        const { employees } = await Offline.cachedEmployees();
        const q = await Offline.listQueue();
        const names = employees.slice(0, 8).map((x) => `<div>${esc(x.name)} <span style="color:var(--muted)">(${esc(x.department)}${esc(x.team)})</span></div>`).join('');
        $id('statCards').innerHTML = `<div class="errorbox">Dashboard offline — showing cached directory (${employees.length} employees, ${q.length} queued). ${esc(e.message)}</div>`;
        $id('recentList').innerHTML = q.length
          ? q.slice(-8).reverse().map((x) => `<div>${esc((x.captured_at_utc || '').slice(11, 16))} — ${esc((x.employee && x.employee.name) || ('Slot ' + x.fingerprint_slot_id))} <span style="color:var(--muted)">queued</span></div>`).join('')
          : '<div class="empty"><span class="glyph">○</span>No queued check-ins.</div>';
        $id('absentList').innerHTML = names || '<div class="empty"><span class="glyph">○</span>No cached directory yet — connect once to cache it.</div>';
      } catch (err) {
        $id('statCards').innerHTML = `<div class="errorbox">Dashboard unavailable: ${esc(e.message)}</div>`;
      }
      $id('devDot').className = 'dot bad'; $id('devTxt').textContent = 'unreachable';
    }
  }
  $id('btnDashRefresh').onclick = (e) => { busy(e.target, loadDash)(); };
  API.pollRecent((ev) => {
    showOverlay(ev.data, ev.data.outcome === 'RECORDED' ? 'match' : 'duplicate');
    if ($id('view-dash').classList.contains('on')) loadDash();
    if ($id('view-att').classList.contains('on')) loadAtt();
  });
  async function busy(btn, fn) {
    return async () => { btn.classList.add('btn-busy'); try { await fn(); } finally { btn.classList.remove('btn-busy'); } };
  }

  // ---- analytics ----
  let anaFirst = true;
  async function loadAnalytics() {
    try {
      const s = await API.get('/api/v1/statistics/overview?trend_days=30');
      line($id('chTrend'), s.trend.map((t) => t.date), s.trend.map((t) => t.present));
      $id('classTable').innerHTML = s.classes.length ? '<table><thead><tr><th>Department</th><th>Team</th><th>Present</th><th>Active</th><th>%</th></tr></thead><tbody>' +
        s.classes.map((c) => `<tr><td>${esc(c.department ?? c.class)}</td><td>${esc(c.team ?? c.section)}</td><td>${c.present}</td><td>${c.active}</td><td>${c.percentage}%</td></tr>`).join('') + '</tbody></table>'
        : '<div class="empty"><span class="glyph">▦</span>No departments yet — add employees first.</div>';
      bars($id('chBusy'), s.busy_times.map((t) => 'xx' + t.hour), s.busy_times.map((t) => t.checkins));
      const month = s.trend.reduce((a, t) => a + t.present, 0);
      $id('monthTable').innerHTML = `<table><tbody><tr><td>Check-ins (30d)</td><td><b>${month}</b></td></tr><tr><td>Active days</td><td><b>${s.trend.filter((t) => t.present > 0).length}</b></td></tr></tbody></table>`;
      anaFirst = false;
    } catch (e) { toast(e.message, 'err') }
  }
  $id('btnAnaRefresh').onclick = (e) => { busy(e.target, loadAnalytics)(); };

  // ---- devices ----
  async function loadDevices() {
    try {
      const r = await API.get('/api/v1/devices');
      $id('devsTable').querySelector('tbody').innerHTML = r.items.map((d) =>
        `<tr><td>${esc(d.device_name)}</td><td>${esc(d.location_name)}</td><td>${d.status}</td><td>${esc(d.firmware_version || '—')}</td><td>${d.sensor_capacity ?? '—'}</td><td>${esc(d.last_seen_at_utc || 'never')}</td></tr>`).join('')
        || '<tr><td colspan="6"><div class="empty">No devices provisioned.</div></td></tr>';
      $id('bleLinkInfo').innerHTML = `<dt>BLE</dt><dd>${window.BLE && window.BLE.connected ? 'connected' : 'disconnected'}</dd>`;
    } catch (e) { toast(e.message, 'err') }
  }
  $id('btnDevsRefresh').onclick = (e) => { busy(e.target, loadDevices)(); };
  $id('btnBle2').onclick = () => { goto('dev'); $id('btnBle').click(); };

  // ---- big overlay ----
  let overlayTimer = null;
  function showOverlay(rec, kind) {
    const ov = $id('overlay');
    const name = `${rec.first_name || ''} ${rec.last_name || ''}`.trim() || 'Unknown fingerprint';
    $id('ovName').textContent = name;
    $id('ovClass').textContent = (rec.department || rec.grade_class) ? `Department ${rec.department || rec.grade_class}${rec.team || rec.section || ''}` : `Slot ${rec.fingerprint_slot_id ?? '—'}`;
    const dup = rec.outcome === 'DUPLICATE_SUPPRESSED' || kind === 'duplicate';
    $id('ovKicker').textContent = kind === 'nomatch' ? 'NO MATCH' : kind === 'error' ? 'SENSOR' : 'ATTENDANCE';
    $id('ovCheck').textContent = kind === 'nomatch' ? '?' : dup ? '⧗' : '✓';
    $id('ovStatus').textContent = kind === 'nomatch' ? 'NOT ENROLLED' : dup ? 'ALREADY RECORDED' : 'PRESENT';
    $id('ovStatus').className = 'ov-status ' + (kind === 'nomatch' || kind === 'error' ? 'bad' : dup ? 'warn' : 'ok');
    const ts = rec.captured_at_utc || rec.captured_at || '';
    $id('ovTime').textContent = ts ? ts.slice(0, 10) + '  ' + ts.slice(11, 16) + ' UTC' : new Date().toLocaleString();
    $id('ovFp').textContent = `Fingerprint #${rec.fingerprint_slot_id ?? '—'}` + (rec.confidence != null ? ` · confidence ${rec.confidence}` : '');
    ov.hidden = false;
    ov.classList.remove('show');
    void ov.offsetWidth;
    ov.classList.add('show');
    clearTimeout(overlayTimer);
    overlayTimer = setTimeout(() => { ov.classList.remove('show'); setTimeout(() => { ov.hidden = true; }, 300); }, 6000);
  }
  window.showOverlay = showOverlay;
  $id('overlay').addEventListener('click', () => { clearTimeout(overlayTimer); $id('overlay').classList.remove('show'); $id('overlay').hidden = true; });

  // ---- hero scan ----
  $id('btnHeroScan').onclick = async (e) => {
    if (!window.BLE || !window.BLE.connected) {
      toast('Connect BLE first (Devices page)', 'warn');
      goto('dev');
      return;
    }
    e.target.classList.add('btn-busy');
  window.ScanUI = {
    set(stage, sub = '') {
      const svg = fpSvg;
      svg.classList.remove('scanning', 'done', 'fail');
      scanStage.textContent = stage;
      scanSub.textContent = sub;
      if (stage === 'SCANNING' || stage === 'PROCESSING') svg.classList.add('scanning');
      if (stage === 'MATCH FOUND' || stage === 'ENROLLED') svg.classList.add('done');
      if (stage === 'NO MATCH' || stage === 'FAILED') svg.classList.add('fail');
    },
  };

    ScanUI.set('SCANNING', 'Place your finger on the sensor…');
    try {
      const r = await window.BLE.send('FINGERPRINT_SEARCH', {}, 30000);
      if (r.code === 'match') {
        showOverlay({ ...r, first_name: '', last_name: '' }, 'match');
        const eventUuid = (crypto.randomUUID ? crypto.randomUUID() : null) || ('scan-' + Date.now() + '-' + r.slot);
        try {
          const a = await API.post('/api/v1/assisted-checkin', { fingerprint_slot_id: r.slot, event_uuid: eventUuid });
          showOverlay({ ...a, confidence: r.confidence }, a.outcome === 'RECORDED' ? 'match' : 'duplicate');
          loadDash();
        } catch (err) {
          if (/backend unreachable|timed out|Failed to fetch|NetworkError/i.test(err.message || '')) {
            // Genuine offline path: durable local queue, sync later. No fake success.
            const queued = await Offline.enqueueCheckin({ fingerprint_slot_id: r.slot, clock_uncertain: true });
            showOverlay({ fingerprint_slot_id: r.slot, captured_at_utc: queued.captured_at_utc }, 'match');
            toast(`Offline — check-in queued (#${queued.client_seq}, will sync)`, 'warn');
          } else { toast('Check-in: ' + err.message, 'err'); }
        }
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
    $id('scanReady').textContent = ok ? 'READY FOR SCAN' : 'not connected';
    $id('scanReady').style.color = ok ? 'var(--ok)' : 'var(--muted)';
  }, 2000);

  // ---- attendance ----
  let attPage = 0; const attLimit = 25;
  function attParams() {
    const p = new URLSearchParams({ limit: attLimit, offset: attPage * attLimit, sort: $id('fSort').value });
    const v = (id) => $id(id).value.trim();
    if (v('fQ')) p.set('q', v('fQ'));
    if (v('fDay')) p.set('day', v('fDay'));
    if (v('fFrom')) p.set('date_from', v('fFrom'));
    if (v('fTo')) p.set('date_to', v('fTo'));
    if (v('fTFrom')) p.set('time_from', v('fTFrom'));
    if (v('fTTo')) p.set('time_to', v('fTTo'));
    if (v('fClass')) p.set('department', v('fClass'));
    if (v('fSection')) p.set('team', v('fSection'));
    if (v('fSlot')) p.set('slot', v('fSlot'));
    if (v('fOutcome')) p.set('outcome', v('fOutcome'));
    return p;
  }
  async function loadAtt() {
    const tb = $id('attTable').querySelector('tbody');
    tb.classList.add('fading');
    try {
      const r = await API.get('/api/v1/attendance?' + attParams());
      $id('attErr').innerHTML = '';
      const queued = await Offline.listQueue().catch(() => []);
      const pendingNote = queued.length ? ` · ${queued.length} queued offline` : '';
      $id('attMeta').textContent = `${r.total} record(s)${pendingNote}`;
      const queuedRows = (attPage === 0 ? queued.slice(-5).reverse().map((x) =>
        `<tr class="fresh"><td>${esc((x.captured_at_utc || '').slice(0, 10))}</td><td>${esc((x.captured_at_utc || '').slice(11, 16))}</td><td>${esc((x.employee && x.employee.name) || '—')}</td><td>${esc((x.employee && x.employee.employee_code) || '—')}</td><td>${esc((x.employee && x.employee.department) || '—')}</td><td></td><td>${x.fingerprint_slot_id}</td><td>QUEUED_OFFLINE</td></tr>`).join('') : '');
      tb.innerHTML = queuedRows + r.items.map((x, i) =>
        `<tr class="${i === 0 && attPage === 0 && !queuedRows ? 'fresh' : ''}"><td>${esc(x.captured_at_utc.slice(0, 10))}</td><td>${esc(x.captured_at_utc.slice(11, 16))}</td><td>${esc(empName(x))}</td><td>${esc(empCode(x))}</td><td>${esc(empDept(x))}</td><td>${esc(empTeam(x))}</td><td>${x.fingerprint_slot_id}</td><td>${x.outcome}</td></tr>`).join('')
        || (queuedRows || '<tr><td colspan="8"><div class="empty"><span class="glyph">∅</span>No records match these filters.</div></td></tr>');
      $id('pgInfo').textContent = `Page ${attPage + 1} of ${Math.max(1, Math.ceil(r.total / attLimit))}`;
    } catch (e) {
      // Offline: show the durable queue so operators see what will sync.
      try {
        const queued = await Offline.listQueue();
        $id('attErr').innerHTML = `<div class="errorbox">Attendance offline — showing ${queued.length} queued event(s). ${esc(e.message)}</div>`;
        tb.innerHTML = queued.length ? queued.slice().reverse().map((x) =>
          `<tr><td>${esc((x.captured_at_utc || '').slice(0, 10))}</td><td>${esc((x.captured_at_utc || '').slice(11, 16))}</td><td>${esc((x.employee && x.employee.name) || '—')}</td><td>${esc((x.employee && x.employee.employee_code) || '—')}</td><td>${esc((x.employee && x.employee.department) || '—')}</td><td></td><td>${x.fingerprint_slot_id}</td><td>QUEUED_OFFLINE</td></tr>`).join('')
          : '<tr><td colspan="8"><div class="empty"><span class="glyph">∅</span>No queued events.</div></td></tr>';
        $id('attMeta').textContent = `${queued.length} queued offline`;
      } catch (err) { $id('attErr').innerHTML = `<div class="errorbox">Attendance unavailable: ${esc(e.message)}</div>`; }
    }
    requestAnimationFrame(() => tb.classList.remove('fading'));
  }
  $id('flt').onsubmit = (e) => { e.preventDefault(); attPage = 0; loadAtt(); };
  let deb = null;
  $id('fQ').oninput = () => { clearTimeout(deb); deb = setTimeout(() => { attPage = 0; loadAtt(); }, 350); };
  $id('pgPrev').onclick = () => { if (attPage > 0) { attPage--; loadAtt(); } };
  $id('pgNext').onclick = () => { attPage++; loadAtt(); };
  $id('btnCsv').onclick = (e) => busy(e.target, () => API.download('/api/v1/export.csv?' + attParams(), 'attendance.csv').then(() => toast('Export complete', 'ok')).catch((err) => toast(err.message, 'err')))();
  $id('btnXlsx').onclick = (e) => busy(e.target, () => API.download('/api/v1/export.xlsx?' + attParams(), 'attendance.xlsx').then(() => toast('Export complete', 'ok')).catch((err) => toast(err.message, 'err')))();

  // ---- employees ----
  let editing = null;
  const empId = (s) => s.employee_uuid || s.student_uuid;
  async function loadStu() {
    try {
      const devs = await API.get('/api/v1/devices');
      if (!devs.items.length) {
        toast('No active device: provision one first — see Help → Setup step 5', 'warn');
      }
    } catch (e) {}
    try {
      const p = new URLSearchParams({ limit: 100, offset: 0 });
      if ($id('sQ').value.trim()) p.set('q', $id('sQ').value.trim());
      if ($id('sClass').value.trim()) p.set('department', $id('sClass').value.trim());
      if ($id('sStatus').value) p.set('status', $id('sStatus').value);
      const r = await API.get('/api/v1/students?' + p);
      try { await Offline.saveEmployees(r.items); } catch (e) {}
      $id('stuTable').querySelector('tbody').innerHTML = r.items.map((s) =>
        `<tr><td>${esc(s.first_name)} ${esc(s.last_name)}</td><td>${esc(s.employee_code || s.roll_number)}</td><td>${esc(s.department || s.grade_class)}</td><td>${esc(s.team ?? s.section)}</td><td>${s.status}</td><td>${s.fingerprint_slot_id ?? '—'}</td><td><button data-act="view" data-id="${empId(s)}">Open</button></td></tr>`).join('')
        || '<tr><td colspan="7"><div class="empty"><span class="glyph">○</span>No employees found. Add one to begin enrollment.</div></td></tr>';
      $id('stuTable').querySelectorAll('button').forEach((b) => { b.onclick = () => openStudent(b.dataset.id); });
    } catch (e) {
      try {
        const { employees, cached_at_utc } = await Offline.cachedEmployees();
        const q = $id('sQ').value.trim().toLowerCase();
        const rows = employees.filter((x) => !q || x.name.toLowerCase().includes(q) || (x.employee_code || '').toLowerCase().includes(q));
        $id('stuTable').querySelector('tbody').innerHTML = rows.map((s) =>
          `<tr><td>${esc(s.name)}</td><td>${esc(s.employee_code)}</td><td>${esc(s.department)}</td><td>${esc(s.team)}</td><td>cached</td><td>${s.fingerprint_slot_id ?? '—'}</td><td></td></tr>`).join('')
          || '<tr><td colspan="7"><div class="empty"><span class="glyph">○</span>Offline — no cached directory yet.</div></td></tr>';
        toast(`Employees offline — cached directory${cached_at_utc ? ' from ' + cached_at_utc.slice(0, 16) : ''}`, 'warn');
      } catch (err) { toast(e.message, 'err'); }
    }
  }
  $id('stuFlt').onsubmit = (e) => { e.preventDefault(); loadStu(); };
  $id('btnStuNew').onclick = () => { editing = null; $id('stuDlgTitle').textContent = 'Add employee'; $id('stuForm').reset(); $id('stuDlg').showModal(); };
  $id('stuCancel').onclick = () => $id('stuDlg').close();
  $id('stuForm').onsubmit = async (e) => {
    const body = { employee_code: $id('stuRoll').value.trim(), first_name: $id('stuFirst').value.trim(), last_name: $id('stuLast').value.trim(), department: $id('stuClass').value.trim(), team: $id('stuSection').value.trim() };
    try {
      if (editing) { await API.patch('/api/v1/students/' + editing, body); }
      else { await API.post('/api/v1/students', body); }
      $id('stuDlg').close(); loadStu(); toast('Saved', 'ok');
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
      const code = s.employee_code || s.roll_number, dept = s.department || s.grade_class, team = s.team ?? s.section;
      const d = $id('stuDetail'); d.hidden = false;
      $id('stuDetailName').textContent = `${s.first_name} ${s.last_name} (${code} · ${dept}${team} · ${s.status})`;
      const act0 = $id('btnStuActivate'); if (act0) act0.hidden = s.status !== 'PENDING_ENROLLMENT';
      d.innerHTML = `<h2>${esc(s.first_name)} ${esc(s.last_name)} <span style="color:var(--muted)">(${esc(code)} · ${esc(dept)}${esc(team)} · ${s.status})</span></h2>
        <div class="progress"><i style="width:${s.attendance_percentage}%"></i></div>
        <p>30-day attendance: <b>${s.attendance_percentage}%</b> · days present: ${s.days_present}/${s.window_days} · first: ${s.first || '—'} · last: ${s.last || '—'}</p>
        <div class="row"><button id="btnStuEdit">Edit</button>${s.status === 'PENDING_ENROLLMENT' ? '<button id="btnStuActivate">Mark enrolled</button>' : ''}<button id="btnStuDeact">Deactivate</button><button id="btnStuDel">Delete</button></div>`;
      $id('btnStuEdit').onclick = () => { editing = id; $id('stuDlgTitle').textContent = 'Edit employee'; $id('stuRoll').value = code; $id('stuFirst').value = s.first_name; $id('stuLast').value = s.last_name; $id('stuClass').value = dept; $id('stuSection').value = team; $id('stuDlg').showModal(); };
      $id('btnStuDeact').onclick = async () => { if (confirm('Deactivate this employee?')) { await API.post(`/api/v1/students/${id}/deactivate`); toast('Deactivated', 'ok'); loadStu(); d.hidden = true; } };
      $id('btnStuDel').onclick = async () => {
        if (!confirm(`Permanently DELETE ${s.first_name} ${s.last_name}? Their attendance rows stay but lose the name link.`)) return;
        try {
          const r = await API.del(`/api/v1/students/${id}`);
          toast(`Deleted (${r.orphaned_attendance_records} orphaned record(s))`, 'ok');
          loadStu(); d.hidden = true;
        } catch (err) { toast(err.message, 'err') }
      };
      const act = $id('btnStuActivate');
      if (act) act.onclick = async () => {
        if (!confirm(`Confirm the finger template is stored in slot ${s.fingerprint_slot_id}, then activate?`)) return;
        try { await API.post(`/api/v1/students/${id}/activate`); toast('Employee activated', 'ok'); loadStu(); openStudent(id); }
        catch (err) { toast(err.message, 'err') };
      };
      d.scrollIntoView({ block: 'nearest' });
    } catch (e) { toast(e.message, 'err') };
  }

  // ---- AI assistant (was dead UI: form had no handler — now wired) ----
  const AI_SUGGESTIONS = ['Who is absent today?', 'What is attendance for department Engineering?',
    'Show the 7-day trend summary', 'Who has low attendance this month?'];
  function aiMsg(role, text) {
    const log = $id('aiLog');
    const div = document.createElement('div');
    div.className = 'msg ' + role;
    div.textContent = text;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
  }
  async function aiAsk(question) {
    const q = (question || '').trim();
    if (!q) return;
    aiMsg('you', q);
    $id('aiQ').value = '';
    try {
      const r = await API.post('/api/v1/ai/chat', { question: q });
      aiMsg('bot', (r.ai_available ? '' : '[local data] ') + r.answer);
    } catch (e) { aiMsg('bot', 'Assistant unavailable: ' + e.message); }
  }
  $id('aiForm').onsubmit = (e) => { e.preventDefault(); aiAsk($id('aiQ').value); };
  $id('aiChips').innerHTML = AI_SUGGESTIONS.map((s) => `<button type="button">${esc(s)}</button>`).join('');
  $id('aiChips').querySelectorAll('button').forEach((b) => { b.onclick = () => aiAsk(b.textContent); });
  (async () => {
    try {
      const s = await API.get('/api/v1/settings/ai', true);
      $id('keyState').textContent = s.gemini_configured ? 'key configured' : 'no key — local answers only';
      if (!s.gemini_configured) $id('aiNote').hidden = false, $id('aiNote').textContent = 'No Gemini key configured — answers come from local data.';
    } catch (e) {}
  })();
  $id('btnKeySave').onclick = async () => {
    const key = $id('aiKey').value.trim();
    try {
      const r = await API.put('/api/v1/settings/ai', { gemini_api_key: key });
      $id('keyState').textContent = r.gemini_configured ? 'key saved' : 'key cleared';
      $id('aiKey').value = '';
      $id('aiNote').hidden = r.gemini_configured;
      toast(r.gemini_configured ? 'AI key saved (server-side only)' : 'AI key cleared', 'ok');
    } catch (e) { toast(e.message, 'err'); }
  };

  // ---- command palette (was dead UI: Ctrl+K hint with no implementation) ----
  const COMMANDS = [
    ['Go: Home', () => goto('dash')], ['Go: Attendance', () => goto('att')],
    ['Go: Employees', () => goto('stu')], ['Go: Analytics', () => goto('ana')],
    ['Go: Devices', () => goto('devs')], ['Go: Fingerprints', () => goto('dev')],
    ['Go: AI Assistant', () => goto('ai')], ['Go: Help', () => goto('help')],
    ['Refresh dashboard', () => loadDash()], ['Sync now', () => window.SyncEngine && SyncEngine.syncNow()],
    ['Toggle dark mode', () => $id('btnTheme').click()],
  ];
  function closePal() { $id('palette').classList.remove('open'); }
  function openPal() {
    $id('palette').classList.add('open');
    $id('palInput').value = '';
    renderPal('');
    setTimeout(() => $id('palInput').focus(), 30);
  }
  function renderPal(filter) {
    const q = filter.trim().toLowerCase();
    const list = COMMANDS.filter(([name]) => !q || name.toLowerCase().includes(q));
    $id('palList').innerHTML = list.map(([name], i) => `<li data-i="${COMMANDS.indexOf(list[i])}" class="${i === 0 ? 'sel' : ''}">${esc(name)}</li>`).join('')
      || '<li>(no matching command)</li>';
    $id('palList').querySelectorAll('li[data-i]').forEach((li) => {
      li.onclick = () => { closePal(); COMMANDS[parseInt(li.dataset.i, 10)][1](); };
    });
  }
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); $id('palette').classList.contains('open') ? closePal() : openPal(); }
    if (e.key === 'Escape') closePal();
  });
  $id('palInput').oninput = (e) => renderPal(e.target.value);
  $id('palette').addEventListener('click', (e) => { if (e.target === $id('palette')) closePal(); });

  // ---- offline sync UI ----
  function renderSync(s) {
    const label = s.state === 'syncing' ? 'Sync: syncing…'
      : s.state === 'offline' ? `Sync: offline (${s.pending} pending)`
      : s.pending ? `Sync: online (${s.pending} pending)` : 'Sync: up to date';
    $id('syncTxt').textContent = label;
    $id('syncDot').className = 'dot ' + (s.state === 'offline' ? 'bad' : s.pending ? 'warn' : 'ok');
    const banner = $id('syncBanner');
    const degraded = s.state === 'offline' || s.state === 'syncing' || s.pending > 0 || s.failed > 0;
    banner.hidden = !degraded;
    banner.classList.toggle('ok', s.state !== 'offline' && s.failed === 0 && s.state !== 'syncing');
    $id('syncBannerDot').className = 'dot ' + (s.state === 'offline' ? 'bad' : s.state === 'syncing' ? 'warn' : 'ok');
    $id('syncBannerTxt').textContent = s.state === 'offline'
      ? 'Offline — check-ins are queued locally and will sync on reconnect.'
      : s.state === 'syncing' ? 'Syncing queued check-ins…' : 'Back online — queue draining.';
    $id('syncCounts').textContent = `pending ${s.pending} · failed ${s.failed}${s.lastSync ? ' · last sync ' + String(s.lastSync).slice(11, 16) : ''} · ${s.storage || ''}`;
    $id('btnSyncRetry').hidden = s.failed === 0;
    const panel = $id('syncPanel');
    if (panel) panel.innerHTML = `<dt>State</dt><dd>${esc(s.state)}</dd><dt>Pending</dt><dd>${s.pending}</dd><dt>Failed</dt><dd>${s.failed}</dd><dt>Last sync</dt><dd>${esc(s.lastSync || 'never')}</dd><dt>Storage</dt><dd>${esc(s.storage || '?')}</dd>`;
    const retry2 = $id('btnSyncRetry2'); if (retry2) retry2.hidden = s.failed === 0;
  }
  async function bootOffline() {
    try { await Offline.init(); } catch (e) {}
    if (window.SyncEngine) {
      SyncEngine.onStatus(renderSync);
      SyncEngine.start();
    }
    const go = () => { if (window.SyncEngine) SyncEngine.syncNow().catch(() => {}); };
    $id('btnSyncNow').onclick = go;
    const b2 = $id('btnSyncNow2'); if (b2) b2.onclick = go;
    const retry = async () => { await Offline.resetFailed().catch(() => {}); go(); };
    $id('btnSyncRetry').onclick = retry;
    const r2 = $id('btnSyncRetry2'); if (r2) r2.onclick = retry;
    // Company name in the brand bar (best effort, cached default otherwise).
    try {
      const c = await API.get('/api/v1/settings/company', true);
      if (c && c.company_name) $id('brandName').textContent = c.company_name + ' Attendance';
    } catch (e) {}
    if (document.hidden === false && $id('view-dash').classList.contains('on')) loadDash();
  }
  bootOffline();
})();
