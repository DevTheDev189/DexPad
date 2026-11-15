<script setup lang="ts">
import { ref, computed } from 'vue';
import type {
  ControllerControlId,
  Profile,
  ButtonBinding,
  StickConfig,
  ButtonBindingType,
  StickMode,
  StickCurve,
} from '../types/keymap';
import { MAC_KEY_OPTIONS } from '../types/keymap';
import CosmicIcon from './CosmicIcon.vue';

const props = defineProps<{
  controlId: ControllerControlId | null;
  profile: Profile;
}>();

const emit = defineEmits<{
  (e: 'update-button', id: string, binding: ButtonBinding): void;
  (e: 'update-stick', stick: 'left' | 'right', config: StickConfig): void;
  (e: 'open-capture-modal', id: ControllerControlId): void;
}>();

const isStick = computed(() => {
  return props.controlId === 'left_stick' || props.controlId === 'right_stick';
});

const currentStickConfig = computed<StickConfig | null>(() => {
  if (props.controlId === 'left_stick') return props.profile.sticks.left;
  if (props.controlId === 'right_stick') return props.profile.sticks.right;
  return null;
});

const currentButtonBinding = computed<ButtonBinding>(() => {
  if (!props.controlId || isStick.value) {
    return { type: 'none' };
  }
  return props.profile.buttons[props.controlId] || { type: 'none' };
});

const searchFilter = ref('');
const filteredKeyOptions = computed(() => {
  if (!searchFilter.value) return MAC_KEY_OPTIONS;
  const q = searchFilter.value.toLowerCase();
  return MAC_KEY_OPTIONS.filter(
    (k) => k.label.toLowerCase().includes(q) || k.code.toLowerCase().includes(q)
  );
});

const setBindingType = (type: ButtonBindingType) => {
  if (!props.controlId || isStick.value) return;
  const current = { ...currentButtonBinding.value, type };
  if (type === 'key' && !current.code) current.code = 'KEY_SPACE';
  if (type === 'mouse_button' && !current.code) current.code = 'MOUSE_LEFT';
  if (type === 'mouse_scroll') {
    current.delta = current.delta || 1;
    current.repeat_ms = current.repeat_ms || 120;
  }
  emit('update-button', props.controlId, current);
};

const setKeyCode = (code: string) => {
  if (!props.controlId || isStick.value) return;
  emit('update-button', props.controlId, {
    ...currentButtonBinding.value,
    type: 'key',
    code,
  });
};

const setMouseButton = (code: string) => {
  if (!props.controlId || isStick.value) return;
  emit('update-button', props.controlId, {
    ...currentButtonBinding.value,
    type: 'mouse_button',
    code,
    threshold: currentButtonBinding.value.threshold ?? 40,
  });
};

const setScrollDelta = (delta: number) => {
  if (!props.controlId || isStick.value) return;
  emit('update-button', props.controlId, {
    ...currentButtonBinding.value,
    type: 'mouse_scroll',
    delta,
    repeat_ms: currentButtonBinding.value.repeat_ms || 120,
  });
};

const setScrollRepeat = (repeat_ms: number) => {
  if (!props.controlId || isStick.value) return;
  emit('update-button', props.controlId, {
    ...currentButtonBinding.value,
    repeat_ms,
  });
};

const setTriggerThreshold = (threshold: number) => {
  if (!props.controlId || isStick.value) return;
  emit('update-button', props.controlId, {
    ...currentButtonBinding.value,
    threshold,
  });
};

// Stick handlers
const updateStickMode = (mode: StickMode) => {
  if (!props.controlId || !isStick.value || !currentStickConfig.value) return;
  const stickKey = props.controlId === 'left_stick' ? 'left' : 'right';
  emit('update-stick', stickKey, { ...currentStickConfig.value, mode });
};

const updateStickDeadzone = (deadzone: number) => {
  if (!props.controlId || !isStick.value || !currentStickConfig.value) return;
  const stickKey = props.controlId === 'left_stick' ? 'left' : 'right';
  emit('update-stick', stickKey, { ...currentStickConfig.value, deadzone });
};

const updateStickSensitivity = (sensitivity: number) => {
  if (!props.controlId || !isStick.value || !currentStickConfig.value) return;
  const stickKey = props.controlId === 'left_stick' ? 'left' : 'right';
  emit('update-stick', stickKey, { ...currentStickConfig.value, sensitivity });
};

const updateStickCurve = (curve: StickCurve) => {
  if (!props.controlId || !isStick.value || !currentStickConfig.value) return;
  const stickKey = props.controlId === 'left_stick' ? 'left' : 'right';
  emit('update-stick', stickKey, { ...currentStickConfig.value, curve });
};

