import { ref, onMounted, onUnmounted } from 'vue';
import type { SerialPortEntry, InputTelemetry, Profile } from '../types/keymap';
import type { PlatformLegendMode } from '../types/controllers';

export type DongleConnectionStatus = 'disconnected' | 'searching' | 'ready';

export interface PicoBootloaderDevice {
  mount_path: string;
  volume_name: string;
  board_id: string;
  model: string;
  is_pico_2: boolean;
}

// Check if running inside Tauri window
const isTauri = typeof window !== 'undefined' && ('__TAURI_INTERNALS__' in window || '__TAURI__' in window);

export function useSerial() {
  const ports = ref<SerialPortEntry[]>([]);
  const selectedPort = ref<string>('');
  const isConnected = ref(false);
  const controllerConnected = ref(false);
  const connectionStatus = ref<DongleConnectionStatus>('disconnected');
  const dongleFw = ref('2.0.0');
  const dongleDevice = ref('dexpad-bridge');
  const detectedControllerType = ref<PlatformLegendMode>('playstation');
  const detectedControllerName = ref<string>('DualSense Wireless Controller');
  const picoBootloaderDevice = ref<PicoBootloaderDevice | null>(null);
  const isFlashingPico = ref(false);
  const flashStatusMessage = ref<string | null>(null);
  const flashError = ref<string | null>(null);
  const isStreamingTelemetry = ref(false);
  const telemetryData = ref<InputTelemetry | null>(null);
  const lastAckMessage = ref<string>('');
  const connectionError = ref<string | null>(null);

  // Tauri unlisten functions
  let unlistenTelemetry: (() => void) | null = null;
  let unlistenAck: (() => void) | null = null;
  let unlistenProfile: (() => void) | null = null;
  let unlistenHeartbeat: (() => void) | null = null;
  let unlistenDisconnect: (() => void) | null = null;
  let autoConnectTimer: any = null;

  // Scan serial ports
  const refreshPorts = async () => {
    if (!isTauri) {
      ports.value = [
        {
          name: 'COM4 (Pico 2 W 8BitDo Bridge)',
          port_type: 'USB',
          vid: 0x2e8a,
          pid: 0x000a,
          manufacturer: 'Raspberry Pi',
          product: 'Pico 2 W 8BitDo Bridge',
          is_esp32: false,
          is_pico: true,
        },
      ];
      if (!selectedPort.value && ports.value.length > 0) {
        selectedPort.value = ports.value[0].name;
        isConnected.value = true;
        controllerConnected.value = true;
        connectionStatus.value = 'ready';
      }
      return;
    }

    try {
      const { invoke } = await import('@tauri-apps/api/core');
      const list = await invoke<SerialPortEntry[]>('get_ports');
      ports.value = list;

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

  // Attempt auto connect
  const attemptAutoConnect = async () => {
    if (!isTauri || isConnected.value) return;

    try {
      const { invoke } = await import('@tauri-apps/api/core');
      const connectedName = await invoke<string | null>('auto_connect_dongle');
      if (connectedName) {
        isConnected.value = true;
        selectedPort.value = connectedName;
        connectionStatus.value = 'searching';
        connectionError.value = null;
      }
    } catch {
      // Ignored during passive background scan
    }
  };

  // Connect to selected port
  const connect = async (portName?: string) => {
    const target = portName || selectedPort.value;
    if (!target) return;

    connectionError.value = null;

    if (!isTauri) {
      isConnected.value = true;
      controllerConnected.value = true;
      connectionStatus.value = 'ready';
      selectedPort.value = target;
      lastAckMessage.value = 'Connected in Simulation Mode';
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
      connectionStatus.value = 'searching';
    } catch (e: any) {
      connectionError.value = typeof e === 'string' ? e : e.message || 'Connection failed';
      isConnected.value = false;
      controllerConnected.value = false;
      connectionStatus.value = 'disconnected';
    }
  };

  // Disconnect
  const disconnect = async () => {
    if (!isTauri) {
      isConnected.value = false;
      controllerConnected.value = false;
      connectionStatus.value = 'disconnected';
      return;
    }

    try {
      const { invoke } = await import('@tauri-apps/api/core');
      await invoke('disconnect_port');
      isConnected.value = false;
      controllerConnected.value = false;
      connectionStatus.value = 'disconnected';
    } catch (e: any) {
      console.warn('Disconnect error:', e);
      isConnected.value = false;
      controllerConnected.value = false;
      connectionStatus.value = 'disconnected';
    }
  };

  // Send profile to dongle NVS
  const sendProfileToDevice = async (profile: Profile) => {
    if (!isTauri) {
      lastAckMessage.value = `Profile "${profile.name}" saved to slot ${profile.slot + 1} (Simulation)`;
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

    if (!isTauri) return;

    try {
      const { invoke } = await import('@tauri-apps/api/core');
      await invoke('set_input_stream', { enabled: targetState });
    } catch (e: any) {
      console.warn('Failed to toggle input stream:', e);
    }
  };

  const rebootToBootloader = async () => {
    if (!isTauri) {
      lastAckMessage.value = 'Simulated reboot to UF2 Bootloader (RPI-RP2)';
      return true;
    }
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      await invoke('reboot_to_bootloader');
      return true;
    } catch (e: any) {
      console.warn('Failed to reboot to bootloader:', e);
      return false;
    }
  };

  // Pico Bootloader scan
  const checkPicoBootloader = async (): Promise<PicoBootloaderDevice | null> => {
    if (!isTauri) return null;
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      const device = await invoke<PicoBootloaderDevice | null>('detect_pico_bootloader');
      picoBootloaderDevice.value = device;
      return device;
    } catch (e) {
      console.warn('Failed to scan for Pico bootloaders:', e);
      return null;
    }
  };

  // Flash firmware to mounted Pico bootloader
  const flashPico = async (mountPath: string, target?: string): Promise<boolean> => {
    if (!isTauri) {
      isFlashingPico.value = true;
      flashStatusMessage.value = 'Simulating UF2 firmware copy...';
      await new Promise((r) => setTimeout(r, 1200));
      isFlashingPico.value = false;
      flashStatusMessage.value = 'Firmware successfully flashed (Simulation). Device is rebooting into DexPad mode...';
      picoBootloaderDevice.value = null;
      return true;
    }

    isFlashingPico.value = true;
    flashStatusMessage.value = 'Writing DexPad UF2 firmware to Pico volume...';
    flashError.value = null;

    try {
      const { invoke } = await import('@tauri-apps/api/core');
      const result = await invoke<string>('flash_pico_firmware', {
        mountPath,
        target,
      });
      flashStatusMessage.value = result;
      picoBootloaderDevice.value = null;

      // Auto reconnect after reboot
      setTimeout(() => {
        refreshPorts();
        attemptAutoConnect();
      }, 2500);
      return true;
    } catch (e: any) {
      flashError.value = typeof e === 'string' ? e : e.message || 'Flashing failed';
      return false;
    } finally {
      isFlashingPico.value = false;
    }
  };

  const updateControllerFromPayload = (payload: any) => {
    if (!payload) return;
    if (payload.controller_connected !== undefined) {
      controllerConnected.value = Boolean(payload.controller_connected);
      connectionStatus.value = controllerConnected.value ? 'ready' : 'searching';
    }
    if (payload.fw) dongleFw.value = payload.fw;
    if (payload.device) dongleDevice.value = payload.device;

    if (payload.controller_type) {
      const raw = String(payload.controller_type).toLowerCase();
      if (raw.includes('playstation') || raw.includes('dualsense') || raw.includes('dualshock') || raw.includes('sony')) {
        detectedControllerType.value = 'playstation';
      } else if (raw.includes('xbox') || raw.includes('microsoft')) {
        detectedControllerType.value = 'xbox';
      } else if (raw.includes('switch') || raw.includes('nintendo') || raw.includes('joycon')) {
        detectedControllerType.value = 'nintendo';
      } else if (raw.includes('8bitdo')) {
        detectedControllerType.value = 'eightbitdo';
      }
    }

    if (payload.controller_name && typeof payload.controller_name === 'string') {
      detectedControllerName.value = payload.controller_name;
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
        updateControllerFromPayload(event.payload);
      });

      unlistenHeartbeat = await listen<any>('serial-heartbeat', (event) => {
        updateControllerFromPayload(event.payload);
      });

      unlistenProfile = await listen<any>('serial-profile-data', (event) => {
        if (event.payload) {
          lastAckMessage.value = `Profile received: ${event.payload.name || ''}`;
        }
      });

      unlistenDisconnect = await listen<string>('serial-disconnected', (event) => {
        isConnected.value = false;
        controllerConnected.value = false;
        connectionStatus.value = 'disconnected';
        connectionError.value = event.payload;
      });
    } catch (e: any) {
      console.warn('Could not attach Tauri event listeners:', e);
    }
  };

  onMounted(() => {
    refreshPorts();
    setupEventListeners();
    attemptAutoConnect();
    checkPicoBootloader();

    // Auto-detect polling every 2s if disconnected or check bootloader
    autoConnectTimer = setInterval(() => {
      if (!isConnected.value) {
        attemptAutoConnect();
        checkPicoBootloader();
      }
    }, 2000);
  });

  onUnmounted(() => {
    if (autoConnectTimer) clearInterval(autoConnectTimer);
    if (unlistenTelemetry) unlistenTelemetry();
    if (unlistenAck) unlistenAck();
    if (unlistenHeartbeat) unlistenHeartbeat();
    if (unlistenProfile) unlistenProfile();
    if (unlistenDisconnect) unlistenDisconnect();
  });

  return {
    ports,
    selectedPort,
    isConnected,
    controllerConnected,
    connectionStatus,
    dongleFw,
    dongleDevice,
    detectedControllerType,
    detectedControllerName,
    picoBootloaderDevice,
    isFlashingPico,
    flashStatusMessage,
    flashError,
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
    rebootToBootloader,
    checkPicoBootloader,
    flashPico,
  };
}
