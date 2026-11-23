<script setup lang="ts">
import { computed } from 'vue';
import type { PicoBootloaderDevice } from '../composables/useSerial';
import CosmicIcon from './CosmicIcon.vue';

const props = defineProps<{
  isOpen: boolean;
  device: PicoBootloaderDevice | null;
  isFlashing: boolean;
  flashStatus: string | null;
  flashError: string | null;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'flash', target?: string): void;
}>();

const boardTitle = computed(() => {
  if (!props.device) return 'Raspberry Pi Pico';
  return props.device.model || (props.device.is_pico_2 ? 'Raspberry Pi Pico 2 W' : 'Raspberry Pi Pico W');
});

const chipset = computed(() => {
  if (!props.device) return 'RP2040 / RP2350';
  return props.device.is_pico_2 ? 'RP2350 (Dual ARM Cortex-M33)' : 'RP2040 (Dual ARM Cortex-M0+)';
});

const isSuccess = computed(() => {
  return props.flashStatus && props.flashStatus.toLowerCase().includes('success');
});

const handleFlash = () => {
  if (props.isFlashing || isSuccess.value) return;
  const target = props.device?.is_pico_2 ? 'rp2350' : 'rp2040';
  emit('flash', target);
};
</script>

<template>
  <div v-if="isOpen && device" class="modal-backdrop" @click="emit('close')">
    <div class="modal-card" @click.stop>
      <!-- Modal Header -->
      <header class="modal-header">
        <div class="modal-title-group">
          <div class="title-glyph">
            <CosmicIcon name="sparkles" size="20" />
          </div>
          <div>
            <h3 class="modal-title">Hardware Flasher</h3>
            <p class="modal-subtitle">Blank Raspberry Pi Pico detected in BOOTSEL mode</p>
          </div>
        </div>
        <button class="close-btn" title="Dismiss" @click="emit('close')">
          <CosmicIcon name="close" size="14" />
        </button>
      </header>

      <!-- Body -->
      <div class="modal-body">
        <!-- Hardware Detection Card -->
        <div class="device-banner">
          <div class="device-icon-wrap">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="pico-svg">
              <rect x="4" y="3" width="16" height="18" rx="2" />
              <rect x="8" y="7" width="8" height="6" rx="1" />
              <circle cx="8" cy="17" r="1" />
              <circle cx="16" cy="17" r="1" />
              <path d="M9 3v2" />
              <path d="M15 3v2" />
            </svg>
          </div>

          <div class="device-info">
            <div class="device-row">
              <span class="device-name">{{ boardTitle }}</span>
              <span class="chip-badge">{{ device.is_pico_2 ? 'RP2350' : 'RP2040' }}</span>
            </div>
            <div class="device-details">
              <span>Drive: <strong class="mono">{{ device.mount_path }}</strong> ({{ device.volume_name }})</span>
              <span>•</span>
              <span>{{ chipset }}</span>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="flasher-explanation">
          <p>
            Your Raspberry Pi is currently in mass-storage <strong>BOOTSEL mode</strong>.
            DexPad can automatically install the bridge firmware to transform your Pico into an ultra-low latency controller bridge for macOS.
          </p>
          <ul class="feature-bullets">
            <li>
              <CosmicIcon name="sparkles" size="12" class="bullet-icon" />
              <span>Native USB composite keyboard & mouse output (bypasses macOS X-Input limitations).</span>
            </li>
            <li>
              <CosmicIcon name="sparkles" size="12" class="bullet-icon" />
              <span>Zero terminal commands or driver installs — 1-click automated UF2 flashing.</span>
            </li>
            <li>
              <CosmicIcon name="sparkles" size="12" class="bullet-icon" />
              <span>Auto-reboots directly into DexPad Dongle mode upon completion.</span>
            </li>
          </ul>
        </div>

        <!-- Flashing Status / Progress -->
        <div v-if="isFlashing" class="progress-container">
          <div class="progress-bar-wrap">
            <div class="progress-shimmer"></div>
          </div>
          <span class="status-text">{{ flashStatus || 'Writing DexPad UF2 firmware...' }}</span>
        </div>

        <!-- Success Message -->
        <div v-else-if="isSuccess" class="success-banner">
          <CosmicIcon name="sparkles" size="16" class="success-icon" />
          <span>{{ flashStatus }}</span>
        </div>

        <!-- Error Message -->
        <div v-else-if="flashError" class="error-banner">
          <span>{{ flashError }}</span>
        </div>
      </div>

      <!-- Footer Actions -->
      <footer class="modal-footer">
        <button class="btn-secondary" @click="emit('close')">
          {{ isSuccess ? 'Done' : 'Later' }}
        </button>

        <button
          v-if="!isSuccess"
          class="btn-primary"
          :disabled="isFlashing"
          @click="handleFlash"
        >
          <CosmicIcon v-if="!isFlashing" name="sparkles" size="14" />
          <span>{{ isFlashing ? 'Flashing...' : 'Flash DexPad Firmware' }}</span>
        </button>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  background-color: rgba(5, 7, 13, 0.65);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-card {
  width: 100%;
  max-width: 520px;
  background: var(--glass-surface, rgba(15, 23, 42, 0.85));
  backdrop-filter: blur(32px) saturate(180%);
  border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.12));
  border-radius: 20px;
  box-shadow:
    0 24px 48px -12px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.08) inset;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: popIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-glyph {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(56, 189, 248, 0.14);
  border: 1px solid rgba(56, 189, 248, 0.28);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #38bdf8;
}

