# Mobile App (`mobile/`)

Stack: Expo React Native + `react-native-ble-plx` for BLE, `fetch` for the
backend REST API, AsyncStorage for settings. Same BLE protocol module as
web (`../shared/ble_protocol.js`); same REST contract as web/desktop.

## Self-hosted first run (no rebuilds, no hardcoded server)

1. Open the app → setup screen.
2. Enter your server URL (e.g. `http://192.168.1.100:8000` — shown as an
   example only; whatever you type is validated, never assumed).
3. **Test Connection** hits `GET /health` (no auth) and shows backend
   schema version; **Continue** persists the endpoint on-device.
4. Enter admin credentials in Settings when the API asks (stored
   on-device only alongside the URL; change servers anytime via
   Settings → Change server).

Unreachable/timeout/invalid-URL/auth failures render explicit errors
with Retry/Settings — never a crash. The Gemini key and device tokens
never ship in the app; AI calls go through the backend.

```powershell
cd mobile
npm install
node protocol.test.js
npx expo start            # dev
npx expo run:android      # on-device build (needs Android SDK)
```

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
