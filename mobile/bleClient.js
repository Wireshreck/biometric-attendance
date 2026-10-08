// BLE transport for the mobile app. Uses the single shared protocol
// (../shared/ble_protocol.js) over react-native-ble-plx. Characteristic
// UUIDs are the 16-bit forms 0x1101..0x1108 under the custom service,
// exactly as the firmware exposes them (see docs/protocol.md).
import { BleManager } from 'react-native-ble-plx';
import { Buffer } from 'buffer';
import {
  BLE_SERVICE_UUID, BLE_CHARS, CHAR_FOR_COMMAND,
  buildRequest, parseResponse, TIMEOUTS_MS,
} from '../shared/ble_protocol.js';

const charUuid = (name) => {
  const short = BLE_CHARS[name];
  // ble-plx accepts full 128-bit UUIDs; 16-bit values expand against the
  // Bluetooth base UUID, which matches the firmware's 16-bit registration.
  const hex = short.padStart(4, '0').toLowerCase();
  return `0000${hex}-0000-1000-8000-00805f9b34fb`;
};

export class DeviceClient {
  constructor() {
    this.manager = new BleManager();
    this.device = null;
  }

  async scan(onFound, timeoutMs = 10000) {
    const seen = new Set();
    return new Promise((resolve) => {
      const sub = this.manager.onStateChange((state) => {
        if (state !== 'PoweredOn') return;
        this.manager.startDeviceScan([BLE_SERVICE_UUID], null, (err, dev) => {
          if (err || !dev) return;
          if (seen.has(dev.id)) return;
          seen.add(dev.id);
          onFound({ id: dev.id, name: dev.name || dev.localName || 'unknown' });
        });
      }, true);
      setTimeout(() => {
        this.manager.stopDeviceScan();
        sub.remove();
        resolve();
      }, timeoutMs);
    });
  }

  async connect(id) {
    this.device = await this.manager.connectToDevice(id);
    await this.device.discoverAllServicesAndCharacteristics();
    return this.device;
  }

  async disconnect() {
    if (this.device) {
      await this.manager.cancelDeviceConnection(this.device.id).catch(() => {});
      this.device = null;
    }
  }

  get connected() { return !!this.device; }

  async send(cmd, params = {}, timeoutMs = TIMEOUTS_MS.DEFAULT) {
    if (!this.device) throw new Error('not connected');
    const charName = CHAR_FOR_COMMAND[cmd];
    const uuid = charUuid(charName);
    const body = buildRequest(cmd, params);
    const t0 = Date.now();
    await this.device.writeCharacteristicWithResponseForService(
      BLE_SERVICE_UUID, uuid, Buffer.from(body, 'utf8').toString('base64'));
    for (;;) {
      await new Promise((r) => setTimeout(r, 400));
      const w = await this.device.readCharacteristicForService(BLE_SERVICE_UUID, uuid);
      const msg = parseResponse(Buffer.from(w.value, 'base64').toString('utf8'));
      if (msg.status !== 'busy' || Date.now() - t0 > timeoutMs) return msg;
    }
  }
}

export const client = new DeviceClient();
