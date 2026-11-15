<script setup lang="ts">
import { ref } from 'vue';
import type { ControllerControlId, ButtonBinding, Profile } from './types/keymap';
import MetaballDefs from './components/MetaballDefs.vue';
import CosmicBackground from './components/CosmicBackground.vue';
import NimbusControllerSvg from './components/NimbusControllerSvg.vue';
import BindingTable from './components/BindingTable.vue';
import ProfilePillBar from './components/ProfilePillBar.vue';
import BindingInspector from './components/BindingInspector.vue';
import KeyCaptureModal from './components/KeyCaptureModal.vue';
import ProfileManagerModal from './components/ProfileManagerModal.vue';
import CosmicIcon from './components/CosmicIcon.vue';
import { useProfiles } from './composables/useProfiles';
import { useSerial } from './composables/useSerial';

const {
  profiles,
  activeSlot,
  activeProfile,
  selectedControl,
  hoveredControl,
  isDirty,
  selectSlot,
  renameProfile,
  setProfileInSlot,
  updateButtonBinding,
  updateStickConfig,
  markClean,
  exportCurrentProfileJson,
  importProfileJson,
} = useProfiles();

const {
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
} = useSerial();

// UI View Modes & Modals
const currentView = ref<'controller' | 'table'>('controller');
const isManagerOpen = ref(false);
const capturingControlId = ref<ControllerControlId | null>(null);

const toastMessage = ref<string | null>(null);
let toastTimer: any = null;

const showToast = (msg: string) => {
  toastMessage.value = msg;
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toastMessage.value = null;
  }, 3500);
};

// Spotlight state for reactive background aura
const spotlightState = ref<{ x: number; y: number; active: boolean; color?: string }>({
  x: window.innerWidth * 0.45,
  y: window.innerHeight * 0.5,
  active: false,
});

const handleControlSelect = (id: ControllerControlId) => {
  selectedControl.value = id;
};

const handleControlHover = (id: ControllerControlId | null, pos?: { x: number; y: number }) => {
  hoveredControl.value = id;
  if (id && pos) {
    const rect = document.querySelector('.controller-svg')?.getBoundingClientRect();
    if (rect) {
      const scaleX = rect.width / 980;
      const scaleY = rect.height / 600;
      spotlightState.value = {
        x: rect.left + pos.x * scaleX,
        y: rect.top + pos.y * scaleY,
        active: true,
        color: id === 'a' || id.startsWith('dpad') ? 'cyan' : 'violet',
      };
    }
  } else {
    spotlightState.value.active = false;
  }
};

const handleSlotChange = (slot: number) => {
  selectSlot(slot);
  switchDeviceSlot(slot);
  showToast(`Active Slot: ${slot + 1} (${profiles.value[slot].name})`);
};

const handleSaveToDevice = async () => {
  const success = await sendProfileToDevice(activeProfile.value);
  if (success) {
    markClean();
    showToast(`Saved "${activeProfile.value.name}" to Dongle Flash!`);
  } else {
    showToast('Failed to save to dongle');
  }
};

const openCaptureModal = (id: ControllerControlId) => {
  capturingControlId.value = id;
};

const handleCapturedBinding = (binding: ButtonBinding) => {
  if (capturingControlId.value) {
    updateButtonBinding(capturingControlId.value, binding);
    showToast(`Mapped ${capturingControlId.value.toUpperCase()} to ${binding.code || binding.type}`);
  }
  capturingControlId.value = null;
};

const handleAddProfileFromHub = (newProf: Profile, targetSlot: number) => {
  setProfileInSlot(targetSlot, newProf);
  selectSlot(targetSlot);
  isManagerOpen.value = false;
  showToast(`Applied "${newProf.name}" to Slot ${targetSlot + 1}`);
};

