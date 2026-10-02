/**
 * @file r307s_uart_diag.cpp
 * @brief R307S UART bring-up diagnostic suite (Phase 4/5 probe, read-only).
 * @project Biometric School Attendance System
 *
 * Answers ONE question with maximum evidence: is the R307S reachable over
 * UART from the ESP32, and if not, what can software determine about why?
 *
 * Stages (all bounded in time; the sketch never hangs):
 *   1. TX-line idle-level probe  - passively discriminates a FLOATING wire
 *      from a DRIVEN-HIGH (UART idle) and DRIVEN-LOW line using the ESP32's
 *      internal pull resistors and ADC. This is a coarse 1-bit+ADC probe,
 *      NOT a calibrated voltage measurement (no multimeter required).
 *   2. Falling-edge activity monitor on the RX line (1.5 s) to catch any
 *      unsolicited data.
 *   3. Baud ladder scan over the OFFICIAL documented set: baud = 9600 x N,
 *      N = 1..12 (R307/R307S datasheet; default N = 6 -> 57600). At each
 *      baud: one VerifyPassword (0x13) probe, raw RX hex dump, checksum-
 *      validated ACK parse. Includes software-swapped UART routing probes
 *      (RX<->TX via GPIO matrix) - see caution note inline.
 *   4. At the baud that produced a valid ACK: read-only command suite -
 *      ReadSysPara (0x0F) and TemplateCount (0x1D) - with per-command
 *      records (packet sent / expected / actual / checksum / interpretation).
 *   5. Final classification: responding correctly / responding at another
 *      baud / malformed data / completely silent (+ line-state context).
 *
 * READ-ONLY GUARANTEE: only VerifyPassword, ReadSysPara and TemplateCount
 * are sent. No enrollment, deletion, matching, SetSysPara, SetAddr, baud
 * writes, password writes, or flash/template modifications of any kind.
 *
 * PROVISIONAL VALUES (docs/r307s-integration-plan.md): address 0xFFFFFFFF
 * and password 0x00000000 are factory-typical defaults, unverified for this
 * physical module until it confirms them. A module with a changed address
 * silently ignores packets - a documented cause of total silence.
 *
 * Remove this file, r307s_uart_diag.h and the call in main.cpp once the
 * real fingerprint driver lands.
 */

#include "r307s_uart_diag.h"

#include "config.h"

// ---------------------------------------------------------------------------
// Protocol constants (R307/R307S family datasheet + R30X manual)
// ---------------------------------------------------------------------------
static constexpr uint32_t R307S_DEFAULT_ADDRESS  = 0xFFFFFFFFu;
static constexpr uint32_t R307S_DEFAULT_PASSWORD = 0x00000000u;

static constexpr uint8_t PKT_HEADER_1 = 0xEF;
static constexpr uint8_t PKT_HEADER_2 = 0x01;
static constexpr uint8_t PID_COMMAND  = 0x01;
static constexpr uint8_t PID_DATA     = 0x02;
static constexpr uint8_t PID_RESPONSE = 0x07;

static constexpr uint8_t CMD_VERIFY_PASSWORD = 0x13;
static constexpr uint8_t CMD_READ_SYS_PARAM  = 0x0F;
static constexpr uint8_t CMD_TEMPLATE_COUNT  = 0x1D;

static constexpr uint8_t CONF_OK = 0x00;

// OFFICIAL baud ladder: baud = 9600 x N, N = 1..12 (R307/R307S datasheet,
// "Communication baud rate (UART): (9600 x N) bps, N=1~12, default N=6").
// Default (57600) is probed first; the rest ascend.
static const uint32_t BAUD_LADDER[] = {
    57600, 9600, 19200, 28800, 38400, 48000,
    67200, 76800, 86400, 96000, 105600, 115200
};
static constexpr size_t BAUD_LADDER_LEN = sizeof(BAUD_LADDER) / sizeof(BAUD_LADDER[0]);

