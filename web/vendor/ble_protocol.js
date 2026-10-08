// Shared BLE protocol constants. Mirrors firmware/include/ble_protocol.h
// and docs/protocol.md. Web, mobile, desktop, and test.exe must import
// this file instead of redefining commands.
const BLE_SERVICE_UUID = '89ea2240-04cc-4e36-9356-c71647be1c8d';
const BLE_CHARS = {
  DEVICE_INFO: '1101',
  DEVICE_STATUS: '1102',
  PING: '1103',
  RTC: '1104',
  FINGERPRINT_STATUS: '1105',
  FINGERPRINT_CONTROL: '1106',
  DIAGNOSTIC: '1107',
  ATTENDANCE: '1108',
};

const COMMANDS = [
  'DEVICE_INFO', 'DEVICE_STATUS', 'PING',
  'RTC_GET', 'RTC_SET',
  'FINGERPRINT_STATUS', 'FINGERPRINT_COUNT', 'FINGERPRINT_ENROLL',
  'FINGERPRINT_SEARCH', 'FINGERPRINT_DELETE', 'FINGERPRINT_DELETE_ALL',
  'BUZZER_TEST', 'FULL_DIAGNOSTIC',
  'ATTENDANCE_STATUS', 'ATTENDANCE_READ', 'ATTENDANCE_CLEAR',
];

const CHAR_FOR_COMMAND = {
  DEVICE_INFO: 'DEVICE_INFO',
  DEVICE_STATUS: 'DEVICE_STATUS',
  PING: 'PING',
  RTC_GET: 'RTC',
  RTC_SET: 'RTC',
  FINGERPRINT_STATUS: 'FINGERPRINT_STATUS',
  FINGERPRINT_COUNT: 'FINGERPRINT_STATUS',
  FINGERPRINT_ENROLL: 'FINGERPRINT_CONTROL',
  FINGERPRINT_SEARCH: 'FINGERPRINT_CONTROL',
  FINGERPRINT_DELETE: 'FINGERPRINT_CONTROL',
  FINGERPRINT_DELETE_ALL: 'FINGERPRINT_CONTROL',
  BUZZER_TEST: 'DIAGNOSTIC',
  FULL_DIAGNOSTIC: 'DIAGNOSTIC',
  ATTENDANCE_STATUS: 'ATTENDANCE',
  ATTENDANCE_READ: 'ATTENDANCE',
  ATTENDANCE_CLEAR: 'ATTENDANCE',
};

const STATUS = ['ok', 'error', 'busy', 'unreachable', 'not_supported'];
const ERROR_CODES = [
  'UNKNOWN', 'SENSOR_UNAVAILABLE', 'NO_FINGER', 'BAD_IMAGE',
  'IMAGE_MISMATCH', 'DUPLICATE', 'INVALID_ID', 'STORAGE_FULL',
  'TIMEOUT', 'COMMUNICATION', 'WRITE_FAILED', 'RTC_INVALID',
  'RTC_LOST_POWER', 'NOT_IMPLEMENTED',
];
const ENROLL_STATES = [
  'ENROLL_PLACE_FINGER', 'ENROLL_REMOVE_FINGER',
  'ENROLL_PLACE_FINGER_AGAIN', 'ENROLL_SUCCESS', 'ENROLL_FAILED',
];
const DIAG_TESTS = [
  'ESP32', 'BLE', 'R307S_UART', 'R307S_SENSOR', 'FINGERPRINT_DB',
  'DS3231', 'RTC', 'BUZZER', 'STORAGE', 'ATTENDANCE',
];
const DIAG_RESULTS = ['PASS', 'FAIL', 'WARN', 'SKIPPED'];

const TIMEOUTS_MS = { DEFAULT: 20000, ENROLL: 300000, SEARCH: 30000 };

function buildRequest(cmd, params = {}) {
  if (!COMMANDS.includes(cmd)) throw new Error(`unknown command ${cmd}`);
  return JSON.stringify({ cmd, ...params });
}

function parseResponse(text) {
  const msg = JSON.parse(text);
  if (typeof msg.status !== 'string') throw new Error('response missing status');
  return msg;
}

// Returns true only for honest device semantics: PASS requires the device
// to have actually run the test; disconnected hardware must not be PASS.
function isHonestDiagResult(entry, connected) {
  if (!entry || !DIAG_TESTS.includes(entry.test)) return false;
  if (!DIAG_RESULTS.includes(entry.result)) return false;
  if (!connected && entry.result === 'PASS' &&
      ['R307S_UART', 'R307S_SENSOR', 'FINGERPRINT_DB', 'DS3231', 'RTC'].includes(entry.test)) {
    return false;
  }
  return true;
}

// Classic-script fallback so the static web app can load this file with a
// plain <script> tag (Web Bluetooth pages served over file:// or http://).
if (typeof window !== 'undefined') {
  window.BLE_PROTOCOL = {
    BLE_SERVICE_UUID, BLE_CHARS, COMMANDS, CHAR_FOR_COMMAND, STATUS,
    ERROR_CODES, ENROLL_STATES, DIAG_TESTS, DIAG_RESULTS, TIMEOUTS_MS,
    buildRequest, parseResponse, isHonestDiagResult,
  };
}
