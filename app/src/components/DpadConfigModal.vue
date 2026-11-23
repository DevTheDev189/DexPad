<script setup lang="ts">
import { ref } from 'vue';
import type { ButtonBinding } from '../types/keymap';
import CosmicIcon from './CosmicIcon.vue';
import ControllerButtonIcon from './ControllerButtonIcon.vue';

const props = defineProps<{
  buttons: Record<string, ButtonBinding>;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'save', bindings: { up: string; down: string; left: string; right: string }): void;
}>();

// Read existing keys from bindings if available
const getKey = (id: string, fallback: string): string => {
  const b = props.buttons[id];
  if (b && b.type === 'key' && b.code) return b.code;
  return fallback;
};

const upKey = ref(getKey('dpad_up', 'w'));
const downKey = ref(getKey('dpad_down', 's'));
const leftKey = ref(getKey('dpad_left', 'a'));
const rightKey = ref(getKey('dpad_right', 'd'));

const selectedPreset = ref<'wasd' | 'arrows' | 'numpad' | 'custom'>('custom');

// Detect current preset
if (
  upKey.value.toLowerCase() === 'w' &&
  downKey.value.toLowerCase() === 's' &&
  leftKey.value.toLowerCase() === 'a' &&
  rightKey.value.toLowerCase() === 'd'
) {
  selectedPreset.value = 'wasd';
} else if (
  upKey.value.includes('UP') &&
  downKey.value.includes('DOWN') &&
  leftKey.value.includes('LEFT') &&
  rightKey.value.includes('RIGHT')
) {
  selectedPreset.value = 'arrows';
}

const applyPreset = (preset: 'wasd' | 'arrows' | 'numpad') => {
  selectedPreset.value = preset;
  if (preset === 'wasd') {
    upKey.value = 'w';
    downKey.value = 's';
    leftKey.value = 'a';
    rightKey.value = 'd';
  } else if (preset === 'arrows') {
    upKey.value = 'KEY_UP_ARROW';
    downKey.value = 'KEY_DOWN_ARROW';
    leftKey.value = 'KEY_LEFT_ARROW';
    rightKey.value = 'KEY_RIGHT_ARROW';
  } else if (preset === 'numpad') {
    upKey.value = '8';
    downKey.value = '2';
    leftKey.value = '4';
    rightKey.value = '6';
  }
};

const cleanDisplay = (val: string): string => {
  if (!val) return 'None';
  return val.replace(/^KEY_/, '').replace(/_ARROW$/, '').replace(/_/g, ' ');
};

const handleSave = () => {
  emit('save', {
    up: upKey.value.trim(),
    down: downKey.value.trim(),
    left: leftKey.value.trim(),
    right: rightKey.value.trim(),
  });
};
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="modal-card glass-panel-elevated">
      <!-- Modal Header -->
      <div class="modal-header">
        <div class="title-group">
          <div class="header-icon">
            <ControllerButtonIcon control-id="dpad" size="22" />
          </div>
          <div>
            <h3 class="modal-title">Configure D-Pad</h3>
            <p class="modal-subtitle">
              Configure 4-way direction bindings and rapid movement presets.
            </p>
          </div>
        </div>
        <button class="close-btn" @click="emit('close')">
          <CosmicIcon name="x" size="16" />
        </button>
      </div>

      <!-- Quick Presets -->
      <div class="setting-section">
        <label class="section-label">DIRECTIONAL PRESETS</label>
        <div class="preset-grid">
          <button
            class="preset-card"
            :class="{ active: selectedPreset === 'wasd' }"
            @click="applyPreset('wasd')"
          >
            <span class="preset-title">WASD Movement</span>
            <span class="preset-keys">W • A • S • D</span>
          </button>

          <button
            class="preset-card"
            :class="{ active: selectedPreset === 'arrows' }"
            @click="applyPreset('arrows')"
          >
            <span class="preset-title">Arrow Keys</span>
            <span class="preset-keys">↑ • ← • ↓ • →</span>
          </button>

          <button
            class="preset-card"
            :class="{ active: selectedPreset === 'numpad' }"
            @click="applyPreset('numpad')"
          >
            <span class="preset-title">Numpad Directional</span>
            <span class="preset-keys">8 • 4 • 2 • 6</span>
          </button>
        </div>
      </div>

      <!-- Visual Directional Pad Preview & Custom Inputs -->
      <div class="setting-section">
        <label class="section-label">4-WAY DIRECTIONAL BINDINGS</label>
        <div class="dpad-visual-layout">
          <!-- Up -->
          <div class="pos-up">
            <span class="dir-tag">UP</span>
            <input
              v-model="upKey"
              class="text-input"
              placeholder="e.g. w or KEY_UP_ARROW"
              @input="selectedPreset = 'custom'"
            />
          </div>

          <!-- Middle Row: Left - Center Visual - Right -->
          <div class="pos-middle">
            <div class="pos-left">
              <span class="dir-tag">LEFT</span>
              <input
                v-model="leftKey"
                class="text-input"
                placeholder="e.g. a or KEY_LEFT_ARROW"
                @input="selectedPreset = 'custom'"
              />
            </div>

            <div class="dpad-center-disc">
              <div class="disc-facet up" :title="cleanDisplay(upKey)">{{ cleanDisplay(upKey) }}</div>
              <div class="disc-facet down" :title="cleanDisplay(downKey)">{{ cleanDisplay(downKey) }}</div>
              <div class="disc-facet left" :title="cleanDisplay(leftKey)">{{ cleanDisplay(leftKey) }}</div>
              <div class="disc-facet right" :title="cleanDisplay(rightKey)">{{ cleanDisplay(rightKey) }}</div>
              <div class="disc-core"></div>
            </div>

            <div class="pos-right">
              <span class="dir-tag">RIGHT</span>
              <input
                v-model="rightKey"
                class="text-input"
                placeholder="e.g. d or KEY_RIGHT_ARROW"
                @input="selectedPreset = 'custom'"
              />
            </div>
          </div>

          <!-- Down -->
          <div class="pos-down">
            <span class="dir-tag">DOWN</span>
            <input
              v-model="downKey"
              class="text-input"
              placeholder="e.g. s or KEY_DOWN_ARROW"
              @input="selectedPreset = 'custom'"
            />
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="emit('close')">Cancel</button>
        <button class="btn btn-primary" @click="handleSave">
          <CosmicIcon name="check" size="14" />
          <span>Save Unified D-Pad</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(3, 7, 18, 0.35);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

