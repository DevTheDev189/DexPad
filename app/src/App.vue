<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import type { ControllerControlId, ButtonBinding, StickConfig } from './types/keymap';
import type { PlatformLegendMode, ChassisFinish } from './types/controllers';
import AmbientBackground from './components/AmbientBackground.vue';
import ProfilePillBar from './components/ProfilePillBar.vue';
import PS5ControllerView from './components/PS5ControllerView.vue';
import MappingTable from './components/MappingTable.vue';
import KeyCaptureModal from './components/KeyCaptureModal.vue';
import StickConfigModal from './components/StickConfigModal.vue';
import DpadConfigModal from './components/DpadConfigModal.vue';
import GameLibraryModal from './components/GameLibraryModal.vue';
import HardwareBridgeModal from './components/HardwareBridgeModal.vue';
import AppearanceSettingsModal from './components/AppearanceSettingsModal.vue';
import PicoFlasherModal from './components/PicoFlasherModal.vue';
import CosmicIcon from './components/CosmicIcon.vue';
import type { DiscoveredGame } from './services/gameDiscoveryService';
import { useProfiles } from './composables/useProfiles';
import { useSerial } from './composables/useSerial';
import { useTheme } from './composables/useTheme';

const platformMode = ref<PlatformLegendMode>('playstation');
const chassisFinish = ref<ChassisFinish>('sky_blue');
const showHardwareModal = ref(false);
const isAppearanceModalOpen = ref(false);
const isPicoFlasherModalOpen = ref(false);
const dismissedBootloaderPath = ref<string | null>(null);

const { applyThemeToDOM } = useTheme();

onMounted(() => {
  applyThemeToDOM();
});

// Query parameter initialization for testing and automated showcase renders
if (typeof window !== 'undefined') {
  const urlParams = new URLSearchParams(window.location.search);
  const qFinish = urlParams.get('finish') as ChassisFinish | null;
  if (qFinish && ['sky_blue', 'obsidian', 'galaxy', 'arctic', 'cyberpunk'].includes(qFinish)) {
    chassisFinish.value = qFinish;
  }
}

const {
  profiles,
  activeSlot,
  activeProfile,
  selectedControl,
  isDirty,
  selectSlot,
  addGameProfile,
  removeProfile,
  updateButtonBinding,
  updateStickConfig,
  markClean,
} = useProfiles();

if (typeof window !== 'undefined') {
  const urlParams = new URLSearchParams(window.location.search);
  const qControl = urlParams.get('control') as ControllerControlId | null;
  if (qControl) {
    selectedControl.value = qControl;
  }
}

const {
  ports,
  selectedPort,
  connectionStatus,
  detectedControllerType,
  detectedControllerName,
  picoBootloaderDevice,
  isFlashingPico,
  flashStatusMessage,
  flashError,
  telemetryData,
  refreshPorts,
  connect,
  disconnect,
  sendProfileToDevice,
  switchDeviceSlot,
  flashPico,
} = useSerial();

// Auto-detect controller type and sync 2D visual & platform legends
watch(detectedControllerType, (newType) => {
  if (newType && platformMode.value !== newType) {
    platformMode.value = newType;
    showToast(`Detected: ${detectedControllerName.value} (${newType.toUpperCase()})`);
  }
});

// Auto-prompt when a blank or BOOTSEL Raspberry Pi Pico is connected
watch(picoBootloaderDevice, (newDevice) => {
  if (newDevice && newDevice.mount_path !== dismissedBootloaderPath.value) {
    isPicoFlasherModalOpen.value = true;
  }
});

const handleCloseFlasher = () => {
  if (picoBootloaderDevice.value) {
    dismissedBootloaderPath.value = picoBootloaderDevice.value.mount_path;
  }
  isPicoFlasherModalOpen.value = false;
};

const handleFlashPico = async (target?: string) => {
  if (!picoBootloaderDevice.value) return;
  const ok = await flashPico(picoBootloaderDevice.value.mount_path, target);
  if (ok) {
    showToast('DexPad Firmware Flashed! Board is rebooting...');
  }
};

// Modal States
const isGameLibraryModalOpen = ref(false);
const capturingControlId = ref<ControllerControlId | null>(null);
const configuringStickId = ref<'left_stick' | 'right_stick' | null>(null);
const isDpadConfigModalOpen = ref(false);

const handleOpenDpadConfig = () => {
  isDpadConfigModalOpen.value = true;
};

const handleSaveDpadConfig = (bindings: { up: string; down: string; left: string; right: string }) => {
  updateButtonBinding('dpad_up', { type: bindings.up ? 'key' : 'none', code: bindings.up });
  updateButtonBinding('dpad_down', { type: bindings.down ? 'key' : 'none', code: bindings.down });
  updateButtonBinding('dpad_left', { type: bindings.left ? 'key' : 'none', code: bindings.left });
  updateButtonBinding('dpad_right', { type: bindings.right ? 'key' : 'none', code: bindings.right });
  showToast('Saved D-Pad configuration');
  isDpadConfigModalOpen.value = false;
};

