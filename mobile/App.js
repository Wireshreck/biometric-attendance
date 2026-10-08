import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Button, ScrollView, StyleSheet, Text, TextInput, View, Alert } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { client } from './bleClient';
import { TIMEOUTS_MS } from '../shared/ble_protocol.js';

const STORE_KEY = 'biometric-attendance-settings-v1';

function normalizeUrl(raw) {
  const t = (raw || '').trim().replace(/\/+$/, '');
  if (!/^https?:\/\/[^/]+/.test(t)) throw new Error('Use http(s)://host[:port], e.g. http://192.168.1.100:8000');
  return t;
}

async function loadSettings() {
  try {
    const raw = await AsyncStorage.getItem(STORE_KEY);
    if (raw) return JSON.parse(raw);
  } catch (e) {}
  return { host: '', user: '', pass: '', done: false };
}

function useApi(cfg) {
  const headers = () => ({
    Authorization: 'Basic ' + btoa(`${cfg.user}:${cfg.pass}`),
    'Content-Type': 'application/json',
  });
  const get = async (p, opts = {}) => {
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), opts.timeout || 12000);
    try {
      const r = await fetch(cfg.host + p, { headers: headers(), signal: ctl.signal });
      if (r.status === 401) throw new Error('Sign-in rejected — check admin user/password in Settings.');
      if (!r.ok) throw new Error(`Server error ${r.status}`);
      return r.json();
    } catch (e) {
      if (e.name === 'AbortError') throw new Error(`Timed out reaching ${cfg.host}.`);
      if (/Network request failed/i.test(e.message)) {
        throw new Error(`Cannot reach ${cfg.host}. Same Wi-Fi? Server running?`);
      }
      throw e;
    } finally { clearTimeout(timer); }
  };
  const post = async (p, body) => {
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), 15000);
    try {
      const r = await fetch(cfg.host + p, { method: 'POST', headers: headers(), body: JSON.stringify(body || {}), signal: ctl.signal });
      if (r.status === 401) throw new Error('Sign-in rejected — check admin user/password in Settings.');
      if (!r.ok) throw new Error(`Server error ${r.status}`);
      return r.json();
    } catch (e) {
      if (e.name === 'AbortError') throw new Error(`Timed out reaching ${cfg.host}.`);
      throw e;
    } finally { clearTimeout(timer); }
  };
  const put = async (p, body) => {
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), 15000);
    try {
      const r = await fetch(cfg.host + p, { method: 'PUT', headers: headers(), body: JSON.stringify(body || {}), signal: ctl.signal });
      if (r.status === 401) throw new Error('Sign-in rejected — check admin user/password in Settings.');
      if (!r.ok) {
        let detail = `Server error ${r.status}`;
        try { detail = (await r.json()).error?.message || detail; } catch (e) {}
        throw new Error(detail);
      }
      return r.json();
    } catch (e) {
      if (e.name === 'AbortError') throw new Error(`Timed out reaching ${cfg.host}.`);
      throw e;
    } finally { clearTimeout(timer); }
  };
  return { get, post, put };
}

function Section({ title, children }) {
  return <View style={styles.sec}><Text style={styles.h2}>{title}</Text>{children}</View>;
}

function Setup({ initial, onDone }) {
  const [host, setHost] = useState(initial.host || '');
  const [user, setUser] = useState(initial.user || '');
  const [pass, setPass] = useState('');
  const [state, setState] = useState({ phase: 'idle', msg: '' });
  const test = async () => {
    setState({ phase: 'busy', msg: 'Contacting server…' });
    try {
      const base = normalizeUrl(host);
      const ctl = new AbortController();
      const timer = setTimeout(() => ctl.abort(), 10000);
      const r = await fetch(base + '/health', { signal: ctl.signal });
      clearTimeout(timer);
      if (!r.ok) throw new Error(`Server replied ${r.status}`);
      const h = await r.json();
      setState({ phase: 'ok', msg: `Connected — schema v${h.schema_version}.`, base });
    } catch (e) {
      setState({ phase: 'fail', msg: e.name === 'AbortError' ? 'Timed out. Same Wi-Fi? Correct IP/port?' : String(e.message || e) });
    }
  };
  const cont = async () => {
    const base = state.base || normalizeUrl(host);
    await AsyncStorage.setItem(STORE_KEY, JSON.stringify({ host: base, user, pass, done: true }));
    onDone({ host: base, user, pass, done: true });
  };
  return (
    <View style={styles.setup}>
      <Text style={styles.h1}>Biometric Attendance</Text>
      <Text>Connect to your self-hosted server. Nothing is hardcoded — the backend runs on your own machine.</Text>
      <Text>Server URL</Text>
      <TextInput style={styles.input} value={host} onChangeText={setHost} placeholder="http://192.168.1.100:8000" autoCapitalize="none" />
      <Text>Admin user</Text>
      <TextInput style={styles.input} value={user} onChangeText={setUser} autoCapitalize="none" />
      <Text>Admin password</Text>
      <TextInput style={styles.input} value={pass} onChangeText={setPass} secureTextEntry />
      {state.phase === 'busy' && <ActivityIndicator />}
      {!!state.msg && <Text style={state.phase === 'fail' ? styles.err : styles.ok}>{state.msg}</Text>}
      <Button title="Test Connection" onPress={test} />
      <Button title="Continue" disabled={state.phase !== 'ok'} onPress={cont} />
    </View>
  );
}

