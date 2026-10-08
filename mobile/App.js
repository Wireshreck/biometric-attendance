import React, { useState } from 'react';
import { ActivityIndicator, Button, ScrollView, StyleSheet, Text, TextInput, View, Alert } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { client } from './bleClient';
import { TIMEOUTS_MS } from '../shared/ble_protocol.js';

const API_DEFAULT = 'http://192.168.137.1:8000';

function useApi(host, user, pass) {
  const headers = { Authorization: 'Basic ' + btoa(`${user}:${pass}`), 'Content-Type': 'application/json' };
  const get = async (p) => {
    const r = await fetch(host + p, { headers });
    if (!r.ok) throw new Error(`API ${r.status}`);
    return r.json();
  };
  const post = async (p, body) => {
    const r = await fetch(host + p, { method: 'POST', headers, body: JSON.stringify(body || {}) });
    if (!r.ok) throw new Error(`API ${r.status}`);
    return r.json();
  };
  return { get, post };
}

function Section({ title, children }) {
  return <View style={styles.sec}><Text style={styles.h2}>{title}</Text>{children}</View>;
}

export default function App() {
  const [tab, setTab] = useState('home');
  const [host, setHost] = useState(API_DEFAULT);
  const [user, setUser] = useState('');
  const [pass, setPass] = useState('');
  const [out, setOut] = useState(['Biometric Attendance v1.1.0']);
  const [busy, setBusy] = useState(false);
  const [slot, setSlot] = useState('1');
  const [query, setQuery] = useState('');
  const [devices, setDevices] = useState([]);
  const api = useApi(host, user, pass);
  const push = (o) => setOut((l) => [...l.slice(-40), typeof o === 'string' ? o : JSON.stringify(o)]);
  const run = async (label, fn) => {
    setBusy(true);
    try { push(`> ${label}`); push(await fn()); }
    catch (e) { push(`${label} FAILED: ${e.message}`); }
    finally { setBusy(false); }
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
      </Section>}

      {tab === 'settings' && <Section title="Settings">
        <Text>API host</Text><TextInput style={styles.input} value={host} onChangeText={setHost} />
        <Text>Admin user</Text><TextInput style={styles.input} value={user} onChangeText={setUser} />
        <Text>Admin password</Text><TextInput style={styles.input} value={pass} onChangeText={setPass} secureTextEntry />
        <Text>Hardware: R307S yellow→GPIO32/green→GPIO33, DS3231 GPIO25/26, buzzer GPIO27.</Text>
      </Section>}

      <Text style={styles.log}>{out.slice(-30).join('\n')}</Text>
      <StatusBar style="auto" />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { padding: 14, marginTop: 30 },
  h1: { fontSize: 22, fontWeight: 'bold' },
  h2: { fontSize: 16, fontWeight: 'bold', marginBottom: 6 },
  sec: { marginVertical: 8, gap: 6 },
  tabs: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginVertical: 8 },
  tab: { color: '#555', padding: 4 },
  tabOn: { color: '#000', fontWeight: 'bold', padding: 4, textDecorationLine: 'underline' },
  input: { borderWidth: 1, borderColor: '#888', padding: 7, marginVertical: 4 },
  log: { fontFamily: 'monospace', backgroundColor: '#111', color: '#eee', padding: 8, marginTop: 10 },
});