// Toast
const toastMessage = ref<string | null>(null);
let toastTimer: any = null;

const showToast = (msg: string) => {
  toastMessage.value = msg;
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toastMessage.value = null;
  }, 3500);
};

// Handlers
const handleSelectControl = (id: ControllerControlId) => {
  selectedControl.value = id;
};

const handleConfigureControl = (id: ControllerControlId) => {
  selectedControl.value = id;
  if (id === 'left_stick') {
    handleOpenStickConfig('left_stick');
  } else if (id === 'right_stick') {
    handleOpenStickConfig('right_stick');
  } else if (id === 'dpad') {
    handleOpenDpadConfig();
  } else {
    handleOpenRebind(id);
  }
};

const handleSelectProfile = (slot: number) => {
  selectSlot(slot);
  switchDeviceSlot(slot);
  showToast(`Active Profile: "${profiles.value[slot]?.name || 'Profile'}"`);
};

const handleAddGameFromDatabase = (game: DiscoveredGame) => {
  const newSlot = addGameProfile({
    name: game.name,
    gameTitle: game.name,
    coverUrl: game.coverUrl,
    genre: game.genre,
    description: game.description,
    defaultProfile: game.defaultProfile,
  });
  switchDeviceSlot(newSlot);
  showToast(`Added "${game.name}" to Library`);
};

const handleAddCustomGame = (name: string) => {
  const newSlot = addGameProfile({
    name,
    gameTitle: name,
    genre: 'Custom',
    description: 'Blank controller mapping ready for custom configuration.',
  });
  switchDeviceSlot(newSlot);
  showToast(`Created Custom Profile: "${name}"`);
};