// ---------------------------------------------------------------------------
// Timing / buffer tuning (all waits are finite by design)
// ---------------------------------------------------------------------------
static constexpr uint32_t LINE_PROBE_SETTLE_MS = 2;
static constexpr uint32_t ACTIVITY_WINDOW_MS   = 1500;
static constexpr uint32_t UART_SETTLE_MS       = 25;
static constexpr uint32_t PROBE_WINDOW_MS      = 350;   // per-baud VerifyPassword
static constexpr uint32_t CMD_WINDOW_MS        = 800;   // ReadSysPara/TemplateCount
static constexpr size_t   RX_CAPACITY          = 160;   // ACK(12) + data(27) + slack

// UART2: free on classic ESP32, routed to any GPIOs via the GPIO matrix.
static HardwareSerial& sensorUart = Serial2;

// ---------------------------------------------------------------------------
// Small helpers
// ---------------------------------------------------------------------------
static void print_hex_line(const char* label, const uint8_t* data, size_t len)
{
    Serial.printf("%s (%u bytes):", label, static_cast<unsigned>(len));
    if (len == 0) {
        Serial.print(" <none>");
    }
    for (size_t i = 0; i < len; ++i) {
        Serial.printf(" %02X", static_cast<unsigned>(data[i]));
    }
    Serial.println();
}

// Protocol checksum: arithmetic sum of packet ID + length (2) + packet
// content, modulo 0x10000. `start` points at the PID byte; `len` is the
// packet length field (content + 2 checksum bytes).
static uint16_t packet_checksum(const uint8_t* pkt, size_t pidIndex, uint16_t len)
{
    uint16_t sum = pkt[pidIndex];                        // packet ID
    sum += pkt[pidIndex + 1];                            // length high
    sum += pkt[pidIndex + 2];                            // length low
    for (uint16_t k = 0; k + 2 < len; ++k) {             // content bytes
        sum += pkt[pidIndex + 3 + k];
    }
    return sum;  // 16-bit wrap is part of the protocol
}

// Build a command packet: header(2) + addr(4) + PID 0x01 + len(2) +
// instruction(1) + params + checksum(2). Returns total length.
static size_t build_command(uint8_t* out, uint8_t instruction,
                            const uint8_t* params, size_t nparams)
{
    size_t i = 0;
    out[i++] = PKT_HEADER_1;
    out[i++] = PKT_HEADER_2;
    out[i++] = static_cast<uint8_t>(R307S_DEFAULT_ADDRESS >> 24);
    out[i++] = static_cast<uint8_t>(R307S_DEFAULT_ADDRESS >> 16);
    out[i++] = static_cast<uint8_t>(R307S_DEFAULT_ADDRESS >> 8);
    out[i++] = static_cast<uint8_t>(R307S_DEFAULT_ADDRESS);
    out[i++] = PID_COMMAND;
    const uint16_t len = static_cast<uint16_t>(1 + nparams + 2);  // instr + params + chksum
    out[i++] = static_cast<uint8_t>(len >> 8);
    out[i++] = static_cast<uint8_t>(len);
    out[i++] = instruction;
    for (size_t k = 0; k < nparams; ++k) {
        out[i++] = params[k];
    }
    const uint16_t sum = packet_checksum(out, 6, len);
    out[i++] = static_cast<uint8_t>(sum >> 8);
    out[i++] = static_cast<uint8_t>(sum);
    return i;
}

// Collect UART bytes for up to window_ms. Stops early once no new byte has
// arrived for 60 ms after at least one full minimal ACK could be present.
static size_t collect_bytes(uint8_t* rx, size_t cap, uint32_t windowMs)
{
    const uint32_t start = millis();
    uint32_t lastByteMs = start;
    size_t n = 0;
    while ((millis() - start) < windowMs && n < cap) {
        if (sensorUart.available() > 0) {
            rx[n++] = static_cast<uint8_t>(sensorUart.read());
            lastByteMs = millis();
        } else if (n >= 12 && (millis() - lastByteMs) > 60) {
            break;  // a full ACK could be buffered and the line went quiet
        } else {
            delay(1);
        }
    }
    return n;
}

