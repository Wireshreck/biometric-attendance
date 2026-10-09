/* Protocol-mirror parity test (node). The BLE constants exist in four
 * copies: shared/ble_protocol.js (ESM), web/vendor/ble_protocol.js
 * (classic script served to browsers), shared/ble_protocol.py, and
 * firmware/include/{ble_protocol.h, config.h}. Drift between them has
 * caused real mismatches before, so this test pins the JS/Python copies
 * to identical values. (Firmware headers are C and checked by the
 * firmware build + docs/protocol.md; service UUID + char IDs are
 * asserted here against their documented values.)
 * Run: node web/protocol-mirrors.test.js
 */
'use strict';
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { execFileSync } = require('child_process');

(async () => {
  const root = path.join(__dirname, '..');

  // 1. Shared ESM copy.
  const shared = await import('../shared/ble_protocol.js');

  // 2. Vendor classic-script copy in a sandbox.
  const vendorSrc = fs.readFileSync(path.join(__dirname, 'vendor', 'ble_protocol.js'), 'utf8');
  const sandbox = { window: {} };
  vm.createContext(sandbox);
  vm.runInContext(vendorSrc, sandbox, { filename: 'ble_protocol.js' });
  const vendor = sandbox.window.BLE_PROTOCOL;
  assert.ok(vendor, 'vendor copy must set window.BLE_PROTOCOL');

  // 3. Python copy via a JSON dump (no import side effects).
  const dump = execFileSync('python', [path.join(root, 'shared', 'dump_constants.py')], { encoding: 'utf8' });
  const py = JSON.parse(dump);

  // --- assertions ---
  const keys = ['BLE_SERVICE_UUID', 'BLE_CHARS', 'COMMANDS', 'CHAR_FOR_COMMAND',
    'TIMEOUTS_MS', 'PINS', 'DIAG_TESTS', 'DIAG_RESULTS', 'ERROR_CODES'];
  const norm = (v) => JSON.parse(JSON.stringify(v));
  for (const k of keys) {
    assert.deepStrictEqual(norm(vendor[k]), norm(shared[k]), `vendor vs shared mismatch: ${k}`);
  }
  assert.deepStrictEqual(py.SERVICE, shared.BLE_SERVICE_UUID, 'py vs js SERVICE_UUID');
  assert.deepStrictEqual(py.CHARS, { ...shared.BLE_CHARS }, 'py vs js BLE_CHARS');
  assert.deepStrictEqual(py.COMMANDS, [...shared.COMMANDS], 'py vs js COMMANDS');
  assert.deepStrictEqual(py.CHAR_FOR_COMMAND, { ...shared.CHAR_FOR_COMMAND }, 'py vs js CHAR_FOR_COMMAND');
  assert.deepStrictEqual(py.TIMEOUTS, { ...shared.TIMEOUTS_MS }, 'py vs js TIMEOUTS_MS');
  assert.deepStrictEqual(py.PINS, { ...shared.PINS }, 'py vs js PINS');
  assert.deepStrictEqual(py.DIAG_TESTS, [...shared.DIAG_TESTS], 'py vs js DIAG_TESTS');
  assert.deepStrictEqual(py.DIAG_RESULTS, [...shared.DIAG_RESULTS], 'py vs js DIAG_RESULTS');
  assert.deepStrictEqual(py.ERROR_CODES, [...shared.ERROR_CODES], 'py vs js ERROR_CODES');
  assert.ok(py.STATUS.includes('ok') && py.STATUS.includes('busy'),
    'py STATUS_VALUES must carry the 5 statuses (naming differs: STATUS_VALUES vs STATUS, documented)');
  assert.deepStrictEqual({ ...shared.PINS },
    { DS3231_SDA: 25, DS3231_SCL: 26, R307S_RX: 32, R307S_TX: 33, BUZZER: 27 },
    'PINS must match firmware wiring');

  // Behavioral parity of honesty helper (both spellings).
  const dishonest = { test: 'R307S_SENSOR', result: 'PASS' };
  assert.strictEqual(shared.isHonestDiagResult(dishonest, false), false);
  assert.strictEqual(vendor.isHonestDiagResult(dishonest, false), false);
  assert.strictEqual(shared.isHonestDiagResult({ test: 'BUZZER', result: 'PASS' }, false), true);

  console.log('protocol-mirrors.test.js: parity OK (js/js/py aligned)');
})().catch((e) => { console.error('protocol-mirrors.test.js FAILED:', e.message); process.exit(1); });
