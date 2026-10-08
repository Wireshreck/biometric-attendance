"""test.exe — standalone Windows diagnostic application.

GUI buttons: CONNECT DEVICE, RUN FULL SYSTEM TEST, R307S TEST, RTC TEST,
BUZZER TEST, BLE TEST, STORAGE TEST, ATTENDANCE TEST, EXPORT LOG.

Honesty rules (never faked):
- Disconnected hardware never becomes PASS; it becomes FAIL/SKIPPED/WARN.
- Unsupported tests become SKIPPED.
- Every result carries a reason when it is not PASS.
"""
import asyncio
import json
import sys
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk
from datetime import datetime, timezone

sys.path.insert(0, "..\\..\\shared")
sys.path.insert(0, "../../shared")
import ble_protocol as P

try:
    from bleak import BleakClient, BleakScanner
    HAVE_BLEAK = True
except ImportError:
    HAVE_BLEAK = False

BASE = "0000{:04x}-0000-1000-8000-00805f9b34fb"


def char_uuid(name):
    return BASE.format(int(P.BLE_CHARS[name], 16))


class DiagApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Biometric Attendance — System Test v1.0.0")
        self.geometry("860x680")
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()
        self.client = None
        self.entries = []
        self._build()

    def run_coro(self, coro, done, timeout=130):
        def _r():
            try:
                res = asyncio.run_coroutine_threadsafe(coro, self.loop).result(timeout)
                self.after(0, lambda: done(res, None))
            except Exception as e:  # noqa: BLE001
                self.after(0, lambda: done(None, e))
        threading.Thread(target=_r, daemon=True).start()

    def _build(self):
        bar = ttk.Frame(self); bar.pack(fill=tk.X, padx=8, pady=6)
        ttk.Button(bar, text="CONNECT DEVICE", command=self.on_connect).pack(side=tk.LEFT)
        ttk.Button(bar, text="RUN FULL SYSTEM TEST", command=self.on_full).pack(side=tk.LEFT, padx=4)
        ttk.Button(bar, text="EXPORT LOG", command=self.on_export).pack(side=tk.LEFT)
        self.conn = ttk.Label(bar, text="DISCONNECTED"); self.conn.pack(side=tk.LEFT, padx=8)

        grid = ttk.Frame(self); grid.pack(fill=tk.X, padx=8)
        tests = [("R307S TEST", self.on_r307s), ("RTC TEST", self.on_rtc),
                 ("BUZZER TEST", self.on_buzzer), ("BLE TEST", self.on_ble),
                 ("STORAGE TEST", self.on_storage), ("ATTENDANCE TEST", self.on_attendance)]
        for i, (label, fn) in enumerate(tests):
            ttk.Button(grid, text=label, command=fn).grid(row=i // 3, column=i % 3, padx=4, pady=4, sticky="ew")

        self.table = ttk.Treeview(self, columns=("test", "result", "reason"), show="headings", height=12)
        for c in ("test", "result", "reason"):
            self.table.heading(c, text=c)
        self.table.pack(fill=tk.X, padx=8, pady=6)
        self.logbox = scrolledtext.ScrolledText(self, height=14)
        self.logbox.pack(fill=tk.BOTH, padx=8, pady=6, expand=True)

    def log(self, msg):
        stamp = datetime.now().astimezone().isoformat(timespec="seconds")
        line = f"[{stamp}] {msg if isinstance(msg, str) else json.dumps(msg)}"
        self.entries.append(line)
        self.logbox.insert(tk.END, line + "\n")
        self.logbox.see(tk.END)

    def row(self, test, result, reason=""):
        assert result in P.DIAG_RESULTS, result
        for rid in self.table.get_children():
            if self.table.set(rid, "test") == test:
                self.table.delete(rid)
        self.table.insert("", tk.END, values=(test, result, reason))
        self.log({"test": test, "result": result, "reason": reason})

    async def _send(self, cmd, params=None, timeout=20.0):
        if self.client is None or not self.client.is_connected:
            raise RuntimeError("not connected")
        uuid = char_uuid(P.CHAR_FOR_COMMAND[cmd])
        await self.client.write_gatt_char(uuid, P.build_request(cmd, params).encode(), response=True)
        raw = await asyncio.wait_for(self.client.read_gatt_char(uuid), timeout)
        return P.parse_response(bytes(raw).decode("utf-8"))

    def need(self):
        if self.client is None or not self.client.is_connected:
            self.log("not connected: results would be dishonest as PASS; refusing")
            return False
        return True

    def on_connect(self):
        if not HAVE_BLEAK:
            self.log("bleak not installed; pip install bleak"); return
        self.log("scanning for biometric-attendance-esp32...")

        async def _go():
            devs = await BleakScanner.discover(timeout=8.0)
            tgt = None
            for d in devs:
                uuids = [u.lower() for u in (d.metadata.get("uuids") or [])]
                if P.BLE_SERVICE_UUID.lower() in uuids:
                    tgt = d; break
            if tgt is None:
                for d in devs:
                    if d.name and "biometric" in d.name.lower():
                        tgt = d; break
            if tgt is None:
                raise RuntimeError(f"no device advertising {P.BLE_SERVICE_UUID} found")
            c = BleakClient(tgt.address)
            await c.connect()
            return c, tgt
        def _done(r, e):
            if e:
                self.log(f"CONNECT FAILED: {e}")
                self.row("BLE", "FAIL", str(e)); return
            self.client, tgt = r
            self.conn.config(text=f"CONNECTED · {tgt.address}")
            self.log(f"connected to {tgt.name} @ {tgt.address}")
            self.row("BLE", "PASS", "GATT connected")
        self.run_coro(_go(), _done)

    def on_full(self):
        if not self.need(): return
        self.log("running FULL_DIAGNOSTIC on device...")

        def _done(r, e):
            if e:
                self.log(f"FULL SYSTEM TEST FAILED: {e}")
                self.row("FULL", "FAIL", str(e)); return
            for t in r.get("data", {}).get("results", []):
                honest = P.is_honest_diag_result(t, True)
                self.row(t.get("test"), t.get("result"), t.get("reason", "") + ("" if honest else " [DISHONEST]"))
        self.run_coro(self._send("FULL_DIAGNOSTIC"), _done)

    def on_r307s(self):
        if not self.need(): return

        async def _go():
            st = await self._send("FINGERPRINT_STATUS")
            d = st.get("data", {})
            return st, ("PASS" if d.get("ready") else "FAIL", d.get("note", "sensor did not respond"))
        def _done(r, e):
            if e:
                self.row("R307S", "FAIL", str(e)); return
            st, (res, reason) = r
            self.row("R307S_UART", res, reason if res != "PASS" else "")
            self.row("R307S_SENSOR", res if res == "PASS" else "SKIPPED", "" if res == "PASS" else "UART check failed")
            self.log(st)
        self.run_coro(_go(), _done)

    def on_rtc(self):
        if not self.need(): return

        def _done(r, e):
            if e:
                self.row("RTC", "FAIL", str(e)); return
            d = r.get("data", {})
            if d.get("valid") and not d.get("lost_power"):
                self.row("DS3231", "PASS"); self.row("RTC", "PASS", d.get("time", ""))
            elif d.get("lost_power"):
                self.row("DS3231", "WARN", "lost power — set RTC"); self.row("RTC", "FAIL", "lost power")
            else:
                self.row("DS3231", "FAIL", "invalid time"); self.row("RTC", "FAIL", "invalid time")
            self.log(r)
        self.run_coro(self._send("RTC_GET"), _done)

    def on_buzzer(self):
        if not self.need(): return

        def _done(r, e):
            if e:
                self.row("BUZZER", "FAIL", str(e)); return
            self.row("BUZZER", "PASS", f"GPIO{P.PINS['BUZZER']} two-beep executed")
            self.log(r)
        self.run_coro(self._send("BUZZER_TEST"), _done)

    def on_ble(self):
        if not self.need(): return

        def _done(r, e):
            if e:
                self.row("BLE", "FAIL", str(e)); return
            self.row("BLE", "PASS", "PING pong")
            self.log(r)
        self.run_coro(self._send("PING"), _done)

    def on_storage(self):
        if not self.need(): return

        def _done(r, e):
            if e:
                self.row("STORAGE", "FAIL", str(e)); return
            ok = r.get("data", {}).get("storage_ok", False)
            self.row("STORAGE", "PASS" if ok else "FAIL", "" if ok else "storage unhealthy")
            self.log(r)
        self.run_coro(self._send("DEVICE_STATUS"), _done)

    def on_attendance(self):
        if not self.need(): return

        def _done(r, e):
            if e:
                self.row("ATTENDANCE", "FAIL", str(e)); return
            self.row("ATTENDANCE", "PASS", f"{r.get('data', {}).get('records', 0)} records")
            self.log(r)
        self.run_coro(self._send("ATTENDANCE_STATUS"), _done)

    def on_export(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(defaultextension=".log",
                                            filetypes=[("Log", "*.log"), ("All", "*.*")],
                                            initialfile="biometric-diag.log")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Biometric Attendance diagnostic log — {datetime.now().isoformat()}\n")
            f.write(f"service={P.BLE_SERVICE_UUID} pins={P.PINS}\n")
            f.write("\n".join(self.entries) + "\n")
        self.log(f"exported {len(self.entries)} lines to {path}")


if __name__ == "__main__":
    DiagApp().mainloop()
