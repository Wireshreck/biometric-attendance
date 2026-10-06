#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <RTClib.h>
#include <ArduinoJson.h>
#include "config.h"
#include "test_result.h"
#include "r307s_uart_diag.h"

#ifndef INTEGRATION_CASE
#define INTEGRATION_CASE 1
#endif

static RTC_DS3231 rtc;

static bool connectWifi(TestResult& result) {
    if (DEFAULT_WIFI_SSID[0] == '\0' || DEFAULT_WIFI_PASSWORD[0] == '\0') {
        result.skip("Wi-Fi connection", "local_config.h has no isolated test credentials");
        return false;
    }
    WiFi.mode(WIFI_STA);
    WiFi.begin(DEFAULT_WIFI_SSID, DEFAULT_WIFI_PASSWORD);
    const uint32_t started = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - started < 15000) delay(100);
    const bool connected = WiFi.status() == WL_CONNECTED;
    result.check(connected, "Wi-Fi association", "15 second timeout");
    if (connected) Serial.printf("[INFO] IP=%s RSSI=%d\n", WiFi.localIP().toString().c_str(), WiFi.RSSI());
    return connected;
}

static bool backendHealth(TestResult& result) {
    if (!connectWifi(result)) return false;
    const String url = String("http://") + DEFAULT_SERVER_HOST + ":" + String(DEFAULT_SERVER_PORT) + "/health";
    HTTPClient http;
    http.setConnectTimeout(3000);
    http.setTimeout(3000);
    const bool started = http.begin(url);
    result.check(started, "HTTP health client initialized");
    if (!started) return false;
    const int status = http.GET();
    const String body = status > 0 ? http.getString() : String();
    result.check(status == 200, "Backend /health HTTP status", "GET only; no attendance record submitted");
    JsonDocument doc;
    const DeserializationError error = deserializeJson(doc, body);
    result.check(!error && doc["status"] == "ok", "Backend health JSON parsed");
    http.end();
    return status == 200 && !error;
}

void setup() {
    Serial.begin(115200);
    delay(400);
    const char* titles[] = {
        "INT-02 ESP32 + RTC", "INT-04 ESP32 + R307S", "INT-06 R307S + RTC",
        "INT-07 ESP32 + Wi-Fi", "INT-08 ESP32 + backend", "INT-09 Full hardware integration"
    };
    TestResult result(titles[INTEGRATION_CASE - 1]);

#if INTEGRATION_CASE == 1 || INTEGRATION_CASE == 3 || INTEGRATION_CASE == 6
    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL, 100000);
    const bool rtcOk = rtc.begin();
    result.check(rtcOk, "RTC initialized at configured address");
    if (rtcOk) {
        const DateTime now = rtc.now();
        const bool valid = now.year() >= 2024 && now.year() <= 2099 && !rtc.lostPower();
        result.check(valid, "RTC time appears valid and oscillator has not stopped");
    }
#endif

#if INTEGRATION_CASE == 2 || INTEGRATION_CASE == 3 || INTEGRATION_CASE == 6
    result.info("R307S diagnostic is read-only. 0-byte result means no valid communication, not proof of sensor failure.");
    result.check(r307s_uart_diag_run(), "R307S returned valid success ACK");
#endif

#if INTEGRATION_CASE == 4 || INTEGRATION_CASE == 6
    WiFi.mode(WIFI_STA);
    const int visible = WiFi.scanNetworks(false, true);
    result.check(visible >= 0, "Wi-Fi radio scan completed");
    Serial.printf("[INFO] visible_network_count=%d\n", visible);
    WiFi.scanDelete();
    if (DEFAULT_WIFI_SSID[0] != '\0' && DEFAULT_WIFI_PASSWORD[0] != '\0') connectWifi(result);
    else result.skip("Wi-Fi association", "no local credentials configured");
    WiFi.disconnect(false, false); WiFi.mode(WIFI_OFF);
#endif

#if INTEGRATION_CASE == 5 || INTEGRATION_CASE == 6
    backendHealth(result);
    WiFi.disconnect(false, false); WiFi.mode(WIFI_OFF);
#endif

#if INTEGRATION_CASE == 6
    result.info("This integration image covers RTC, R307S, Wi-Fi and backend. OLED and indicator LEDs were removed from this project; see config.h and final-pin-map.md.");
    result.info("Offline queue, fingerprint match/enrollment, and attendance POST are not implemented by this integration test.");
#endif
    result.finish();
}

void loop() { delay(1000); }