const updateStickInvertY = (invert_y: boolean) => {
  if (!props.controlId || !isStick.value || !currentStickConfig.value) return;
  const stickKey = props.controlId === 'left_stick' ? 'left' : 'right';
  emit('update-stick', stickKey, { ...currentStickConfig.value, invert_y });
};

const updateStickDirectionKey = (dir: 'up' | 'down' | 'left' | 'right', val: string) => {
  if (!props.controlId || !isStick.value || !currentStickConfig.value) return;
  const stickKey = props.controlId === 'left_stick' ? 'left' : 'right';
  emit('update-stick', stickKey, { ...currentStickConfig.value, [dir]: val });
};
</script>

<template>
  <aside class="inspector-panel glass-panel">
    <!-- Header -->
    <div class="inspector-header">
      <div class="target-title-row">
        <span class="target-tag">CONTROL INSPECTOR</span>
        <h2 class="target-name">
          {{ controlId ? controlId.toUpperCase().replace('_', ' ') : 'Select a Control' }}
        </h2>
      </div>

      <button
        v-if="controlId && !isStick"
        class="record-btn btn-cosmic"
        title="Record live keyboard key or mouse click"
        @click="emit('open-capture-modal', controlId)"
      >
        <CosmicIcon name="record" size="12" class="rec-dot-icon" />
        <span>Record</span>
      </button>
    </div>

    <!-- Empty State -->
    <div v-if="!controlId" class="empty-state">
      <div class="empty-icon-wrap">
        <CosmicIcon name="gamepad" size="32" class="empty-icon" />
      </div>
      <p class="empty-title">No Input Selected</p>
      <p class="empty-text">Click any button, trigger, or stick on the controller or the table to configure its mapping.</p>
    </div>

    <!-- ================================================================== -->
    <!-- STICK INSPECTOR -->
    <!-- ================================================================== -->
    <div v-else-if="isStick && currentStickConfig" class="inspector-body">
      <!-- Stick Mode -->
      <div class="field-group">
        <label class="field-label">Stick Mode</label>
        <div class="pill-selector">
          <button
            class="pill-opt"
            :class="{ active: currentStickConfig.mode === 'digital_keys' }"
            @click="updateStickMode('digital_keys')"
          >
            Digital WASD
          </button>
          <button
            class="pill-opt"
            :class="{ active: currentStickConfig.mode === 'mouse' }"
            @click="updateStickMode('mouse')"
          >
            Smooth Mouse
          </button>
          <button
            class="pill-opt"
            :class="{ active: currentStickConfig.mode === 'none' }"
            @click="updateStickMode('none')"
          >
            Disabled
          </button>
        </div>
      </div>

      <!-- Deadzone Slider -->
      <div class="field-group">
        <div class="slider-header">
          <label class="field-label">Deadzone Radius</label>
          <span class="slider-value">{{ currentStickConfig.deadzone }}</span>
        </div>
        <input
          type="range"
          min="10"
          max="300"
          :value="currentStickConfig.deadzone"
          class="cosmic-range"
          @input="updateStickDeadzone(Number(($event.target as HTMLInputElement).value))"
        />
      </div>

      <!-- Mouse Mode Settings -->
      <template v-if="currentStickConfig.mode === 'mouse'">
        <div class="field-group">
          <div class="slider-header">
            <label class="field-label">Camera Sensitivity</label>
            <span class="slider-value">{{ (currentStickConfig.sensitivity || 1.35).toFixed(2) }}x</span>
          </div>
          <input
            type="range"
            min="0.4"
            max="3.5"
            step="0.05"
            :value="currentStickConfig.sensitivity || 1.35"
            class="cosmic-range"
            @input="updateStickSensitivity(Number(($event.target as HTMLInputElement).value))"
          />
        </div>

        <div class="field-group">
          <label class="field-label">Acceleration Curve</label>
          <div class="pill-selector">
            <button
              class="pill-opt"
              :class="{ active: currentStickConfig.curve === 'linear' }"
              @click="updateStickCurve('linear')"
            >
              Linear
            </button>
            <button
              class="pill-opt"
              :class="{ active: (currentStickConfig.curve || 'exponential') === 'exponential' }"
              @click="updateStickCurve('exponential')"
            >
              Exponential
            </button>
            <button
              class="pill-opt"
              :class="{ active: currentStickConfig.curve === 'aggressive' }"
              @click="updateStickCurve('aggressive')"
            >
              Aggressive
            </button>
          </div>
        </div>

        <div class="field-group toggle-row">
          <label class="field-label">Invert Y-Axis</label>
          <input
            type="checkbox"
            :checked="currentStickConfig.invert_y || false"
            class="cosmic-toggle"
            @change="updateStickInvertY(($event.target as HTMLInputElement).checked)"
          />
        </div>
      </template>

      <!-- Digital WASD Settings -->
      <template v-if="currentStickConfig.mode === 'digital_keys'">
        <div class="field-group">
          <label class="field-label">Directional Keycodes</label>
          <div class="dir-grid">
            <div class="dir-item">
              <span class="dir-label">UP</span>
              <input
                class="dir-input"
                :value="currentStickConfig.up || 'w'"
                @input="updateStickDirectionKey('up', ($event.target as HTMLInputElement).value)"
              />
            </div>
            <div class="dir-item">
              <span class="dir-label">LEFT</span>
              <input
                class="dir-input"
                :value="currentStickConfig.left || 'a'"
                @input="updateStickDirectionKey('left', ($event.target as HTMLInputElement).value)"
              />
            </div>
            <div class="dir-item">
              <span class="dir-label">DOWN</span>
              <input
                class="dir-input"
                :value="currentStickConfig.down || 's'"
                @input="updateStickDirectionKey('down', ($event.target as HTMLInputElement).value)"
              />
            </div>
            <div class="dir-item">
              <span class="dir-label">RIGHT</span>
              <input
                class="dir-input"
                :value="currentStickConfig.right || 'd'"
                @input="updateStickDirectionKey('right', ($event.target as HTMLInputElement).value)"
              />
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- ================================================================== -->
    <!-- BUTTON INSPECTOR -->
    <!-- ================================================================== -->
    <div v-else class="inspector-body">
      <!-- Binding Type -->
      <div class="field-group">
        <label class="field-label">Output Action</label>
        <div class="pill-selector">
          <button
            class="pill-opt"
            :class="{ active: currentButtonBinding.type === 'key' }"
            @click="setBindingType('key')"
          >
            Keyboard
          </button>
          <button
            class="pill-opt"
            :class="{ active: currentButtonBinding.type === 'mouse_button' }"
            @click="setBindingType('mouse_button')"
          >
            Mouse Click
          </button>
          <button
            class="pill-opt"
            :class="{ active: currentButtonBinding.type === 'mouse_scroll' }"
            @click="setBindingType('mouse_scroll')"
          >
            Scroll
          </button>
          <button
            class="pill-opt"
            :class="{ active: currentButtonBinding.type === 'none' }"
            @click="setBindingType('none')"
          >
            None
          </button>
        </div>
      </div>

      <!-- KEYBOARD KEY OPTION -->
      <template v-if="currentButtonBinding.type === 'key'">
        <div class="field-group">
          <label class="field-label">Select Key or Modifier</label>
          <div class="search-input-wrap">
            <CosmicIcon name="search" size="13" class="search-icon" />
            <input
              v-model="searchFilter"
              type="text"
              placeholder="Search key (e.g. Space, Command, F5)..."
              class="search-input"
            />
          </div>

          <div class="key-list-box">
            <button
              v-for="k in filteredKeyOptions"
              :key="k.code"
              class="key-option-row"
              :class="{ selected: currentButtonBinding.code === k.code }"
              @click="setKeyCode(k.code)"
            >
              <span class="key-badge">{{ k.label }}</span>
              <span class="key-code-sub">{{ k.code }}</span>
            </button>
          </div>
        </div>
      </template>

      <!-- MOUSE BUTTON OPTION -->
      <template v-if="currentButtonBinding.type === 'mouse_button'">
        <div class="field-group">
          <label class="field-label">Mouse Button</label>
          <div class="pill-selector">
            <button
              class="pill-opt"
              :class="{ active: currentButtonBinding.code === 'MOUSE_LEFT' }"
              @click="setMouseButton('MOUSE_LEFT')"
            >
              Left Click
            </button>
            <button
              class="pill-opt"
              :class="{ active: currentButtonBinding.code === 'MOUSE_RIGHT' }"
              @click="setMouseButton('MOUSE_RIGHT')"
            >
              Right Click
            </button>
            <button
              class="pill-opt"
              :class="{ active: currentButtonBinding.code === 'MOUSE_MIDDLE' }"
              @click="setMouseButton('MOUSE_MIDDLE')"
            >
              Middle
            </button>
          </div>
        </div>

        <div v-if="controlId === 'l2' || controlId === 'r2'" class="field-group">
          <div class="slider-header">
            <label class="field-label">Analog Activation Threshold</label>
            <span class="slider-value">{{ currentButtonBinding.threshold ?? 40 }}</span>
          </div>
          <input
            type="range"
            min="10"
            max="300"
            :value="currentButtonBinding.threshold ?? 40"
            class="cosmic-range"
            @input="setTriggerThreshold(Number(($event.target as HTMLInputElement).value))"
          />
        </div>
      </template>

      <!-- MOUSE SCROLL OPTION -->
      <template v-if="currentButtonBinding.type === 'mouse_scroll'">
        <div class="field-group">
          <label class="field-label">Scroll Direction</label>
          <div class="pill-selector">
            <button
              class="pill-opt"
              :class="{ active: (currentButtonBinding.delta || 1) > 0 }"
              @click="setScrollDelta(1)"
            >
              Scroll Up (+1)
            </button>
            <button
              class="pill-opt"
              :class="{ active: (currentButtonBinding.delta || 1) < 0 }"
              @click="setScrollDelta(-1)"
            >
              Scroll Down (-1)
            </button>
          </div>
        </div>

        <div class="field-group">
          <div class="slider-header">
            <label class="field-label">Repeat Interval</label>
            <span class="slider-value">{{ currentButtonBinding.repeat_ms || 120 }} ms</span>
          </div>
          <input
            type="range"
            min="40"
            max="300"
            step="10"
            :value="currentButtonBinding.repeat_ms || 120"
            class="cosmic-range"
            @input="setScrollRepeat(Number(($event.target as HTMLInputElement).value))"
          />
        </div>
      </template>
    </div>
  </aside>
