<script setup lang="ts">
import { ref, computed } from 'vue';
import type { ControllerControlId, Profile, ButtonBinding } from '../types/keymap';
import CosmicIcon from './CosmicIcon.vue';

const props = defineProps<{
  profile: Profile;
  selectedControl: ControllerControlId | null;
  telemetryActiveId?: ControllerControlId | null;
}>();

const emit = defineEmits<{
  (e: 'select-control', id: ControllerControlId): void;
  (e: 'record-control', id: ControllerControlId): void;
  (e: 'clear-binding', id: ControllerControlId): void;
}>();

const searchQuery = ref('');

interface TableRowItem {
  id: ControllerControlId;
  label: string;
  category: 'Face' | 'Shoulder' | 'D-Pad' | 'Stick' | 'System';
  isStick?: boolean;
}

const ALL_CONTROLS: TableRowItem[] = [
  // Face Buttons
  { id: 'a', label: 'Button A', category: 'Face' },
  { id: 'b', label: 'Button B', category: 'Face' },
  { id: 'x', label: 'Button X', category: 'Face' },
  { id: 'y', label: 'Button Y', category: 'Face' },
  // Shoulder & Triggers
  { id: 'l1', label: 'Left Bumper (L1)', category: 'Shoulder' },
  { id: 'r1', label: 'Right Bumper (R1)', category: 'Shoulder' },
  { id: 'l2', label: 'Left Trigger (L2)', category: 'Shoulder' },
  { id: 'r2', label: 'Right Trigger (R2)', category: 'Shoulder' },
  // D-Pad
  { id: 'dpad_up', label: 'D-Pad Up', category: 'D-Pad' },
  { id: 'dpad_down', label: 'D-Pad Down', category: 'D-Pad' },
  { id: 'dpad_left', label: 'D-Pad Left', category: 'D-Pad' },
  { id: 'dpad_right', label: 'D-Pad Right', category: 'D-Pad' },
  // Sticks
  { id: 'left_stick', label: 'Left Thumbstick', category: 'Stick', isStick: true },
  { id: 'right_stick', label: 'Right Thumbstick', category: 'Stick', isStick: true },
  { id: 'l3', label: 'Left Stick Click (L3)', category: 'Stick' },
  { id: 'r3', label: 'Right Stick Click (R3)', category: 'Stick' },
  // System
  { id: 'menu', label: 'Menu Button', category: 'System' },
  { id: 'options', label: 'Options Button', category: 'System' },
  { id: 'home', label: 'Home / Guide Button', category: 'System' },
];

const getBindingDisplay = (item: TableRowItem): { type: string; badge: string; detail: string } => {
  if (item.id === 'left_stick') {
    const s = props.profile.sticks.left;
    if (s.mode === 'digital_keys') {
      return {
        type: 'Digital Directional',
        badge: `${(s.up || 'W').toUpperCase()} ${(s.left || 'A').toUpperCase()} ${(s.down || 'S').toUpperCase()} ${(s.right || 'D').toUpperCase()}`,
        detail: `Deadzone: ${s.deadzone}`,
      };
    }
    if (s.mode === 'mouse') {
      return {
        type: 'Smooth Mouse',
        badge: 'Mouse Cursor',
        detail: `Sens: ${(s.sensitivity || 1).toFixed(1)}x`,
      };
    }
    return { type: 'Disabled', badge: 'Unmapped', detail: '' };
  }

  if (item.id === 'right_stick') {
    const s = props.profile.sticks.right;
    if (s.mode === 'mouse') {
      return {
        type: 'Smooth Mouse',
        badge: 'Mouse Cursor',
        detail: `Sens: ${(s.sensitivity || 1.35).toFixed(2)}x (${s.curve || 'exp'})`,
      };
    }
    if (s.mode === 'digital_keys') {
      return {
        type: 'Digital Directional',
        badge: `${(s.up || 'U').toUpperCase()} ${(s.left || 'L').toUpperCase()} ${(s.down || 'D').toUpperCase()} ${(s.right || 'R').toUpperCase()}`,
        detail: `Deadzone: ${s.deadzone}`,
      };
    }
    return { type: 'Disabled', badge: 'Unmapped', detail: '' };
  }

  const b: ButtonBinding | undefined = props.profile.buttons[item.id];
  if (!b || b.type === 'none') {
    return { type: 'Unmapped', badge: 'None', detail: 'Click Map to assign' };
  }
  if (b.type === 'key') {
    const code = b.code || '';
    let label = code;
    if (code === 'KEY_SPACE') label = 'Space';
    else if (code === 'KEY_RETURN') label = 'Enter';
    else if (code === 'KEY_ESC') label = 'Esc';
    else if (code === 'KEY_TAB') label = 'Tab';
    else if (code.includes('SHIFT')) label = 'Shift';
    else if (code.includes('CTRL')) label = 'Control';
    else if (code.includes('ALT')) label = 'Option / Alt';
    else if (code.includes('GUI')) label = 'Command';
    else if (code.startsWith('KEY_')) label = code.replace('KEY_', '');
    else label = code.toUpperCase();

    return { type: 'Keyboard Key', badge: label, detail: code };
  }
  if (b.type === 'mouse_button') {
    let name = 'Left Click';
    if (b.code === 'MOUSE_RIGHT') name = 'Right Click';
    if (b.code === 'MOUSE_MIDDLE') name = 'Middle Click';
    return {
      type: 'Mouse Click',
      badge: name,
      detail: b.threshold ? `Threshold: ${b.threshold}` : 'Instant',
    };
  }
  if (b.type === 'mouse_scroll') {
    return {
      type: 'Scroll Wheel',
      badge: (b.delta && b.delta > 0) ? 'Scroll Up (+1)' : 'Scroll Down (-1)',
      detail: `Rate: ${b.repeat_ms || 120}ms`,
    };
  }

  return { type: 'None', badge: 'None', detail: '' };
};

