"""Terminal enrollment/search guide.

Walks you through fingerprint capture with on-screen cues and countdowns,
then shows the real device result. Uses the shared BLE protocol; nothing
is faked. Run:  python tools/enroll_guide/enroll_guide.py

Requires: pip install bleak
"""
import asyncio
import json
import sys
import time

sys.path.insert(0, "shared")
import ble_protocol as P

try:
    from bleak import BleakScanner, BleakClient
except ImportError:
    print("Install BLE support first:  pip install bleak")
    raise SystemExit(1)

BASE = "0000{:04x}-0000-1000-8000-00805f9b34fb"
SVC = P.BLE_SERVICE_UUID


def uuid(short):
    return BASE.format(int(short, 16))


async def countdown(label, seconds):
    for remaining in range(seconds, 0, -1):
        print(f"\r{label}: {remaining:2d}s  ", end="", flush=True)
        await asyncio.sleep(1)
    print(f"\r{label}: done      ")


async def find_device():
    print("Scanning for the ESP32 (10s)...")
    found = await BleakScanner.discover(timeout=10.0, return_adv=True)
    for dev, adv in found.values():
        uuids = [u.lower() for u in (adv.service_uuids or [])]
        if SVC in uuids or (dev.name and "biometric" in dev.name.lower()):
            print(f"Found {dev.name} @ {dev.address}")
            return dev
    print("Device not advertising. Press EN/RST on the ESP32 and retry.")
    return None


async def send(client, cmd, params=None, timeout=130):
    char = uuid(P.BLE_CHARS[P.CHAR_FOR_COMMAND[cmd]])
    if not client.is_connected:
        print("(reconnecting...)")
        await client.connect()
        await asyncio.sleep(1.0)
    await client.write_gatt_char(
        char, P.build_request(cmd, params).encode(), response=True)
    deadline = time.monotonic() + timeout
    await asyncio.sleep(0.4)
    while True:
        raw = await asyncio.wait_for(client.read_gatt_char(char), timeout)
        msg = P.parse_response(bytes(raw).decode("utf-8"))
        if msg.get("status") != "busy":
            return msg
        if time.monotonic() >= deadline:
            raise TimeoutError(f"{cmd} still busy after {timeout}s")
        await asyncio.sleep(0.5)


async def keepalive(client, stop):
    """GAP reads keep the Windows link from going stale during long cues."""
    gap = uuid("2A00")
    while not stop.is_set():
        try:
            await client.read_gatt_char(gap)
        except Exception:  # noqa: BLE001
            pass
        await asyncio.sleep(4)


async def enroll(client):
    slot = input("Slot number to enroll [1]: ").strip() or "1"
    print("Keep your finger OFF the sensor.")
    input("Press ENTER to start (you will get a 3-2-1 first)... ")
    for i in (3, 2, 1):
        print(f"\rStarting in {i}...", end="", flush=True)
        await asyncio.sleep(1)
    print("\r" + "=" * 60)
    stop = asyncio.Event()
    ka = asyncio.ensure_future(keepalive(client, stop))
    try:
        task = asyncio.ensure_future(
            send(client, "FINGERPRINT_ENROLL", {"slot": int(slot)}, timeout=300))
        await asyncio.sleep(1.0)  # let the command stage before cues
        print(">>> PLACE YOUR FINGER ON THE SENSOR — HOLD STILL <<<")
        await countdown("Hold", 15)
        print(">>> LIFT YOUR FINGER OFF <<<")
        await countdown("Finger off", 8)
        print(">>> PLACE THE SAME FINGER AGAIN — HOLD STILL <<<")
        await countdown("Hold again", 20)
        print("Waiting for the device verdict...")
        result = await task
    finally:
        stop.set()
        await ka
    print("=" * 60)
    print("RESULT:", json.dumps(result, indent=1))
    if result.get("code") == "enroll_success":
        print("Enrolled. Note the slot: it must match the backend employee record.")


async def search(client):
    print("Place a finger on the sensor and keep it there.")
    input("Press ENTER to search... ")
    result = await send(client, "FINGERPRINT_SEARCH", {}, timeout=40)
    print("RESULT:", json.dumps(result, indent=1))


async def status(client):
    for cmd in ("DEVICE_STATUS", "FINGERPRINT_COUNT", "FULL_DIAGNOSTIC"):
        try:
            result = await send(client, cmd, {}, timeout=30)
        except Exception as exc:  # noqa: BLE001
            print(cmd, "FAILED:", str(exc)[:100])
            continue
        if cmd == "FULL_DIAGNOSTIC":
            for t in result["data"]["results"]:
                print(f"  {t['test']:15s} {t['result']} {t.get('reason', '')}")
        else:
            print(cmd, json.dumps(result.get("data", result)))


async def main():
    dev = await find_device()
    if not dev:
        return
    async with BleakClient(dev) as client:
        await asyncio.sleep(1.0)
        while True:
            print("\n[1] enroll  [2] search  [3] status  [q] quit")
            choice = input("> ").strip().lower()
            try:
                if choice == "1":
                    await enroll(client)
                elif choice == "2":
                    await search(client)
                elif choice == "3":
                    await status(client)
                elif choice in ("q", "quit", "exit"):
                    return
            except Exception as exc:  # noqa: BLE001 — stay in menu on any failure
                print(f"FAILED (back to menu): {type(exc).__name__}: {str(exc)[:160]}")


if __name__ == "__main__":
    asyncio.run(main())
