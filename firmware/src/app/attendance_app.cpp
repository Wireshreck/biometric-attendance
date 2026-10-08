#include <Arduino.h>
#include <Preferences.h>
#include <esp_system.h>

#include "attendance_state.h"
#include "attendance_store.h"
#include "ble_service.h"
#include "config.h"
#include "device_services.h"
#include "network_service.h"

static RtcService rtcService;
static IndicatorService indicators;
static FingerprintService fingerprint;
static AttendanceStore store;
static NetworkService network;
static BleService bleManager;
static Preferences enrollmentPrefs;
static AttendanceState state = AttendanceState::BOOT;
static uint32_t nextSensorProbeMs = 0, nextSyncMs = 0, nextEnrollmentRetryMs = 0, lastMatchedMs = 0;
static uint32_t lastClockDisplayMs = 0;
static uint32_t showResultUntilMs = 0;
static bool resultScreenActive = false;
static bool fingerLatched = false;
static char serialLine[SERIAL_LINE_MAX];
static size_t serialLength = 0;

struct EnrollmentIntent { char studentUuid[37]; uint16_t slot; uint16_t version; uint32_t checksum; };
static uint32_t intentChecksum(const EnrollmentIntent& item) {
    uint32_t h = 2166136261u;
    for (const unsigned char c : item.studentUuid) h = (h ^ c) * 16777619u;
    h = (h ^ static_cast<uint8_t>(item.slot)) * 16777619u;
    h = (h ^ static_cast<uint8_t>(item.slot >> 8)) * 16777619u;
    h = (h ^ static_cast<uint8_t>(item.version)) * 16777619u;
    h = (h ^ static_cast<uint8_t>(item.version >> 8)) * 16777619u;
    return h;
}
static bool uuidValid(const char* s) {
    if (!s || strlen(s) != 36) return false;
    for (size_t i=0; i<36; ++i) if (!(isxdigit(s[i]) || ((i==8||i==13||i==18||i==23) && s[i]=='-'))) return false;
    return true;
}
static void transition(AttendanceState next, const char* title, const char* detail = "") {
    state = next;
    char stamp[32] = "";
    if (rtcService.valid()) rtcService.timestamp(stamp, sizeof(stamp));
    Serial.printf("[STATE] %s: %s", attendance_state_name(state), title);
    if (detail && detail[0]) Serial.printf(" — %s", detail);
    if (stamp[0]) Serial.printf(" (%s)", stamp);
    Serial.println();
}
static void uuidV4(char out[37]) {
    uint8_t b[16]; esp_fill_random(b, sizeof(b)); b[6] = (b[6] & 0x0F) | 0x40; b[8] = (b[8] & 0x3F) | 0x80;
    snprintf(out, 37, "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x",
        b[0],b[1],b[2],b[3],b[4],b[5],b[6],b[7],b[8],b[9],b[10],b[11],b[12],b[13],b[14],b[15]);
}
static void enrollmentPrompt(const char* title, const char* detail) { transition(AttendanceState::IDENTIFYING, title, detail); }
static bool saveIntent(const char* studentUuid, uint16_t slot) {
    EnrollmentIntent item{}; strlcpy(item.studentUuid, studentUuid, sizeof(item.studentUuid)); item.slot = slot; item.version = 1; item.checksum = intentChecksum(item);
    return enrollmentPrefs.putBytes("intent", &item, sizeof(item)) == sizeof(item);
}
static bool loadIntent(EnrollmentIntent& item) {
    if (enrollmentPrefs.getBytesLength("intent") != sizeof(item) || enrollmentPrefs.getBytes("intent", &item, sizeof(item)) != sizeof(item)) return false;
    return item.version == 1 && item.checksum == intentChecksum(item) && uuidValid(item.studentUuid) && item.slot > 0;
}
static bool enrollmentIntentPresent() { return enrollmentPrefs.getBytesLength("intent") > 0; }
static void completePendingEnrollment() {
    EnrollmentIntent intent{};
    if (!loadIntent(intent)) return;
    transition(AttendanceState::OFFLINE, "ENROLLMENT SAVED", "Confirming with server");
    if (network.enrollmentComplete(intent.studentUuid, intent.slot)) {
        enrollmentPrefs.remove("intent");
        Serial.println("[INFO] Pending sensor enrollment confirmation completed.");
        nextEnrollmentRetryMs = 0;
    } else {
        nextEnrollmentRetryMs = millis() + NETWORK_RETRY_MS;
        Serial.println("[WARN] Enrollment is in sensor and confirmation intent is durable; server confirmation will retry.");
    }
}
static void handleSerialCommand(char* line) {
    if (strncmp(line, "ENROLL ", 7) != 0) {
        if (strcmp(line, "HELP") == 0) Serial.println("Commands: HELP | STATUS | SETTIME YYYY-MM-DD HH:MM:SS (local +05:30) | ENROLL <pending-student-uuid>");
        else if (strcmp(line, "STATUS") == 0) Serial.printf("state=%s sensor=%s rtc=%s storage=%s wifi=%s pending=%u\n", attendance_state_name(state), fingerprint.ready()?"READY":"UNAVAILABLE", rtcService.valid()?"VALID":"INVALID", store.healthy()?"READY":"ERROR", network.connected()?"CONNECTED":"OFFLINE", static_cast<unsigned>(store.pendingCount()));
        else if (strncmp(line, "SETTIME ", 8) == 0) {
            unsigned int y=0, mo=0, d=0, h=0, mi=0, s=0; char tail=0;
            if (sscanf(line + 8, "%u-%u-%u %u:%u:%u%c", &y, &mo, &d, &h, &mi, &s, &tail) == 6 && rtcService.setLocalTime(y, mo, d, h, mi, s)) {
                Serial.println("[PASS] RTC set to the supplied local time (+05:30 policy). Confirm against a trusted clock.");
                if (!fingerprint.ready()) transition(AttendanceState::ERROR, "SENSOR NOT FOUND", "Clock set; retrying sensor");
                else if (!store.healthy()) transition(AttendanceState::ERROR, "STORAGE ERROR", "Clock set; no scans accepted");
                else transition(AttendanceState::WAITING_FOR_FINGER, network.connected()?"READY":"OFFLINE", "Scan finger");
            } else Serial.println("[FAIL] Invalid date/time or RTC unavailable. Use SETTIME YYYY-MM-DD HH:MM:SS.");
        }
        else if (line[0]) Serial.println("[FAIL] Unknown command. Type HELP.");
        return;
    }
    char* studentUuid = line + 7;
    while (*studentUuid == ' ') ++studentUuid;
    if (!uuidValid(studentUuid)) { Serial.println("[FAIL] Use ENROLL followed by a complete student UUID."); return; }
    EnrollmentIntent existingIntent{};
    if (enrollmentIntentPresent() && !loadIntent(existingIntent)) {
        Serial.println("[CRITICAL] Enrollment intent is corrupt; reconcile the pending student/template before any new enrollment."); return;
    }
    if (enrollmentIntentPresent()) {
        completePendingEnrollment();
        if (enrollmentIntentPresent()) { Serial.println("[FAIL] A prior enrollment is awaiting backend confirmation; finish/reconcile it before starting another."); return; }
    }
    if (!fingerprint.ready() || !network.connected()) { Serial.println("[FAIL] Enrollment needs an available sensor and configured online device API."); return; }
    uint16_t slot = 0;
    if (!network.enrollmentAssignment(studentUuid, slot)) { Serial.println("[FAIL] No valid pending enrollment assignment returned by backend."); return; }
    Serial.printf("[INFO] Enrolling pending student into sensor slot %u. Two captures required.\n", slot);
    fingerLatched = true;
    if (!fingerprint.enroll(slot, enrollmentPrompt)) {
        indicators.failurePulse();
        if (!rtcService.valid()) transition(AttendanceState::ERROR, "RTC INVALID", "Enrollment failed; set time");
        else if (!store.healthy()) transition(AttendanceState::ERROR, "STORAGE ERROR", "Enrollment failed");
        else transition(AttendanceState::WAITING_FOR_FINGER, "ENROLL FAILED", "No attendance scan made");
        resultScreenActive = true; showResultUntilMs = millis() + 1800; return;
    }
    if (!saveIntent(studentUuid, slot)) { indicators.failurePulse(); transition(AttendanceState::ERROR, "SAVE ERROR", "Template saved; confirmation not journaled"); Serial.println("[CRITICAL] Fingerprint saved but durable confirmation intent could not be stored. Do not reuse this slot; restore storage before retry."); return; }
    if (network.enrollmentComplete(studentUuid, slot)) {
        enrollmentPrefs.remove("intent"); nextEnrollmentRetryMs = 0; indicators.successPulse(); transition(AttendanceState::READY, "ENROLL COMPLETE", "Return to scan mode");
        Serial.println("[PASS] Sensor template stored and backend student activated.");
    } else {
        nextEnrollmentRetryMs = millis() + NETWORK_RETRY_MS;
        transition(AttendanceState::OFFLINE, "ENROLL PENDING", "Saved; server confirmation retries");
        Serial.println("[WARN] Sensor template is stored. Backend completion is durably queued and will retry.");
    }
}
static void pollSerial() {
    while (Serial.available()) {
        const char c = static_cast<char>(Serial.read());
        if (c == '\r') continue;
        if (c == '\n') { serialLine[serialLength] = '\0'; handleSerialCommand(serialLine); serialLength = 0; }
        else if (serialLength + 1 < sizeof(serialLine)) serialLine[serialLength++] = c;
        else { serialLength = 0; Serial.println("[FAIL] Command too long; discarded."); }
    }
}
static void recordMatch(uint16_t slot) {
    char timestamp[32];
    if (!rtcService.timestamp(timestamp, sizeof(timestamp))) {
        indicators.failurePulse(); transition(AttendanceState::ERROR, "CLOCK INVALID", "Attendance not recorded");
        Serial.println("[FAIL] No trustworthy RTC time; fingerprint match was not converted to attendance."); return;
    }
    AttendanceEvent event{}; uuidV4(event.uuid); event.slot = slot;
    strlcpy(event.capturedAt, timestamp, sizeof(event.capturedAt));
    strlcpy(event.syncStatus, "LIVE", sizeof(event.syncStatus));
    transition(AttendanceState::ATTENDANCE_RECORDED, "SAVING", "Writing durable event");
    if (!store.append(event)) {
        indicators.failurePulse(); transition(AttendanceState::ERROR, "STORAGE ERROR", "Attendance not accepted");
        Serial.println("[FAIL] Durable queue write failed/full; event was not acknowledged or discarded silently."); return;
    }
    if (network.sendAttendance(event, false) && store.acknowledge(event.uuid)) {
        indicators.successPulse(); transition(AttendanceState::ATTENDANCE_RECORDED, "ATTENDANCE OK", "Server accepted event");
        Serial.printf("[PASS] Event acknowledged by API (slot %u, UUID %s).\n", slot, event.uuid);
    } else {
        indicators.successPulse();
        transition(AttendanceState::OFFLINE, "SAVED LOCALLY", "Will sync when online");
        Serial.printf("[INFO] Event durably queued for retry (slot %u, UUID %s).\n", slot, event.uuid);
    }
    lastMatchedMs = millis();
    resultScreenActive = true; showResultUntilMs = lastMatchedMs + 1800;
}
static void syncOne() {
    if (!network.connected() || !store.healthy() || static_cast<int32_t>(millis() - nextSyncMs) < 0) return;
    nextSyncMs = millis() + NETWORK_RETRY_MS;
    AttendanceEvent event{};
    if (!store.nextPending(event)) return;
    transition(AttendanceState::SYNCING, "SYNCING", "Sending saved event");
    if (network.sendAttendance(event, true)) {
        if (store.acknowledge(event.uuid)) {
            Serial.printf("[PASS] Replayed event %s accepted by API.\n", event.uuid);
            transition(AttendanceState::WAITING_FOR_FINGER, "READY", "Saved event synchronized");
        } else transition(AttendanceState::ERROR, "STORAGE ERROR", "Sync ack not saved");
    } else transition(AttendanceState::OFFLINE, "SYNC PENDING", "Event retained for retry");
}