const filteredRows = computed(() => {
  if (!searchQuery.value) return ALL_CONTROLS;
  const q = searchQuery.value.toLowerCase();
  return ALL_CONTROLS.filter((row) => {
    const binding = getBindingDisplay(row);
    return (
      row.label.toLowerCase().includes(q) ||
      row.category.toLowerCase().includes(q) ||
      binding.type.toLowerCase().includes(q) ||
      binding.badge.toLowerCase().includes(q) ||
      binding.detail.toLowerCase().includes(q)
    );
  });
});
</script>

<template>
  <div class="binding-table-container glass-panel">
    <!-- Table Header & Controls -->
    <div class="table-top-bar">
      <div class="table-info">
        <h3 class="table-title">Controller Mappings Table</h3>
        <p class="table-sub">
          Click any button row to map a keyboard key, mouse click, or stick response to the game.
        </p>
      </div>

      <div class="table-search-box">
        <CosmicIcon name="search" size="14" class="search-icon" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Filter bindings (e.g. Space, Trigger, WASD)..."
          class="table-search-input"
        />
        <button v-if="searchQuery" class="clear-search-btn" @click="searchQuery = ''">
          <CosmicIcon name="x" size="12" />
        </button>
      </div>
    </div>

    <!-- Table Body -->
    <div class="table-scroll-area">
      <table class="cosmic-table">
        <thead>
          <tr>
            <th class="th-input">Controller Input</th>
            <th class="th-cat">Category</th>
            <th class="th-type">Action Type</th>
            <th class="th-binding">Assigned Key / Action</th>
            <th class="th-actions text-right">Quick Map</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in filteredRows"
            :key="row.id"
            class="table-row"
            :class="{
              selected: selectedControl === row.id,
              active: telemetryActiveId === row.id,
            }"
            @click="emit('select-control', row.id)"
          >
            <!-- Controller Input -->
            <td class="td-input">
              <div class="input-cell">
                <span class="control-indicator-dot" :class="{ live: telemetryActiveId === row.id }"></span>
                <span class="control-label">{{ row.label }}</span>
                <span class="control-id-badge">{{ row.id.toUpperCase() }}</span>
              </div>
            </td>

            <!-- Category -->
            <td class="td-cat">
              <span class="category-chip" :class="row.category.toLowerCase()">
                {{ row.category }}
              </span>
            </td>

            <!-- Action Type -->
            <td class="td-type">
              <span class="type-text">{{ getBindingDisplay(row).type }}</span>
            </td>

            <!-- Assigned Key / Badge -->
            <td class="td-binding">
              <div class="binding-cell">
                <span
                  class="key-chip"
                  :class="{
                    unmapped: getBindingDisplay(row).badge === 'None' || getBindingDisplay(row).badge === 'Unmapped',
                    stick: row.isStick,
                  }"
                >
                  {{ getBindingDisplay(row).badge }}
                </span>
                <span v-if="getBindingDisplay(row).detail" class="binding-detail">
                  {{ getBindingDisplay(row).detail }}
                </span>
              </div>
            </td>

            <!-- Quick Map Action Button -->
            <td class="td-actions text-right">
              <div class="row-actions">
                <button
                  v-if="!row.isStick"
                  class="btn-glass-secondary map-btn"
                  title="Record physical keystroke"
                  @click.stop="emit('record-control', row.id)"
                >
                  <CosmicIcon name="record" size="12" class="rec-icon" />
                  <span>Map Key</span>
                </button>
                <button
                  class="btn-glass-secondary inspect-btn"
                  title="Configure in Inspector"
                  @click.stop="emit('select-control', row.id)"
                >
                  <CosmicIcon name="sliders" size="12" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.binding-table-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 16px;
  position: relative;
  z-index: 2;
}

