#include "network_service.h"

#include <HTTPClient.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include "config.h"

namespace {
static bool configured() { return DEFAULT_WIFI_SSID[0] && DEFAULT_WIFI_PASSWORD[0]; }
static String baseUrl() { return String("http://") + DEFAULT_SERVER_HOST + ":" + String(DEFAULT_SERVER_PORT); }
static bool deviceConfigured() { return DEVICE_UUID[0] && DEVICE_TOKEN[0]; }
static bool request(const String& method, const String& path, const String* body, String& response, int& status) {
    if (WiFi.status() != WL_CONNECTED) return false;
    HTTPClient http;
    http.setTimeout(HTTP_TIMEOUT_MS);
    http.setReuse(false);
    if (!http.begin(baseUrl() + path)) return false;
    if (deviceConfigured()) http.addHeader("Authorization", String("Bearer ") + DEVICE_TOKEN);
    if (body) http.addHeader("Content-Type", "application/json");
    int code = -1;
    if (method == "GET") code = http.GET();
    else if (body) code = http.POST(*body);
    status = code;
    if (code > 0) response = http.getString();
    if (code > 0 && (code < 200 || code > 299)) Serial.printf("[WARN] Local API returned HTTP %d for %s\n", code, path.c_str());
    http.end();
    return code > 0;
}
static String encode(const JsonDocument& doc) { String out; serializeJson(doc, out); return out; }
static bool validUuidText(const char* value) {
    if (!value || strlen(value) != 36) return false;
    for (size_t i=0; i<36; ++i) if (!(isxdigit(value[i]) || (i==8 || i==13 || i==18 || i==23) && value[i]=='-')) return false;
    return true;
}
}

void NetworkService::begin() {
    WiFi.mode(WIFI_STA);
    WiFi.setAutoReconnect(true);
    if (configured()) WiFi.begin(DEFAULT_WIFI_SSID, DEFAULT_WIFI_PASSWORD);
    retryAt_ = millis() + NETWORK_RETRY_MS;
}

bool NetworkService::connected() const { return WiFi.status() == WL_CONNECTED; }

void NetworkService::pollReconnect() {
    if (!configured() || connected() || static_cast<int32_t>(millis() - retryAt_) < 0) return;
    WiFi.disconnect(false, false);
    WiFi.begin(DEFAULT_WIFI_SSID, DEFAULT_WIFI_PASSWORD);
    retryAt_ = millis() + NETWORK_RETRY_MS;
}

bool NetworkService::sendAttendance(const AttendanceEvent& event, bool replay) {
    if (!deviceConfigured() || !validUuidText(event.uuid) || !connected()) return false;
    JsonDocument payload;
    payload["event_uuid"] = event.uuid;
    payload["fingerprint_slot_id"] = event.slot;
    payload["captured_at"] = event.capturedAt;
    payload["sync_status"] = replay ? "REPLAYED_OFFLINE" : "LIVE";
    String body = encode(payload), response; int status = 0;
    if (!request("POST", ATTENDANCE_ENDPOINT, &body, response, status) || (status != 200 && status != 201)) return false;
    JsonDocument result;
    if (deserializeJson(result, response) != DeserializationError::Ok) return false;
    const char* id = result["event_uuid"] | "";
    const char* outcome = result["outcome"] | "";
    return strcmp(id, event.uuid) == 0 && (strcmp(outcome, "RECORDED") == 0 || strcmp(outcome, "DUPLICATE_SUPPRESSED") == 0);
}

bool NetworkService::enrollmentAssignment(const char* studentUuid, uint16_t& slot) {
    if (!deviceConfigured() || !validUuidText(studentUuid)) return false;
    String path = String("/api/v1/devices/") + DEVICE_UUID + "/enrollment/" + studentUuid, response; int status = 0;
    if (!request("GET", path, nullptr, response, status) || status != 200) return false;
    JsonDocument result;
    if (deserializeJson(result, response) != DeserializationError::Ok) return false;
    const char* returned = result["student_uuid"] | "";
    const unsigned int candidate = result["fingerprint_slot_id"] | 0;
    const unsigned int capacity = result["capacity"] | 0;
    if (strcmp(returned, studentUuid) != 0 || candidate < 1 || candidate > capacity || candidate > UINT16_MAX) return false;
    slot = static_cast<uint16_t>(candidate);
    return true;
}

bool NetworkService::enrollmentComplete(const char* studentUuid, uint16_t slot) {
    if (!deviceConfigured() || !validUuidText(studentUuid)) return false;
    JsonDocument payload; payload["result"] = "SUCCESS"; payload["fingerprint_slot_id"] = slot;
    String body = encode(payload), response; int status = 0;
    String path = String("/api/v1/devices/") + DEVICE_UUID + "/enrollment/" + studentUuid + "/complete";
    if (!request("POST", path, &body, response, status) || status != 200) return false;
    JsonDocument result;
    if (deserializeJson(result, response) != DeserializationError::Ok) return false;
    return strcmp(result["student_uuid"] | "", studentUuid) == 0 && strcmp(result["status"] | "", "ACTIVE") == 0;
}
