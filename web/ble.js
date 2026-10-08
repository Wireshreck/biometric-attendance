/* BLE device tab. Same shared protocol as every client
 * (window.BLE_PROTOCOL). Raw GATT write/read; no invented commands.
 * Scan state machine (IDLE → SCANNING → PROCESSING → MATCH/NO MATCH)
 * is rendered through window.ScanUI with staged transitions. */
(() => {
  const P = window.BLE_PROTOCOL;
  const enc = new TextEncoder(), dec = new TextDecoder();
  const ble = { device: null, server: null, chars: {} };
  const $ = (id) => document.getElementById(id);
  const num = (name) => parseInt(P.BLE_CHARS[name], 16);

  function setState(on, name = '') {
    $('bleTxt').textContent = on ? `BLE: connected${name ? ' · ' + name : ''}` : 'BLE: disconnected';
    $('bleDot').className = 'dot' + (on ? ' ok' : '');
  }
  function say(el, v) { el.textContent = typeof v === 'string' ? v : JSON.stringify(v, null, 1); }

  async function send(cmd, params = {}, timeoutMs = 20000) {
    if (!ble.server) throw new Error('BLE not connected');
    const charName = P.CHAR_FOR_COMMAND[cmd];
    const ch = ble.chars[charName];
    if (!ch) throw new Error(`characteristic ${charName} unavailable`);
    await ch.writeValue(enc.encode(P.buildRequest(cmd, params)));
    // The device stages the request and publishes the response from its
    // loop task; a busy envelope means "not ready yet".
    const t0 = performance.now();
    await new Promise((r) => setTimeout(r, 400));
    for (;;) {
      try {
        const v = P.parseResponse(dec.decode(await ch.readValue()));
        if (v.status !== 'busy' || performance.now() - t0 > timeoutMs) return v;
      } catch (e) {
        if (performance.now() - t0 > timeoutMs) throw e;
      }
      await new Promise((r) => setTimeout(r, 500));
    }
  }

  async function connect() {
    if (!navigator.bluetooth) throw new Error('Web Bluetooth unsupported — use Chrome/Edge');
    setState(false); $('bleTxt').textContent = 'BLE: connecting…';
    $('bleDot').className = 'dot warn';
    ble.device = await navigator.bluetooth.requestDevice({
      filters: [{ services: [P.BLE_SERVICE_UUID] }], optionalServices: [P.BLE_SERVICE_UUID],
    });
    ble.device.addEventListener('gattserverdisconnected', () => { ble.server = null; ble.chars = {}; setState(false); });
    ble.server = await ble.device.gatt.connect();
    const svc = await ble.server.getPrimaryService(P.BLE_SERVICE_UUID);
    for (const name of Object.keys(P.BLE_CHARS)) {
      try { ble.chars[name] = await svc.getCharacteristic(num(name)); } catch (e) {}
    }
    setState(true, ble.device.name || '');
  }

  window.BLE = {
    send, connect,
    disconnect() { try { ble.device?.gatt?.disconnect(); } catch (e) {} ble.server = null; setState(false); },
    get connected() { return !!ble.server; },
  };

  const kv = (obj) => Object.entries(obj).map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join('');
  $('btnBle').onclick = async () => { try { await connect(); toast('Device connected', 'ok'); } catch (e) { setState(false); toast('BLE: ' + e.message, 'err'); } };
  $('btnBleOff').onclick = () => { window.BLE.disconnect(); toast('Disconnected'); };
  $('btnDevRefresh').onclick = async (e) => {
    e.target.classList.add('btn-busy');
    try {
      const info = await send('DEVICE_INFO'), st = await send('DEVICE_STATUS');
      $('devInfo').innerHTML = kv({ ...info.data, ...st.data });
    } catch (err) { toast('Device: ' + err.message, 'err'); }
    finally { e.target.classList.remove('btn-busy'); }
  };
  $('btnDiag').onclick = async (e) => {
    const btn = e.target;
    btn.classList.add('btn-busy');
    ScanUI.set('PROCESSING', 'Running system checks…');
    $('diagProg').hidden = false;
    const bar = $('diagProg').querySelector('i');
    bar.style.width = '5%';
    try {
      const r = await send('FULL_DIAGNOSTIC');
      const results = r.data.results;
      $('diagOut').innerHTML = '';
      results.forEach((t, i) => {
        setTimeout(() => {
          bar.style.width = Math.round(((i + 1) / results.length) * 100) + '%';
          const cls = t.result === 'PASS' ? 'pass' : t.result === 'FAIL' ? 'fail' : t.result === 'WARN' ? 'warn' : 'skip';
          const div = document.createElement('div');
          div.className = 'dtest';
          div.innerHTML = `<span style="min-width:130px">${t.test}</span><span class="badge ${cls}">${t.result}</span><span style="color:var(--muted)">${t.reason || ''}</span>`;
          $('diagOut').appendChild(div);
          if (i === results.length - 1) {
            const fails = results.filter((x) => x.result === 'FAIL').length;
            ScanUI.set(fails ? 'FAILED' : 'IDLE', fails ? `${fails} check(s) failing` : 'All checks complete.');
            toast(fails ? `${fails} diagnostic failure(s)` : 'Diagnostics complete', fails ? 'err' : 'ok');
            setTimeout(() => { $('diagProg').hidden = true; }, 600);
          }
        }, 120 * i);
      });
    } catch (err) { ScanUI.set('FAILED', err.message); toast('Diagnostic: ' + err.message, 'err'); $('diagProg').hidden = true; }
    finally { btn.classList.remove('btn-busy'); }
  };
  $('btnBuzz').onclick = async () => { try { say($('diagOut'), await send('BUZZER_TEST')); toast('Buzzer test sent', 'ok'); } catch (e) { toast(e.message, 'err'); } };
  $('btnFpCount').onclick = async () => { try { say($('fpMsg'), await send('FINGERPRINT_COUNT')); } catch (e) { say($('fpMsg'), e.message); } };
  $('btnEnroll').onclick = async (e) => {
    const slot = parseInt($('fpSlot').value, 10);
    e.target.classList.add('btn-busy');
    ScanUI.set('READY', 'Place your finger on the sensor…');
    say($('fpMsg'), 'Enrolling — place finger…');
    setTimeout(() => { if ($('scanStage').textContent === 'READY') ScanUI.set('SCANNING', 'Capturing first impression…'); }, 2500);
    try {
      const r = await send('FINGERPRINT_ENROLL', { slot }, P.TIMEOUTS_MS.ENROLL);
      if (r.code === 'enroll_success') { ScanUI.set('ENROLLED', `Slot ${r.slot} stored.`); toast(`Enrolled slot ${r.slot}`, 'ok'); }
      else { ScanUI.set('FAILED', r.message || r.code); }
      say($('fpMsg'), r);
    } catch (err) { ScanUI.set('FAILED', err.message); say($('fpMsg'), 'Enroll: ' + err.message); }
    finally { e.target.classList.remove('btn-busy'); }
  };
  $('btnSearch').onclick = async (e) => {
    e.target.classList.add('btn-busy');
    ScanUI.set('SCANNING', 'Place your finger on the sensor…');
    say($('fpMsg'), 'Searching — place finger…');
    try {
      const r = await send('FINGERPRINT_SEARCH', {}, P.TIMEOUTS_MS.SEARCH);
      if (r.code === 'match') { ScanUI.set('MATCH FOUND', `Slot ${r.slot} · confidence ${r.confidence}`); toast(`Match: slot ${r.slot}`, 'ok'); }
      else if (r.code === 'no_match') ScanUI.set('NO MATCH', 'Not enrolled — try again.');
      else ScanUI.set('FAILED', r.message || r.code);
      say($('fpMsg'), r);
    } catch (err) { ScanUI.set('FAILED', err.message); say($('fpMsg'), 'Search: ' + err.message); }
    finally { e.target.classList.remove('btn-busy'); }
  };
  $('btnDel').onclick = async () => {
    try { say($('fpMsg'), await send('FINGERPRINT_DELETE', { slot: parseInt($('fpSlot').value, 10) })); toast('Delete sent', 'ok'); }
    catch (e) { say($('fpMsg'), e.message); toast(e.message, 'err'); }
  };
  $('btnRtcGet').onclick = async () => { try { say($('rtcMsg'), await send('RTC_GET')); } catch (e) { say($('rtcMsg'), e.message); } };
  $('btnRtcSet').onclick = async () => {
    const n = new Date();
    try {
      say($('rtcMsg'), await send('RTC_SET', { year: n.getFullYear(), month: n.getMonth() + 1, day: n.getDate(), hour: n.getHours(), minute: n.getMinutes(), second: n.getSeconds() }));
      toast('RTC set', 'ok');
    } catch (e) { say($('rtcMsg'), e.message); toast(e.message, 'err'); }
  };
  function toast(m) { window.toast ? window.toast(m) : null; }
})();
