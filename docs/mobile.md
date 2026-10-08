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

## Hosting the backend ON the phone (Termux, no PC needed)

1. Install Termux (F-Droid) and open it. Turn off battery optimization
   for Termux so Android doesn't kill the server.
2. `pkg install -y python git`, then get this repo on the phone
   (`git clone <repo-url>` or copy the `backend/` folder over USB).
3. `cd backend`, `pip install fastapi "uvicorn[standard]" pydantic aiosqlite tzdata python-dotenv openpyxl`.
4. Copy `.env.example` → `.env`, set `ADMIN_USERNAME`/`ADMIN_PASSWORD`
   (≥16 chars). Leave `GEMINI_API_KEY` empty for now.
5. `python -m app.provision_device --name phone-terminal --location pocket --sensor-capacity 1000`
6. `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
7. In the app setup screen enter `http://127.0.0.1:8000`, Test, Continue.
8. Paste the Gemini key in the app's AI tab — it is stored in the
   phone-side `.env` via the admin settings endpoint, never in the app.

```powershell
cd mobile
npm install
node protocol.test.js
npx expo start            # dev
npx expo run:android      # on-device build (needs Android SDK)
```

## Local SDK setup (Windows, as used for the v1.2.0 APK)

1. JDK 17 (Gradle/Groovy cannot run on JDK 25): unpack Temurin 17 to
   `C:\Java\jdk-17.0.11+9`, set `JAVA_HOME` to it.
2. Android cmdline-tools zip → `C:\Android\Sdk\cmdline-tools\latest`,
   then accept licenses and install (SDK 34 shown):
   `sdkmanager --licenses`, plus `platform-tools`,
   `platforms;android-34`, `build-tools;34.0.0`. Set
   `ANDROID_HOME`/`ANDROID_SDK_ROOT` to `C:\Android\Sdk`.
3. `npx expo prebuild --platform android` (regenerates `mobile/android/`,
   gitignored), then `gradlew assembleDebug` in `mobile/android`.
4. Result: `mobile/android/app/build/outputs/apk/debug/app-debug.apk`
   (debug-signed, installable; release-sign separately for stores).
5. `minSdkVersion` is 24 via the `expo-build-properties` plugin (required
   by async-storage 1.x); use `@react-native-async-storage/async-storage`
   1.23.x with Expo SDK 51 (3.x needs newer Kotlin).

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
