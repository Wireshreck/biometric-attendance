// Software-only protocol test for the mobile/web shared module.
// Runs with plain node (no device needed): node protocol.test.js
import assert from 'node:assert/strict';
import {
  COMMANDS, CHAR_FOR_COMMAND, ERROR_CODES, ENROLL_STATES, DIAG_TESTS,
  DIAG_RESULTS, buildRequest, parseResponse, isHonestDiagResult,
  BLE_SERVICE_UUID, BLE_CHARS,
} from '../shared/ble_protocol.js';

assert.equal(BLE_SERVICE_UUID, '89ea2240-04cc-4e36-9356-c71647be1c8d');
for (const c of ['DEVICE_INFO', 'DEVICE_STATUS', 'PING', 'RTC_GET', 'RTC_SET',
  'FINGERPRINT_STATUS', 'FINGERPRINT_COUNT', 'FINGERPRINT_ENROLL',
  'FINGERPRINT_SEARCH', 'FINGERPRINT_DELETE', 'FINGERPRINT_DELETE_ALL',
  'BUZZER_TEST', 'FULL_DIAGNOSTIC', 'ATTENDANCE_STATUS', 'ATTENDANCE_READ',
  'ATTENDANCE_CLEAR']) {
  assert.ok(COMMANDS.includes(c), `missing command ${c}`);
  assert.ok(CHAR_FOR_COMMAND[c], `missing char mapping ${c}`);
}
assert.ok(ERROR_CODES.includes('SENSOR_UNAVAILABLE'));
assert.ok(ENROLL_STATES.includes('ENROLL_PLACE_FINGER'));
assert.deepEqual(DIAG_TESTS.length, 10);
assert.ok(DIAG_RESULTS.includes('SKIPPED'));
const req = JSON.parse(buildRequest('FINGERPRINT_ENROLL', { slot: 3 }));
assert.equal(req.cmd, 'FINGERPRINT_ENROLL');
assert.equal(req.slot, 3);
assert.throws(() => buildRequest('NOPE'), /unknown command/);
assert.equal(parseResponse('{"status":"ok","code":"pong"}').code, 'pong');
assert.throws(() => parseResponse('{"code":"x"}'), /missing status/);
// Honesty rule: disconnected hardware must not report PASS for HW tests.
assert.equal(isHonestDiagResult({ test: 'R307S_UART', result: 'PASS' }, false), false);
assert.equal(isHonestDiagResult({ test: 'R307S_UART', result: 'FAIL' }, false), true);
assert.equal(isHonestDiagResult({ test: 'BUZZER', result: 'PASS' }, false), true);
assert.equal(isHonestDiagResult({ test: 'NOPE', result: 'PASS' }, true), false);
assert.ok(Object.keys(BLE_CHARS).length === 8);
console.log('mobile/web protocol tests: PASS');
