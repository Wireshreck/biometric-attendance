import React, { useState } from 'react';
import { Button, ScrollView, StyleSheet, Text, TextInput, View, Alert } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { client } from './bleClient';
import { TIMEOUTS_MS } from '../shared/ble_protocol.js';

function Log({ lines }) {
  return <Text style={styles.log}>{lines.slice(-30).join('\n')}</Text>;
}

export default function App() {
  const [lines, setLines] = useState(['Biometric Attendance mobile client', 'protocol: docs/protocol.md']);
  const [devices, setDevices] = useState([]);
  const [slot, setSlot] = useState('1');
  const push = (o) => setLines((l) => [...l, typeof o === 'string' ? o : JSON.stringify(o)]);

  const run = async (label, fn) => {
    try { push(`> ${label}`); push(await fn()); }
    catch (e) { push(`${label} FAILED: ${e.message}`); }
  };

  return (
    <ScrollView style={styles.root}>
      <Text style={styles.h1}>Biometric Attendance</Text>
      <Text>ESP32 + R307S + DS3231 · BLE · GPIO25/26 RTC · GPIO32/33 sensor · GPIO27 buzzer</Text>
      <View style={styles.row}>
        <Button title="Scan BLE" onPress={() => run('scan', async () => {
          const found = [];
          await client.scan((d) => { found.push(d); setDevices([...found]); }, 8000);
          return `found ${found.length} device(s)`;
        })} />
        <Button title="Disconnect" onPress={() => client.disconnect().then(() => push('disconnected'))} />
      </View>
      {devices.map((d) => (
        <View key={d.id} style={styles.row}>
          <Text style={styles.dev}>{d.name} · {d.id}</Text>
          <Button title="Connect" onPress={() => run(`connect ${d.name}`, () => client.connect(d.id))} />
        </View>
      ))}
      <Text style={styles.h2}>Dashboard</Text>
      <Button title="Refresh (INFO+STATUS+ATTENDANCE)" onPress={() => run('dashboard', async () => {
        const info = await client.send('DEVICE_INFO');
        const status = await client.send('DEVICE_STATUS');
        const att = await client.send('ATTENDANCE_STATUS');
        return { info: info.data, status: status.data, attendance: att.data };
      })} />
      <Text style={styles.h2}>Fingerprint</Text>
      <View style={styles.row}>
        <TextInput style={styles.input} value={slot} onChangeText={setSlot} keyboardType="numeric" />
        <Button title="Status" onPress={() => run('FINGERPRINT_STATUS', () => client.send('FINGERPRINT_STATUS'))} />
        <Button title="Count" onPress={() => run('FINGERPRINT_COUNT', () => client.send('FINGERPRINT_COUNT'))} />
      </View>
      <View style={styles.row}>
        <Button title="Enroll" onPress={() => run(`ENROLL slot ${slot}`, () =>
          client.send('FINGERPRINT_ENROLL', { slot: parseInt(slot, 10) }, TIMEOUTS_MS.ENROLL))} />
        <Button title="Search" onPress={() => run('SEARCH', () =>
          client.send('FINGERPRINT_SEARCH', {}, TIMEOUTS_MS.SEARCH))} />
        <Button title="Delete" onPress={() => run(`DELETE slot ${slot}`, () =>
          client.send('FINGERPRINT_DELETE', { slot: parseInt(slot, 10) }))} />
      </View>
      <Button title="Delete ALL (confirm)" color="#c0392b" onPress={() =>
        Alert.alert('Confirm', 'Delete all templates?', [
          { text: 'Cancel' },
          { text: 'Delete', onPress: () => run('DELETE_ALL', () => client.send('FINGERPRINT_DELETE_ALL')) },
        ])} />
      <Text style={styles.h2}>RTC</Text>
      <View style={styles.row}>
        <Button title="RTC_GET" onPress={() => run('RTC_GET', () => client.send('RTC_GET'))} />
        <Button title="RTC_SET to now" onPress={() => run('RTC_SET', () => {
          const n = new Date();
          return client.send('RTC_SET', {
            year: n.getFullYear(), month: n.getMonth() + 1, day: n.getDate(),
            hour: n.getHours(), minute: n.getMinutes(), second: n.getSeconds(),
          });
        })} />
      </View>
      <Text style={styles.h2}>Attendance</Text>
      <View style={styles.row}>
        <Button title="Status" onPress={() => run('ATTENDANCE_STATUS', () => client.send('ATTENDANCE_STATUS'))} />
        <Button title="Read" onPress={() => run('ATTENDANCE_READ', () => client.send('ATTENDANCE_READ'))} />
        <Button title="Clear" color="#c0392b" onPress={() =>
          Alert.alert('Confirm', 'Clear attendance records?', [
            { text: 'Cancel' },
            { text: 'Clear', onPress: () => run('ATTENDANCE_CLEAR', () => client.send('ATTENDANCE_CLEAR')) },
          ])} />
      </View>
      <Text style={styles.h2}>Diagnostics</Text>
      <View style={styles.row}>
        <Button title="FULL_DIAGNOSTIC" onPress={() => run('FULL_DIAGNOSTIC', () => client.send('FULL_DIAGNOSTIC'))} />
        <Button title="BUZZER_TEST" onPress={() => run('BUZZER_TEST', () => client.send('BUZZER_TEST'))} />
        <Button title="PING" onPress={() => run('PING', () => client.send('PING'))} />
      </View>
      <Text style={styles.h2}>Help</Text>
      <Text>Setup: R307S red VIN / black GND / yellow GPIO32 / green GPIO33; DS3231 GPIO25/26; buzzer GPIO27. Demo: PING → INFO → STATUS → RTC_GET → COUNT → ENROLL → SEARCH → ATTENDANCE_READ → FULL_DIAGNOSTIC. Disconnected hardware reports FAIL/SKIPPED, never PASS.</Text>
      <Log lines={lines} />
      <StatusBar style="auto" />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { padding: 16, marginTop: 32 },
  h1: { fontSize: 22, fontWeight: 'bold' },
  h2: { fontSize: 17, fontWeight: 'bold', marginTop: 14 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 8, marginVertical: 4, flexWrap: 'wrap' },
  input: { borderWidth: 1, borderColor: '#888', padding: 6, width: 70 },
  dev: { flex: 1 },
  log: { fontFamily: 'monospace', backgroundColor: '#111', color: '#eee', padding: 8, marginTop: 10 },
});
