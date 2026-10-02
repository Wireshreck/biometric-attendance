#include <Arduino.h>
#include "test_result.h"

void setup() {
    Serial.begin(115200);
    delay(500);
    TestResult result("ESP32 CORE TEST");
    result.info(ESP.getChipModel());
    result.check(ESP.getCpuFreqMHz() > 0, "CPU frequency available");
    result.check(ESP.getFreeHeap() > 0, "Heap available");
    result.check(ESP.getFlashChipSize() >= 1024 * 1024, "Flash size reported");
    Serial.printf("[INFO] revision=%u cores=%u heap=%u flash=%u reset=%d\n",
                  ESP.getChipRevision(), ESP.getChipCores(), ESP.getFreeHeap(),
                  ESP.getFlashChipSize(), static_cast<int>(esp_reset_reason()));
    result.info("No arbitrary GPIO is driven by this test.");
    result.finish();
}

void loop() { delay(1000); }
