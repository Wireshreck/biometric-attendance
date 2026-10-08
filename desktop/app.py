"""Windows desktop manager v1.1.0: dashboard, attendance, students,
fingerprints, device, diagnostics, AI assistant, settings.

Backends: BLE GATT (shared/ble_protocol.py) for device ops, HTTP REST
(same API as the web UI) for data. Real queries, no mock data.
"""
import asyncio
import base64
import json
import threading
import tkinter as tk
import urllib.request
import urllib.parse
from tkinter import messagebox, scrolledtext, ttk
from datetime import datetime

import sys
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


class API:
    def __init__(self):
        self.host = "http://127.0.0.1:8000"
        self.user = ""
        self.password = ""

    def _req(self, method, path, body=None):
        token = base64.b64encode(f"{self.user}:{self.password}".encode()).decode()
        req = urllib.request.Request(
            self.host + path, method=method,
            headers={"Authorization": "Basic " + token, "Content-Type": "application/json"},
            data=json.dumps(body).encode() if body is not None else None)
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                ctype = r.headers.get("Content-Type", "")
                return json.loads(r.read().decode()) if "json" in ctype else r.read()
        except urllib.error.HTTPError as e:
            try:
                detail = json.loads(e.read().decode())["error"]["message"]
            except Exception:
                detail = f"HTTP {e.code}"
            raise RuntimeError(detail)

    def get(self, path):
        return self._req("GET", path)

    def post(self, path, body=None):
        return self._req("POST", path, body or {})

    def patch(self, path, body):
        return self._req("PATCH", path, body)