void attendance_app_setup() {
    Serial.begin(115200); delay(250);
    Serial.println("BIOMETRIC ATTENDANCE DEVICE - local-first demo firmware");
    Serial.println("[INFO] OLED removed from this project. Status is reported on the serial console only.");
    indicators.begin(); enrollmentPrefs.begin("attendance", false);
    EnrollmentIntent bootIntent{};
    if (enrollmentIntentPresent() && !loadIntent(bootIntent)) Serial.println("[CRITICAL] Stored enrollment intent is corrupt; manual sensor/backend reconciliation is required.");
    transition(AttendanceState::SELF_TEST, "SELF TEST", "Starting local services");
    const bool rtcOk = rtcService.begin();
    const bool storageOk = store.begin();
    network.begin();
    const bool sensorOk = fingerprint.begin();
    bleManager.configure(&rtcService, &fingerprint, &indicators, &store);
    const bool bleOk = bleManager.begin(DEVICE_NAME);
    Serial.printf("[INFO] reset=%d heap=%u RTC=%s storage=%s sensor=%s BLE=%s\n", static_cast<int>(esp_reset_reason()), ESP.getFreeHeap(), rtcOk?"VALID":"INVALID", storageOk?"READY":"ERROR", sensorOk?"READY":"UNAVAILABLE", bleOk?"ADVERTISING":"OFF");
    if (sensorOk) {
        uint16_t capacity = 0, used = 0;
        if (fingerprint.readInventory(capacity, used)) Serial.printf("[INFO] sensor template inventory: capacity=%u occupied=%u\n", capacity, used);
    }
    if (!storageOk) { transition(AttendanceState::ERROR, "STORAGE ERROR", "No scan accepted"); Serial.println("[FAIL] LittleFS missing/corrupt. It is not auto-formatted to protect queued data."); }
    if (!sensorOk) {
        nextSensorProbeMs = millis() + SENSOR_RETRY_MS;
        transition(AttendanceState::ERROR, "SENSOR NOT FOUND", "Retrying; check hardware");
        Serial.println("[WARN] Sensor response unavailable; this does not prove module failure. Power/logic remain unverified.");
    } else if (!rtcOk) transition(AttendanceState::ERROR, "RTC INVALID", "No timestamps accepted");
    else if (!storageOk) transition(AttendanceState::ERROR, "STORAGE ERROR", "No scan accepted");
    else transition(AttendanceState::WAITING_FOR_FINGER, network.connected()?"READY":"OFFLINE", network.connected()?"Scan finger":"Offline queue enabled");
    completePendingEnrollment();
}

