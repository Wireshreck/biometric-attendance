#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "config.h"
#include "test_result.h"
void setup() {
    Serial.begin(115200);
    delay(300);
    TestResult result("LOCAL BACKEND HTTP TEST (SAFE HEALTH GET)");
    if (DEFAULT_WIFI_SSID[0] == '\0' || DEFAULT_WIFI_PASSWORD[0] == '\0') {
        result.skip("Wi-Fi and backend HTTP", "configure ignored local_config.h with isolated demo Wi-Fi first");
        result.finish();
        return;
    }
    WiFi.mode(WIFI_STA);
    WiFi.begin(DEFAULT_WIFI_SSID, DEFAULT_WIFI_PASSWORD);
    const uint32_t start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - start < 15000) delay(100);
    if (WiFi.status() != WL_CONNECTED) {
        result.check(false, "Connected to configured local test Wi-Fi", "timeout");
        result.finish();
        return;
    }
    result.check(true, "Connected to configured local test Wi-Fi");
    const String url = String("http://") + DEFAULT_SERVER_HOST + ":" + String(DEFAULT_SERVER_PORT) + "/health";
    HTTPClient http;
    http.setConnectTimeout(3000);
    http.setTimeout(3000);
    result.check(http.begin(url), "HTTP client initialized", "local /health only; no attendance event is submitted");
    const int status = http.GET();
    const String body = status > 0 ? http.getString() : String();
    Serial.printf("[INFO] GET /health status=%d response_bytes=%u\n", status, static_cast<unsigned>(body.length()));
    result.check(status == 200, "Backend returned HTTP 200", "verify backend host/bind/firewall");
    JsonDocument doc;
    const DeserializationError error = deserializeJson(doc, body);
    result.check(!error && doc["status"] == "ok", "Health response parsed as JSON");
    http.end();
    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);
    result.info("Attendance POST is intentionally disabled here; use backend API tests and synthetic local fixtures for payload validation.");
    result.finish();
}
void loop() { delay(1000); }
