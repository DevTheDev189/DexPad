<script setup lang="ts">
import { ref } from 'vue';
import type { StickConfig } from '../types/keymap';
import CosmicIcon from './CosmicIcon.vue';
import ControllerButtonIcon from './ControllerButtonIcon.vue';

const props = defineProps<{
  stickId: 'left_stick' | 'right_stick';
  config: StickConfig;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'save', config: StickConfig): void;
}>();

const mode = ref<'digital_keys' | 'mouse' | 'none'>(props.config.mode || 'digital_keys');
const deadzone = ref<number>(props.config.deadzone || 150);
const sensitivity = ref<number>(props.config.sensitivity || 1.2);
const curve = ref<'linear' | 'exponential' | 'aggressive'>(props.config.curve || 'exponential');
const invertY = ref<boolean>(props.config.invert_y || false);

// Digital keys
const upKey = ref(props.config.up || 'w');
const downKey = ref(props.config.down || 's');
const leftKey = ref(props.config.left || 'a');
const rightKey = ref(props.config.right || 'd');

const saveChanges = () => {
  emit('save', {
    mode: mode.value,
    deadzone: deadzone.value,
    sensitivity: sensitivity.value,
    curve: curve.value,
    invert_y: invertY.value,
    up: upKey.value,
    down: downKey.value,
    left: leftKey.value,
    right: rightKey.value,
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
            <ControllerButtonIcon :control-id="stickId" size="22" />
          </div>
          <div>
            <h3 class="modal-title">
              Configure {{ stickId === 'left_stick' ? 'Left Analog Stick' : 'Right Analog Stick' }}
            </h3>
            <p class="modal-subtitle">
              Set stick behavior between discrete digital directional keys or high-precision mouse emulation.
            </p>
          </div>
        </div>
        <button class="close-btn" @click="emit('close')">
          <CosmicIcon name="x" size="16" />
        </button>
      </div>

      <!-- Mode Selector -->
      <div class="setting-section">
        <label class="section-label">STICK EMULATION MODE</label>
        <div class="mode-tabs">
          <button
            class="mode-tab"
            :class="{ active: mode === 'digital_keys' }"
            @click="mode = 'digital_keys'"
          >
            <CosmicIcon name="gamepad" size="14" />
            <div class="tab-text">
              <span class="tab-title">Digital Keys</span>
              <span class="tab-desc">WASD or 4-way navigation</span>
            </div>
          </button>

          <button
            class="mode-tab"
            :class="{ active: mode === 'mouse' }"
            @click="mode = 'mouse'"
          >
            <CosmicIcon name="radio" size="14" />
            <div class="tab-text">
              <span class="tab-title">Mouse Emulation</span>
              <span class="tab-desc">Analog cursor / FPS camera look</span>
            </div>
          </button>

          <button
            class="mode-tab"
            :class="{ active: mode === 'none' }"
            @click="mode = 'none'"
          >
            <CosmicIcon name="x" size="14" />
            <div class="tab-text">
              <span class="tab-title">Disabled</span>
              <span class="tab-desc">Pass no inputs</span>
            </div>
          </button>
        </div>
      </div>

      <!-- Settings based on mode -->
      <div v-if="mode === 'digital_keys'" class="setting-section">
        <label class="section-label">DIRECTIONAL BINDINGS</label>
        <div class="keys-grid">
          <div class="key-field">
            <span class="field-tag">UP</span>
            <input v-model="upKey" class="text-input" placeholder="e.g. w or KEY_UP_ARROW" />
          </div>
          <div class="key-field">
            <span class="field-tag">DOWN</span>
            <input v-model="downKey" class="text-input" placeholder="e.g. s or KEY_DOWN_ARROW" />
          </div>
          <div class="key-field">
            <span class="field-tag">LEFT</span>
            <input v-model="leftKey" class="text-input" placeholder="e.g. a or KEY_LEFT_ARROW" />
          </div>
          <div class="key-field">
            <span class="field-tag">RIGHT</span>
            <input v-model="rightKey" class="text-input" placeholder="e.g. d or KEY_RIGHT_ARROW" />
          </div>
        </div>
      </div>

      <div v-if="mode === 'mouse'" class="setting-section">
        <label class="section-label">MOUSE ACCELERATION & SENSITIVITY</label>
        <div class="slider-row">
          <div class="slider-header">
            <span>Sensitivity</span>
            <span class="val-tag">{{ sensitivity.toFixed(1) }}x</span>
          </div>
          <input
            v-model.number="sensitivity"
            type="range"
            min="0.2"
            max="4.0"
            step="0.1"
            class="cosmic-slider"
          />
        </div>

        <div class="curve-selection">
          <span class="field-tag">RESPONSE CURVE:</span>
          <div class="curve-pills">
            <button
              class="curve-pill"
              :class="{ active: curve === 'linear' }"
              @click="curve = 'linear'"
            >
              Linear
            </button>
            <button
              class="curve-pill"
              :class="{ active: curve === 'exponential' }"
              @click="curve = 'exponential'"
            >
              Exponential
            </button>
            <button
              class="curve-pill"
              :class="{ active: curve === 'aggressive' }"
              @click="curve = 'aggressive'"
            >
              Aggressive
            </button>
          </div>
        </div>

        <div class="checkbox-row" @click="invertY = !invertY">
          <input v-model="invertY" type="checkbox" class="cosmic-check" @click.stop />
          <span>Invert Y-Axis (Flight / Camera Invert)</span>
        </div>
      </div>

      <!-- Deadzone Setting -->
      <div v-if="mode !== 'none'" class="setting-section">
        <div class="slider-row">
          <div class="slider-header">
            <span>Stick Deadzone (0 - 500)</span>
            <span class="val-tag">{{ deadzone }}</span>
          </div>
          <input
            v-model.number="deadzone"
            type="range"
            min="10"
            max="400"
            step="5"
            class="cosmic-slider"
          />
        </div>
      </div>

      <!-- Modal Actions -->
      <div class="modal-footer">
        <button class="cancel-btn" @click="emit('close')">Cancel</button>
        <button class="save-btn" @click="saveChanges">
          <CosmicIcon name="check" size="14" />
          <span>Apply Stick Settings</span>
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
  padding: 20px;
}

.modal-card {
  width: 100%;
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
  padding-bottom: 16px;
}

.title-group {
  display: flex;
  gap: 12px;
}

.header-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: rgba(var(--accent-custom-rgb, 125, 211, 252), 0.16);
  border: 1px solid rgba(var(--accent-custom-rgb, 125, 211, 252), 0.4);
  color: var(--accent-custom);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.modal-subtitle {
  margin: 4px 0 0 0;
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  display: flex;
}
.close-btn:hover {
  color: var(--text-primary);
  background: var(--btn-bg);
}

.setting-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.06em;
}

.mode-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
}