// Parse result for one scanned RX buffer.
struct AckView {
    bool sawHeader   = false;
    bool sawResponse = false;   // a PID 0x07 packet header was found
    bool complete    = false;
    bool checksumOk  = false;
    uint8_t conf     = 0xFF;
    uint32_t addr    = 0;
    uint16_t len     = 0;
    size_t index     = 0;
};

static void scan_for_ack(const uint8_t* rx, size_t n, AckView& out)
{
    for (size_t i = 0; (i + 12) <= n; ++i) {
        if (rx[i] != PKT_HEADER_1 || rx[i + 1] != PKT_HEADER_2) {
            continue;
        }
        out.sawHeader = true;
        const uint8_t pid = rx[i + 6];
        if (pid != PID_RESPONSE) {
            continue;
        }
        out.sawResponse = true;
        out.index = i;
        out.addr = (static_cast<uint32_t>(rx[i + 2]) << 24) |
                   (static_cast<uint32_t>(rx[i + 3]) << 16) |
                   (static_cast<uint32_t>(rx[i + 4]) << 8)  |
                    static_cast<uint32_t>(rx[i + 5]);
        out.len = static_cast<uint16_t>((rx[i + 7] << 8) | rx[i + 8]);
        const size_t total = 9u + out.len;
        if ((n - i) < total || out.len < 3) {
            continue;  // truncated or implausible length
        }
        out.complete = true;
        const uint16_t expected = packet_checksum(rx, i + 6, out.len);
        const size_t chkIdx = i + 9u + (out.len - 2u);
        const uint16_t found = static_cast<uint16_t>((rx[chkIdx] << 8) | rx[chkIdx + 1]);
        out.checksumOk = (expected == found);
        out.conf = rx[i + 9];  // first content byte of a response packet
        if (out.checksumOk) {
            return;  // first checksum-valid response wins
        }
    }
}

// Locate a data packet (PID 0x02) and return its content span.
static bool find_data_packet(const uint8_t* rx, size_t n, size_t& index,
                             uint16_t& len, const uint8_t** content)
{
    for (size_t i = 0; (i + 12) <= n; ++i) {
        if (rx[i] != PKT_HEADER_1 || rx[i + 1] != PKT_HEADER_2) {
            continue;
        }
        if (rx[i + 6] != PID_DATA) {
            continue;
        }
        const uint16_t l = static_cast<uint16_t>((rx[i + 7] << 8) | rx[i + 8]);
        if (l < 3 || (n - i) < (9u + l)) {
            continue;
        }
        const uint16_t expected = packet_checksum(rx, i + 6, l);
        const size_t chkIdx = i + 9u + (l - 2u);
        const uint16_t found = static_cast<uint16_t>((rx[chkIdx] << 8) | rx[chkIdx + 1]);
        if (expected != found) {
            continue;
        }
        index = i;
        len = l;
        *content = &rx[i + 9];
        return true;
    }
    return false;
}

