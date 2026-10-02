#include <Arduino.h>
#include "esp_system.h"
#include "test_result.h"
void setup() {
    const uint32_t bootAt = millis();
    Serial.begin(115200);
    delay(300);
    TestResult result("POWER / RESET SOFTWARE DIAGNOSTICS");
    const esp_reset_reason_t reason = esp_reset_reason();
    Serial.printf("[INFO] reset_reason=%d free_heap=%u min_heap=%u boot_ms=%u cpu_mhz=%u\n",
                  static_cast<int>(reason), ESP.getFreeHeap(), ESP.getMinFreeHeap(), bootAt, ESP.getCpuFreqMHz());
    result.check(ESP.getFreeHeap() > 0, "Heap telemetry available");
    result.check(ESP.getCpuFreqMHz() > 0, "CPU telemetry available");
    result.info("Reset reason may indicate brownout; software cannot measure rail voltage, current, ripple, or prove supply adequacy.");
    result.finish();
}
void loop() { delay(1000); }
