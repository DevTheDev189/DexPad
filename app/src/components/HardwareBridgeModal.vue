<script setup lang="ts">
import { ref } from 'vue';
import type { SerialPortEntry, Profile } from '../types/keymap';
import type { PlatformLegendMode } from '../types/controllers';
import CosmicIcon, { type IconName } from './CosmicIcon.vue';

interface BluetoothGamepad {
  mac: string;
  name: string;
  type: PlatformLegendMode;
  icon: IconName;
  connected: boolean;
  saved: boolean;
}

const props = defineProps<{
  isOpen: boolean;
  ports?: SerialPortEntry[];
  selectedPort?: string;
  isConnected: boolean;
  activeProfile?: Profile;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'connect', portName: string): void;
  (e: 'disconnect'): void;
  (e: 'refresh-ports'): void;
  (e: 'sync-profile'): void;
  (e: 'select-controller', type: PlatformLegendMode): void;
}>();

const isScanning = ref(false);

const devices = ref<BluetoothGamepad[]>([
  {
    mac: 'A4:53:04:88:1A:92',
    name: 'DualSense Wireless Controller',
    type: 'playstation',
    icon: 'playstation',
    connected: true,
    saved: true,
  },
  {
    mac: '48:2C:A0:F3:99:C1',
    name: 'Xbox Wireless Controller',
    type: 'xbox',
    icon: 'xbox',
    connected: false,
    saved: true,
  },
  {
    mac: '00:90:E1:55:72:0B',
    name: 'Nintendo Switch Pro Controller',
    type: 'nintendo',
    icon: 'nintendo',
    connected: false,
    saved: false,
  },
]);

const handleScan = () => {
  if (isScanning.value) return;
  isScanning.value = true;
  emit('refresh-ports');
  setTimeout(() => {
    isScanning.value = false;
  }, 1800);
};

const handleConnectGamepad = (device: BluetoothGamepad) => {
  // Disconnect others in single-device mode
  devices.value.forEach((d) => {
    if (d.mac !== device.mac) d.connected = false;
  });
  device.connected = true;
  device.saved = true; // Auto-saved to dongle

  // If dongle isn't connected yet, attempt to connect to available port
  if (!props.isConnected && props.ports && props.ports.length > 0) {
    emit('connect', props.ports[0].name);
  }

  // Auto-switch platform mode in main app UI
  emit('select-controller', device.type);
  emit('sync-profile');
};

const handleDisconnectGamepad = (device: BluetoothGamepad) => {
  device.connected = false;
};

const handleConnectDongle = () => {
  if (props.ports && props.ports.length > 0) {
    emit('connect', props.ports[0].name);
  } else {
    emit('refresh-ports');
  }
};
</script>

