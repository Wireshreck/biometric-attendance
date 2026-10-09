#include "attendance_store.h"

#include <ArduinoJson.h>
#include <LittleFS.h>
#include <vector>
#include "config.h"

namespace {
struct Entry { AttendanceEvent event; bool acked; };
static bool tailWasTruncated = false;
// Serializes LittleFS access between the main loop task and the BLE task.
// LittleFS is not thread-safe; concurrent opens from two tasks corrupt the
// heap and crash the device (observed via BLE ATTENDANCE_* commands).
struct StoreLock {
    SemaphoreHandle_t m;
    bool held = false;
    explicit StoreLock(SemaphoreHandle_t mtx, uint32_t waitMs = 5000) : m(mtx) {
        if (m) held = xSemaphoreTake(m, pdMS_TO_TICKS(waitMs)) == pdTRUE;
    }
    ~StoreLock() { if (held) xSemaphoreGive(m); }
};
static uint32_t crc32(const uint8_t* data, size_t size) {
    uint32_t crc = 0xFFFFFFFFu;
    while (size--) {
        crc ^= *data++;
        for (uint8_t i = 0; i < 8; ++i) crc = (crc >> 1) ^ (0xEDB88320u & (-(int32_t)(crc & 1)));
    }
    return ~crc;
}
static bool writeLine(File& file, JsonDocument& doc) {
    String body;
    serializeJson(doc, body);
    char checksum[9]; snprintf(checksum, sizeof(checksum), "%08lX", static_cast<unsigned long>(crc32(reinterpret_cast<const uint8_t*>(body.c_str()), body.length())));
    return file.print(body) == body.length() && file.print('\t') == 1 && file.print(checksum) == 8 && file.print('\n') == 1;
}
static bool parseLine(const String& line, JsonDocument& doc) {
    const int tab = line.lastIndexOf('\t');
    if (tab < 1 || line.length() - tab != 9) return false;
    String body = line.substring(0, tab);
    char expected[9]; snprintf(expected, sizeof(expected), "%08lX", static_cast<unsigned long>(crc32(reinterpret_cast<const uint8_t*>(body.c_str()), body.length())));
    if (!line.substring(tab + 1).equalsIgnoreCase(expected)) return false;
    return deserializeJson(doc, body) == DeserializationError::Ok;
}
static bool loadEntries(std::vector<Entry>& entries) {
    entries.clear();
    tailWasTruncated = false;
    File file = LittleFS.open(QUEUE_PATH, "r");
    if (!file) return true;
    while (file.available()) {
        String line;
        bool terminated = false;
        while (file.available()) {
            const int c = file.read();
            if (c < 0) break;
            if (c == '\n') { terminated = true; break; }
            if (line.length() > 512) { file.close(); return false; }
            line += static_cast<char>(c);
        }
        JsonDocument doc;
        if (!parseLine(line, doc)) {
            // A truncated final append is a power-loss tail; do not reinterpret it as a record.
            if (!terminated && !file.available()) { tailWasTruncated = true; break; }
            file.close(); return false;
        }
        const char* kind = doc["kind"] | "event";
        if (strcmp(kind, "ack") == 0) {
            const char* id = doc["uuid"] | "";
            for (auto& item : entries) if (strcmp(item.event.uuid, id) == 0) item.acked = true;
        } else if (strcmp(kind, "event") == 0) {
            Entry item{};
            strlcpy(item.event.uuid, doc["uuid"] | "", sizeof(item.event.uuid));
            item.event.slot = doc["slot"] | 0;
            strlcpy(item.event.capturedAt, doc["captured_at"] | "", sizeof(item.event.capturedAt));
            strlcpy(item.event.syncStatus, doc["sync_status"] | "", sizeof(item.event.syncStatus));
            if (!item.event.uuid[0] || item.event.slot == 0 || !item.event.capturedAt[0]) { file.close(); return false; }
            entries.push_back(item);
        } else { file.close(); return false; }
    }
    file.close();
    return true;
}
}

bool AttendanceStore::begin() {
    if (!mutex_) mutex_ = xSemaphoreCreateMutex();
    StoreLock lock(mutex_);
    if (!lock.held) return false;
    if (!LittleFS.begin(false)) return false; // Never format automatically: unreadable data must be preserved.
    if (!LittleFS.exists(QUEUE_PATH) && LittleFS.exists("/attendance.bak")) LittleFS.rename("/attendance.bak", QUEUE_PATH);
    if (LittleFS.exists(QUEUE_PATH)) { LittleFS.remove("/attendance.tmp"); LittleFS.remove("/attendance.bak"); }
    if (!LittleFS.exists(QUEUE_PATH)) {
        File file = LittleFS.open(QUEUE_PATH, "w");
        if (!file) return false;
        file.close();
    }
    std::vector<Entry> entries;
    healthy_ = loadEntries(entries) && entries.size() <= QUEUE_MAX_PENDING;
    if (healthy_ && tailWasTruncated) healthy_ = compactLocked(); // Rewrite only complete, CRC-valid pending events before further appends.
    return healthy_;
}

