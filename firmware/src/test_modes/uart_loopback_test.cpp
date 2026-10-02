#include <Arduino.h>
#include "test_result.h"

#ifndef UART_TEST_PORT
#define UART_TEST_PORT 2
#endif
#ifndef UART_TEST_RX_PIN
#define UART_TEST_RX_PIN 26
#endif
#ifndef UART_TEST_TX_PIN
#define UART_TEST_TX_PIN 25
#endif
#ifndef UART_TEST_BAUD
#define UART_TEST_BAUD 57600
#endif

static HardwareSerial& testUart = (UART_TEST_PORT == 1) ? Serial1 : Serial2;
static uint16_t crc16(const uint8_t* data, size_t size) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < size; ++i) {
        crc ^= static_cast<uint16_t>(data[i]) << 8;
        for (uint8_t bit = 0; bit < 8; ++bit)
            crc = (crc & 0x8000) ? static_cast<uint16_t>((crc << 1) ^ 0x1021) : static_cast<uint16_t>(crc << 1);
    }
    return crc;
}

void setup() {
    Serial.begin(115200);
    delay(300);
    TestResult result("UART LOOPBACK TEST");
    Serial.printf("[INFO] UART%u RX=GPIO%u TX=GPIO%u baud=%u\n",
                  UART_TEST_PORT, UART_TEST_RX_PIN, UART_TEST_TX_PIN, UART_TEST_BAUD);
    result.info("Install a jumper from the listed TX GPIO to RX GPIO. Do not use the R307S as the loopback device.");
    testUart.begin(UART_TEST_BAUD, SERIAL_8N1, UART_TEST_RX_PIN, UART_TEST_TX_PIN);
    delay(20);
    while (testUart.available()) testUart.read();
    uint8_t sent[18];
    for (uint8_t i = 0; i < 16; ++i) sent[i] = static_cast<uint8_t>(0x30 + i * 7);
    const uint16_t expectedCrc = crc16(sent, 16);
    sent[16] = static_cast<uint8_t>(expectedCrc >> 8);
    sent[17] = static_cast<uint8_t>(expectedCrc);
    testUart.write(sent, sizeof(sent));
    testUart.flush();
    result.check(true, "UART initialized and test pattern transmitted");

    uint8_t received[sizeof(sent)]{};
    size_t count = 0;
    const uint32_t start = millis();
    while (millis() - start < 1000 && count < sizeof(received)) {
        if (testUart.available()) received[count++] = static_cast<uint8_t>(testUart.read());
        else delay(1);
    }
    const bool exact = count == sizeof(sent) && memcmp(sent, received, sizeof(sent)) == 0;
    const uint16_t receivedCrc = count >= 2 ? static_cast<uint16_t>((received[count - 2] << 8) | received[count - 1]) : 0;
    result.check(exact, "Received byte-for-byte loopback", "expected 18 bytes; verify jumper if this fails");
    result.check(exact && receivedCrc == crc16(received, count - 2), "Payload checksum");
    Serial.printf("[INFO] RX bytes=%u timeout_ms=1000\n", static_cast<unsigned>(count));
    result.finish();
}

void loop() { delay(1000); }
