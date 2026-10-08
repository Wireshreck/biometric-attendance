"""Windows desktop manager: dashboard, attendance, students,
fingerprints, device, diagnostics, AI assistant, settings.

Backends: BLE GATT (shared/ble_protocol.py) for device ops, HTTP REST
(same API as the web UI) for data. Real queries, no mock data.
"""
import asyncio
import base64
import ctypes
import json
import threading
import tkinter as tk
import urllib.request
import urllib.parse
from tkinter import font, messagebox, scrolledtext, ttk
from datetime import datetime

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # per-monitor V2: crisp, not blurry
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

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

    def put(self, path, body):
        return self._req("PUT", path, body)

    def delete(self, path):
        return self._req("DELETE", path)

    def patch(self, path, body):
        return self._req("PATCH", path, body)


ACCENT = "#2f5fd0"
INK = "#16213a"
MUTED = "#5b6b82"
SIDEBAR_BG = "#141a2b"
SIDEBAR_FG = "#dbe3f0"


def apply_theme(root):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(family="Segoe UI", size=10)
    text_font = font.nametofont("TkTextFont")
    text_font.configure(family="Segoe UI", size=10)
    style.configure(".", background="#f4f6f9", foreground=INK, fieldbackground="#ffffff")
    style.configure("TFrame", background="#f4f6f9")
    style.configure("Card.TFrame", background="#ffffff", relief="flat")
    style.configure("TLabel", background="#f4f6f9", foreground=INK)
    style.configure("Muted.TLabel", foreground=MUTED)
    style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
    style.configure("TButton", padding=(12, 7), relief="flat", background="#ffffff",
                    borderwidth=1, focusthickness=2)
    style.map("TButton", background=[("active", "#e9effe")])
    style.configure("Accent.TButton", background=ACCENT, foreground="#ffffff")
    style.map("Accent.TButton", background=[("active", "#2450b8")])
    style.configure("Nav.TButton", background=SIDEBAR_BG, foreground=SIDEBAR_FG,
                    relief="flat", anchor="w", padding=(14, 10), font=("Segoe UI", 10))
    style.map("Nav.TButton", background=[("active", "#1d2939")])
    style.configure("NavOn.TButton", background="#1d2939", foreground="#ffffff",
                    relief="flat", anchor="w", padding=(14, 10),
                    font=("Segoe UI", 10, "bold"))
    style.configure("Treeview", rowheight=26, fieldbackground="#ffffff")
    style.configure("Treeview.Heading", background="#fafbfd", foreground=MUTED)
    return style


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
        self.title("Biometric Attendance v1.3.0")
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

    def show(self, key):
        for page in self._pages.values():
            page.pack_forget()
        for name, btn in self._nav_buttons.items():
            btn.configure(style="NavOn.TButton" if name == key else "Nav.TButton")
        self._pages[key].pack(fill=tk.BOTH, expand=True)
        self._status.config(text=f"● {key}")

    def _title(self, parent, text):
        ttk.Label(parent, text=text, style="Title.TLabel").pack(anchor=tk.W, pady=(0, 6))

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
        apply_theme(self)
        self.title("Biometric Attendance")
        self.geometry("1080x760")
        self.configure(background="#f4f6f9")
        shell = ttk.Frame(self)
        shell.pack(fill=tk.BOTH, expand=True)
        side = tk.Frame(shell, bg=SIDEBAR_BG, width=200)
        side.pack(side=tk.LEFT, fill=tk.Y)
        side.pack_propagate(False)
        brand = tk.Label(side, text="Attendance", bg=SIDEBAR_BG, fg=SIDEBAR_FG,
                         font=("Segoe UI", 13, "bold"), anchor="w", padx=14, pady=14)
        brand.pack(fill=tk.X)
        self._nav_buttons = {}
        body = ttk.Frame(shell, padding=14)
        body.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._pages = {}
        for key, name in [("dash", "Dashboard"), ("att", "Attendance"),
                          ("stu", "Students"), ("fp", "Fingerprints"),
                          ("dev", "Device"), ("diag", "Diagnostics"),
                          ("ai", "AI Assistant"), ("set", "Settings")]:
            page = ttk.Frame(body)
            self._pages[key] = page
            btn = ttk.Button(side, text=name, style="Nav.TButton",
                             command=lambda k=key: self.show(k))
            btn.pack(fill=tk.X, padx=8, pady=1)
            self._nav_buttons[key] = btn
        self._status = ttk.Label(side, text="● idle", style="Muted.TLabel",
                                 background=SIDEBAR_BG, foreground="#8fa0b8")
        self._status.pack(side=tk.BOTTOM, fill=tk.X, padx=14, pady=10)
        self.pg_dash = self._pages["dash"]; self.pg_att = self._pages["att"]
        self.pg_stu = self._pages["stu"]; self.pg_fp = self._pages["fp"]
        self.pg_dev = self._pages["dev"]; self.pg_diag = self._pages["diag"]
        self.pg_ai = self._pages["ai"]; self.pg_set = self._pages["set"]
        self.show("dash")

        title = ttk.Label(self.pg_dash, text="Home", style="Title.TLabel")
        title.pack(anchor=tk.W, pady=(0, 6))
        scanrow = ttk.Frame(self.pg_dash)
        scanrow.pack(fill=tk.X, pady=(0, 6))
        ttk.Button(scanrow, text="SCAN", command=self.on_hero_scan,
                   style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 8))
        self.scan_state = ttk.Label(scanrow, text="not connected", style="Muted.TLabel")
        self.scan_state.pack(side=tk.LEFT)
        ttk.Button(self.pg_dash, text="Refresh dashboard", command=self.on_dash).pack(anchor=tk.W)
        self.dash_lbl = ttk.Label(self.pg_dash, text="—", justify=tk.LEFT)
        self.dash_lbl.pack(anchor=tk.W, pady=4)
        self.recent = self._table(self.pg_dash, ("time", "student", "class"), 8)
        self._sse_start()

        self._title(self.pg_att, "Attendance")
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

        self._title(self.pg_stu, "Students")
        row2 = ttk.Frame(self.pg_stu); row2.pack(fill=tk.X)
        self.stu_q = tk.StringVar()
        ttk.Entry(row2, textvariable=self.stu_q, width=24).pack(side=tk.LEFT)
        ttk.Button(row2, text="Search", command=self.on_stu).pack(side=tk.LEFT, padx=3)
        ttk.Button(row2, text="Add", command=lambda: self.stu_dialog(None)).pack(side=tk.LEFT)
        self.stutable = self._table(self.pg_stu, ("name", "roll", "class", "status", "fp"), 12)
        self.stutable.bind("<Double-1>", lambda e: self.stu_open())

        self._title(self.pg_fp, "Fingerprints")
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
        self.auto_btn = ttk.Button(row3, text="Auto-scan: off", command=self.on_auto)
        self.auto_btn.pack(side=tk.LEFT, padx=2)
        self.auto_lbl = ttk.Label(self.pg_fp, text="Auto-scan places no demands — put any enrolled finger on the sensor anytime.")
        self.auto_lbl.pack(anchor=tk.W)
        self._auto_on = False
        self._auto_busy = False

        self._title(self.pg_dev, "Device")
        ttk.Button(self.pg_dev, text="Scan + connect", command=self.on_scan_connect).pack(anchor=tk.W)
        self.dev_lbl = ttk.Label(self.pg_dev, text="BLE: disconnected")
        self.dev_lbl.pack(anchor=tk.W)
        for label, fn in [("Device refresh", self.on_dev_refresh),
                          ("RTC read", lambda: self.ble_cmd("RTC_GET")),
                          ("RTC set to PC time", self.on_rtc_set)]:
            ttk.Button(self.pg_dev, text=label, command=fn).pack(anchor=tk.W, pady=1)

        self._title(self.pg_diag, "Diagnostics")
        for label, fn in [("Full diagnostic", self.on_diag),
                          ("Buzzer test", lambda: self.ble_cmd("BUZZER_TEST")),
                          ("Ping", lambda: self.ble_cmd("PING"))]:
            ttk.Button(self.pg_diag, text=label, command=fn).pack(anchor=tk.W, pady=1)
        self.diagtable = self._table(self.pg_diag, ("test", "result", "reason"), 11)

        self._title(self.pg_ai, "AI Assistant")
        self.ai_q = tk.StringVar()
        ttk.Entry(self.pg_ai, textvariable=self.ai_q, width=70).pack(fill=tk.X)
        ttk.Button(self.pg_ai, text="Ask", command=self.on_ai).pack(anchor=tk.W, pady=2)
        self.ai_out = scrolledtext.ScrolledText(self.pg_ai, height=10)
        self.ai_out.pack(fill=tk.BOTH, expand=True)
        keyrow = ttk.Frame(self.pg_ai)
        keyrow.pack(fill=tk.X, pady=4)
        ttk.Label(keyrow, text="Gemini key (stored on server only):").pack(side=tk.LEFT)
        self.ai_key = tk.StringVar()
        ttk.Entry(keyrow, textvariable=self.ai_key, width=40, show="*").pack(side=tk.LEFT, padx=4)
        ttk.Button(keyrow, text="Save key", command=self.on_ai_key).pack(side=tk.LEFT)
        self.ai_key_lbl = ttk.Label(self.pg_ai, text="key status: unknown", style="Muted.TLabel")
        self.ai_key_lbl.pack(anchor=tk.W)

        self._title(self.pg_set, "Settings")
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
        resp = messagebox.askyesno(
            "Student",
            f"{s['first_name']} {s['last_name']}:\nYES = permanently DELETE (attendance rows lose the name link)\nNO = deactivate (keeps everything)")
        if resp is None:
            return
        if resp:
            self.api_bg(lambda: self.api.delete(f"/api/v1/students/{sel[0]}"),
                        lambda r, e: (self.log(f"delete: {e}") if e
                                      else (self.log(f"deleted, {r['orphaned_attendance_records']} orphaned"), self.on_stu())))
        else:
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

    def on_hero_scan(self):
        if not self.ble.connected:
            self.scan_state.config(text="BLE not connected — use Device tab")
            self.show("dev")
            return
        self.scan_state.config(text="SCANNING — place finger…")

        def _done(r, e):
            if e:
                self.scan_state.config(text=f"scan failed: {e}")
                return
            if r.get("code") == "match":
                slot = r["slot"]
                self.scan_state.config(text=f"match slot {slot} — recording…")
                self.api_bg(
                    lambda: self.api.post("/api/v1/assisted-checkin", {"fingerprint_slot_id": slot}),
                    lambda a, e2: self._scan_recorded(a, e2, r))
            elif r.get("code") == "no_match":
                self.scan_state.config(text="no match — unknown finger")
                self._overlay("NO MATCH", "Unknown fingerprint", "", "NOT ENROLLED", "", "")
            else:
                self.scan_state.config(text=f"scan: {r.get('code')}")
        self.bg(self.ble._send("FINGERPRINT_SEARCH", timeout=30), _done)

    def _scan_recorded(self, r, e, match):
        if e:
            self.scan_state.config(text=f"check-in failed: {e}")
            return
        dup = r.get("outcome") == "DUPLICATE_SUPPRESSED"
        self.scan_state.config(text="READY FOR SCAN" if not dup else "already recorded")
        self._overlay("ATTENDANCE",
                      f"{r.get('first_name', '')} {r.get('last_name', '')}".strip() or f"Slot {match.get('slot')}",
                      f"Class {r.get('grade_class', '')}{r.get('section', '')}",
                      "ALREADY RECORDED" if dup else "PRESENT",
                      (r.get("captured_at_utc", "")[:10] + "  " + r.get("captured_at_utc", "")[11:16]),
                      f"Fingerprint #{match.get('slot')} · confidence {match.get('confidence', '—')}")
        self.on_dash()

    def _overlay(self, kicker, name, cls, status, when, fp):
        top = tk.Toplevel(self)
        top.title("Attendance")
        top.geometry("420x360")
        top.attributes("-topmost", True)
        frm = ttk.Frame(top, padding=24)
        frm.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frm, text=kicker, style="Muted.TLabel").pack()
        ttk.Label(frm, text="✓" if status == "PRESENT" else ("⧗" if "ALREADY" in status else "?"),
                  font=("Segoe UI", 40)).pack()
        ttk.Label(frm, text=name, font=("Segoe UI", 18, "bold")).pack()
        ttk.Label(frm, text=cls, style="Muted.TLabel").pack()
        color = "#177245" if status == "PRESENT" else ("#9a6200" if "ALREADY" in status else "#b3261e")
        lbl = tk.Label(frm, text=status, font=("Segoe UI", 14, "bold"), fg=color, bg="#ffffff")
        lbl.pack(pady=6)
        ttk.Label(frm, text=when).pack()
        ttk.Label(frm, text=fp, style="Muted.TLabel").pack()
        self.after(6000, top.destroy)

    def _sse_start(self):
        def _run():
            import time as _time
            while True:
                try:
                    if not self.api.user:
                        _time.sleep(5)
                        continue
                    token = base64.b64encode(f"{self.api.user}:{self.api.password}".encode()).decode()
                    req = urllib.request.Request(
                        self.api.host + "/api/v1/events",
                        headers={"Authorization": "Basic " + token})
                    with urllib.request.urlopen(req, timeout=65) as r:
                        buf = b""
                        for chunk in r:
                            buf += chunk
                            while b"\n\n" in buf:
                                frame, buf = buf.split(b"\n\n", 1)
                                for line in frame.split(b"\n"):
                                    if line.startswith(b"data: "):
                                        try:
                                            msg = json.loads(line[6:].decode())
                                        except Exception:
                                            continue
                                        if msg.get("type") == "attendance.recorded":
                                            d = msg["data"]
                                            self.after(0, lambda d=d: self._sse_event(d))
                except Exception:
                    _time.sleep(5)
        threading.Thread(target=_run, daemon=True).start()

    def _sse_event(self, d):
        dup = d.get("outcome") == "DUPLICATE_SUPPRESSED"
        name = f"{d.get('first_name', '')} {d.get('last_name', '')}".strip() or "Unknown"
        self._overlay("ATTENDANCE", name,
                      f"Class {d.get('grade_class', '')}{d.get('section', '')}",
                      "ALREADY RECORDED" if dup else "PRESENT",
                      (d.get("captured_at_utc", "")[:10] + "  " + d.get("captured_at_utc", "")[11:16]),
                      f"Fingerprint #{d.get('fingerprint_slot_id', '—')}")
        self.on_dash()
        self.log({"live-event": d.get("event_uuid")})

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

    def on_auto(self):
        if self._auto_on:
            self._auto_on = False
            self.auto_btn.config(text="Auto-scan: off")
            self.auto_lbl.config(text="Auto-scan stopped.")
            return
        if not self.ble.connected:
            self.log("auto-scan: connect BLE first")
            return
        self._auto_on = True
        self.auto_btn.config(text="Auto-scan: on")
        self.auto_lbl.config(text="Listening — place any enrolled finger anytime.")
        self._auto_tick()

    def _auto_tick(self):
        if not self._auto_on:
            return
        if not self.ble.connected:
            self._auto_on = False
            self.auto_btn.config(text="Auto-scan: off")
            self.auto_lbl.config(text="Auto-scan stopped (disconnected).")
            return
        if self._auto_busy:
            self.after(2500, self._auto_tick)
            return
        self._auto_busy = True

        def _searched(r, e):
            try:
                if e:
                    if "not connected" in str(e).lower():
                        self._auto_on = False
                        self.auto_btn.config(text="Auto-scan: off")
                    return
                if r.get("code") == "match":
                    slot = r["slot"]
                    self.auto_lbl.config(text=f"Match: slot {slot} — recording…")
                    self.api_bg(
                        lambda: self.api.post("/api/v1/assisted-checkin", {"fingerprint_slot_id": slot}),
                        lambda a2, e2: self._auto_recorded(a2, e2, slot))
                else:
                    self.after(2500, self._auto_tick)
            finally:
                self._auto_busy = False

        self.bg(self.ble._send("FINGERPRINT_SEARCH", timeout=30), _searched)

    def _auto_recorded(self, r, e, slot):
        if e:
            self.log(f"auto check-in: {e}")
        else:
            outcome = r.get("outcome")
            self.auto_lbl.config(text=f"Slot {slot}: {outcome}")
            self.log(f"auto check-in slot {slot}: {outcome}")
            self.on_dash()
        self.after(4000, self._auto_tick)

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

    def on_ai_key(self):
        key = self.ai_key.get().strip()
        if not key:
            self.log("paste a key first")
            return

        def _done(r, e):
            if e:
                self.log(f"key save: {e}")
                return
            self.ai_key.set("")
            self.ai_key_lbl.config(text="key status: configured")
            self.log("Gemini key saved on server")

        self.api_bg(lambda: self.api.put("/api/v1/settings/ai", {"gemini_api_key": key}), _done)


if __name__ == "__main__":
    App().mainloop()
