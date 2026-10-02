#include <Arduino.h>
#include <WiFi.h>
#include "config.h"
#include "test_result.h"
void setup() {
    Serial.begin(115200);
    delay(300);
    TestResult result("WIFI RADIO TEST");
    WiFi.mode(WIFI_STA);
    WiFi.disconnect(false, false);
    const int found = WiFi.scanNetworks(false, true);
    result.check(found >= 0, "Wi-Fi radio initialized and scan completed", "SSID values are intentionally not logged");
    Serial.printf("[INFO] visible_network_count=%d\n", found);
    if (DEFAULT_WIFI_SSID[0] != '\0' && DEFAULT_WIFI_PASSWORD[0] != '\0') {
        WiFi.begin(DEFAULT_WIFI_SSID, DEFAULT_WIFI_PASSWORD);
        const uint32_t started = millis();
        while (WiFi.status() != WL_CONNECTED && millis() - started < 15000) delay(100);
        const bool connected = WiFi.status() == WL_CONNECTED;
        result.check(connected, "Configured Wi-Fi connection", connected ? "connected; credential not logged" : "timeout");
        if (connected) {
            Serial.printf("[INFO] RSSI=%d IP=%s gateway=%s DNS=%s\n", WiFi.RSSI(), WiFi.localIP().toString().c_str(), WiFi.gatewayIP().toString().c_str(), WiFi.dnsIP().toString().c_str());
            WiFi.disconnect(true);
        }
    } else result.skip("Wi-Fi association / DHCP", "local_config.h must contain isolated test credentials");
    WiFi.mode(WIFI_OFF);
    result.finish();
}
void loop() { delay(1000); }
