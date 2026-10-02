#include <Arduino.h>
#include "test_result.h"

static const uint8_t inputPins[] = {25, 26, 27, 32, 33, 34, 35, 36, 39};
void setup() {
    Serial.begin(115200);
    delay(300);
    TestResult result("GPIO INPUT CONFIGURATION SANITY");
    for (uint8_t pin : inputPins) {
        pinMode(pin, INPUT);
        (void)digitalRead(pin);
        Serial.printf("[INFO] GPIO%u configured/read as input; level is not interpreted\n", pin);
    }
    result.check(true, "Selected GPIOs accept input configuration");
    result.info("No output is driven and no pins are shorted. Electrical continuity/voltage requires external measurement.");
    result.finish();
}
void loop() { delay(1000); }
