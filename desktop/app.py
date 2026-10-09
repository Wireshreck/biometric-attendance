"""Biometric Attendance desktop shell v1.5.0.

A native window (Edge WebView2) hosting the exact web console served by
the local backend — the desktop UI is pixel-identical to the web UI by
construction. This launcher ensures the backend is running (starting it
if needed), waits for health, then opens the console. Closing the window
stops a backend it started itself.

First run: if backend/.env is missing, it is created from .env.example
with a generated admin password, shown once so it can be used to sign in.
"""
import ctypes
import os
import secrets
import shutil
import socket
import subprocess
import sys
import time
import urllib.request

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

HOST = "127.0.0.1"
PORT = 8000
BASE = f"http://{HOST}:{PORT}"


def repo_root():
    # Source tree (desktop/..), or an installed tree with backend/+web/
    # siblings next to the exe (see tools/installer).
    here = os.path.abspath(os.path.dirname(__file__))
    if getattr(sys, "frozen", False):
        here = os.path.dirname(sys.executable)
    if os.path.isdir(os.path.join(here, "..", "backend")):
        return os.path.abspath(os.path.join(here, ".."))
    return here


def port_open():
    sock = socket.socket()
    sock.settimeout(1.0)
    try:
        sock.connect((HOST, PORT))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def healthy():
    try:
        with urllib.request.urlopen(BASE + "/health", timeout=5) as r:
            return r.status == 200
    except Exception:
        return False


def ensure_env(backend_dir):
    env_path = os.path.join(backend_dir, ".env")
    generated = None
    if not os.path.exists(env_path):
        example = os.path.join(backend_dir, ".env.example")
        if os.path.exists(example):
            shutil.copy(example, env_path)
        password = "admin-" + secrets.token_hex(4)
        lines = []
        if os.path.exists(env_path):
            with open(env_path, encoding="utf-8") as f:
                lines = f.read().splitlines()
        out, seen_user, seen_pass = [], False, False
        for line in lines:
            if line.startswith("ADMIN_USERNAME="):
                out.append("ADMIN_USERNAME=admin")
                seen_user = True
            elif line.startswith("ADMIN_PASSWORD="):
                out.append(f"ADMIN_PASSWORD={password}")
                seen_pass = True
            else:
                out.append(line)
        if not seen_user:
            out.append("ADMIN_USERNAME=admin")
        if not seen_pass:
            out.append(f"ADMIN_PASSWORD={password}")
        with open(env_path, "w", encoding="utf-8", newline="") as f:
            f.write("\n".join(out) + "\n")
        generated = ("admin", password)
    return env_path, generated


def start_backend(backend_dir):
    env = dict(os.environ)
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", HOST, "--port", str(PORT)],
        cwd=backend_dir, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return proc


def main():
    import tkinter as tk
    from tkinter import messagebox

    root = repo_root()
    backend_dir = os.path.join(root, "backend")
    if not os.path.isdir(backend_dir) or not os.path.isdir(os.path.join(root, "web")):
        messagebox.showerror("Backend missing",
                             "Install the backend next to this app (see install.exe), "
                             f"or run from the repository.\nLooked under:\n{root}")
        return 1
    env_path, generated = ensure_env(backend_dir)
    owned = False
    backend_proc = None
    if not healthy():
        if port_open():
            messagebox.showerror("Port busy",
                                 f"Port {PORT} is taken by something that is not this backend.")
            return 1
        backend_proc = start_backend(backend_dir)
        owned = True
        for _ in range(30):
            time.sleep(1)
            if healthy():
                break
        else:
            messagebox.showerror("Backend failed",
                                 "The backend did not become healthy. Check backend/.env.")
            if backend_proc:
                backend_proc.terminate()
            return 1
    if generated:
        messagebox.showinfo(
            "First-run sign-in (shown once)",
            f"A backend admin account was created:\n\nusername: {generated[0]}\n"
            f"password: {generated[1]}\n\nIt is saved in backend/.env — "
            "use it to sign in to the console.",
        )
    try:
        import webview
    except ImportError:
        messagebox.showerror("Missing component",
                             "pywebview is not installed. Run: pip install pywebview")
        if owned and backend_proc:
            backend_proc.terminate()
        return 1
    window = webview.create_window("Biometric Attendance", BASE,
                                   width=1280, height=800)
    try:
        webview.start(gui="edgechromium")
    finally:
        if owned and backend_proc:
            backend_proc.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