// ---------------------------------------------------------------------------
// Stage 1: passive RX-line state probe (coarse, software-only "voltmeter")
// ---------------------------------------------------------------------------
static void probe_rx_line_state()
{
    Serial.println("---- TX-line idle-state probe (software only, coarse) ----");

    uint32_t mvSum = 0;
    pinMode(PIN_R307S_RX, INPUT);
    delay(LINE_PROBE_SETTLE_MS);
    for (int k = 0; k < 16; ++k) {
        mvSum += analogReadMilliVolts(PIN_R307S_RX);
        delayMicroseconds(500);
    }
    const uint32_t mvAvg = mvSum / 16;

    pinMode(PIN_R307S_RX, INPUT_PULLDOWN);
    delay(LINE_PROBE_SETTLE_MS);
    int highWithPulldown = 0;
    for (int k = 0; k < 200; ++k) {
        highWithPulldown += (digitalRead(PIN_R307S_RX) == HIGH) ? 1 : 0;
    }

    pinMode(PIN_R307S_RX, INPUT_PULLUP);
    delay(LINE_PROBE_SETTLE_MS);
    int highWithPullup = 0;
    for (int k = 0; k < 200; ++k) {
        highWithPullup += (digitalRead(PIN_R307S_RX) == HIGH) ? 1 : 0;
    }
    pinMode(PIN_R307S_RX, INPUT);

    Serial.printf("GPIO %u analog estimate: ~%lu mV (uncalibrated, saturates near 3100 mV)\n",
                  static_cast<unsigned>(PIN_R307S_RX), static_cast<unsigned long>(mvAvg));
    Serial.printf("GPIO %u reads HIGH %u/200 with internal pull-DOWN, %u/200 with internal pull-UP\n",
                  static_cast<unsigned>(PIN_R307S_RX),
                  static_cast<unsigned>(highWithPulldown),
                  static_cast<unsigned>(highWithPullup));

    const bool pdHigh = highWithPulldown >= 190;
    const bool puHigh = highWithPullup >= 190;
    const bool pdLow  = highWithPulldown <= 10;
    const bool puLow  = highWithPullup <= 10;

    if (puHigh && pdLow) {
        Serial.println("LINE STATE: FLOATING - nothing is driving this wire.");
        Serial.println("  => the sensor is NOT outputting a UART idle level. Causes:");
        Serial.println("     unpowered module / dead module / broken wire / this wire is");
        Serial.println("     not the sensor's TXD. (Voltage value is NOT proof of power.)");
    } else if (puHigh && pdHigh) {
        Serial.println("LINE STATE: DRIVEN HIGH - an active output holds the line at UART");
        Serial.println("  idle level. The sensor's TXD appears alive (powered) but silent.");
    } else if (puLow && pdLow) {
        Serial.println("LINE STATE: DRIVEN LOW - abnormal for an idle UART TX line.");
    } else {
        Serial.println("LINE STATE: INDETERMINATE (mixed readings).");
    }
    Serial.println("NOTE: digital thresholds are coarse (HIGH >~2.5 V, LOW <~0.8 V).");
    Serial.println("      This probe cannot prove the supply voltage is correct.");
}

// Stage 2: watch the RX line for ANY falling edges (unsolicited data).
static void monitor_rx_activity()
{
    Serial.printf("---- RX activity monitor: watching GPIO %u for %lu ms ----\n",
                  static_cast<unsigned>(PIN_R307S_RX),
                  static_cast<unsigned long>(ACTIVITY_WINDOW_MS));
    const uint32_t start = millis();
    uint32_t edges = 0;
    pinMode(PIN_R307S_RX, INPUT);
    int last = digitalRead(PIN_R307S_RX);
    while ((millis() - start) < ACTIVITY_WINDOW_MS) {
        const int now = digitalRead(PIN_R307S_RX);
        if (now != last) {
            ++edges;
            last = now;
        }
    }
    Serial.printf("Transitions observed: %lu %s\n", static_cast<unsigned long>(edges),
                  edges > 0 ? "(unsolicited data present!)" : "(no unsolicited data - expected)");
}

// ---------------------------------------------------------------------------
// Stage 3: baud ladder scan
// ---------------------------------------------------------------------------
struct ProbeResult {
    uint32_t baud    = 0;
    bool swapped     = false;
    size_t rxLen     = 0;
    bool sawHeader   = false;
    bool sawResponse = false;
    bool ackValid    = false;
    bool checksumOk  = false;
    uint8_t conf     = 0xFF;
    uint32_t addr    = 0;
    uint8_t first[8] = {0};
};

