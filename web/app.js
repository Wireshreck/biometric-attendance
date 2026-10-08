/* Web management app. Uses the single shared protocol (window.BLE_PROTOCOL
 * from shared/ble_protocol.js). Talks to the ESP32 BLE service documented
 * in docs/protocol.md. Never invents commands. */
(() => {
  const P = window.BLE_PROTOCOL;
  const $ = (id) => document.getElementById(id);
  const enc = new TextEncoder();
  const dec = new TextDecoder();
  let device = null, server = null, chars = {};

  const log = (el, obj) => {
    el.textContent = (typeof obj === 'string' ? obj : JSON.stringify(obj, null, 2)) + '\n' + el.textContent;
  };
  const setConn = (on, name = '') => {
    $('connState').textContent = on ? `CONNECTED${name ? ' · ' + name : ''}` : 'DISCONNECTED';
    $('connState').className = 'pill ' + (on ? 'on' : 'off');
    $('btnConnect').disabled = on;
    $('btnDisconnect').disabled = !on;
  };
  const charUuid = (short) => parseInt(short, 16);
  // Firmware exposes 16-bit characteristic UUIDs 0x1101..0x1108 under the
  // custom 128-bit service. Web Bluetooth accepts the numeric 16-bit form.
  const fullChar = (name) => parseInt(P.BLE_CHARS[name], 16);

  async function send(cmd, params = {}, timeoutMs = 20000) {
    if (!server) throw new Error('not connected');
    const body = P.buildRequest(cmd, params);
    const charName = P.CHAR_FOR_COMMAND[cmd];
    const ch = chars[charName];
    if (!ch) throw new Error(`characteristic ${charName} not discovered`);
    await ch.writeValue(enc.encode(body));
    const resp = await ch.readValue();
    return P.parseResponse(dec.decode(resp));
  }

  $('btnConnect').onclick = async () => {
    try {
      if (!navigator.bluetooth) { $('needBle').hidden = false; return; }
      device = await navigator.bluetooth.requestDevice({
        filters: [{ services: [P.BLE_SERVICE_UUID] }],
        optionalServices: [P.BLE_SERVICE_UUID],
      });
      device.addEventListener('gattserverdisconnected', () => { chars = {}; setConn(false); });
      server = await device.gatt.connect();
      const svc = await server.getPrimaryService(P.BLE_SERVICE_UUID);
      for (const name of Object.keys(P.BLE_CHARS)) {
        try { chars[name] = await svc.getCharacteristic(fullChar(name)); } catch (e) { /* missing char */ }
      }
      setConn(true, device.name || '');
      const info = await send('DEVICE_INFO');
      $('dDevice').textContent = info.data?.device ?? '—';
      $('dFw').textContent = info.data?.firmware ?? '—';
      $('dUptime').textContent = info.data?.uptime_seconds ?? '—';
      log($('dashLog'), info);
    } catch (e) { log($('dashLog'), 'CONNECT FAILED: ' + e.message); }
  };
  $('btnDisconnect').onclick = () => { try { device?.gatt?.disconnect(); } catch (e) {} chars = {}; setConn(false); };

  $('btnRefresh').onclick = async () => {
    try {
      const [info, status, att] = await Promise.all([
        send('DEVICE_INFO'), send('DEVICE_STATUS'), send('ATTENDANCE_STATUS')]);
      $('dDevice').textContent = info.data.device;
      $('dFw').textContent = info.data.firmware;
      $('dUptime').textContent = `${info.data.uptime_seconds}s`;
      $('dRtc').textContent = status.data.rtc_valid ? status.data.rtc_time : 'INVALID / LOST-POWER';
      $('dR307s').textContent = status.data.sensor_ready ? 'READY' : 'NOT CONNECTED';
      $('dCount').textContent = `${status.data.template_count}/${status.data.template_capacity}`;
      $('dStorage').textContent = status.data.storage_ok ? 'OK' : 'ERROR';
      $('dAtt').textContent = `${att.data.records} records`;
      log($('dashLog'), { info: info.data, status: status.data, attendance: att.data });
    } catch (e) { log($('dashLog'), 'REFRESH FAILED: ' + e.message); }
  };

  $('btnFpStatus').onclick = async () => { try { log($('fpLog'), await send('FINGERPRINT_STATUS')); } catch (e) { log($('fpLog'), e.message); } };
  $('btnFpCount').onclick = async () => { try { log($('fpLog'), await send('FINGERPRINT_COUNT')); } catch (e) { log($('fpLog'), e.message); } };
  $('btnEnroll').onclick = async () => {
    const slot = parseInt($('fpSlot').value, 10);
    $('enrollState').textContent = 'ENROLL PLACE FINGER'; $('enrollState').className = 'pill busy';
    try { const r = await send('FINGERPRINT_ENROLL', { slot }, P.TIMEOUTS_MS.ENROLL); log($('fpLog'), r); $('enrollState').textContent = 'ENROLL SUCCESS'; $('enrollState').className = 'pill ok'; }
    catch (e) { log($('fpLog'), 'ENROLL FAILED: ' + e.message); $('enrollState').textContent = 'ENROLL FAILED'; $('enrollState').className = 'pill err'; }
  };
  $('btnSearch').onclick = async () => { try { log($('fpLog'), await send('FINGERPRINT_SEARCH', {}, P.TIMEOUTS_MS.SEARCH)); } catch (e) { log($('fpLog'), e.message); } };
  $('btnDelete').onclick = async () => { try { log($('fpLog'), await send('FINGERPRINT_DELETE', { slot: parseInt($('fpSlot').value, 10) })); } catch (e) { log($('fpLog'), e.message); } };
  $('btnDeleteAll').onclick = async () => {
    if (!confirm('Delete ALL fingerprint templates?')) return;
    try { log($('fpLog'), await send('FINGERPRINT_DELETE_ALL')); } catch (e) { log($('fpLog'), e.message); }
  };

  $('btnRtcGet').onclick = async () => {
    try {
      const r = await send('RTC_GET'); log($('rtcLog'), r);
      $('rtcWarn').hidden = !!(r.data && r.data.valid && !r.data.lost_power);
    } catch (e) { log($('rtcLog'), e.message); }
  };
  $('btnRtcSetLocal').onclick = async () => {
    try {
      const n = new Date();
      const r = await send('RTC_SET', { year: n.getFullYear(), month: n.getMonth() + 1, day: n.getDate(), hour: n.getHours(), minute: n.getMinutes(), second: n.getSeconds() });
      log($('rtcLog'), r);
    } catch (e) { log($('rtcLog'), e.message); }
  };

  $('btnAttStatus').onclick = async () => { try { log($('attLog'), await send('ATTENDANCE_STATUS')); } catch (e) { log($('attLog'), e.message); } };
  $('btnAttRead').onclick = async () => {
    try {
      const r = await send('ATTENDANCE_READ');
      const tb = $('attTable').querySelector('tbody'); tb.innerHTML = '';
      for (const rec of (r.data?.records ?? [])) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${rec.slot}</td><td>${rec.captured_at}</td><td>${rec.status}</td>`;
        tb.appendChild(tr);
      }
      log($('attLog'), r);
    } catch (e) { log($('attLog'), e.message); }
  };
  $('btnAttClear').onclick = async () => {
    if (!confirm('Clear all attendance records on the device?')) return;
    try { log($('attLog'), await send('ATTENDANCE_CLEAR')); } catch (e) { log($('attLog'), e.message); }
  };

  $('btnDiag').onclick = async () => {
    try {
      const r = await send('FULL_DIAGNOSTIC');
      const tb = $('diagTable').querySelector('tbody'); tb.innerHTML = '';
      for (const t of (r.data?.results ?? [])) {
        const tr = document.createElement('tr');
        const cls = t.result === 'PASS' ? 'pass' : t.result === 'FAIL' ? 'fail' : t.result === 'WARN' ? 'warnr' : 'skip';
        tr.innerHTML = `<td>${t.test}</td><td class="${cls}">${t.result}</td><td>${t.reason ?? ''}</td>`;
        tb.appendChild(tr);
      }
      log($('diagLog'), r);
    } catch (e) { log($('diagLog'), e.message); }
  };
  $('btnBuzz').onclick = async () => { try { log($('diagLog'), await send('BUZZER_TEST')); } catch (e) { log($('diagLog'), e.message); } };
  $('btnPing').onclick = async () => { try { log($('diagLog'), await send('PING')); } catch (e) { log($('diagLog'), e.message); } };

  if (!navigator.bluetooth) $('needBle').hidden = false;
})();