.modal-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--text-primary, #f8fafc);
}

.modal-subtitle {
  margin: 2px 0 0 0;
  font-size: 0.8rem;
  color: var(--text-secondary, #94a3b8);
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary, #94a3b8);
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.modal-body {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.device-banner {
  display: flex;
  align-items: center;
  gap: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 14px 16px;
  border-radius: 14px;
}

.device-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(14, 165, 233, 0.12);
  border: 1px solid rgba(14, 165, 233, 0.24);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #38bdf8;
  flex-shrink: 0;
}

.device-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 0;
}

.device-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.device-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-primary, #f8fafc);
}

.chip-badge {
  background: rgba(56, 189, 248, 0.18);
  border: 1px solid rgba(56, 189, 248, 0.35);
  color: #38bdf8;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 1px 7px;
  border-radius: 9999px;
  letter-spacing: 0.03em;
}

.device-details {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  color: var(--text-secondary, #94a3b8);
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  color: #cbd5e1;
}

.flasher-explanation p {
  margin: 0 0 10px 0;
  font-size: 0.85rem;
  line-height: 1.45;
  color: var(--text-secondary, #94a3b8);
}

.feature-bullets {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.feature-bullets li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 0.82rem;
  line-height: 1.4;
  color: var(--text-secondary, #cbd5e1);
}

.bullet-icon {
  color: #38bdf8;
  margin-top: 2px;
  flex-shrink: 0;
}

/* Progress Bar */
.progress-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: rgba(56, 189, 248, 0.08);
  border: 1px solid rgba(56, 189, 248, 0.2);
  border-radius: 12px;
}

.progress-bar-wrap {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 9999px;
  overflow: hidden;
  position: relative;
}

.progress-shimmer {
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, #38bdf8, #818cf8, #38bdf8);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite linear;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.status-text {
  font-size: 0.8rem;
  color: #38bdf8;
  font-weight: 500;
  text-align: center;
}

.success-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.28);
  border-radius: 12px;
  color: #4ade80;
  font-size: 0.84rem;
  font-weight: 500;
}

.success-icon {
  flex-shrink: 0;
}

.error-banner {
  padding: 12px 14px;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.28);
  border-radius: 12px;
  color: #f87171;
  font-size: 0.84rem;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(0, 0, 0, 0.1);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: var(--text-primary, #f8fafc);
  padding: 8px 18px;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.14);
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  padding: 8px 20px;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.35);
  transition: all 0.15s ease;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.94;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(14, 165, 233, 0.45);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes popIn {
  from { opacity: 0; transform: scale(0.96) translateY(6px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
</style>
