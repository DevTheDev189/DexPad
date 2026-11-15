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

// Search filter for keycode dropdown
const searchFilter = ref('');
const filteredKeyOptions = computed(() => {
  if (!searchFilter.value) return MAC_KEY_OPTIONS;
  const q = searchFilter.value.toLowerCase();
  return MAC_KEY_OPTIONS.filter(
    (k) => k.label.toLowerCase().includes(q) || k.code.toLowerCase().includes(q)
  );
});

// Modifiers helper
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

// Stick update handlers
const updateStickMode = (mode: StickMode) => {
  if (!props.controlId || !isStick.value || !currentStickConfig.value) return;
  const stickKey = props.controlId === 'left_stick' ? 'left' : 'right';
  emit('update-stick', stickKey, {
    ...currentStickConfig.value,
    mode,
  });
};

const updateStickDeadzone = (deadzone: number) => {
  if (!props.controlId || !isStick.value || !currentStickConfig.value) return;
  const stickKey = props.controlId === 'left_stick' ? 'left' : 'right';
  emit('update-stick', stickKey, {
    ...currentStickConfig.value,
    deadzone,
  });
};

const updateStickSensitivity = (sensitivity: number) => {
  if (!props.controlId || !isStick.value || !currentStickConfig.value) return;
  const stickKey = props.controlId === 'left_stick' ? 'left' : 'right';
  emit('update-stick', stickKey, {
    ...currentStickConfig.value,
    sensitivity,
  });
};

const updateStickCurve = (curve: StickCurve) => {
  if (!props.controlId || !isStick.value || !currentStickConfig.value) return;
  const stickKey = props.controlId === 'left_stick' ? 'left' : 'right';
  emit('update-stick', stickKey, {
    ...currentStickConfig.value,
    curve,
  });
};

const updateStickInvertY = (invert_y: boolean) => {
  if (!props.controlId || !isStick.value || !currentStickConfig.value) return;
  const stickKey = props.controlId === 'left_stick' ? 'left' : 'right';
  emit('update-stick', stickKey, {
    ...currentStickConfig.value,
    invert_y,
  });
};

const updateStickDirectionKey = (dir: 'up' | 'down' | 'left' | 'right', val: string) => {
  if (!props.controlId || !isStick.value || !currentStickConfig.value) return;
  const stickKey = props.controlId === 'left_stick' ? 'left' : 'right';
  emit('update-stick', stickKey, {
    ...currentStickConfig.value,
    [dir]: val,
  });
};
</script>

<template>
  <aside class="inspector-panel glass-panel">
    <!-- Header -->
    <div class="inspector-header">
      <div class="target-title-row">
        <span class="target-tag">CONTROL</span>
        <h2 class="target-name">
          {{ controlId ? controlId.toUpperCase().replace('_', ' ') : 'Select a Control' }}
        </h2>
      </div>

      <button
        v-if="controlId && !isStick"
        class="record-btn btn-cosmic"
        title="Record keystroke or mouse click"
        @click="emit('open-capture-modal', controlId)"
      >
        <span class="rec-dot"></span>
        <span>Record</span>
      </button>
    </div>

    <!-- Empty State -->
    <div v-if="!controlId" class="empty-state">
      <div class="empty-icon">🎮</div>
      <p class="empty-text">Click any button, trigger, or stick on the controller to edit its mapping.</p>
    </div>

    <!-- ================================================================== -->
    <!-- STICK INSPECTOR -->
    <!-- ================================================================== -->
    <div v-else-if="isStick && currentStickConfig" class="inspector-body">
      <!-- Stick Mode -->
      <div class="field-group">
        <label class="field-label">Stick Function</label>
        <div class="pill-selector">
          <button
            class="pill-opt"
            :class="{ active: currentStickConfig.mode === 'digital_keys' }"
            @click="updateStickMode('digital_keys')"
          >
            Digital Keys (WASD)
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
          <label class="field-label">Deadzone</label>
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
        <!-- Sensitivity -->
        <div class="field-group">
          <div class="slider-header">
            <label class="field-label">Mouse Sensitivity</label>
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

        <!-- Curve Selection -->
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

        <!-- Invert Y -->
        <div class="field-group toggle-row">
          <label class="field-label">Invert Y Axis</label>
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
        <label class="field-label">Action Type</label>
        <div class="pill-selector">
          <button
            class="pill-opt"
            :class="{ active: currentButtonBinding.type === 'key' }"
            @click="setBindingType('key')"
          >
            Keyboard Key
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
            Scroll Wheel
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
          <label class="field-label">Assigned Key</label>
          <input
            v-model="searchFilter"
            type="text"
            placeholder="Search key or modifier (e.g. Command, Space, F5)..."
            class="search-input"
          />

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
              Middle Click
            </button>
          </div>
        </div>

        <!-- Trigger Threshold if L2 or R2 -->
        <div v-if="controlId === 'l2' || controlId === 'r2'" class="field-group">
          <div class="slider-header">
            <label class="field-label">Trigger Sensitivity Threshold</label>
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
            <label class="field-label">Repeat Rate</label>
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
  padding: 18px;
  position: relative;
  z-index: 10;
  border-radius: 16px;
  overflow: hidden;
}

.inspector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(147, 197, 253, 0.12);
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
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}

.record-btn {
  padding: 5px 12px;
  font-size: 11px;
}

.rec-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #f43f5e;
  box-shadow: 0 0 6px #f43f5e;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 12px;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 36px;
  opacity: 0.6;
}

.empty-text {
  font-size: 12px;
  max-width: 200px;
}

.inspector-body {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 11.5px;
  font-weight: 600;
  color: var(--text-secondary);
}

.pill-selector {
  display: flex;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(147, 197, 253, 0.12);
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
  font-size: 11px;
  font-weight: 600;
  padding: 5px 6px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.pill-opt:hover:not(.active) {
  color: var(--text-secondary);
}

.pill-opt.active {
  background: rgba(56, 189, 248, 0.2);
  color: #fff;
  border: 1px solid rgba(56, 189, 248, 0.4);
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
  background: rgba(30, 41, 59, 0.8);
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

.search-input {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(147, 197, 253, 0.16);
  border-radius: 8px;
  padding: 7px 10px;
  color: #fff;
  font-size: 11.5px;
  font-family: var(--font-sans);
  outline: none;
  transition: border-color 0.2s ease;
}

.search-input:focus {
  border-color: var(--accent-cyan);
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
  background: rgba(15, 23, 42, 0.45);
  border: 1px solid transparent;
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
}

.key-option-row:hover {
  background: rgba(56, 189, 248, 0.1);
  color: #fff;
}

.key-option-row.selected {
  background: rgba(56, 189, 248, 0.18);
  border-color: rgba(56, 189, 248, 0.45);
  color: #fff;
}

.key-badge {
  font-size: 11.5px;
  font-weight: 600;
}

.key-code-sub {
  font-family: var(--font-mono);
  font-size: 9.5px;
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
  border: 1px solid rgba(147, 197, 253, 0.12);
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
  border: 1px solid rgba(147, 197, 253, 0.2);
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