const handleRemoveProfile = (slot: number) => {
  const name = profiles.value[slot]?.name || 'Profile';
  removeProfile(slot);
  showToast(`Removed "${name}" from Library`);
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

const handleOpenRebind = (id: ControllerControlId) => {
  capturingControlId.value = id;
};

const handleClearBinding = (id: ControllerControlId) => {
  updateButtonBinding(id, { type: 'none' });
  showToast(`Cleared binding for ${id.toUpperCase()}`);
};

const handleCapturedBinding = (binding: ButtonBinding) => {
  if (capturingControlId.value) {
    updateButtonBinding(capturingControlId.value, binding);
    showToast(`Mapped ${capturingControlId.value.toUpperCase()} to ${binding.code || binding.type}`);
  }
  capturingControlId.value = null;
};

const handleOpenStickConfig = (stickId: 'left_stick' | 'right_stick') => {
  configuringStickId.value = stickId;
};

const handleSaveStickConfig = (config: StickConfig) => {
  if (configuringStickId.value === 'left_stick') {
    updateStickConfig('left', config);
    showToast('Updated Left Stick configuration');
  } else if (configuringStickId.value === 'right_stick') {
    updateStickConfig('right', config);
    showToast('Updated Right Stick configuration');
  }
  configuringStickId.value = null;
};
</script>

<template>
  <div class="app-root">
    <!-- Galaxy Space Background -->
    <AmbientBackground />

    <!-- Application Shell -->
    <div class="app-shell">
      <!-- Top Pill Bar with Left-aligned Active Game Profile Button -->
      <ProfilePillBar
        :active-profile="activeProfile"
        :profiles="profiles"
        :active-slot="activeSlot"
        :is-dirty="isDirty"
        :is-connected="connectionStatus === 'ready'"
        :bootloader-device="picoBootloaderDevice"
        @open-library="isGameLibraryModalOpen = true"
        @save-to-dongle="handleSaveToDevice"
        @open-appearance="isAppearanceModalOpen = true"
        @open-hardware="showHardwareModal = true"
        @open-flasher="isPicoFlasherModalOpen = true"
      />

      <!-- Main Split View Stage -->
      <main class="main-split-stage">
        <!-- Left Side: Interactive 2D Controller Render with Hotspots -->
        <section class="left-pane">
          <PS5ControllerView
            :selected-control="selectedControl"
            :buttons="activeProfile.buttons"
            :left-stick="activeProfile.sticks.left"
            :right-stick="activeProfile.sticks.right"
            :telemetry="telemetryData"
            :platform-mode="platformMode"
            :chassis-finish="chassisFinish"
            @select-control="handleSelectControl"
            @configure-control="handleConfigureControl"
            @update:platform-mode="platformMode = $event"
          />
        </section>

        <!-- Right Side: Mapping Table with Floating Pill Rows -->
        <section class="right-pane">
          <MappingTable
            :platform-mode="platformMode"
            :selected-control="selectedControl"
            :buttons="activeProfile.buttons"
            :left-stick="activeProfile.sticks.left"
            :right-stick="activeProfile.sticks.right"
            @select-control="handleSelectControl"
            @rebind="handleOpenRebind"
            @clear-binding="handleClearBinding"
            @configure-stick="handleOpenStickConfig"
            @configure-dpad="handleOpenDpadConfig"
          />
        </section>
      </main>
    </div>

    <!-- Modals -->
    <!-- Hardware Dongle & Bluetooth Pairing Modal -->
    <HardwareBridgeModal
      :is-open="showHardwareModal"
      :ports="ports"
      :selected-port="selectedPort"
      :is-connected="connectionStatus === 'ready'"
      :active-profile="activeProfile"
      @close="showHardwareModal = false"
      @connect="connect($event)"
      @disconnect="disconnect"
      @refresh-ports="refreshPorts"
      @sync-profile="handleSaveToDevice"
      @select-controller="platformMode = $event as PlatformLegendMode"
    />

    <!-- Key Capture / Rebind Modal -->
    <KeyCaptureModal
      v-if="capturingControlId"
      :control-id="capturingControlId"
      :platform-mode="platformMode"
      @captured="handleCapturedBinding"
      @close="capturingControlId = null"
    />

    <!-- Analog Stick Configuration Modal -->
    <StickConfigModal
      v-if="configuringStickId"
      :stick-id="configuringStickId"
      :config="configuringStickId === 'left_stick' ? activeProfile.sticks.left : activeProfile.sticks.right"
      @save="handleSaveStickConfig"
      @close="configuringStickId = null"
    />

    <!-- Unified Directional D-Pad Configuration Modal -->
    <DpadConfigModal
      v-if="isDpadConfigModalOpen"
      :buttons="activeProfile.buttons"
      @save="handleSaveDpadConfig"
      @close="isDpadConfigModalOpen = false"
    />

    <!-- Game Profiles & Database Library Modal -->
    <GameLibraryModal
      :is-open="isGameLibraryModalOpen"
      :profiles="profiles"
      :active-slot="activeSlot"
      @close="isGameLibraryModalOpen = false"
      @select-profile="handleSelectProfile"
      @add-game="handleAddGameFromDatabase"
      @add-custom-game="handleAddCustomGame"
      @remove-profile="handleRemoveProfile"
    />

    <!-- Appearance & Background Settings Modal -->
    <AppearanceSettingsModal
      :is-open="isAppearanceModalOpen"
      @close="isAppearanceModalOpen = false"
    />

    <!-- Blank / BOOTSEL Pico Flasher Modal -->
    <PicoFlasherModal
      :is-open="isPicoFlasherModalOpen"
      :device="picoBootloaderDevice"
      :is-flashing="isFlashingPico"
      :flash-status="flashStatusMessage"
      :flash-error="flashError"
      @close="handleCloseFlasher"
      @flash="handleFlashPico"
    />

    <!-- Floating Toast Notification -->
    <div v-if="toastMessage" class="toast-pill">
      <CosmicIcon name="sparkles" size="14" class="toast-icon" />
      <span>{{ toastMessage }}</span>
    </div>
  </div>
</template>

<style scoped>
.app-root {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background-color: transparent;
  color: var(--text-primary);
  font-family: var(--font-sans);
}

.app-shell {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

/* Two-column split main workspace matching Gemini mockup */
.main-split-stage {
  position: relative;
  flex: 1;
  display: grid;
  grid-template-columns: 1.12fr 1fr;
  gap: 20px;
  padding: 8px 28px 24px 28px;
  min-height: 0;
  overflow: hidden;
}

.left-pane,
.right-pane {
  height: 100%;
  min-height: 0;
  overflow: hidden;
}

/* Port Flyout Drawer */
.port-flyout {
  position: absolute;
  bottom: 40px;
  left: 28px;
  width: 280px;
  background: rgba(18, 14, 30, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.7), 0 0 20px rgba(168, 85, 247, 0.2);
  backdrop-filter: blur(24px);
  padding: 10px;
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.flyout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 11px;
  font-weight: 700;
  color: #c084fc;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.icon-btn-tiny {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  display: flex;
}
.icon-btn-tiny:hover {
  color: #ffffff;
}

.flyout-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 160px;
  overflow-y: auto;
}

.flyout-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-family: ui-monospace, monospace;
  cursor: pointer;
  color: #cbd5e1;
  background: rgba(255, 255, 255, 0.03);
}

.flyout-item:hover {
  background: rgba(168, 85, 247, 0.2);
  color: #ffffff;
}

.flyout-item.active {
  background: rgba(168, 85, 247, 0.3);
  border: 1px solid #c084fc;
  color: #ffffff;
}

.tag-chip {
  font-size: 9px;
  color: #c084fc;
  text-transform: uppercase;
}

.empty-hint {
  padding: 8px;
  font-size: 11px;
  color: #64748b;
  text-align: center;
}

.disconnect-btn {
  margin-top: 4px;
  padding: 6px;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}
.disconnect-btn:hover {
  background: rgba(239, 68, 68, 0.25);
}

/* Toast */
.toast-pill {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--glass-surface-elevated);
  border: 1px solid var(--accent-custom);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25), 0 0 20px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.35);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 8px 18px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 2000;
  animation: slideUp 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-icon {
  color: var(--accent-sky);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translate(-50%, 15px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}
</style>