static ProbeResult probe_baud(uint32_t baud, bool swapped)
{
    ProbeResult r;
    r.baud = baud;
    r.swapped = swapped;

    const int rxPin = swapped ? PIN_R307S_TX : PIN_R307S_RX;
    const int txPin = swapped ? PIN_R307S_RX : PIN_R307S_TX;

    sensorUart.end();
    sensorUart.begin(baud, SERIAL_8N1, rxPin, txPin);
    delay(UART_SETTLE_MS);
    while (sensorUart.available() > 0) {
        sensorUart.read();
    }

    uint8_t pkt[16];
    const uint8_t pwd[4] = {
        static_cast<uint8_t>(R307S_DEFAULT_PASSWORD >> 24),
        static_cast<uint8_t>(R307S_DEFAULT_PASSWORD >> 16),
        static_cast<uint8_t>(R307S_DEFAULT_PASSWORD >> 8),
        static_cast<uint8_t>(R307S_DEFAULT_PASSWORD)
    };
    const size_t pktLen = build_command(pkt, CMD_VERIFY_PASSWORD, pwd, 4);
    sensorUart.write(pkt, pktLen);
    sensorUart.flush();

    uint8_t rx[RX_CAPACITY];
    r.rxLen = collect_bytes(rx, sizeof(rx), PROBE_WINDOW_MS);

    AckView ack;
    scan_for_ack(rx, r.rxLen, ack);
    r.sawHeader = ack.sawHeader;
    r.sawResponse = ack.sawResponse;
    r.ackValid = ack.complete && ack.checksumOk;
    r.checksumOk = ack.checksumOk;
    r.conf = ack.conf;
    r.addr = ack.addr;
    for (size_t k = 0; k < 8 && k < r.rxLen; ++k) {
        r.first[k] = rx[k];
    }

    Serial.printf("[probe] %5lu baud %s : TX 16 B -> RX %3u B | hdr=%d resp=%d cks=%d conf=0x%02X",
                  static_cast<unsigned long>(baud), swapped ? "(swapped routing)" : "(normal routing) ",
                  static_cast<unsigned>(r.rxLen),
                  ack.sawHeader ? 1 : 0, ack.sawResponse ? 1 : 0,
                  r.ackValid ? 1 : 0, static_cast<unsigned>(r.conf));
    if (r.rxLen > 0) {
        Serial.print(" first: ");
        for (size_t k = 0; k < 8 && k < r.rxLen; ++k) {
            Serial.printf("%02X ", static_cast<unsigned>(rx[k]));
        }
    }
    Serial.println();
    return r;
}

