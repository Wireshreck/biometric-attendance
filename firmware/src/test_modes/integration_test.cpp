#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <RTClib.h>
#include <ArduinoJson.h>
#include "config.h"
#include "test_result.h"
#include "r307s_uart_diag.h"

#ifndef INTEGRATION_CASE
#define INTEGRATION_CASE 1
#endif

static Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
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
        "INT-01 ESP32 + OLED", "INT-02 ESP32 + RTC", "INT-03 ESP32 + indicators",
        "INT-04 ESP32 + R307S", "INT-05 R307S + OLED", "INT-06 R307S + RTC",
        "INT-07 ESP32 + Wi-Fi", "INT-08 ESP32 + backend", "INT-09 Full hardware integration"
    };
    TestResult result(titles[INTEGRATION_CASE - 1]);

#if INTEGRATION_CASE == 1 || INTEGRATION_CASE == 5 || INTEGRATION_CASE == 9
    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL, 100000);
    const bool oledOk = display.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDR);
    result.check(oledOk, "OLED initialized at configured address");
    if (oledOk) { display.clearDisplay(); display.setTextColor(SSD1306_WHITE); display.setCursor(0, 0); display.println("INTEGRATION"); display.println("OLED linked"); display.display(); result.unverified("Confirm integration text is visible on the OLED."); }
#endif

#if INTEGRATION_CASE == 2 || INTEGRATION_CASE == 6 || INTEGRATION_CASE == 9
    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL, 100000);
    const bool rtcOk = rtc.begin();
    result.check(rtcOk, "RTC initialized at configured address");
    if (rtcOk) {
        const DateTime now = rtc.now();
        const bool valid = now.year() >= 2024 && now.year() <= 2099 && !rtc.lostPower();
        result.check(valid, "RTC time appears valid and oscillator has not stopped");
    }
#endif

#if INTEGRATION_CASE == 3 || INTEGRATION_CASE == 9
    pinMode(PIN_LED_GREEN, OUTPUT); pinMode(PIN_LED_RED, OUTPUT); pinMode(PIN_BUZZER, OUTPUT);
    digitalWrite(PIN_LED_RED, LOW); digitalWrite(PIN_BUZZER, LOW); digitalWrite(PIN_LED_GREEN, HIGH); delay(250);
    digitalWrite(PIN_LED_GREEN, LOW); digitalWrite(PIN_LED_RED, HIGH); delay(250);
    digitalWrite(PIN_LED_RED, LOW); digitalWrite(PIN_BUZZER, HIGH); delay(80); digitalWrite(PIN_BUZZER, LOW);
    result.check(true, "Green/red/buzzer output sequence executed");
    result.unverified("Confirm LED light and buzzer sound physically; firmware cannot sense them.");
#endif

#if INTEGRATION_CASE == 4 || INTEGRATION_CASE == 5 || INTEGRATION_CASE == 6 || INTEGRATION_CASE == 9
    result.info("R307S diagnostic is read-only. 0-byte result means no valid communication, not proof of sensor failure.");
    result.check(r307s_uart_diag_run(), "R307S returned valid success ACK");
#endif

#if INTEGRATION_CASE == 7 || INTEGRATION_CASE == 9
    WiFi.mode(WIFI_STA);
    const int visible = WiFi.scanNetworks(false, true);
    result.check(visible >= 0, "Wi-Fi radio scan completed");
    Serial.printf("[INFO] visible_network_count=%d\n", visible);
    WiFi.scanDelete();
    if (DEFAULT_WIFI_SSID[0] != '\0' && DEFAULT_WIFI_PASSWORD[0] != '\0') connectWifi(result);
    else result.skip("Wi-Fi association", "no local credentials configured");
    WiFi.disconnect(false, false); WiFi.mode(WIFI_OFF);
#endif

#if INTEGRATION_CASE == 8 || INTEGRATION_CASE == 9
    backendHealth(result);
    WiFi.disconnect(false, false); WiFi.mode(WIFI_OFF);
#endif

#if INTEGRATION_CASE == 9
    result.info("RTC/OLED are shared on I2C. Ensure GPIO18/19/23 are correctly resistor/driver protected.");
    result.info("Offline queue, fingerprint match/enrollment, and attendance POST are not implemented by this integration test.");
#endif
    result.finish();
}

void loop() { delay(1000); }