const handleExportJson = () => {
  const data = exportCurrentProfileJson();
  const blob = new Blob([data], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${activeProfile.value.name.toLowerCase().replace(/\s+/g, '_')}_profile.json`;
  a.click();
  URL.revokeObjectURL(url);
  showToast('Profile JSON exported');
};

const handleImportJson = () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json';
  input.onchange = (e: any) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result as string;
        if (importProfileJson(content)) {
          showToast('Profile imported successfully');
        } else {
          showToast('Invalid profile JSON file');
        }
      };
      reader.readAsText(file);
    }
  };
  input.click();
};
</script>

<template>
  <div class="app-root">
    <!-- SVG Metaball Defs -->
    <MetaballDefs />

    <!-- Parallax Cosmic Background + Reactive Orb -->
    <CosmicBackground :spotlight="spotlightState" />

    <!-- Main App Container -->
    <div class="app-shell">
      <!-- ============================================================== -->
      <!-- TOP NAVIGATION BAR -->
      <!-- ============================================================== -->
      <header class="top-nav glass-panel">
        <div class="brand-group">
          <div class="brand-orb"></div>
          <div>
            <h1 class="brand-title">NIMBUS+ <span class="accent-text">COSMIC BRIDGE</span></h1>
            <p class="brand-subtitle">Driverless Hardware USB Gamepad Bridge for macOS</p>
          </div>
        </div>

        <!-- Serial Port Connection Cluster -->
        <div class="serial-cluster">
          <div class="port-picker-group">
            <select v-model="selectedPort" class="port-select">
              <option value="" disabled>Select Serial Port</option>
              <option v-for="p in ports" :key="p.name" :value="p.name">
                {{ p.name }} {{ p.is_esp32 ? '[ESP32-S3]' : '' }}
              </option>
            </select>
            <button class="icon-btn" title="Refresh serial ports" @click="refreshPorts">
              <CosmicIcon name="refresh" size="13" />
            </button>
          </div>

          <button
            class="btn-cosmic conn-btn"
            :class="{ disconnect: isConnected }"
            @click="isConnected ? disconnect() : connect()"
          >
            <CosmicIcon :name="isConnected ? 'unlink' : 'link'" size="13" />
            <span>{{ isConnected ? 'Disconnect' : 'Connect Dongle' }}</span>
          </button>

          <!-- Telemetry Toggle -->
          <button
            class="btn-glass-secondary stream-btn"
            :class="{ active: isStreamingTelemetry }"
            :title="isStreamingTelemetry ? 'Stop live telemetry' : 'Stream live inputs from controller (30Hz)'"
            @click="toggleTelemetryStream()"
          >
            <CosmicIcon name="radio" size="13" />
            <span>Telemetry</span>
          </button>
        </div>

        <!-- Export / Import Actions -->
        <div class="extra-actions">
          <button class="btn-glass-secondary btn-sm" title="Import JSON profile" @click="handleImportJson">
            <CosmicIcon name="upload" size="12" />
            <span>Import</span>
          </button>
          <button class="btn-glass-secondary btn-sm" title="Export current profile as JSON" @click="handleExportJson">
            <CosmicIcon name="download" size="12" />
            <span>Export</span>
          </button>
        </div>
      </header>

      <!-- ============================================================== -->
      <!-- PROFILE TABS & VIEW SWITCHER BAR -->
      <!-- ============================================================== -->
      <ProfilePillBar
        :profiles="profiles"
        :active-slot="activeSlot"
        :is-dirty="isDirty"
        :is-connected="isConnected"
        :current-view="currentView"
        @select-slot="handleSlotChange"
        @rename-slot="renameProfile"
        @save-to-device="handleSaveToDevice"
        @open-manager="isManagerOpen = true"
        @toggle-view="currentView = $event"
      />

      <!-- ============================================================== -->
      <!-- WORKSPACE: Controller View / Table View + Inspector -->
      <!-- ============================================================== -->
      <main class="main-workspace">
        <!-- Center Viewport (Controller or Table) -->
        <div class="main-display-card glass-panel">
          <!-- View 1: Interactive Vector Controller -->
          <NimbusControllerSvg
            v-if="currentView === 'controller'"
            :profile="activeProfile"
            :selected-control="selectedControl"
            :hovered-control="hoveredControl"
            :telemetry="telemetryData"
            :active-slot="activeSlot"
            @select="handleControlSelect"
            @hover="handleControlHover"
          />

          <!-- View 2: Controller-to-Keybind Mapping Table -->
          <BindingTable
            v-else
            :profile="activeProfile"
            :selected-control="selectedControl"
            @select-control="handleControlSelect"
            @record-control="openCaptureModal"
          />
        </div>

        <!-- Right Side: Binding Inspector -->
        <BindingInspector
          :control-id="selectedControl"
          :profile="activeProfile"
          @update-button="updateButtonBinding"
          @update-stick="updateStickConfig"
          @open-capture-modal="openCaptureModal"
        />
      </main>

      <!-- Status Footer Bar -->
      <footer class="app-footer">
        <div class="footer-left">
          <span class="footer-tag">STATUS:</span>
          <span class="footer-val">
            {{ connectionError || lastAckMessage || (isConnected ? 'Connected to ' + selectedPort : 'Awaiting hardware connection') }}
          </span>
        </div>
        <div class="footer-right">
          <span>Firmware v2.0.0</span>
          <span class="dot-sep">•</span>
          <span>Shortcut: Home + D-Pad to cycle slots</span>
        </div>
      </footer>
    </div>

    <!-- Modals -->
    <!-- 1. Live Input Capture Modal -->
    <KeyCaptureModal
      v-if="capturingControlId"
      :control-id="capturingControlId"
      @captured="handleCapturedBinding"
      @close="capturingControlId = null"
    />

    <!-- 2. Game Profile & Presets Hub Modal -->
    <ProfileManagerModal
      v-if="isManagerOpen"
      :profiles="profiles"
      :active-slot="activeSlot"
      @close="isManagerOpen = false"
      @select-profile="handleSlotChange"
      @add-profile="handleAddProfileFromHub"
    />

    <!-- Toast Notification Banner -->
    <div v-if="toastMessage" class="toast-banner">
      <CosmicIcon name="sparkles" size="13" class="toast-sparkle" />
      <span>{{ toastMessage }}</span>
    </div>
  </div>
</template>

<style scoped>
.app-root {
  width: 100vw;
  height: 100vh;
  position: relative;
  overflow: hidden;
  display: flex;
}

.app-shell {
  position: relative;
  z-index: 5;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 12px 18px 8px 18px;
  gap: 10px;
}

/* Top Nav */
.top-nav {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  border-radius: 14px;
}

.brand-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-orb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #ffffff 0%, var(--accent-cyan) 40%, var(--accent-violet) 100%);
  box-shadow: 0 0 18px rgba(56, 189, 248, 0.75);
  animation: pulseGlow 2.5s infinite;
}

.brand-title {
  font-size: 13.5px;
  font-weight: 800;
  letter-spacing: 1.5px;
  color: #fff;
}

.accent-text {
  background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-violet) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-subtitle {
  font-size: 10px;
  color: var(--text-muted);
}

/* Serial Cluster */
.serial-cluster {
  display: flex;
  align-items: center;
  gap: 10px;
}

.port-picker-group {
  display: flex;
  align-items: center;
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 8px;
  padding: 2px 6px;
}

.port-select {
  background: transparent;
  border: none;
  color: #fff;
  font-family: var(--font-sans);
  font-size: 12px;
  outline: none;
  cursor: pointer;
  max-width: 210px;
}

.port-select option {
  background: #0f172a;
  color: #fff;
}

.icon-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
}

.icon-btn:hover {
  color: var(--accent-cyan);
}

.conn-btn {
  padding: 6px 14px;
  font-size: 12px;
}

.conn-btn.disconnect {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.45) 0%, rgba(185, 28, 28, 0.45) 100%);
  border-color: rgba(239, 68, 68, 0.4);
}

.stream-btn {
  padding: 6px 12px;
  font-size: 12px;
}

.stream-btn.active {
  background: rgba(56, 189, 248, 0.2);
  border-color: var(--accent-cyan);
  color: #fff;
  box-shadow: 0 0 14px rgba(56, 189, 248, 0.35);
}

.extra-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-sm {
  padding: 5px 11px;
  font-size: 11.5px;
}

/* Workspace */
.main-workspace {
  flex: 1;
  display: flex;
  gap: 12px;
  min-height: 0;
}

.main-display-card {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  position: relative;
  overflow: hidden;
}

/* Footer */
.app-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2px 8px;
  font-size: 11px;
  color: var(--text-muted);
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.footer-tag {
  font-family: var(--font-mono);
  font-weight: 700;
  color: var(--accent-cyan);
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dot-sep {
  opacity: 0.4;
}

/* Toast */
.toast-banner {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(12, 18, 36, 0.92);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(56, 189, 248, 0.45);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.8), 0 0 24px rgba(56, 189, 248, 0.35);
  padding: 8px 18px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 1000;
  animation: slideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-sparkle {
  color: var(--accent-cyan);
}

@keyframes slideUp {
  from { opacity: 0; transform: translate(-50%, 15px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}
</style>