</template>

<style scoped>
.inspector-panel {
  width: 320px;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
  position: relative;
  z-index: 10;
  border-radius: 16px;
  overflow: hidden;
}

.inspector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.target-title-row {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.target-tag {
  font-family: var(--font-mono);
  font-size: 9px;
  font-weight: 700;
  color: var(--accent-cyan);
  letter-spacing: 1.5px;
}

.target-name {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
}

.record-btn {
  padding: 5px 12px;
  font-size: 11px;
}

.rec-dot-icon {
  color: #f43f5e;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 10px;
  color: var(--text-muted);
  padding: 20px;
}

.empty-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.empty-title {
  font-size: 13.5px;
  font-weight: 600;
  color: #fff;
}

.empty-text {
  font-size: 11.5px;
  line-height: 1.4;
  color: var(--text-muted);
}

.inspector-body {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding-right: 2px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
}

.pill-selector {
  display: flex;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  padding: 2px;
  gap: 2px;
}

.pill-opt {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-family: var(--font-sans);
  font-size: 10.5px;
  font-weight: 600;
  padding: 5px 6px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  text-align: center;
}

.pill-opt:hover:not(.active) {
  color: var(--text-secondary);
}

.pill-opt.active {
  background: rgba(56, 189, 248, 0.22);
  color: #fff;
  border: 1px solid rgba(56, 189, 248, 0.45);
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
}

.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.slider-value {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  color: var(--accent-cyan);
}

.cosmic-range {
  -webkit-appearance: none;
  width: 100%;
  height: 5px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 9999px;
  outline: none;
}

.cosmic-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--accent-cyan);
  cursor: pointer;
  box-shadow: 0 0 10px var(--accent-cyan);
  transition: transform 0.1s ease;
}