void attendance_app_loop() {
    pollSerial(); network.pollReconnect();
    if (nextEnrollmentRetryMs && static_cast<int32_t>(millis() - nextEnrollmentRetryMs) >= 0) completePendingEnrollment();
    syncOne();
    const uint32_t now = millis();
    if (resultScreenActive && static_cast<int32_t>(now - showResultUntilMs) >= 0) {
        resultScreenActive = false;
        if (fingerprint.ready() && rtcService.valid() && store.healthy()) transition(AttendanceState::WAITING_FOR_FINGER, network.connected()?"READY":"OFFLINE", "Scan finger");
    }
    if (state == AttendanceState::OFFLINE && network.connected() && store.healthy() && store.pendingCount() == 0 && rtcService.valid() && fingerprint.ready())
        transition(AttendanceState::WAITING_FOR_FINGER, "READY", "Network restored");
    if (!resultScreenActive && state == AttendanceState::WAITING_FOR_FINGER && now - lastClockDisplayMs >= 5000) {
        char stamp[32] = "";
        if (rtcService.timestamp(stamp, sizeof(stamp))) {
            Serial.printf("[CLOCK] %s — %s\n", network.connected() ? "READY" : "OFFLINE", stamp);
        }
        lastClockDisplayMs = now;
    }
    if (!fingerprint.ready()) {
        if (static_cast<int32_t>(now - nextSensorProbeMs) >= 0) {
            transition(AttendanceState::RECOVERY, "CHECKING SENSOR", "Bounded handshake retry");
            if (fingerprint.begin() && rtcService.valid() && store.healthy()) transition(AttendanceState::WAITING_FOR_FINGER, "READY", "Scan finger");
            else if (fingerprint.ready() && !rtcService.valid()) transition(AttendanceState::ERROR, "RTC INVALID", "No timestamps accepted");
            else if (fingerprint.ready() && !store.healthy()) transition(AttendanceState::ERROR, "STORAGE ERROR", "No scans accepted");
            else { nextSensorProbeMs = now + SENSOR_RETRY_MS; transition(AttendanceState::ERROR, "SENSOR NOT FOUND", "Retrying"); }
        }
        delay(10); return;
    }
    if (!store.healthy() || !rtcService.valid()) { delay(50); return; }
    if (now - lastMatchedMs < FINGER_DEBOUNCE_MS) { delay(10); return; }
    uint16_t slot = 0, confidence = 0;
    const FingerprintScan result = fingerprint.scan(slot, confidence);
    if (fingerLatched) {
        if (result == FingerprintScan::NO_FINGER) fingerLatched = false;
        delay(10);
        return;
    }
    if (result == FingerprintScan::MATCH) {
        fingerLatched = true;
        Serial.printf("[INFO] Fingerprint match in template slot %u (confidence %u). No identity is displayed.\n", slot, confidence);
        recordMatch(slot);
    } else if (result == FingerprintScan::NO_MATCH) {
        fingerLatched = true;
        indicators.failurePulse(); transition(AttendanceState::WAITING_FOR_FINGER, "NOT FOUND", "Try again"); lastMatchedMs = millis();
        resultScreenActive = true; showResultUntilMs = lastMatchedMs + 1400;
    } else if (result == FingerprintScan::SENSOR_ERROR) {
        nextSensorProbeMs = millis() + SENSOR_RETRY_MS; transition(AttendanceState::ERROR, "SENSOR ERROR", "Will retry");
    }
    delay(10);
}