.modal-card {
  width: 90%;
  max-width: 520px;
  background-color: var(--glass-surface-elevated);
  background-image: linear-gradient(
    135deg,
    rgba(var(--accent-custom-rgb, 125, 211, 252), calc(var(--glass-tint-val, 0.14) * 0.45)) 0%,
    transparent 85%
  );
  backdrop-filter: blur(var(--glass-blur-val, 28px)) saturate(190%);
  -webkit-backdrop-filter: blur(var(--glass-blur-val, 28px)) saturate(190%);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 24px;
  box-shadow: var(--shadow-glass-elevated);
  display: flex;
  flex-direction: column;
  gap: 20px;
  color: var(--text-primary);
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  border-bottom: 1px solid var(--glass-border-subtle);
  padding-bottom: 14px;
}

.title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: rgba(var(--accent-custom-rgb, 125, 211, 252), 0.16);
  border: 1px solid rgba(var(--accent-custom-rgb, 125, 211, 252), 0.4);
  color: var(--accent-sky);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.modal-subtitle {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--text-secondary);
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.close-btn:hover {
  color: var(--text-primary);
  background: var(--btn-bg);
}

.setting-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}

.preset-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.preset-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 8px;
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border-subtle);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.preset-card:hover {
  background: var(--glass-surface-elevated);
  border-color: var(--accent-custom);
}

.preset-card.active {
  background: var(--glass-surface-active);
  border-color: var(--accent-custom);
}

.preset-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
}

.preset-card.active .preset-title {
  color: var(--accent-sky);
}

.preset-keys {
  font-size: 10px;
  color: var(--text-muted);
}

/* 4-Way Cross Layout */
.dpad-visual-layout {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border-subtle);
  border-radius: 16px;
}

.pos-up,
.pos-down {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  width: 170px;
}

.pos-middle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
}

.pos-left,
.pos-right {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.dir-tag {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.04em;
}

.text-input {
  width: 100%;
  padding: 7px 10px;
  background: var(--input-bg);
  border: 1px solid var(--glass-border-subtle);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 600;
  text-align: center;
  outline: none;
  transition: all 0.15s ease;
}

.text-input:focus {
  border-color: var(--accent-custom);
  box-shadow: 0 0 0 2px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.25);
}

/* Center Faceted Disc Preview */
.dpad-center-disc {
  position: relative;
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, rgba(var(--accent-custom-rgb, 125, 211, 252), 0.45), rgba(var(--accent-custom-rgb, 125, 211, 252), 0.15));
  border: 2px solid var(--glass-border);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2), inset 0 2px 4px rgba(255, 255, 255, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.disc-facet {
  position: absolute;
  font-size: 9px;
  font-weight: 700;
  color: var(--text-primary);
  text-transform: uppercase;
  max-width: 32px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.disc-facet.up { top: 6px; }
.disc-facet.down { bottom: 6px; }
.disc-facet.left { left: 6px; }
.disc-facet.right { right: 6px; }

.disc-core {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(var(--accent-custom-rgb, 125, 211, 252), 0.5), rgba(var(--accent-custom-rgb, 125, 211, 252), 0.2));
  border: 1px solid var(--glass-border);
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  border-top: 1px solid var(--glass-border-subtle);
  padding-top: 16px;
}

.btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-secondary {
  background: var(--btn-bg);
  border: 1px solid var(--glass-border-subtle);
  color: var(--text-secondary);
}

.btn-secondary:hover {
  color: var(--text-primary);
  background: var(--glass-surface-elevated);
}

.btn-primary {
  background: linear-gradient(
    135deg,
    rgba(var(--accent-custom-rgb, 125, 211, 252), 0.95) 0%,
    rgba(var(--accent-custom-rgb, 125, 211, 252), 0.75) 100%
  );
  border: 1px solid rgba(255, 255, 255, 0.4);
  color: var(--text-on-accent);
  box-shadow: 0 4px 16px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.35);
}

.btn-primary:hover {
  filter: brightness(1.08);
  transform: translateY(-1px);
}
</style>