// ---------------------------------------------------------------------------
// Stage 4: read-only command suite at a baud that produced a valid ACK
// ---------------------------------------------------------------------------
static void run_command_suite(uint32_t baud)
{
    Serial.printf("---- Read-only command suite at %lu baud ----\n",
                  static_cast<unsigned long>(baud));
    sensorUart.end();
    sensorUart.begin(baud, SERIAL_8N1, PIN_R307S_RX, PIN_R307S_TX);
    delay(UART_SETTLE_MS);

    uint8_t pkt[16];
    uint8_t rx[RX_CAPACITY];

    // --- ReadSysPara (0x0F): reads the 16-byte system parameter block. ---
    {
        const size_t pktLen = build_command(pkt, CMD_READ_SYS_PARAM, nullptr, 0);
        print_hex_line("[ReadSysPara] packet sent", pkt, pktLen);
        Serial.println("[ReadSysPara] expected: ACK EF01 ADDR 07 0003 conf chk (+ data packet 02 0012, 16 B params)");
        while (sensorUart.available() > 0) { sensorUart.read(); }
        sensorUart.write(pkt, pktLen);
        sensorUart.flush();
        const size_t n = collect_bytes(rx, sizeof(rx), CMD_WINDOW_MS);
        print_hex_line("[ReadSysPara] actual RX", rx, n);
        AckView ack;
        scan_for_ack(rx, n, ack);
        Serial.printf("[ReadSysPara] ACK: hdr=%d pid=%d cks=%d conf=0x%02X addr=0x%08lX\n",
                      ack.sawHeader ? 1 : 0, ack.sawResponse ? 1 : 0,
                      ack.checksumOk ? 1 : 0, static_cast<unsigned>(ack.conf),
                      static_cast<unsigned long>(ack.addr));
        size_t dIdx = 0; uint16_t dLen = 0; const uint8_t* d = nullptr;
        if (find_data_packet(rx, n, dIdx, dLen, &d) && dLen >= 0x0012) {
            const uint16_t statusReg  = static_cast<uint16_t>((d[0] << 8) | d[1]);
            const uint16_t sysId      = static_cast<uint16_t>((d[2] << 8) | d[3]);
            const uint16_t capacity   = static_cast<uint16_t>((d[4] << 8) | d[5]);
            const uint16_t security   = static_cast<uint16_t>((d[6] << 8) | d[7]);
            const uint32_t devAddr    = (static_cast<uint32_t>(d[8]) << 24) |
                                        (static_cast<uint32_t>(d[9]) << 16) |
                                        (static_cast<uint32_t>(d[10]) << 8) |
                                         static_cast<uint32_t>(d[11]);
            const uint16_t pktSize    = static_cast<uint16_t>((d[12] << 8) | d[13]);
            const uint16_t baudMult   = static_cast<uint16_t>((d[14] << 8) | d[15]);
            Serial.printf("[ReadSysPara] checksum VALID. status=0x%04X sysID=0x%04X capacity=%u security=%u addr=0x%08lX pktSize=%u baudN=%u (%lu bps)\n",
                          static_cast<unsigned>(statusReg), static_cast<unsigned>(sysId),
                          static_cast<unsigned>(capacity), static_cast<unsigned>(security),
                          static_cast<unsigned long>(devAddr), static_cast<unsigned>(pktSize),
                          static_cast<unsigned>(baudMult),
                          static_cast<unsigned long>(9600ul * baudMult));
            Serial.println("[ReadSysPara] interpretation: READ-ONLY query succeeded; values are the module's self-declaration.");
        } else if (ack.checksumOk) {
            Serial.println("[ReadSysPara] ACK ok but no checksum-valid data packet found.");
        } else {
            Serial.println("[ReadSysPara] no checksum-valid response (see conf/raw above).");
        }
    }

    // --- TemplateCount (0x1D): reads the number of stored templates. ---
    {
        const size_t pktLen = build_command(pkt, CMD_TEMPLATE_COUNT, nullptr, 0);
        print_hex_line("[TemplateCount] packet sent", pkt, pktLen);
        Serial.println("[TemplateCount] expected: ACK EF01 ADDR 07 0003 conf chk (+ data packet 02 0004, 2 B count)");
        while (sensorUart.available() > 0) { sensorUart.read(); }
        sensorUart.write(pkt, pktLen);
        sensorUart.flush();
        const size_t n = collect_bytes(rx, sizeof(rx), CMD_WINDOW_MS);
        print_hex_line("[TemplateCount] actual RX", rx, n);
        AckView ack;
        scan_for_ack(rx, n, ack);
        size_t dIdx = 0; uint16_t dLen = 0; const uint8_t* d = nullptr;
        if (find_data_packet(rx, n, dIdx, dLen, &d) && dLen >= 0x0004) {
            const uint16_t count = static_cast<uint16_t>((d[0] << 8) | d[1]);
            Serial.printf("[TemplateCount] checksum VALID. stored templates = %u\n",
                          static_cast<unsigned>(count));
        } else if (ack.checksumOk) {
            Serial.printf("[TemplateCount] ACK cks ok conf=0x%02X, no valid data packet.\n",
                          static_cast<unsigned>(ack.conf));
        } else {
            Serial.println("[TemplateCount] no checksum-valid response.");
        }
    }
}