export default function App() {
  const [cfg, setCfg] = useState(null);
  const [tab, setTab] = useState('home');
  const [user, setUser] = useState('');
  const [pass, setPass] = useState('');
  const [out, setOut] = useState(['Biometric Attendance']);
  const [busy, setBusy] = useState(false);
  const [auto, setAuto] = useState(false);
  const [keyInput, setKeyInput] = useState('');
  const [keyStatus, setKeyStatus] = useState('unknown');
  const [slot, setSlot] = useState('1');
  const [query, setQuery] = useState('');
  const [devices, setDevices] = useState([]);
  const [lastEvent, setLastEvent] = useState(null);
  const api = useApi(cfg || { host: '', user: '', pass: '' });
  const push = (o) => setOut((l) => [...l.slice(-40), typeof o === 'string' ? o : JSON.stringify(o)]);

  useEffect(() => { loadSettings().then(setCfg); }, []);
  useEffect(() => { if (cfg) { setUser(cfg.user || ''); } }, [cfg]);
  const seenRef = React.useRef('');
  const seenInit = React.useRef(false);
  useEffect(() => {
    if (!cfg || !cfg.done || tab !== 'home') return;
    let alive = true;
    const tick = async () => {
      try {
        const r = await api.get('/api/v1/attendance?limit=1&offset=0');
        const cur = r.items[0];
        if (!alive || !cur) return;
        if (!seenInit.current) { seenInit.current = true; seenRef.current = cur.event_uuid; return; }
        if (cur.event_uuid !== seenRef.current) {
          seenRef.current = cur.event_uuid;
          setLastEvent(cur);
        }
      } catch (e) {}
    };
    tick();
    const id = setInterval(tick, 5000);
    return () => { alive = false; clearInterval(id); };
  }, [tab, cfg]);
  useEffect(() => {
    if (!cfg || !cfg.done) return;
    api.get('/api/v1/settings/ai').then(
      (s) => setKeyStatus(s.gemini_configured ? 'configured ✓' : 'not set'),
      () => setKeyStatus('unknown'));
  }, [tab]);

  if (!cfg) return <View style={styles.root}><ActivityIndicator size="large" /></View>;
  if (!cfg.done) return <ScrollView style={styles.root}><Setup initial={cfg} onDone={setCfg} /><StatusBar style="auto" /></ScrollView>;

  const run = async (label, fn) => {
    setBusy(true);
    try { push(`> ${label}`); push(await fn()); }
    catch (e) { push(`${label} FAILED: ${e.message}`); }
    finally { setBusy(false); }
  };
  const autoRef = React.useRef({ on: false, busy: false });
  const startAuto = async () => {
    if (!client.connected) { push('Connect BLE first.'); return; }
    autoRef.current.on = true; setAuto(true);
    push('Auto-scan on — place any enrolled finger anytime.');
    while (autoRef.current.on) {
      if (!client.connected) { push('Auto-scan stopped (disconnected).'); break; }
      if (autoRef.current.busy) { await new Promise((r) => setTimeout(r, 2500)); continue; }
      autoRef.current.busy = true;
      try {
        const r = await client.send('FINGERPRINT_SEARCH', {}, TIMEOUTS_MS.SEARCH);
        if (r.code === 'match') {
          push(`Match slot ${r.slot} — recording…`);
          try {
            const a = await api.post('/api/v1/assisted-checkin', { fingerprint_slot_id: r.slot });
            push(`Check-in: ${a.outcome}`);
          } catch (e) { push(`Check-in FAILED: ${e.message}`); }
          await new Promise((r2) => setTimeout(r2, 4000));
        }
      } catch (e) {
        if (/not connected/i.test(e.message || '')) break;
      } finally { autoRef.current.busy = false; }
      await new Promise((r) => setTimeout(r, 2500));
    }
    autoRef.current.on = false; setAuto(false);
  };
  const stopAuto = () => { autoRef.current.on = false; setAuto(false); push('Auto-scan stopped.'); };
  const saveCreds = async () => {
    const next = { ...cfg, user, pass };
    await AsyncStorage.setItem(STORE_KEY, JSON.stringify(next));
    setCfg(next);
    push('Credentials updated.');
  };
  const refreshKey = async () => {
    try {
      const s = await api.get('/api/v1/settings/ai');
      setKeyStatus(s.gemini_configured ? 'configured ✓' : 'not set');
    } catch (e) { setKeyStatus('unknown'); }
  };
  const changeServer = async () => {
    await AsyncStorage.setItem(STORE_KEY, JSON.stringify({ host: '', user, pass: '', done: false }));
    setCfg({ host: '', user, pass: '', done: false });
  };

  const tabs = ['home', 'attend', 'students', 'finger', 'device', 'diag', 'ai', 'settings'];
  return (
    <ScrollView style={styles.root}>
      <Text style={styles.h1}>Attendance</Text>
      {busy && <ActivityIndicator size="small" />}
      <View style={styles.tabs}>{tabs.map((t) => (
        <Text key={t} onPress={() => setTab(t)} style={tab === t ? styles.tabOn : styles.tab}>{t}</Text>
      ))}</View>

      {tab === 'home' && <Section title="Today">
        <Text style={styles.mut}>Server: {cfg.host}</Text>
        <Text style={styles.mut}>{client.connected ? 'READY FOR SCAN' : 'BLE not connected'}</Text>
        <Button title="SCAN — place finger" color="#2f5fd0" onPress={() => run('scan-now', async () => {
          const r = await client.send('FINGERPRINT_SEARCH', {}, TIMEOUTS_MS.SEARCH);
          if (r.code !== 'match') return r;
          const a = await api.post('/api/v1/assisted-checkin', { fingerprint_slot_id: r.slot });
          setLastEvent({ ...a, confidence: r.confidence });
          return { match: r.slot, outcome: a.outcome };
        })} />
        {lastEvent && <View style={styles.overlay}>
          <Text style={styles.h2}>{lastEvent.outcome === 'RECORDED' ? '✓ PRESENT' : '⧗ ALREADY RECORDED'}</Text>
          <Text style={styles.big}>{lastEvent.first_name} {lastEvent.last_name}</Text>
          <Text>Class {lastEvent.grade_class}{lastEvent.section} · {(lastEvent.captured_at_utc || '').slice(11, 16)} UTC</Text>
          <Text style={styles.mut}>Fingerprint #{lastEvent.fingerprint_slot_id}{lastEvent.confidence != null ? ` · conf ${lastEvent.confidence}` : ''}</Text>
        </View>}
        <Button title="Load dashboard" onPress={() => run('overview', () => api.get('/api/v1/statistics/overview'))} />
        <Button title="Scan + connect BLE" onPress={() => run('scan', async () => {
          const found = [];
          await client.scan((d) => { found.push(d); setDevices([...found]); }, 8000);
          return `found ${found.length}`;
        })} />
        {devices.map((d) => <View key={d.id}><Text>{d.name} {d.id}</Text><Button title="Connect" onPress={() => run('connect', () => client.connect(d.id))} /></View>)}
      </Section>}

      {tab === 'attend' && <Section title="Attendance">
        <TextInput style={styles.input} value={query} onChangeText={setQuery} placeholder="Name, roll, class" />
        <Button title="Search" onPress={() => run('search', () => api.get(`/api/v1/attendance?q=${encodeURIComponent(query)}&limit=25`))} />
        <Button title="Today" onPress={() => run('today', () => api.get('/api/v1/attendance?limit=25'))} />
      </Section>}

      {tab === 'students' && <Section title="Students">
        <TextInput style={styles.input} value={query} onChangeText={setQuery} placeholder="Name or roll" />
        <Button title="Search students" onPress={() => run('students', () => api.get(`/api/v1/students?q=${encodeURIComponent(query)}&limit=25`))} />
      </Section>}

      {tab === 'finger' && <Section title="Fingerprints (BLE)">
        <TextInput style={styles.input} value={slot} onChangeText={setSlot} keyboardType="numeric" />
        <Button title="Count" onPress={() => run('count', () => client.send('FINGERPRINT_COUNT'))} />
        <Button title="Enroll slot" onPress={() => run('enroll', () => client.send('FINGERPRINT_ENROLL', { slot: parseInt(slot, 10) }, TIMEOUTS_MS.ENROLL))} />
        <Button title="Search" onPress={() => run('search', () => client.send('FINGERPRINT_SEARCH', {}, TIMEOUTS_MS.SEARCH))} />
        <Button title={auto ? 'Stop auto-scan' : 'Auto-scan (finger anytime)'} onPress={() => (auto ? stopAuto() : startAuto())} />
        <Button title="Delete slot" onPress={() => run('delete', () => client.send('FINGERPRINT_DELETE', { slot: parseInt(slot, 10) }))} />
      </Section>}

      {tab === 'device' && <Section title="Device">
        <Button title="Status" onPress={() => run('status', () => client.send('DEVICE_STATUS'))} />
        <Button title="RTC read" onPress={() => run('rtc', () => client.send('RTC_GET'))} />
        <Button title="RTC set to now" onPress={() => run('rtc-set', () => {
          const n = new Date();
          return client.send('RTC_SET', { year: n.getFullYear(), month: n.getMonth() + 1, day: n.getDate(), hour: n.getHours(), minute: n.getMinutes(), second: n.getSeconds() });
        })} />
        <Button title="Disconnect" onPress={() => client.disconnect().then(() => push('disconnected'))} />
      </Section>}

      {tab === 'diag' && <Section title="Diagnostics">
        <Button title="Full diagnostic" onPress={() => run('diag', () => client.send('FULL_DIAGNOSTIC'))} />
        <Button title="Buzzer test" onPress={() => run('buzzer', () => client.send('BUZZER_TEST'))} />
        <Button title="Ping" onPress={() => run('ping', () => client.send('PING'))} />
      </Section>}

      {tab === 'ai' && <Section title="AI Assistant">
        <TextInput style={styles.input} value={query} onChangeText={setQuery} placeholder="Who was absent today?" />
        <Button title="Ask" onPress={() => run('ai', () => api.post('/api/v1/ai/chat', { question: query }))} />
        <Text style={styles.mut}>Gemini key: {keyStatus}</Text>
        <TextInput style={styles.input} value={keyInput} onChangeText={setKeyInput} placeholder="Paste Gemini API key here" secureTextEntry autoCapitalize="none" />
        <Button title="Save key on server" onPress={() => run('save-key', () => api.put('/api/v1/settings/ai', { gemini_api_key: keyInput }).then(async (r) => { setKeyInput(''); await refreshKey(); return r; }))} />
      </Section>}

      {tab === 'settings' && <Section title="Settings">
        <Text>Server: {cfg.host}</Text>
        <Text>Admin user</Text><TextInput style={styles.input} value={user} onChangeText={setUser} autoCapitalize="none" />
        <Text>Admin password</Text><TextInput style={styles.input} value={pass} onChangeText={setPass} secureTextEntry />
        <Button title="Save credentials" onPress={saveCreds} />
        <Button title="Change server…" color="#c0392b" onPress={() =>
          Alert.alert('Change server?', 'This clears the saved endpoint.', [
            { text: 'Cancel' }, { text: 'Change', onPress: changeServer },
          ])} />
        <Text style={styles.mut}>Hardware: R307S yellow→GPIO32/green→GPIO33, DS3231 GPIO25/26, buzzer GPIO27. Gemini key lives on the server only.</Text>
      </Section>}

      <Text style={styles.log}>{out.slice(-30).join('\n')}</Text>
      <StatusBar style="auto" />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { padding: 14, marginTop: 30 },
  setup: { padding: 20, marginTop: 60, gap: 8 },
  h1: { fontSize: 22, fontWeight: 'bold' },
  h2: { fontSize: 16, fontWeight: 'bold', marginBottom: 6 },
  sec: { marginVertical: 8, gap: 6 },
  tabs: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginVertical: 8 },
  tab: { color: '#555', padding: 4 },
  tabOn: { color: '#000', fontWeight: 'bold', padding: 4, textDecorationLine: 'underline' },
  input: { borderWidth: 1, borderColor: '#888', padding: 7, marginVertical: 4 },
  dev: { flex: 1 },
  log: { fontFamily: 'monospace', backgroundColor: '#111', color: '#eee', padding: 8, marginTop: 10 },
  overlay: { backgroundColor: '#e9effe', borderRadius: 12, padding: 14, marginVertical: 8, gap: 2 },
  big: { fontSize: 20, fontWeight: 'bold' },
  mut: { color: '#555' },
  ok: { color: '#177245', fontWeight: 'bold' },
  err: { color: '#b3261e' },
});
