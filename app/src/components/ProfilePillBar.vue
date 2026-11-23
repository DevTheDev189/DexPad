<script setup lang="ts">
import { ref, watch } from 'vue';
import type { Profile } from '../types/keymap';
import type { PicoBootloaderDevice } from '../composables/useSerial';
import CosmicIcon from './CosmicIcon.vue';
import DexPadLogo from './DexPadLogo.vue';

const props = defineProps<{
  activeProfile?: Profile;
  profiles: Profile[];
  activeSlot: number;
  isDirty?: boolean;
  isConnected?: boolean;
  bootloaderDevice?: PicoBootloaderDevice | null;
}>();

const emit = defineEmits<{
  (e: 'open-library'): void;
  (e: 'save-to-dongle'): void;
  (e: 'open-appearance'): void;
  (e: 'open-hardware'): void;
  (e: 'open-flasher'): void;
}>();

const imgFailed = ref(false);

watch(
  () => props.activeProfile?.coverUrl,
  () => {
    imgFailed.value = false;
  }
);
</script>

<template>
  <div class="top-nav-bar">
    <!-- Left-aligned Active Game Profile Button -->
    <div class="top-profile-left">
      <!-- DexPad Brand Lockup -->
      <div class="brand-logo-pill" title="DexPad Universal Controller Studio">
        <DexPadLogo variant="full" :size="30" />
      </div>

      <!-- Game Profile Selector Button -->
      <button
        class="game-profile-btn"
        title="Open Game Library & Profiles"
        @click="emit('open-library')"
      >
        <div class="game-thumb-avatar">
          <img
            v-if="activeProfile?.coverUrl && !imgFailed"
            :src="activeProfile.coverUrl"
            :alt="activeProfile?.name"
            class="thumb-img"
            @error="imgFailed = true"
          />
          <div v-else class="thumb-icon-placeholder">
            <CosmicIcon name="gamepad" size="15" />
          </div>
        </div>

        <div class="game-meta">
          <span class="game-title">{{ activeProfile?.name || 'Default Game' }}</span>
          <span class="game-subtitle">Profiles & Library</span>
        </div>

        <div class="chevron-badge">
          <CosmicIcon name="chevron-down" size="11" />
        </div>
      </button>
    </div>

    <!-- Right-aligned Actions: Bluetooth, Style, Save to Dongle with Status Dot -->
    <div class="top-actions-right">
      <!-- Flash Pico Pill (shown when blank / BOOTSEL Pico detected) -->
      <button
        v-if="bootloaderDevice"
        class="flash-pico-pill-btn"
        title="Blank Raspberry Pi Pico detected in BOOTSEL mode - Click to Flash"
        @click="emit('open-flasher')"
      >
        <span class="flash-pulse-dot"></span>
        <CosmicIcon name="sparkles" size="13" />
        <span>Flash Pico</span>
      </button>

      <!-- Bluetooth Manager Pill -->
      <button
        class="nav-pill-btn"
        title="Bluetooth Connections"
        @click="emit('open-hardware')"
      >
        <CosmicIcon name="radio" size="13" />
        <span>Bluetooth</span>
      </button>

      <!-- Style Pill -->
      <button
        class="nav-pill-btn"
        title="Style & Theme Settings"
        @click="emit('open-appearance')"
      >
        <CosmicIcon name="brush" size="13" />
        <span>Style</span>
      </button>

      <!-- Save to Dongle Pill with Red / Green Indicator -->
      <button
        class="sync-pill-btn"
        :class="{ 'is-dirty': isDirty }"
        title="Save active profile to Dongle"
        @click="emit('save-to-dongle')"
      >
        <span class="conn-dot" :class="{ online: isConnected }"></span>
        <span>Save to Dongle</span>
        <span v-if="isDirty" class="pulse-dot"></span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.top-nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 28px 12px 28px;
  position: relative;
  z-index: 40;
}