.table-top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  gap: 16px;
  flex-wrap: wrap;
}

.table-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}

.table-sub {
  font-size: 11.5px;
  color: var(--text-muted);
}

.table-search-box {
  display: flex;
  align-items: center;
  background: var(--input-bg);
  border: 1px solid var(--glass-border-subtle);
  border-radius: 10px;
  padding: 5px 10px;
  gap: 8px;
  min-width: 260px;
  box-shadow: inset 0 1px 1px 0 rgba(255, 255, 255, 0.1);
}

.search-icon {
  color: var(--text-muted);
}

.table-search-input {
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: 12px;
  width: 100%;
}

.clear-search-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 2px;
}
.clear-search-btn:hover {
  color: var(--text-primary);
}

/* Scroll area */
.table-scroll-area {
  flex: 1;
  overflow-y: auto;
  padding: 6px 12px 14px 12px;
}

.cosmic-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 4px;
  font-size: 12.5px;
}

th {
  position: sticky;
  top: 0;
  background: rgba(12, 18, 36, 0.95);
  backdrop-filter: blur(20px);
  padding: 10px 14px;
  font-family: var(--font-mono);
  font-size: 10.5px;
  font-weight: 700;
  color: var(--accent-cyan);
  letter-spacing: 1px;
  text-transform: uppercase;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 10;
}

.text-right {
  text-align: right;
}

/* Table Rows */
.table-row {
  background: rgba(255, 255, 255, 0.035);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  cursor: pointer;
  border-radius: 10px;
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.08);
}

.table-row.selected {
  background: rgba(var(--accent-custom-rgb, 125, 211, 252), 0.15);
  box-shadow: inset 0 0 0 1px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.45);
}

.table-row.active {
  background: rgba(var(--accent-custom-rgb, 125, 211, 252), 0.3) !important;
}

td {
  padding: 9px 14px;
  vertical-align: middle;
}

td:first-child {
  border-top-left-radius: 8px;
  border-bottom-left-radius: 8px;
}

td:last-child {
  border-top-right-radius: 8px;
  border-bottom-right-radius: 8px;
}

/* Cell Elements */
.input-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.control-indicator-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  transition: all 0.2s ease;
}

.control-indicator-dot.live {
  background: var(--accent-cyan);
  box-shadow: 0 0 8px var(--accent-cyan);
}

.control-label {
  font-weight: 600;
  color: var(--text-primary);
}

.control-id-badge {
  font-family: var(--font-mono);
  font-size: 9.5px;
  font-weight: 700;
  padding: 2px 5px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-muted);
}

/* Category Chips */
.category-chip {
  font-family: var(--font-mono);
  font-size: 9.5px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 6px;
  letter-spacing: 0.5px;
  border: 1px solid transparent;
}

.category-chip.face {
  background: rgba(192, 132, 252, 0.15);
  color: var(--accent-magenta);
  border-color: rgba(192, 132, 252, 0.3);
}

.category-chip.shoulder {
  background: rgba(var(--accent-custom-rgb, 125, 211, 252), 0.15);
  color: var(--accent-custom);
  border-color: rgba(var(--accent-custom-rgb, 125, 211, 252), 0.3);
}

.category-chip.d-pad {
  background: rgba(59, 130, 246, 0.15);
  color: var(--accent-cobalt);
  border-color: rgba(59, 130, 246, 0.3);
}

.category-chip.stick {
  background: rgba(139, 92, 246, 0.15);
  color: var(--accent-violet);
  border-color: rgba(139, 92, 246, 0.3);
}

.category-chip.system {
  background: rgba(100, 116, 139, 0.2);
  color: #cbd5e1;
  border-color: rgba(255, 255, 255, 0.15);
}

.type-text {
  font-size: 11.5px;
  color: var(--text-secondary);
}

/* Key Chips */
.binding-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.key-chip {
  font-family: var(--font-mono);
  font-size: 11.5px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 6px;
  background: rgba(var(--accent-custom-rgb, 125, 211, 252), 0.18);
  border: 1px solid rgba(var(--accent-custom-rgb, 125, 211, 252), 0.45);
  color: #fff;
  box-shadow: 0 0 10px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.2);
}

.key-chip.unmapped {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.1);
  color: var(--text-muted);
  box-shadow: none;
}

.key-chip.stick {
  background: rgba(139, 92, 246, 0.2);
  border-color: rgba(139, 92, 246, 0.45);
}

.binding-detail {
  font-size: 10.5px;
  color: var(--text-muted);
}

/* Row Action Buttons */
.row-actions {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.map-btn {
  padding: 4px 9px;
  font-size: 11px;
}

.rec-icon {
  color: #f43f5e;
}

.inspect-btn {
  padding: 4px 8px;
}
</style>

