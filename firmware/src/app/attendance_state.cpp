#include "attendance_state.h"

const char* attendance_state_name(AttendanceState state) {
    switch (state) {
        case AttendanceState::BOOT: return "BOOT";
        case AttendanceState::SELF_TEST: return "SELF_TEST";
        case AttendanceState::READY: return "READY";
        case AttendanceState::WAITING_FOR_FINGER: return "WAITING_FOR_FINGER";
        case AttendanceState::IDENTIFYING: return "IDENTIFYING";
        case AttendanceState::ATTENDANCE_RECORDED: return "ATTENDANCE_RECORDED";
        case AttendanceState::SYNCING: return "SYNCING";
        case AttendanceState::ERROR: return "ERROR";
        case AttendanceState::OFFLINE: return "OFFLINE";
        case AttendanceState::RECOVERY: return "RECOVERY";
    }
    return "UNKNOWN";
}
