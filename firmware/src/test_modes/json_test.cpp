#include <Arduino.h>
#include <ArduinoJson.h>
#include "test_result.h"
void setup() {
    Serial.begin(115200);
    delay(300);
    TestResult result("ATTENDANCE JSON TEST");
    JsonDocument source;
    source["event_uuid"] = "00000000-0000-4000-8000-000000000001";
    source["fingerprint_slot_id"] = 7;
    source["captured_at"] = "2026-10-02T08:15:30+05:30";
    source["sync_status"] = "LIVE";
    String payload;
    const size_t bytes = serializeJson(source, payload);
    result.check(bytes > 0, "Attendance payload serialized");
    JsonDocument parsed;
    const DeserializationError error = deserializeJson(parsed, payload);
    result.check(!error, "Serialized payload deserialized");
    result.check(parsed["fingerprint_slot_id"] == 7 && parsed["sync_status"] == "LIVE" && parsed["captured_at"].is<const char*>(), "Payload fields match backend schema");
    Serial.printf("[INFO] payload_bytes=%u\n", static_cast<unsigned>(bytes));
    result.info("Synthetic data only; this test sends nothing over the network.");
    result.finish();
}
void loop() { delay(1000); }
