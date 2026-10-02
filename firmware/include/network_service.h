#pragma once
#include <Arduino.h>
#include "attendance_store.h"

class NetworkService {
public:
    void begin();
    bool connected() const;
    bool sendAttendance(const AttendanceEvent& event, bool replay);
    bool enrollmentAssignment(const char* studentUuid, uint16_t& slot);
    bool enrollmentComplete(const char* studentUuid, uint16_t slot);
    void pollReconnect();
private:
    uint32_t retryAt_ = 0;
};
