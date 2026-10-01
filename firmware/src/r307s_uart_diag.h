/**
 * @file r307s_uart_diag.h
 * @brief R307S UART bring-up diagnostic suite interface.
 * @project Biometric School Attendance System
 *
 * Scope: ONLY determines whether and how the ESP32 <-> R307S UART link works
 * (docs/r307s-integration-plan.md Phase 4/5 probe, gates HW-02..HW-07).
 * Sends read-only command packets (VerifyPassword, ReadSysPara,
 * TemplateCount), parses and checksum-validates the ACKs, and scans the
 * documented baud ladder. Performs NO enrollment, NO matching, NO template
 * or parameter writes, NO password/address/baud changes.
 *
 * Remove this file, r307s_uart_diag.cpp, and the call in main.cpp once
 * Phase 5 passes and the real fingerprint driver lands.
 */

#ifndef R307S_UART_DIAG_H
#define R307S_UART_DIAG_H

#include <Arduino.h>

/**
 * @brief Run the full R307S UART bring-up diagnostic suite once.
 *
 * Sequence: TX-line idle-level probe -> full baud ladder scan -> at the
 * baud that produced a valid ACK, run the read-only command tests
 * (VerifyPassword, ReadSysPara, TemplateCount) and report the module's
 * self-declared parameters. Never blocks indefinitely; every stage has a
 * finite timeout. Only handles command/response traffic at the documented
 * baud rates.
 *
 * @return true ONLY if a valid checksum-verified ACK with confirmation
 *         code 0x00 was received from the physical sensor.
 */
bool r307s_uart_diag_run();

#endif // R307S_UART_DIAG_H
