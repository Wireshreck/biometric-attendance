#include <Arduino.h>
#include <LittleFS.h>
#include "test_result.h"

static uint32_t checksum(const uint8_t* data, size_t size) {
    uint32_t value = 2166136261u;
    for (size_t i = 0; i < size; ++i) value = (value ^ data[i]) * 16777619u;
    return value;
}
void setup() {
    Serial.begin(115200);
    delay(300);
    TestResult result("LITTLEFS STORAGE TEST");
    const bool mounted = LittleFS.begin(false);
    result.check(mounted, "LittleFS mounted without formatting", "test never erases/formats the filesystem");
    if (mounted) {
        const char* path = "/diag-storage-test.bin";
        const uint8_t record[] = {0xBA, 0x55, 0x01, 0x02, 0x03, 0x04};
        const uint32_t crc = checksum(record, sizeof(record));
        File file = LittleFS.open(path, "w");
        const bool wrote = file && file.write(record, sizeof(record)) == sizeof(record) && file.write(reinterpret_cast<const uint8_t*>(&crc), sizeof(crc)) == sizeof(crc);
        if (file) file.close();
        result.check(wrote, "Test record written");
        file = LittleFS.open(path, "r");
        uint8_t loaded[sizeof(record)]{};
        uint32_t savedCrc = 0;
        const bool readOk = file && file.read(loaded, sizeof(loaded)) == sizeof(loaded) && file.read(reinterpret_cast<uint8_t*>(&savedCrc), sizeof(savedCrc)) == sizeof(savedCrc);
        if (file) file.close();
        result.check(readOk && memcmp(record, loaded, sizeof(record)) == 0, "Test record read back");
        result.check(readOk && savedCrc == checksum(loaded, sizeof(loaded)), "Record checksum validates");
        loaded[2] ^= 0xFF;
        result.check(savedCrc != checksum(loaded, sizeof(loaded)), "Corrupt record detected");
        LittleFS.remove(path);
        result.check(!LittleFS.exists(path), "Diagnostic record cleaned up");
    }
    result.info("This validates a local checksum primitive, not an attendance queue/recovery implementation.");
    result.finish();
}
void loop() { delay(1000); }
