"""install.exe — setup wizard for the biometric attendance platform.

Steps: 1 prerequisites, 2 auto-detect ESP32/serial ports, 3 port select
(never hardcoded; COM4 is never assumed), 4 firmware upload, 5 configure,
6 BLE verify, 7 hardware diagnostics, 8 install Windows app, 9 install
test.exe, 10 shortcuts, 11 final verification.
"""
import os
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

sys.path.insert(0, "..\\..\\shared")
sys.path.insert(0, "../../shared")
import ble_protocol as P

try:
    from serial.tools import list_ports
    HAVE_SERIAL = True
except ImportError:
    HAVE_SERIAL = False


def repo_root():
    here = os.path.abspath(os.path.dirname(__file__))
    for _ in range(6):
        if os.path.isdir(os.path.join(here, "firmware")) and os.path.isdir(os.path.join(here, "shared")):
            return here
        here = os.path.dirname(here)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


ESP32_HINTS = ("cp210", "ch340", "ch910", "usb serial", "silicon labs", "wch", "esp32")


class Wizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Biometric Attendance — Setup Wizard v1.2.0")
        self.geometry("860x640")
        self.root = repo_root()
        self.port = tk.StringVar()
        self.steps = []
        self._build()

    def _build(self):
        ttk.Label(self, text="Biometric Attendance — Setup Wizard",
                  font=("", 14, "bold")).pack(pady=6)
        ttk.Label(self, wraplength=820, text=(
            "R307S: red→VIN, black→GND, yellow→GPIO32, green→GPIO33. "
            "DS3231: SDA→GPIO25, SCL→GPIO26. Buzzer→GPIO27. OLED/LEDs removed."
        )).pack()
        body = ttk.Frame(self); body.pack(fill=tk.BOTH, expand=True, padx=8)
        self.table = ttk.Treeview(body, columns=("step", "result"), show="headings", height=12)
        self.table.heading("step", text="step"); self.table.heading("result", text="result")
        self.table.pack(fill=tk.X)
        row = ttk.Frame(body); row.pack(fill=tk.X, pady=6)
        ttk.Label(row, text="Serial port:").pack(side=tk.LEFT)
        self.portbox = ttk.Combobox(row, textvariable=self.port, width=40)
        self.portbox.pack(side=tk.LEFT, padx=6)
        ttk.Button(row, text="Detect ESP32", command=self.on_detect).pack(side=tk.LEFT)
        for label, fn in [("1. Prerequisites", self.s_prereq),
                          ("4. Upload firmware", self.s_upload),
                          ("5-6. Configure + BLE verify", self.s_verify_ble),
                          ("7. Hardware diagnostics", self.s_diag),
                          ("8-10. Install apps + shortcuts", self.s_install),
                          ("11. Final verification", self.s_final)]:
            ttk.Button(body, text=label, command=fn).pack(anchor=tk.W, pady=2)
        self.logbox = scrolledtext.ScrolledText(self, height=12)
        self.logbox.pack(fill=tk.BOTH, padx=8, pady=6, expand=True)

    def log(self, msg):
        self.logbox.insert(tk.END, str(msg) + "\n")
        self.logbox.see(tk.END)

    def mark(self, step, result):
        for rid in self.table.get_children():
            if self.table.set(rid, "step") == step:
                self.table.delete(rid)
        self.table.insert("", tk.END, values=(step, result))
        self.steps.append((step, result))
        self.log(f"{step}: {result}")

    # -- steps -------------------------------------------------------------
    def s_prereq(self):
        import importlib.util
        ok = True
        self.log(f"python {sys.version.split()[0]}")
        for mod in ("bleak", "serial", "PyInstaller"):
            name = "serial" if mod == "serial" else mod
            found = importlib.util.find_spec(name) is not None
            self.log(f"{mod}: {'OK' if found else 'MISSING'}")
            ok = ok and found
        pio = shutil.which("pio") or os.path.expanduser("~/.platformio/penv/Scripts/platformio.exe")
        self.log(f"platformio: {pio if pio and os.path.exists(pio) else 'MISSING'}")
        ok = ok and bool(pio and (shutil.which("pio") or os.path.exists(pio)))
        self.mark("prerequisites", "PASS" if ok else "FAIL (see log)")

    def on_detect(self):
        if not HAVE_SERIAL:
            self.log("pyserial missing: pip install pyserial"); return
        ports = list(list_ports.comports())
        scored = []
        for p in ports:
            desc = f"{p.device} — {p.description}".lower()
            likely = any(h in desc for h in ESP32_HINTS)
            scored.append((not likely, p.device, p.description))
        scored.sort()
        self.portbox["values"] = [f"{dev} | {desc}" for _, dev, desc in scored]
        if scored:
            self.portbox.current(0)
            self.port.set(scored[0][1])
        self.mark("detect-esp32",
                  f"{len(scored)} port(s); likely first" if scored else "FAIL — no serial ports found")

    def selected_port(self):
        raw = self.port.get().strip()
        if not raw:
            messagebox.showinfo("Port", "Run Detect ESP32 first, or pick a port manually.")
            return None
        return raw.split("|")[0].strip().split()[0]

    def s_upload(self):
        port = self.selected_port()
        if not port:
            return
        self.log(f"uploading production firmware via {port} (never assumes COM4)...")
        pio = shutil.which("pio") or os.path.expanduser("~/.platformio/penv/Scripts/platformio.exe")
        fw = os.path.join(self.root, "firmware")
        try:
            r = subprocess.run([pio, "run", "-d", fw, "-e", "production",
                                "-t", "upload", "--upload-port", port],
                               capture_output=True, text=True, timeout=300)
            self.log((r.stdout or "")[-2000:] + (r.stderr or "")[-2000:])
            self.mark("upload-firmware", "PASS" if r.returncode == 0 else "FAIL (see log)")
        except Exception as e:  # noqa: BLE001
            self.mark("upload-firmware", f"FAIL: {e}")

    def s_verify_ble(self):
        self.log("BLE verify: put the ESP32 in range, then use the desktop app or test.exe "
                 "CONNECT + PING. Automated BLE scan from this wizard:")
        try:
            import asyncio
            from bleak import BleakScanner
            devs = asyncio.run(BleakScanner.discover(timeout=8.0))
            names = [f"{d.name}@{d.address}" for d in devs
                     if d.name and "biometric" in d.name.lower()]
            self.mark("ble-verify", f"PASS — advertising: {names}" if names
                      else "WARN — device not seen; verify power/advertising manually")
        except Exception as e:  # noqa: BLE001
            self.mark("ble-verify", f"WARN: {e}")

    def s_diag(self):
        self.log("Run test.exe → RUN FULL SYSTEM TEST. Honesty rules: disconnected "
                 "hardware is FAIL/SKIPPED, never PASS.")
        self.mark("hardware-diagnostics", "MANUAL — run test.exe full system test")

    def s_install(self):
        try:
            apps = os.path.join(os.path.expanduser("~"), "BiometricAttendance")
            os.makedirs(apps, exist_ok=True)
            copied = []
            for src in (os.path.join(self.root, "dist", "BiometricDesktop.exe"),
                        os.path.join(self.root, "dist", "test.exe")):
                if os.path.exists(src):
                    dst = os.path.join(apps, os.path.basename(src))
                    shutil.copy2(src, dst)
                    copied.append(dst)
            bat = os.path.join(apps, "BiometricDesktop.bat")
            with open(bat, "w", encoding="utf-8") as f:
                f.write("@echo off\r\nstart \"\" \"%~dp0BiometricDesktop.exe\"\r\n")
            self.mark("install-apps", f"PASS — {len(copied)} exe(s) + launcher in {apps}"
                      if copied else f"WARN — no dist exes yet; launcher only in {apps}")
        except Exception as e:  # noqa: BLE001
            self.mark("install-apps", f"FAIL: {e}")

    def s_final(self):
        self.log(f"service={P.BLE_SERVICE_UUID} pins={P.PINS}")
        self.log("Final check: desktop app connects, dashboard loads, RTC valid, "
                 "FULL_DIAGNOSTIC honest, attendance round-trip works.")
        self.mark("final-verification", "MANUAL — confirm demo flow in docs/setup.md")


if __name__ == "__main__":
    Wizard().mainloop()