class BLE:
    def __init__(self, loop):
        self.loop = loop
        self.client = None

    @property
    def connected(self):
        return self.client is not None and self.client.is_connected

    async def _scan(self):
        devs = await BleakScanner.discover(timeout=8.0, return_adv=True)
        return [(d, a) for d, a in devs.values()
                if P.BLE_SERVICE_UUID.lower() in [u.lower() for u in (a.service_uuids or [])]]

    async def _send(self, cmd, params=None, timeout=20.0):
        import time as _time
        uuid = char_uuid(P.CHAR_FOR_COMMAND[cmd])
        await self.client.write_gatt_char(uuid, P.build_request(cmd, params).encode(), response=True)
        deadline = _time.monotonic() + timeout
        await asyncio.sleep(0.4)
        while True:
            raw = await asyncio.wait_for(self.client.read_gatt_char(uuid), timeout)
            msg = P.parse_response(bytes(raw).decode("utf-8"))
            if msg.get("status") != "busy" or _time.monotonic() >= deadline:
                return msg
            await asyncio.sleep(0.5)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Biometric Attendance v1.2.0")
        self.geometry("1000x720")
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()
        self.api = API()
        self.ble = BLE(self.loop)
        self._build()

    def bg(self, coro, done, timeout=130):
        def _run():
            try:
                res = asyncio.run_coroutine_threadsafe(coro, self.loop).result(timeout)
                self.after(0, lambda: done(res, None))
            except Exception as e:  # noqa: BLE001
                self.after(0, lambda: done(None, e))
        threading.Thread(target=_run, daemon=True).start()

    def log(self, obj):
        self.logbox.insert(tk.END, (obj if isinstance(obj, str) else json.dumps(obj, indent=1)[:2000]) + "\n")
        self.logbox.see(tk.END)

    def _table(self, parent, cols, height=10):
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=height)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=110)
        tree.pack(fill=tk.BOTH, expand=True, pady=4)
        for tag, color in (("PASS", "#177245"), ("FAIL", "#b3261e"),
                           ("WARN", "#9a6200"), ("SKIPPED", "#5b6b82")):
            tree.tag_configure(tag, foreground=color)
        return tree

    def _build(self):
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        self.pg_dash = ttk.Frame(nb); self.pg_att = ttk.Frame(nb); self.pg_stu = ttk.Frame(nb)
        self.pg_fp = ttk.Frame(nb); self.pg_dev = ttk.Frame(nb); self.pg_diag = ttk.Frame(nb)
        self.pg_ai = ttk.Frame(nb); self.pg_set = ttk.Frame(nb)
        for page, name in [(self.pg_dash, "Dashboard"), (self.pg_att, "Attendance"),
                           (self.pg_stu, "Students"), (self.pg_fp, "Fingerprints"),
                           (self.pg_dev, "Device"), (self.pg_diag, "Diagnostics"),
                           (self.pg_ai, "AI Assistant"), (self.pg_set, "Settings")]:
            nb.add(page, text=name)

        ttk.Button(self.pg_dash, text="Refresh dashboard", command=self.on_dash).pack(anchor=tk.W)
        self.dash_lbl = ttk.Label(self.pg_dash, text="—", justify=tk.LEFT)
        self.dash_lbl.pack(anchor=tk.W, pady=4)
        self.recent = self._table(self.pg_dash, ("time", "student", "class"), 8)

        row = ttk.Frame(self.pg_att); row.pack(fill=tk.X)
        self.att_q = tk.StringVar(); self.att_class = tk.StringVar(); self.att_day = tk.StringVar()
        for label, var in [("Search", self.att_q), ("Class", self.att_class), ("Date", self.att_day)]:
            ttk.Label(row, text=label).pack(side=tk.LEFT)
            ttk.Entry(row, textvariable=var, width=14).pack(side=tk.LEFT, padx=3)
        ttk.Button(row, text="Apply", command=self.on_att).pack(side=tk.LEFT, padx=4)
        ttk.Button(row, text="Export CSV", command=lambda: self.on_export("csv")).pack(side=tk.LEFT)
        self.atttable = self._table(self.pg_att, ("date", "time", "student", "roll", "class", "fp", "status"), 12)
        self.att_meta = ttk.Label(self.pg_att, text="")
        self.att_meta.pack(anchor=tk.W)

        row2 = ttk.Frame(self.pg_stu); row2.pack(fill=tk.X)
        self.stu_q = tk.StringVar()
        ttk.Entry(row2, textvariable=self.stu_q, width=24).pack(side=tk.LEFT)
        ttk.Button(row2, text="Search", command=self.on_stu).pack(side=tk.LEFT, padx=3)
        ttk.Button(row2, text="Add", command=lambda: self.stu_dialog(None)).pack(side=tk.LEFT)
        self.stutable = self._table(self.pg_stu, ("name", "roll", "class", "status", "fp"), 12)
        self.stutable.bind("<Double-1>", lambda e: self.stu_open())

        ttk.Label(self.pg_fp, text="BLE fingerprint management (slot 1-1000)").pack(anchor=tk.W)
        row3 = ttk.Frame(self.pg_fp); row3.pack(fill=tk.X)
        self.slot = tk.StringVar(value="1")
        ttk.Entry(row3, textvariable=self.slot, width=8).pack(side=tk.LEFT)
        for label, fn in [("Count", lambda: self.ble_cmd("FINGERPRINT_COUNT")),
                          ("Enroll", self.on_enroll),
                          ("Search", lambda: self.ble_cmd("FINGERPRINT_SEARCH", timeout=30)),
                          ("Delete", self.on_delete)]:
            ttk.Button(row3, text=label, command=fn).pack(side=tk.LEFT, padx=2)
        ttk.Button(row3, text="Delete ALL", command=self.on_delete_all).pack(side=tk.LEFT, padx=2)

        ttk.Button(self.pg_dev, text="Scan + connect", command=self.on_scan_connect).pack(anchor=tk.W)
        self.dev_lbl = ttk.Label(self.pg_dev, text="BLE: disconnected")
        self.dev_lbl.pack(anchor=tk.W)
        for label, fn in [("Device refresh", self.on_dev_refresh),
                          ("RTC read", lambda: self.ble_cmd("RTC_GET")),
                          ("RTC set to PC time", self.on_rtc_set)]:
            ttk.Button(self.pg_dev, text=label, command=fn).pack(anchor=tk.W, pady=1)

        for label, fn in [("Full diagnostic", self.on_diag),
                          ("Buzzer test", lambda: self.ble_cmd("BUZZER_TEST")),
                          ("Ping", lambda: self.ble_cmd("PING"))]:
            ttk.Button(self.pg_diag, text=label, command=fn).pack(anchor=tk.W, pady=1)
        self.diagtable = self._table(self.pg_diag, ("test", "result", "reason"), 11)

        self.ai_q = tk.StringVar()
        ttk.Entry(self.pg_ai, textvariable=self.ai_q, width=70).pack(fill=tk.X)
        ttk.Button(self.pg_ai, text="Ask", command=self.on_ai).pack(anchor=tk.W, pady=2)
        self.ai_out = scrolledtext.ScrolledText(self.pg_ai, height=14)
        self.ai_out.pack(fill=tk.BOTH, expand=True)

        for label, var, show in [("API host", "host", None), ("Admin user", "user", None), ("Admin password", "password", "*")]:
            ttk.Label(self.pg_set, text=label).pack(anchor=tk.W)
            entry = ttk.Entry(self.pg_set, width=50, show=show or "")
            entry.insert(0, getattr(self.api, var))
            entry.pack(anchor=tk.W)
            entry.bind("<FocusOut>", lambda e, v=var, w=entry: setattr(self.api, v, w.get()))

        self.logbox = scrolledtext.ScrolledText(self, height=8)
        self.logbox.pack(fill=tk.BOTH, padx=8, pady=4)

    # ---- data views ----
    def api_bg(self, fn, done):
        threading.Thread(target=lambda: self._api_run(fn, done), daemon=True).start()

    def _api_run(self, fn, done):
        try:
            res = fn()
            self.after(0, lambda: done(res, None))
        except Exception as e:  # noqa: BLE001
            self.after(0, lambda: done(None, e))

    def on_dash(self):
        def _done(r, e):
            if e:
                self.log(f"dashboard: {e}"); return
            o = r["overview"]
            self.dash_lbl.config(
                text=f"Present {o['present_today']}/{o['total_students']} ({o['attendance_percentage']}%)"
                     f"  Absent {o['absent_today']}  Check-ins {o['checkins_today']}")
            for row in self.recent.get_children():
                self.recent.delete(row)
            for item in r["recent"]:
                self.recent.insert("", tk.END, values=(
                    item["captured_at_utc"][11:16], f"{item['first_name']} {item['last_name']}",
                    item["grade_class"]))
            self.log({"overview": o})
        def _go():
            stats = self.api.get("/api/v1/statistics/overview")
            recent = self.api.get("/api/v1/attendance?limit=8&offset=0")
            return {"overview": stats["overview"], "recent": recent["items"]}
        self.api_bg(_go, _done)

    def on_att(self):
        params = {"limit": 100, "offset": 0}
        if self.att_q.get().strip():
            params["q"] = self.att_q.get().strip()
        if self.att_class.get().strip():
            params["grade_class"] = self.att_class.get().strip()
        if self.att_day.get().strip():
            params["day"] = self.att_day.get().strip()
        def _done(r, e):
            if e:
                self.log(f"attendance: {e}"); return
            for row in self.atttable.get_children():
                self.atttable.delete(row)
            for x in r["items"]:
                self.atttable.insert("", tk.END, values=(
                    x["captured_at_utc"][:10], x["captured_at_utc"][11:16],
                    f"{x['first_name']} {x['last_name']}", x["roll_number"],
                    x["grade_class"], x["fingerprint_slot_id"], x["outcome"]))
            self.att_meta.config(text=f"{r['total']} record(s)")
        self.api_bg(lambda: self.api.get("/api/v1/attendance?" + urllib.parse.urlencode(params)), _done)

    def on_export(self, kind):
        import tkinter.filedialog as fd
        path = fd.asksaveasfilename(defaultextension="." + kind)
        if not path:
            return
        def _done(r, e):
            if e:
                self.log(f"export: {e}"); return
            with open(path, "wb") as f:
                f.write(r if isinstance(r, bytes) else r.encode())
            self.log(f"exported to {path}")
        ext = "export.csv" if kind == "csv" else "export.xlsx"
        self.api_bg(lambda: self.api.get("/api/v1/" + ext), _done)

    def on_stu(self):
        def _done(r, e):
            if e:
                self.log(f"students: {e}"); return
            for row in self.stutable.get_children():
                self.stutable.delete(row)
            self._students = {s["student_uuid"]: s for s in r["items"]}
            for s in r["items"]:
                self.stutable.insert("", tk.END, values=(
                    f"{s['first_name']} {s['last_name']}", s["roll_number"],
                    f"{s['grade_class']}{s['section']}", s["status"], s["fingerprint_slot_id"]),
                    iid=s["student_uuid"])
        q = self.stu_q.get().strip()
        self.api_bg(lambda: self.api.get("/api/v1/students?limit=100" + (f"&q={urllib.parse.quote(q)}" if q else "")), _done)

    def stu_open(self):
        sel = self.stutable.selection()
        if not sel:
            return
        s = self._students[sel[0]]
        if messagebox.askyesno("Student", f"Deactivate {s['first_name']} {s['last_name']}?"):
            self.api_bg(lambda: self.api.post(f"/api/v1/students/{sel[0]}/deactivate"),
                        lambda r, e: (self.log(f"deactivate: {e}") if e else self.on_stu()))

    def stu_dialog(self, _):
        top = tk.Toplevel(self)
        entries = {}
        for key in ("roll_number", "first_name", "last_name", "grade_class", "section"):
            ttk.Label(top, text=key).pack()
            entry = ttk.Entry(top, width=30)
            entry.pack()
            entries[key] = entry
        def _save():
            body = {k: w.get().strip() for k, w in entries.items()}
            self.api_bg(lambda: self.api.post("/api/v1/students", body),
                        lambda r, e: (self.log(f"add: {e}") if e else (top.destroy(), self.on_stu())))
        ttk.Button(top, text="Save", command=_save).pack()

    # ---- BLE ----
    def ble_cmd(self, cmd, params=None, timeout=20):
        self.bg(self.ble._send(cmd, params, timeout),
                lambda r, e: self.log(f"{cmd} FAILED: {e}") if e else self.log({cmd: r}))

    def on_scan_connect(self):
        if not HAVE_BLEAK:
            self.log("bleak not installed"); return
        async def _go():
            devs = await BleakScanner.discover(timeout=8.0, return_adv=True)
            for dev, adv in devs.values():
                uuids = [u.lower() for u in (adv.service_uuids or [])]
                if P.BLE_SERVICE_UUID.lower() in uuids:
                    client = BleakClient(dev)
                    await client.connect()
                    return client, dev.address
            raise RuntimeError("device not found")
        def _done(r, e):
            if e:
                self.log(f"connect: {e}"); return
            self.ble.client, addr = r
            self.dev_lbl.config(text=f"BLE: connected {addr}")
            self.log("connected " + addr)
        self.bg(_go(), _done)

    def on_dev_refresh(self):
        self.ble_cmd("DEVICE_INFO")
        self.ble_cmd("DEVICE_STATUS")

    def on_rtc_set(self):
        n = datetime.now()
        self.ble_cmd("RTC_SET", {"year": n.year, "month": n.month, "day": n.day,
                                 "hour": n.hour, "minute": n.minute, "second": n.second})

    def on_enroll(self):
        self.ble_cmd("FINGERPRINT_ENROLL", {"slot": int(self.slot.get())}, 120)

    def on_delete(self):
        self.ble_cmd("FINGERPRINT_DELETE", {"slot": int(self.slot.get())})

    def on_delete_all(self):
        if messagebox.askyesno("Confirm", "Delete ALL fingerprint templates?"):
            self.ble_cmd("FINGERPRINT_DELETE_ALL")

    def on_diag(self):
        def _done(r, e):
            if e:
                self.log(f"diagnostic: {e}"); return
            for row in self.diagtable.get_children():
                self.diagtable.delete(row)
            for t in r.get("data", {}).get("results", []):
                self.diagtable.insert("", tk.END, values=(t.get("test"), t.get("result"), t.get("reason", "")),
                                      tags=(t.get("result"),))
            self.log(r)
        self.bg(self.ble._send("FULL_DIAGNOSTIC"), _done)

    def on_ai(self):
        q = self.ai_q.get().strip()
        if not q:
            return
        def _done(r, e):
            if e:
                self.ai_out.insert(tk.END, f"Error: {e}\n"); return
            self.ai_out.insert(tk.END, f"Q: {q}\nA: {r['answer']}\n\n")
            self.log({"ai_tool": r["tool"], "ai_available": r["ai_available"]})
        self.api_bg(lambda: self.api.post("/api/v1/ai/chat", {"question": q}), _done)


if __name__ == "__main__":
    App().mainloop()