.mode-tab {
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border-subtle);
  border-radius: 10px;
  padding: 10px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.mode-tab:hover {
  background: var(--glass-surface-elevated);
  border-color: var(--accent-custom);
  color: var(--text-primary);
}

.mode-tab.active {
  background: var(--accent-custom);
  border-color: var(--accent-custom);
  color: var(--text-on-accent);
  box-shadow: 0 4px 18px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.35);
}

.mode-tab.active .tab-title {
  color: var(--text-on-accent);
}

.tab-text {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.tab-title {
  font-size: 12px;
  font-weight: 700;
}

.tab-desc {
  font-size: 9px;
  color: var(--text-muted);
}

.mode-tab.active .tab-desc {
  color: var(--text-on-accent);
  opacity: 0.85;
}

/* Keys grid */
.keys-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.key-field {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--input-bg);
  border: 1px solid var(--glass-border-subtle);
  border-radius: 8px;
  padding: 6px 10px;
}

.field-tag {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-muted);
  min-width: 44px;
}

.text-input {
  background: transparent;
  border: none;
  outline: none;
  color: var(--accent-custom);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-weight: 700;
  font-size: 12px;
  width: 100%;
}

/* Slider Row */
.slider-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: var(--slider-track-bg);
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid var(--slider-track-border);
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
}

.slider-header {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-primary);
}

.val-tag {
  color: var(--accent-custom);
  font-weight: 700;
  font-family: ui-monospace, monospace;
}

.cosmic-slider {
  width: 100%;
  accent-color: var(--accent-custom);
  cursor: pointer;
  height: 6px;
  border-radius: 3px;
}

.curve-selection {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 4px;
}

.curve-pills {
  display: flex;
  gap: 6px;
}

.curve-pill {
  background: var(--btn-bg);
  border: 1px solid var(--glass-border-subtle);
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 9999px;
  cursor: pointer;
}

.curve-pill:hover {
  color: var(--text-primary);
}

.curve-pill.active {
  background: var(--accent-custom);
  border-color: var(--accent-custom);
  color: var(--text-on-accent);
  box-shadow: 0 2px 10px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.3);
}

.checkbox-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  font-size: 11px;
  color: var(--text-secondary);
  cursor: pointer;
  user-select: none;
}

.cosmic-check {
  accent-color: var(--accent-custom);
  cursor: pointer;
}

/* Footer */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  border-top: 1px solid var(--glass-border-subtle);
  padding-top: 16px;
}

.cancel-btn {
  background: var(--btn-bg);
  border: 1px solid var(--glass-border-subtle);
  color: var(--text-muted);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.cancel-btn:hover {
  color: var(--text-primary);
  background: var(--glass-surface-elevated);
}

.save-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(
    135deg,
    rgba(var(--accent-custom-rgb, 125, 211, 252), 0.95) 0%,
    rgba(var(--accent-custom-rgb, 125, 211, 252), 0.75) 100%
  );
  border: 1px solid rgba(255, 255, 255, 0.4);
  color: var(--text-on-accent);
  padding: 8px 18px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 18px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.35);
}
.save-btn:hover {
  box-shadow: 0 6px 24px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.5);
}
</style>
