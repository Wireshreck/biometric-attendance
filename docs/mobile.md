# Mobile App (`mobile/`)

Stack: Expo React Native + `react-native-ble-plx`. Chosen because it shares
the exact same BLE protocol module as the web app
(`../shared/ble_protocol.js` — no second protocol) and is maintainable with
the standard Expo toolchain.

## Structure

- `App.js` — screens: BLE scan/connect, device status, fingerprint
  enrollment/search/deletion, RTC, attendance, diagnostics, help.
- `bleClient.js` — `DeviceClient` transport: scan, connect/disconnect,
  `send(cmd, params)` with JSON envelope; 16-bit characteristic UUIDs
  0x1101–0x1108 expanded to the Bluetooth base UUID.
- `package.json` — Expo dependencies.
- `protocol.test.js` — software-only test: `node protocol.test.js` (or
  `npm test`). No hardware required.

## Develop

```powershell
cd mobile
npm install
node protocol.test.js
npx expo start
```

A full APK build requires the Flutter-free Expo/Android toolchain
(`npx expo run:android` with Android SDK) and is not produced in this
Windows-only CI-less environment; see Known Limitations in the release
notes. Protocol behavior is identical to web/desktop/test.exe by
construction (shared module + shared test vectors).