/* Left-aligned Game Profile Button */
.top-profile-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-logo-pill {
  display: flex;
  align-items: center;
  padding: 4px 12px 4px 6px;
  border-radius: 9999px;
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-pill);
  backdrop-filter: blur(var(--glass-blur-val, 28px)) saturate(180%);
  -webkit-backdrop-filter: blur(var(--glass-blur-val, 28px)) saturate(180%);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.brand-logo-pill:hover {
  border-color: rgba(56, 189, 248, 0.45);
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25), 0 0 16px rgba(56, 189, 248, 0.25);
  transform: translateY(-1px);
}

.game-profile-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 5px 14px 5px 6px;
  border-radius: 9999px;
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-pill);
  backdrop-filter: blur(var(--glass-blur-val, 28px)) saturate(180%);
  -webkit-backdrop-filter: blur(var(--glass-blur-val, 28px)) saturate(180%);
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.game-profile-btn:hover {
  background: var(--glass-surface-elevated);
  border-color: var(--accent-custom);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25), 0 0 16px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.3);
}

.game-thumb-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  overflow: hidden;
  background: #000000;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-icon-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-custom);
}

.game-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1px;
}

.game-title {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.game-subtitle {
  font-size: 10.5px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

.chevron-badge {
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 2px;
  transition: transform 0.2s ease, color 0.2s ease;
}

.game-profile-btn:hover .chevron-badge {
  color: var(--accent-custom);
  transform: translateY(1px);
}

/* Top Actions Right */
.top-actions-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.flash-pico-pill-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 6px 14px;
  border-radius: 9999px;
  background: rgba(14, 165, 233, 0.16);
  border: 1px solid rgba(56, 189, 248, 0.45);
  color: #38bdf8;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  backdrop-filter: blur(var(--glass-blur-val, 28px));
  -webkit-backdrop-filter: blur(var(--glass-blur-val, 28px));
  box-shadow: 0 0 16px rgba(14, 165, 233, 0.28);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  animation: pulseGlow 2.5s infinite ease-in-out;
}

.flash-pico-pill-btn:hover {
  background: rgba(14, 165, 233, 0.28);
  border-color: rgba(56, 189, 248, 0.7);
  transform: translateY(-1px);
  box-shadow: 0 0 20px rgba(14, 165, 233, 0.4);
}

.flash-pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: #38bdf8;
  box-shadow: 0 0 8px #38bdf8;
}

@keyframes pulseGlow {
  0%, 100% {
    box-shadow: 0 0 12px rgba(14, 165, 233, 0.2);
  }
  50% {
    box-shadow: 0 0 20px rgba(14, 165, 233, 0.45);
  }
}

.nav-pill-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border);
  color: var(--text-primary);
  padding: 7px 15px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  backdrop-filter: blur(var(--glass-blur-val, 28px));
  -webkit-backdrop-filter: blur(var(--glass-blur-val, 28px));
  box-shadow: var(--shadow-pill);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.nav-pill-btn:hover {
  background: var(--glass-surface-elevated);
  border-color: var(--accent-custom);
  color: var(--accent-custom);
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.25);
}

.conn-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: #ef4444;
  box-shadow: 0 0 8px #ef4444;
  flex-shrink: 0;
  transition: all 0.25s ease;
}

.conn-dot.online {
  background-color: #22c55e;
  box-shadow: 0 0 10px #22c55e;
}

.sync-pill-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  position: relative;
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border);
  color: var(--text-primary);
  padding: 7px 16px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  backdrop-filter: blur(var(--glass-blur-val, 28px));
  -webkit-backdrop-filter: blur(var(--glass-blur-val, 28px));
  box-shadow: var(--shadow-pill);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.sync-pill-btn:hover {
  background: var(--glass-surface-elevated);
  border-color: var(--accent-custom);
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.25);
}

.sync-pill-btn.is-dirty {
  border-color: #f59e0b;
  color: #fbbf24;
}

.pulse-dot {
  width: 6px;
  height: 6px;
  background: #f59e0b;
  border-radius: 50%;
  box-shadow: 0 0 6px #f59e0b;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.3);
    opacity: 0.7;
  }
}
</style>