// ---------------------------------------------------------------------------
// Suite entry point
// ---------------------------------------------------------------------------
bool r307s_uart_diag_run()
{
    Serial.println();
    Serial.println("========== R307S UART BRING-UP DIAGNOSTIC SUITE (read-only) ==========");
    Serial.printf("UART2 | RX=GPIO %u <- sensor TXD | TX=GPIO %u -> sensor RXD | start 57600 8-N-1\n",
                  static_cast<unsigned>(PIN_R307S_RX), static_cast<unsigned>(PIN_R307S_TX));
    Serial.printf("Provisional (unconfirmed): address 0x%08lX, password 0x%08lX\n",
                  static_cast<unsigned long>(R307S_DEFAULT_ADDRESS),
                  static_cast<unsigned long>(R307S_DEFAULT_PASSWORD));
    Serial.println("Baud ladder source: R307/R307S datasheet: (9600 x N), N=1..12, default N=6.");

    // Stage 1 + 2: passive line evidence BEFORE touching the UART matrix.
    probe_rx_line_state();
    monitor_rx_activity();

    // Stage 3: scan the official ladder, normal routing first...
    ProbeResult best;
    ProbeResult results[BAUD_LADDER_LEN + 2];
    size_t resultCount = 0;
    for (size_t i = 0; i < BAUD_LADDER_LEN; ++i) {
        results[resultCount++] = probe_baud(BAUD_LADDER[i], false);
    }
    // ...then the two software-swapped-routing hypotheses (GPIO matrix only,
    // no wire movement). CAUTION: if wire labels are reversed, the ESP32 TX
    // briefly contends with the sensor TXD output during each 16-byte burst.
    results[resultCount++] = probe_baud(57600, true);
    results[resultCount++] = probe_baud(9600, true);

    for (size_t i = 0; i < resultCount; ++i) {
        if (results[i].ackValid &&
            (best.ackValid == false || results[i].swapped == false)) {
            best = results[i];
        }
    }

    // Stage 4: full read-only suite at the winning baud.
    bool success = false;
    if (best.ackValid) {
        Serial.println();
        Serial.printf("VALID ACK at %lu baud (%s routing), confirmation code 0x%02X\n",
                      static_cast<unsigned long>(best.baud),
                      best.swapped ? "swapped" : "normal",
                      static_cast<unsigned>(best.conf));
        if (!best.swapped) {
            run_command_suite(best.baud);
        }
        success = (best.conf == CONF_OK) && (best.swapped == false);
    }

    // Stage 5: classification.
    Serial.println();
    Serial.println("================ DIAGNOSTIC CLASSIFICATION ================");
    size_t totalBytes = 0;
    for (size_t i = 0; i < resultCount; ++i) {
        totalBytes += results[i].rxLen;
    }

    if (success) {
        Serial.println("RESULT: RESPONDING CORRECTLY.");
        Serial.println("  A checksum-valid ACK with confirmation 0x00 was received from");
        Serial.println("  the physical sensor. UART communication is PROVEN.");
    } else if (best.ackValid) {
        Serial.printf("RESULT: SENSOR RESPONDS, COMMAND REJECTED (conf 0x%02X at %lu baud).\n",
                      static_cast<unsigned>(best.conf), static_cast<unsigned long>(best.baud));
        Serial.println("  UART electrical path PROVEN; command-level rejection (password?).");
    } else if (totalBytes > 0) {
        Serial.printf("RESULT: MALFORMED DATA - %lu byte(s) across the scan, no checksum-valid ACK.\n",
                      static_cast<unsigned long>(totalBytes));
        Serial.println("  The sensor's TX reaches the ESP32 but the stream is desynced:");
        Serial.println("  baud outside the ladder, changed address, damaged data, or 5 V logic.");
    } else {
        Serial.println("RESULT: COMPLETELY SILENT - 0 bytes at every baud, both routings.");
        Serial.println("  Combined with the line-state probe above:");
        Serial.println("   - FLOATING line  -> no live sensor output on this wire (power path,");
        Serial.println("                      dead module, broken wire, or wire is not TXD).");
        Serial.println("   - DRIVEN HIGH    -> this wire is actively held high under the probe;");
        Serial.println("                      that alone does NOT prove module power, identity,");
        Serial.println("                      correct pin mapping, or sensor health.");
        Serial.println("                      Possible causes include RXD path/address/boot fault.");
        Serial.println("  0 bytes CANNOT be produced by unconnected pins 5/6 (touch circuit");
        Serial.println("  only, ~5 uA) per the R307/R307S family datasheet.");
    }

    Serial.println("One-shot suite. Press the ESP32 EN/RST button to run it again.");
    Serial.println("Remove r307s_uart_diag.{h,cpp} and the call in main.cpp once verified.");
    Serial.println("======================================================================");
    return success;
}
