# Mobile App (`mobile/`)

Stack: Expo React Native + `react-native-ble-plx` for BLE, `fetch` for the
backend REST API. Same BLE protocol module as web
(`../shared/ble_protocol.js`); same REST contract as web/desktop.

Tab screens (no navigation dependency, `useState` tabs):

- Home: today's overview, BLE scan/connect, quick actions.
- Attendance: search, today list (server-side queries).
- Students: search, profiles via summary endpoint.
- Fingerprints: enroll/search/delete/count over BLE.
- Device: BLE status, RTC read/set, disconnect.
- Diagnostics: FULL_DIAGNOSTIC, BUZZER_TEST, PING.
- AI Assistant: `/api/v1/ai/chat` with graceful missing-key message.
- Settings: API host (default `http://192.168.137.1:8000`), admin
  credentials, hardware reference.

```powershell
cd mobile
npm install
node protocol.test.js
npx expo start
```

A store/APK build needs the Android SDK (`npx expo run:android`) and is
not produced in this environment. API credentials are kept in component
state only, never persisted. The Gemini key never ships in the app —
AI calls go through the backend.