<template>
  <div v-if="isOpen" class="modal-backdrop" @click="emit('close')">
    <div class="modal-card" @click.stop>
      <!-- Modal Header -->
      <header class="modal-header">
        <div class="modal-title-group">
          <div class="title-glyph">
            <CosmicIcon name="radio" size="18" />
          </div>
          <div>
            <h2 class="modal-title">Bluetooth</h2>
            <p class="modal-subtitle">Controllers connected here are automatically saved to your dongle.</p>
          </div>
        </div>
        <button class="close-btn glass-btn" @click="emit('close')">
          <CosmicIcon name="close" size="14" />
        </button>
      </header>

      <!-- Modal Body -->
      <div class="modal-body custom-scroll">
        <!-- Dongle Hardware Status Card -->
        <section class="dongle-status-card">
          <div class="dongle-status-left">
            <span class="status-dot" :class="{ online: isConnected }"></span>
            <div>
              <div class="dongle-status-title">
                {{ isConnected ? 'Pico W Dongle Connected' : 'Dongle Disconnected' }}
              </div>
              <div class="dongle-status-sub">
                {{ isConnected ? (selectedPort || 'USB Serial Ready') : 'Plug in your Raspberry Pi Pico W dongle' }}
              </div>
            </div>
          </div>
          <div class="dongle-status-actions">
            <button
              v-if="!isConnected"
              class="glass-btn primary-action-btn"
              @click="handleConnectDongle"
            >
              <CosmicIcon name="link" size="12" />
              <span>Connect Dongle</span>
            </button>
            <button
              v-else
              class="glass-btn subtle-action-btn"
              @click="emit('disconnect')"
            >
              <CosmicIcon name="unlink" size="12" />
              <span>Disconnect</span>
            </button>
          </div>
        </section>

        <!-- Bluetooth Gamepads List -->
        <section class="gamepads-section">
          <div class="section-header">
            <h4 class="section-title">Gamepads</h4>
            <button
              class="glass-btn scan-btn"
              :class="{ scanning: isScanning }"
              :disabled="isScanning"
              @click="handleScan"
            >
              <CosmicIcon name="refresh" size="12" :class="{ spin: isScanning }" />
              <span>{{ isScanning ? 'Scanning...' : 'Scan' }}</span>
            </button>
          </div>

          <div class="device-list">
            <div
              v-for="device in devices"
              :key="device.mac"
              class="device-card"
              :class="{ 'is-connected': device.connected }"
            >
              <div class="device-info">
                <div class="device-icon-badge">
                  <CosmicIcon :name="device.icon" size="18" />
                </div>
                <div class="device-meta">
                  <div class="device-name-row">
                    <span class="device-name">{{ device.name }}</span>
                    <span
                      v-if="device.connected"
                      class="status-badge connected"
                    >
                      Connected • Saved to Dongle
                    </span>
                    <span
                      v-else-if="device.saved"
                      class="status-badge saved"
                    >
                      Saved to Dongle
                    </span>
                  </div>
                  <span class="device-mac">{{ device.mac }}</span>
                </div>
              </div>

              <div class="device-actions">
                <button
                  v-if="device.connected"
                  class="glass-btn disconnect-btn"
                  @click="handleDisconnectGamepad(device)"
                >
                  Disconnect
                </button>
                <button
                  v-else
                  class="glass-btn-primary connect-btn"
                  @click="handleConnectGamepad(device)"
                >
                  Connect
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- Modal Footer -->
      <footer class="modal-footer">
        <button class="glass-btn-primary done-btn" @click="emit('close')">
          Done
        </button>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(3, 7, 18, 0.45);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-card {
  width: 100%;
  max-width: 560px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 24px;
  background-color: var(--glass-surface-elevated);
  background-image: linear-gradient(
    135deg,
    rgba(var(--accent-custom-rgb, 125, 211, 252), calc(var(--glass-tint-val, 0.14) * 0.45)) 0%,
    transparent 80%
  );
  backdrop-filter: blur(var(--glass-blur-val, 28px)) saturate(190%);
  -webkit-backdrop-filter: blur(var(--glass-blur-val, 28px)) saturate(190%);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-glass-elevated);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--glass-border-subtle);
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: 14px;
}

.title-glyph {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-custom);
  color: var(--text-on-accent);
  box-shadow: 0 4px 14px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.4);
}

.modal-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.2;
}

.modal-subtitle {
  font-size: 12px;
  color: var(--text-muted);
  margin: 2px 0 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Dongle Status Card */
.dongle-status-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 16px;
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border-subtle);
}

.dongle-status-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ef4444;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
  flex-shrink: 0;
}

.status-dot.online {
  background: #10b981;
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.8);
  animation: pulse-dot 2s infinite ease-in-out;
}

@keyframes pulse-dot {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.15);
    opacity: 0.8;
  }
}

.dongle-status-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.dongle-status-sub {
  font-size: 11px;
  color: var(--text-muted);
}

.primary-action-btn,
.subtle-action-btn {
  font-size: 11.5px;
  padding: 6px 12px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

/* Gamepads Section */
.gamepads-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-title {
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin: 0;
}

.scan-btn {
  font-size: 11.5px;
  padding: 5px 12px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 10px;
}

.spin {
  animation: spin-icon 1s linear infinite;
}

@keyframes spin-icon {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.device-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.device-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 16px;
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border-subtle);
  transition: all 0.2s ease;
}

.device-card.is-connected {
  border-color: rgba(var(--accent-custom-rgb, 125, 211, 252), 0.4);
  background: var(--glass-surface-elevated);
}

.device-info {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.device-icon-badge {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: #000000;
  border: 1px solid rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  flex-shrink: 0;
}

.device-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.device-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.device-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 8px;
}

.status-badge.connected {
  background: rgba(16, 185, 129, 0.18);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.35);
}

.status-badge.saved {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-muted);
  border: 1px solid var(--glass-border-subtle);
}

.device-mac {
  font-size: 11px;
  font-family: monospace;
  color: var(--text-muted);
}

.device-actions {
  flex-shrink: 0;
}

.connect-btn,
.disconnect-btn {
  font-size: 12px;
  padding: 6px 14px;
  border-radius: 10px;
}

.disconnect-btn {
  color: var(--text-secondary);
}

/* Modal Footer */
.modal-footer {
  padding: 14px 24px;
  border-top: 1px solid var(--glass-border-subtle);
  display: flex;
  justify-content: flex-end;
}

.done-btn {
  padding: 8px 24px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 12px;
}
</style>
