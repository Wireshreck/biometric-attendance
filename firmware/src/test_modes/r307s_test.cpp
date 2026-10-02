#include <Arduino.h>
#include "test_result.h"
#include "r307s_uart_diag.h"

void setup() {
    Serial.begin(115200);
    delay(500);
    TestResult result("R307S UART TEST (READ ONLY)");
    const bool acknowledged = r307s_uart_diag_run();
    result.check(acknowledged, "Sensor returned checksum-valid success ACK", "zero response does not prove the sensor is dead");
    result.info("Only VerifyPassword, ReadSysPara, and TemplateCount are sent; no template-changing commands.");
    result.finish();
}

void loop() { delay(1000); }