namespace {
size_t countPendingEntries(std::vector<Entry>& entries) {
    size_t count = 0; for (const auto& item : entries) if (!item.acked) ++count;
    return count;
}
}  // namespace

bool AttendanceStore::append(const AttendanceEvent& event) {
    StoreLock lock(mutex_);
    if (!lock.held) return false;
    std::vector<Entry> entries;
    if (!healthy_ || !loadEntries(entries)) { healthy_ = false; return false; }
    if (countPendingEntries(entries) >= QUEUE_MAX_PENDING) return false;
    File file = LittleFS.open(QUEUE_PATH, "a");
    if (!file || file.size() >= QUEUE_MAX_BYTES) { if (file) file.close(); return false; }
    JsonDocument doc; doc["kind"] = "event"; doc["uuid"] = event.uuid; doc["slot"] = event.slot;
    doc["captured_at"] = event.capturedAt; doc["sync_status"] = event.syncStatus;
    const bool ok = writeLine(file, doc); file.flush(); file.close();
    if (!ok) healthy_ = false;
    return ok;
}

bool AttendanceStore::nextPending(AttendanceEvent& event) {
    StoreLock lock(mutex_);
    if (!lock.held) return false;
    std::vector<Entry> entries;
    if (!healthy_ || !loadEntries(entries)) { healthy_ = false; return false; }
    for (const auto& item : entries) if (!item.acked) { event = item.event; return true; }
    return false;
}

bool AttendanceStore::acknowledge(const char* uuid) {
    StoreLock lock(mutex_);
    if (!lock.held) return false;
    if (!healthy_) return false;
    File file = LittleFS.open(QUEUE_PATH, "a");
    if (!file || file.size() >= QUEUE_MAX_BYTES) { if (file) file.close(); return false; }
    JsonDocument doc; doc["kind"] = "ack"; doc["uuid"] = uuid;
    const bool ok = writeLine(file, doc); file.flush(); file.close();
    if (ok) {
        // Compaction removes only events that have an appended durable acknowledgement.
        std::vector<Entry> entries;
        if (!loadEntries(entries)) { healthy_ = false; return false; }
        if (!entries.empty() && countPendingEntries(entries) * 2 < entries.size()) compactLocked();
    } else healthy_ = false;
    return ok;
}

size_t AttendanceStore::pendingCount() {
    StoreLock lock(mutex_);
    if (!lock.held) return QUEUE_MAX_PENDING;
    std::vector<Entry> entries;
    if (!healthy_ || !loadEntries(entries)) { healthy_ = false; return QUEUE_MAX_PENDING; }
    return countPendingEntries(entries);
}

size_t AttendanceStore::totalCount() {
    StoreLock lock(mutex_);
    if (!lock.held) return 0;
    std::vector<Entry> entries;
    if (!healthy_ || !loadEntries(entries)) { healthy_ = false; return 0; }
    return entries.size();
}

bool AttendanceStore::readAll(AttendanceEvent* out, size_t capacity, size_t& count) {
    StoreLock lock(mutex_);
    if (!lock.held) return false;
    count = 0;
    std::vector<Entry> entries;
    if (!healthy_ || !loadEntries(entries)) { healthy_ = false; return false; }
    for (const auto& item : entries) {
        if (item.acked) continue;
        if (count >= capacity) return true;
        out[count++] = item.event;
    }
    return true;
}

bool AttendanceStore::clear() {
    StoreLock lock(mutex_);
    if (!lock.held) return false;
    if (!healthy_) return false;
    LittleFS.remove("/attendance.tmp");
    File file = LittleFS.open(QUEUE_PATH, "w");
    if (!file) { healthy_ = false; return false; }
    file.close();
    return true;
}

bool AttendanceStore::compactLocked() {
    std::vector<Entry> entries;
    if (!loadEntries(entries)) { healthy_ = false; return false; }
    const char* temp = "/attendance.tmp"; const char* backup = "/attendance.bak";
    LittleFS.remove(temp);
    File output = LittleFS.open(temp, "w");
    if (!output) return false;
    bool ok = true;
    for (const auto& item : entries) if (!item.acked) {
        JsonDocument doc; doc["kind"] = "event"; doc["uuid"] = item.event.uuid; doc["slot"] = item.event.slot;
        doc["captured_at"] = item.event.capturedAt; doc["sync_status"] = item.event.syncStatus;
        if (!writeLine(output, doc)) { ok = false; break; }
    }
    output.flush(); output.close();
    if (!ok) { LittleFS.remove(temp); return false; }
    LittleFS.remove(backup);
    if (!LittleFS.rename(QUEUE_PATH, backup)) { LittleFS.remove(temp); return false; }
    if (!LittleFS.rename(temp, QUEUE_PATH)) {
        LittleFS.rename(backup, QUEUE_PATH); healthy_ = false; return false;
    }
    LittleFS.remove(backup);
    return true;
}