.cosmic-range::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.toggle-row {
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

.cosmic-toggle {
  accent-color: var(--accent-cyan);
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.search-input-wrap {
  display: flex;
  align-items: center;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 8px;
  padding: 6px 10px;
  gap: 8px;
}

.search-icon {
  color: var(--text-muted);
}

.search-input {
  background: transparent;
  border: none;
  outline: none;
  color: #fff;
  font-size: 11.5px;
  font-family: var(--font-sans);
  width: 100%;
}

.key-list-box {
  max-height: 220px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 4px;
}

.key-option-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid transparent;
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
}

.key-option-row:hover {
  background: rgba(56, 189, 248, 0.12);
  color: #fff;
}

.key-option-row.selected {
  background: rgba(56, 189, 248, 0.2);
  border-color: rgba(56, 189, 248, 0.5);
  color: #fff;
}

.key-badge {
  font-size: 11px;
  font-weight: 600;
}

.key-code-sub {
  font-family: var(--font-mono);
  font-size: 9px;
  color: var(--text-muted);
}

/* Direction grid for WASD */
.dir-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.dir-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  padding: 5px 8px;
}

.dir-label {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  color: var(--accent-cyan);
}

.dir-input {
  width: 48px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 4px;
  color: #fff;
  font-family: var(--font-mono);
  font-size: 11px;
  text-align: center;
  padding: 2px;
  outline: none;
}

.dir-input:focus {
  border-color: var(--accent-cyan);
}
</style>
