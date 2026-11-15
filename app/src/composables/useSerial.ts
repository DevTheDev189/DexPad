import { ref, onMounted, onUnmounted } from 'vue';
import type { SerialPortEntry, InputTelemetry, Profile } from '../types/keymap';

// Check if running inside Tauri window
const isTauri = typeof window !== 'undefined' && ('__TAURI_INTERNALS__' in window || '__TAURI__' in window);

export function useSerial() {
  const ports = ref<SerialPortEntry[]>([]);
  const selectedPort = ref<string>('');
  const isConnected = ref(false);
  const isStreamingTelemetry = ref(false);
  const telemetryData = ref<InputTelemetry | null>(null);
  const lastAckMessage = ref<string>('');
  const connectionError = ref<string | null>(null);

  // Tauri unlisten functions
  let unlistenTelemetry: (() => void) | null = null;
  let unlistenAck: (() => void) | null = null;
  let unlistenProfile: (() => void) | null = null;
  let unlistenDisconnect: (() => void) | null = null;

  // Scan serial ports
  const refreshPorts = async () => {
    if (!isTauri) {
      // Mock ports for browser testing / demo
      ports.value = [
        {
          name: '/dev/cu.usbmodem1101 (ESP32-S3 Dongle)',
          port_type: 'USB',
          vid: 0x303a,
          pid: 0x1001,
          manufacturer: 'Espressif',
          product: 'ESP32-S3 Cosmic Bridge',
          is_esp32: true,
        },
        {
          name: 'COM3 (ESP32-S3 CDC)',
          port_type: 'USB',
          vid: 0x303a,
          pid: 0x1001,
          manufacturer: 'Espressif',
          product: 'ESP32-S3 Cosmic Bridge',
          is_esp32: true,
        },
      ];
      if (!selectedPort.value && ports.value.length > 0) {
        selectedPort.value = ports.value[0].name;
      }
      return;
    }

    try {
      const { invoke } = await import('@tauri-apps/api/core');
      const list = await invoke<SerialPortEntry[]>('get_ports');
      ports.value = list;

      // Auto-select ESP32 if found
      const esp = list.find((p) => p.is_esp32);
      if (esp && !selectedPort.value) {
        selectedPort.value = esp.name;
      } else if (list.length > 0 && !selectedPort.value) {
        selectedPort.value = list[0].name;
      }
    } catch (e: any) {
      console.warn('Failed to enumerate ports:', e);
    }
  };

  // Connect to selected port
  const connect = async (portName?: string) => {
    const target = portName || selectedPort.value;
    if (!target) return;

    connectionError.value = null;

    if (!isTauri) {
      isConnected.value = true;
      selectedPort.value = target;
      lastAckMessage.value = 'Connected in Web Simulation Mode';
      return;
    }

    try {
      const { invoke } = await import('@tauri-apps/api/core');
      await invoke('connect_port', {
        portName: target,
        baudRate: 115200,
      });
      isConnected.value = true;
      selectedPort.value = target;
    } catch (e: any) {
      connectionError.value = typeof e === 'string' ? e : e.message || 'Connection failed';
      isConnected.value = false;
    }
  };

  // Disconnect
  const disconnect = async () => {
    if (!isTauri) {
      isConnected.value = false;
      return;
    }

    try {
      const { invoke } = await import('@tauri-apps/api/core');
      await invoke('disconnect_port');
      isConnected.value = false;
    } catch (e: any) {
      console.warn('Disconnect error:', e);
      isConnected.value = false;
    }
  };

  // Send profile to dongle NVS
  const sendProfileToDevice = async (profile: Profile) => {
    if (!isTauri) {
      lastAckMessage.value = `Profile "${profile.name}" saved to slot ${profile.slot} (Simulation)`;
      return true;
    }

    try {
      const { invoke } = await import('@tauri-apps/api/core');
      await invoke('send_profile', {
        slot: profile.slot,
        name: profile.name,
        sticks: profile.sticks,
        buttons: profile.buttons,
      });
      lastAckMessage.value = `Profile "${profile.name}" written to Slot ${profile.slot + 1}`;
      return true;
    } catch (e: any) {
      connectionError.value = `Failed to save profile: ${e}`;
      return false;
    }
  };

  // Switch active slot on dongle
  const switchDeviceSlot = async (slot: number) => {
    if (!isTauri) return;

    try {
      const { invoke } = await import('@tauri-apps/api/core');
      await invoke('switch_slot', { slot });
    } catch (e: any) {
      console.warn('Failed to switch slot:', e);
    }
  };

  // Toggle input telemetry stream
  const toggleTelemetryStream = async (enable?: boolean) => {
    const targetState = enable !== undefined ? enable : !isStreamingTelemetry.value;
    isStreamingTelemetry.value = targetState;

    if (!isTauri) {
      // If browser simulation, trigger dummy telemetry on mouse move or interval
      return;
    }

    try {
      const { invoke } = await import('@tauri-apps/api/core');
      await invoke('set_input_stream', { enabled: targetState });
    } catch (e: any) {
      console.warn('Failed to toggle input stream:', e);
    }
  };

  // Event Listeners setup
  const setupEventListeners = async () => {
    if (!isTauri) return;

    try {
      const { listen } = await import('@tauri-apps/api/event');

      unlistenTelemetry = await listen<InputTelemetry>('serial-telemetry', (event) => {
        telemetryData.value = event.payload;
      });

      unlistenAck = await listen<any>('serial-ack', (event) => {
        if (event.payload.msg) {
          lastAckMessage.value = event.payload.msg;
        }
      });

      unlistenProfile = await listen<any>('serial-profile-data', (event) => {
        if (event.payload) {
          lastAckMessage.value = `Profile received: ${event.payload.name || ''}`;
        }
      });

      unlistenDisconnect = await listen<string>('serial-disconnected', (event) => {
        isConnected.value = false;
        connectionError.value = event.payload;
      });
    } catch (e: any) {
      console.warn('Could not attach Tauri event listeners:', e);
    }
  };

  onMounted(() => {
    refreshPorts();
    setupEventListeners();
  });

  onUnmounted(() => {
    if (unlistenTelemetry) unlistenTelemetry();
    if (unlistenAck) unlistenAck();
    if (unlistenProfile) unlistenProfile();
    if (unlistenDisconnect) unlistenDisconnect();
  });

  return {
    ports,
    selectedPort,
    isConnected,
    isStreamingTelemetry,
    telemetryData,
    lastAckMessage,
    connectionError,
    refreshPorts,
    connect,
    disconnect,
    sendProfileToDevice,
    switchDeviceSlot,
    toggleTelemetryStream,
  };
}
