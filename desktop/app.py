"""Windows desktop BLE manager. Uses the single shared protocol
(shared/ble_protocol.py) against the ESP32 GATT service in docs/protocol.md.
"""
import asyncio
import json
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from datetime import datetime

sys.path.insert(0, "..\\shared")
sys.path.insert(0, "../shared")
import ble_protocol as P

try:
    from bleak import BleakClient, BleakScanner
    HAVE_BLEAK = True
except ImportError:
    HAVE_BLEAK = False

BASE = "0000{:04x}-0000-1000-8000-00805f9b34fb"


def char_uuid(name):
    return BASE.format(int(P.BLE_CHARS[name], 16))


class DeviceClient:
    def __init__(self):
        self.client = None
        self.address = None

    @property
    def connected(self):
        return self.client is not None and self.client.is_connected

    async def scan(self, timeout=8.0):
        devs = await BleakScanner.discover(timeout=timeout)
        out = []
        for d in devs:
            uuids = [u.lower() for u in (d.metadata.get("uuids") or [])]
            if P.BLE_SERVICE_UUID.lower() in uuids or (d.name and "biometric" in d.name.lower()):
                out.append(d)
        return out

    async def connect(self, address):
        self.client = BleakClient(address)
        await self.client.connect()
        self.address = address

    async def disconnect(self):
        if self.client:
            try:
                await self.client.disconnect()
            finally:
                self.client = None

    async def send(self, cmd, params=None, timeout=20.0):
        if not self.connected:
            raise RuntimeError("not connected")
        body = P.build_request(cmd, params)
        uuid = char_uuid(P.CHAR_FOR_COMMAND[cmd])
        await self.client.write_gatt_char(uuid, body.encode("utf-8"), response=True)
        raw = await asyncio.wait_for(self.client.read_gatt_char(uuid), timeout)
        return P.parse_response(bytes(raw).decode("utf-8"))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Biometric Attendance — Desktop Manager v1.0.0")
        self.geometry("900x700")
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()
        self.dev = DeviceClient()
        self._build()

    def run_coro(self, coro, done):
        def _runner():
            try:
                res = asyncio.run_coroutine_threadsafe(coro, self.loop).result(130)
                self.after(0, lambda: done(res, None))
            except Exception as e:  # noqa: BLE001
                self.after(0, lambda: done(None, e))
        threading.Thread(target=_runner, daemon=True).start()

    def log(self, obj):
        self.logbox.insert(tk.END, (obj if isinstance(obj, str) else json.dumps(obj, indent=2)) + "\n")
        self.logbox.see(tk.END)

    def _build(self):
        top = ttk.Frame(self); top.pack(fill=tk.X, padx=8, pady=6)
        ttk.Button(top, text="Scan BLE", command=self.on_scan).pack(side=tk.LEFT)
        self.devbox = ttk.Combobox(top, width=60); self.devbox.pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text="Connect", command=self.on_connect).pack(side=tk.LEFT)
        ttk.Button(top, text="Disconnect", command=self.on_disconnect).pack(side=tk.LEFT, padx=6)
        self.conn = ttk.Label(top, text="DISCONNECTED"); self.conn.pack(side=tk.LEFT, padx=8)

        nb = ttk.Notebook(self); nb.pack(fill=tk.BOTH, expand=True, padx=8)
        self.dash = ttk.Frame(nb); self.fp = ttk.Frame(nb); self.rtc = ttk.Frame(nb)
        self.att = ttk.Frame(nb); self.diag = ttk.Frame(nb); self.help = ttk.Frame(nb)
        for f, t in [(self.dash, "Dashboard"), (self.fp, "Fingerprint"),
                     (self.rtc, "RTC"), (self.att, "Attendance"),
                     (self.diag, "Diagnostics"), (self.help, "Help")]:
            nb.add(f, text=t)

        ttk.Button(self.dash, text="Refresh dashboard", command=self.on_dash).pack(anchor=tk.W, pady=4)
        self.dashvars = {}
        for key in ["device", "firmware", "uptime", "rtc", "r307s", "count", "storage", "attendance"]:
            lbl = ttk.Label(self.dash, text=f"{key}: —")
            lbl.pack(anchor=tk.W)
            self.dashvars[key] = lbl

        ttk.Label(self.fp, text="Slot:").pack(anchor=tk.W)
        self.slot = tk.StringVar(value="1")
        ttk.Entry(self.fp, textvariable=self.slot, width=10).pack(anchor=tk.W)
        for label, fn in [("Status", lambda: self.cmd("FINGERPRINT_STATUS")),
                          ("Count", lambda: self.cmd("FINGERPRINT_COUNT")),
                          ("Enroll", self.on_enroll),
                          ("Search / Test", lambda: self.cmd("FINGERPRINT_SEARCH", timeout=30)),
                          ("Delete slot", self.on_delete),
                          ("Delete ALL (confirm)", self.on_delete_all)]:
            ttk.Button(self.fp, text=label, command=fn).pack(anchor=tk.W, pady=2)
        self.enroll_lbl = ttk.Label(self.fp, text="ENROLL IDLE")
        self.enroll_lbl.pack(anchor=tk.W, pady=4)

        ttk.Button(self.rtc, text="Display current time", command=lambda: self.cmd("RTC_GET")).pack(anchor=tk.W, pady=2)
        ttk.Button(self.rtc, text="Set RTC to this PC time", command=self.on_rtc_set).pack(anchor=tk.W, pady=2)
        ttk.Label(self.rtc, text="DS3231 on GPIO25/26. Lost-power warning appears in the log.").pack(anchor=tk.W)

        for label, fn in [("Attendance status", lambda: self.cmd("ATTENDANCE_STATUS")),
                          ("Display records", self.on_att_read),
                          ("Clear records (confirm)", self.on_att_clear)]:
            ttk.Button(self.att, text=label, command=fn).pack(anchor=tk.W, pady=2)
        self.atttable = ttk.Treeview(self.att, columns=("slot", "time", "status"), show="headings", height=8)
        for c in ("slot", "time", "status"):
            self.atttable.heading(c, text=c)
        self.atttable.pack(fill=tk.X, pady=4)

        for label, fn in [("Run FULL_DIAGNOSTIC", self.on_diag),
                          ("BUZZER_TEST (GPIO27)", lambda: self.cmd("BUZZER_TEST")),
                          ("PING / BLE test", lambda: self.cmd("PING"))]:
            ttk.Button(self.diag, text=label, command=fn).pack(anchor=tk.W, pady=2)
        self.diagtable = ttk.Treeview(self.diag, columns=("test", "result", "reason"), show="headings", height=10)
        for c in ("test", "result", "reason"):
            self.diagtable.heading(c, text=c)
        self.diagtable.pack(fill=tk.X, pady=4)

        ttk.Label(self.help, wraplength=800, justify=tk.LEFT, text=(
            "Setup: R307S red→VIN, black→GND, yellow→GPIO32 (RX), green→GPIO33 (TX), "
            "blue/white open; DS3231 SDA→GPIO25, SCL→GPIO26; buzzer→GPIO27. OLED/LEDs removed.\n\n"
            "Pairing: Scan BLE, select biometric-attendance-esp32, Connect.\n"
            "Enrollment: enter slot, Enroll, place finger, remove, place again. Only "
            "enroll_success counts as success.\n"
            "Demo: PING → DEVICE_INFO → DEVICE_STATUS → RTC_GET → FINGERPRINT_COUNT → "
            "ENROLL → SEARCH → ATTENDANCE_READ → FULL_DIAGNOSTIC.")).pack(anchor=tk.W)

        self.logbox = scrolledtext.ScrolledText(self, height=12)
        self.logbox.pack(fill=tk.BOTH, padx=8, pady=6)
        if not HAVE_BLEAK:
            self.log("bleak not installed; run: pip install bleak")

    def cmd(self, cmd, params=None, timeout=20):
        self.run_coro(self.dev.send(cmd, params, timeout),
                      lambda r, e: self.log(f"{cmd} FAILED: {e}") if e else self.log({cmd: r}))

    def on_scan(self):
        if not HAVE_BLEAK:
            self.log("bleak not installed"); return
        self.log("scanning...")
        self.run_coro(self.dev.scan(),
                      lambda r, e: self.log(f"scan failed: {e}") if e else self._scan_done(r))

    def _scan_done(self, devs):
        self.found = devs
        self.devbox["values"] = [f"{d.name or 'unknown'} | {d.address}" for d in devs]
        if devs:
            self.devbox.current(0)
        self.log(f"found {len(devs)} matching device(s)")

    def on_connect(self):
        if not getattr(self, "found", None):
            messagebox.showinfo("Connect", "Scan first."); return
        addr = self.found[self.devbox.current()].address
        self.log(f"connecting {addr}...")
        self.run_coro(self.dev.connect(addr),
                      lambda r, e: self.log(f"connect failed: {e}") if e
                      else (self.conn.config(text=f"CONNECTED · {addr}"), self.log("connected")))

    def on_disconnect(self):
        self.run_coro(self.dev.disconnect(),
                      lambda r, e: (self.conn.config(text="DISCONNECTED"), self.log("disconnected")))

    def on_dash(self):
        async def _go():
            info = await self.dev.send("DEVICE_INFO")
            status = await self.dev.send("DEVICE_STATUS")
            att = await self.dev.send("ATTENDANCE_STATUS")
            return info, status, att
        def _done(r, e):
            if e:
                self.log(f"dashboard failed: {e}"); return
            info, status, att = r
            d, s = info.get("data", {}), status.get("data", {})
            self.dashvars["device"].config(text=f"device: {d.get('device')}")
            self.dashvars["firmware"].config(text=f"firmware: {d.get('firmware')}")
            self.dashvars["uptime"].config(text=f"uptime: {d.get('uptime_seconds')}s")
            self.dashvars["rtc"].config(text=f"rtc: {s.get('rtc_time') if s.get('rtc_valid') else 'INVALID / LOST-POWER'}")
            self.dashvars["r307s"].config(text=f"r307s: {'READY' if s.get('sensor_ready') else 'NOT CONNECTED'}")
            self.dashvars["count"].config(text=f"count: {s.get('template_count')}/{s.get('template_capacity')}")
            self.dashvars["storage"].config(text=f"storage: {'OK' if s.get('storage_ok') else 'ERROR'}")
            self.dashvars["attendance"].config(text=f"attendance: {att.get('data', {}).get('records')} records")
            self.log({"dashboard": {"info": d, "status": s, "attendance": att.get("data")}})
        self.run_coro(_go(), _done)

    def on_enroll(self):
        self.enroll_lbl.config(text="ENROLL PLACE FINGER")
        self.run_coro(self.dev.send("FINGERPRINT_ENROLL", {"slot": int(self.slot.get())}, 120),
                      lambda r, e: (self.enroll_lbl.config(text="ENROLL FAILED" if e else "ENROLL SUCCESS"),
                                    self.log(f"enroll failed: {e}") if e else self.log(r)))

    def on_delete(self):
        self.cmd("FINGERPRINT_DELETE", {"slot": int(self.slot.get())})

    def on_delete_all(self):
        if messagebox.askyesno("Confirm", "Delete ALL fingerprint templates?"):
            self.cmd("FINGERPRINT_DELETE_ALL")

    def on_rtc_set(self):
        n = datetime.now()
        self.cmd("RTC_SET", {"year": n.year, "month": n.month, "day": n.day,
                             "hour": n.hour, "minute": n.minute, "second": n.second})

    def on_att_read(self):
        def _done(r, e):
            if e:
                self.log(f"read failed: {e}"); return
            for row in self.atttable.get_children():
                self.atttable.delete(row)
            for rec in r.get("data", {}).get("records", []):
                self.atttable.insert("", tk.END, values=(rec.get("slot"), rec.get("captured_at"), rec.get("status")))
            self.log(r)
        self.run_coro(self.dev.send("ATTENDANCE_READ"), _done)

    def on_att_clear(self):
        if messagebox.askyesno("Confirm", "Clear all attendance records on the device?"):
            self.cmd("ATTENDANCE_CLEAR")

    def on_diag(self):
        def _done(r, e):
            if e:
                self.log(f"diagnostic failed: {e}"); return
            for row in self.diagtable.get_children():
                self.diagtable.delete(row)
            for t in r.get("data", {}).get("results", []):
                self.diagtable.insert("", tk.END, values=(t.get("test"), t.get("result"), t.get("reason", "")))
            self.log(r)
        self.run_coro(self.dev.send("FULL_DIAGNOSTIC"), _done)


if __name__ == "__main__":
    App().mainloop()
