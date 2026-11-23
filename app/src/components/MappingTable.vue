<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import type { ControllerControlId, ButtonBinding, StickConfig } from '../types/keymap';
import type { PlatformLegendMode } from '../types/controllers';
import CosmicIcon from './CosmicIcon.vue';
import ControllerButtonIcon from './ControllerButtonIcon.vue';

interface MappingRowItem {
  id: ControllerControlId;
  name: string;
  category: 'Face Buttons' | 'Bumpers & Triggers' | 'D-Pad' | 'Thumbsticks' | 'System';
  description: string;
  isStick?: boolean;
  isDpadUnified?: boolean;
}

const props = withDefaults(
  defineProps<{
    selectedControl: ControllerControlId | null;
    buttons: Record<string, ButtonBinding>;
    leftStick: StickConfig;
    rightStick: StickConfig;
    platformMode?: PlatformLegendMode;
  }>(),
  {
    platformMode: 'playstation',
  }
);

const emit = defineEmits<{
  (e: 'select-control', id: ControllerControlId): void;
  (e: 'rebind', id: ControllerControlId): void;
  (e: 'clear-binding', id: ControllerControlId): void;
  (e: 'configure-stick', id: 'left_stick' | 'right_stick'): void;
  (e: 'configure-dpad'): void;
}>();

const searchQuery = ref('');
const rowElements = ref<Record<string, HTMLElement | null>>({});

const getControlName = (id: ControllerControlId, fallback: string): string => {
  const mode = props.platformMode;
  if (mode === 'eightbitdo' || mode === 'nintendo') {
    switch (id) {
      case 'a': return 'B Button';
      case 'b': return 'A Button';
      case 'x': return 'Y Button';
      case 'y': return 'X Button';
      case 'l1': return 'L1 Bumper';
      case 'r1': return 'R1 Bumper';
      case 'l4': return 'L4 Extra Bumper';
      case 'r4': return 'R4 Extra Bumper';
      case 'l2': return 'L2 Trigger';
      case 'r2': return 'R2 Trigger';
      case 'l3': return 'L3 (Left Stick Press)';
      case 'r3': return 'R3 (Right Stick Press)';
      case 'menu': return 'Plus (+)';
      case 'options': return 'Minus (-)';
      case 'home': return 'Home Button';
      case 'dpad_up': return 'D-Pad Up';
      case 'dpad_down': return 'D-Pad Down';
      case 'dpad_left': return 'D-Pad Left';
      case 'dpad_right': return 'D-Pad Right';
    }
  } else if (mode === 'playstation') {
    switch (id) {
      case 'a': return 'Cross Button';
      case 'b': return 'Circle Button';
      case 'x': return 'Square Button';
      case 'y': return 'Triangle Button';
      case 'l1': return 'L1 Shoulder';
      case 'r1': return 'R1 Shoulder';
      case 'l4': return 'L4 Bumper';
      case 'r4': return 'R4 Bumper';
      case 'l2': return 'L2 Trigger';
      case 'r2': return 'R2 Trigger';
      case 'l3': return 'L3 Press';
      case 'r3': return 'R3 Press';
      case 'menu': return 'Options';
      case 'options': return 'Share';
      case 'home': return 'PS Button';
      case 'touchpad': return 'Touchpad';
      case 'dpad_up': return 'D-Pad Up';
      case 'dpad_down': return 'D-Pad Down';
      case 'dpad_left': return 'D-Pad Left';
      case 'dpad_right': return 'D-Pad Right';
    }
  } else {
    // Default Xbox
    switch (id) {
      case 'a': return 'A Button';
      case 'b': return 'B Button';
      case 'x': return 'X Button';
      case 'y': return 'Y Button';
      case 'l1': return 'LB (Left Bumper)';
      case 'r1': return 'RB (Right Bumper)';
      case 'l4': return 'L4 Extra Bumper';
      case 'r4': return 'R4 Extra Bumper';
      case 'l2': return 'LT (Left Trigger)';
      case 'r2': return 'RT (Right Trigger)';
      case 'l3': return 'LS Press';
      case 'r3': return 'RS Press';
      case 'menu': return 'Menu';
      case 'options': return 'View';
      case 'home': return 'Home / Guide';
      case 'dpad_up': return 'D-Pad Up';
      case 'dpad_down': return 'D-Pad Down';
      case 'dpad_left': return 'D-Pad Left';
      case 'dpad_right': return 'D-Pad Right';
    }
  }
  return fallback;
};

const tableItems = computed<MappingRowItem[]>(() => {
  const items: MappingRowItem[] = [
    // Face Buttons
    { id: 'a', name: getControlName('a', 'A Button'), category: 'Face Buttons', description: 'Primary Action / Jump' },
    { id: 'b', name: getControlName('b', 'B Button'), category: 'Face Buttons', description: 'Secondary Action / Crouch' },
    { id: 'x', name: getControlName('x', 'X Button'), category: 'Face Buttons', description: 'Interact / Reload' },
    { id: 'y', name: getControlName('y', 'Y Button'), category: 'Face Buttons', description: 'Inventory / Switch Weapon' },

    // Bumpers & Triggers
    { id: 'l1', name: getControlName('l1', 'L1 Bumper'), category: 'Bumpers & Triggers', description: 'Left Shoulder Bumper' },
    { id: 'r1', name: getControlName('r1', 'R1 Bumper'), category: 'Bumpers & Triggers', description: 'Right Shoulder Bumper' },
  ];

  if (props.platformMode === 'eightbitdo') {
    items.push(
      { id: 'l4', name: getControlName('l4', 'L4 Extra Bumper'), category: 'Bumpers & Triggers', description: 'Quick-Access Mini Bumper' },
      { id: 'r4', name: getControlName('r4', 'R4 Extra Bumper'), category: 'Bumpers & Triggers', description: 'Quick-Access Mini Bumper' }
    );
  }

  items.push(
    { id: 'l2', name: getControlName('l2', 'L2 Trigger'), category: 'Bumpers & Triggers', description: 'Left Analog Trigger' },
    { id: 'r2', name: getControlName('r2', 'R2 Trigger'), category: 'Bumpers & Triggers', description: 'Right Analog Trigger' },

    // Thumbsticks
    { id: 'left_stick', name: 'Left Stick', category: 'Thumbsticks', description: 'Digital Movement / WASD', isStick: true },
    { id: 'right_stick', name: 'Right Stick', category: 'Thumbsticks', description: 'Precision Mouse Pointer', isStick: true },
    { id: 'l3', name: getControlName('l3', 'L3 Click'), category: 'Thumbsticks', description: 'Left Stick Click' },
    { id: 'r3', name: getControlName('r3', 'R3 Click'), category: 'Thumbsticks', description: 'Right Stick Click' },

    // D-Pad
    { id: 'dpad_up', name: getControlName('dpad_up', 'D-Pad Up'), category: 'D-Pad', description: 'Directional Up' },
    { id: 'dpad_down', name: getControlName('dpad_down', 'D-Pad Down'), category: 'D-Pad', description: 'Directional Down' },
    { id: 'dpad_left', name: getControlName('dpad_left', 'D-Pad Left'), category: 'D-Pad', description: 'Directional Left' },
    { id: 'dpad_right', name: getControlName('dpad_right', 'D-Pad Right'), category: 'D-Pad', description: 'Directional Right' },

    // System
    { id: 'menu', name: getControlName('menu', 'Plus (+)'), category: 'System', description: 'Pause / Menu' },
    { id: 'options', name: getControlName('options', 'Minus (-)'), category: 'System', description: 'Map / Select' },
    { id: 'home', name: getControlName('home', 'Home Button'), category: 'System', description: 'Hardware Profile Cycle' }
  );

  if (props.platformMode === 'playstation') {
    items.push({
      id: 'touchpad',
      name: 'Touchpad',
      category: 'System',
      description: 'Touchpad Click / Surface',
    });
  }

  return items;
});

const filteredItems = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return tableItems.value;
  return tableItems.value.filter(
    (item) =>
      item.name.toLowerCase().includes(q) ||
      item.description.toLowerCase().includes(q) ||
      item.category.toLowerCase().includes(q) ||
      item.id.toLowerCase().includes(q)
  );
});

const setRowRef = (id: string, el: any) => {
  if (el) {
    rowElements.value[id] = el;
  }
};

watch(
  () => props.selectedControl,
  (newId) => {
    if (!newId) return;
    nextTick(() => {
      const el = rowElements.value[newId];
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    });
  }
);

const getMappingDisplay = (item: MappingRowItem): string => {
  if (item.isStick) {
    const s = item.id === 'left_stick' ? props.leftStick : props.rightStick;
    if (s.mode === 'mouse') {
      const sens = s.sensitivity ?? 1.0;
      return `Mouse Pointer (${sens.toFixed(1)}x)`;
    }
    if (s.mode === 'digital_keys') {
      const u = s.up ? s.up.replace(/^KEY_/, '') : 'W';
      const d = s.down ? s.down.replace(/^KEY_/, '') : 'S';
      const l = s.left ? s.left.replace(/^KEY_/, '') : 'A';
      const r = s.right ? s.right.replace(/^KEY_/, '') : 'D';
      return `${u} ${l} ${d} ${r}`;
    }
    return 'Disabled';
  }

  if (item.isDpadUnified) {
    const clean = (c?: string) => (c ? c.replace(/^KEY_/, '').replace(/_/g, ' ') : '');
    const u = clean(props.buttons['dpad_up']?.code);
    const d = clean(props.buttons['dpad_down']?.code);
    const l = clean(props.buttons['dpad_left']?.code);
    const r = clean(props.buttons['dpad_right']?.code);

    if (u.toLowerCase() === 'w' && d.toLowerCase() === 's' && l.toLowerCase() === 'a' && r.toLowerCase() === 'd') {
      return 'WASD Movement';
    }
    if (u.includes('UP') && d.includes('DOWN') && l.includes('LEFT') && r.includes('RIGHT')) {
      return 'Arrow Keys';
    }
    if (u || d || l || r) {
      return `${u || '-'} • ${l || '-'} • ${d || '-'} • ${r || '-'}`;
    }
    return 'Unmapped';
  }

  const b = props.buttons[item.id];
  if (!b || b.type === 'none') return 'Unmapped';
  if (b.type === 'key') {
    return (b.code || 'Unmapped').replace(/^KEY_/, '').replace(/_/g, ' ');
  }
  if (b.type === 'consumer_control') {
    return (b.code || 'Media').replace(/^MEDIA_/, '').replace(/_/g, ' ');
  }
  if (b.type === 'gyro_aim') return 'Gyro Aim';
  if (b.type === 'mouse_button') return b.code || 'Mouse Click';
  if (b.type === 'mouse_scroll') return (b.delta || 0) > 0 ? 'Scroll Up' : 'Scroll Down';
  return 'Unmapped';
};

const isMapped = (item: MappingRowItem): boolean => {
  if (item.isStick) return true;
  if (item.isDpadUnified) {
    return Boolean(
      (props.buttons['dpad_up'] && props.buttons['dpad_up'].type !== 'none') ||
      (props.buttons['dpad_down'] && props.buttons['dpad_down'].type !== 'none') ||
      (props.buttons['dpad_left'] && props.buttons['dpad_left'].type !== 'none') ||
      (props.buttons['dpad_right'] && props.buttons['dpad_right'].type !== 'none')
    );
  }
  const b = props.buttons[item.id];
  return Boolean(b && b.type !== 'none');
};
</script>

<template>
  <div class="mapping-table-card glass-panel">
    <!-- Header with Quick Filter & Counter -->
    <div class="table-header">
      <div class="search-box">
        <CosmicIcon name="search" size="13" class="search-icon" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Filter controls..."
          class="search-input"
        />
        <button
          v-if="searchQuery"
          class="clear-search-btn"
          @click="searchQuery = ''"
        >
          <CosmicIcon name="x" size="11" />
        </button>
      </div>

      <span class="count-tag">{{ filteredItems.length }} Controls</span>
    </div>

    <!-- Scrollable Floating Pill Rows matching the Sky Glass mockup -->
    <div class="table-body custom-scroll">
      <div
        v-for="item in filteredItems"
        :key="item.id"
        :ref="(el) => setRowRef(item.id, el)"
        class="floating-row"
        :class="{
          'is-selected': selectedControl === item.id,
          'is-mapped': isMapped(item),
        }"
        @click="emit('select-control', item.id)"
      >
        <!-- Left: Controller Button Icon & Name -->
        <div class="cell-control">
          <div class="icon-avatar">
            <ControllerButtonIcon :control-id="item.id" :platform-mode="platformMode" :size="20" />
          </div>
          <div class="meta-texts">
            <span class="control-name">{{ item.name }}</span>
          </div>
        </div>

        <!-- Center: Key Mapping Capsule Pill -->
        <div class="cell-mapping">
          <div
            class="key-capsule"
            :class="{
              unmapped: !isMapped(item),
              stick: item.isStick,
            }"
          >
            <span class="key-text">{{ getMappingDisplay(item) }}</span>
          </div>
        </div>

        <!-- Right: Map Key & Clear Actions -->
        <div class="cell-actions" @click.stop>
          <template v-if="item.isStick">
            <button
              class="action-btn config-btn"
              title="Configure Analog Stick"
              @click="emit('configure-stick', item.id as 'left_stick' | 'right_stick')"
            >
              <CosmicIcon name="sliders" size="12" />
              <span>Config</span>
            </button>
          </template>

          <template v-else-if="item.isDpadUnified">
            <button
              class="action-btn config-btn"
              title="Configure D-Pad"
              @click="emit('configure-dpad')"
            >
              <CosmicIcon name="sliders" size="12" />
              <span>Config</span>
            </button>
          </template>

          <template v-else>
            <button
              class="action-btn map-btn"
              title="Map to key"
              @click="emit('rebind', item.id)"
            >
              <CosmicIcon name="edit" size="12" />
              <span>Map Key</span>
            </button>

            <button
              v-if="isMapped(item)"
              class="clear-icon-btn"
              title="Clear binding"
              @click="emit('clear-binding', item.id)"
            >
              <CosmicIcon name="x" size="11" />
            </button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mapping-table-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  border-radius: 24px;
  background-color: var(--glass-surface);
  background-image: linear-gradient(
    135deg,
    rgba(var(--accent-custom-rgb, 125, 211, 252), calc(var(--glass-tint-val, 0.14) * 0.50)) 0%,
    rgba(var(--accent-custom-rgb, 125, 211, 252), calc(var(--glass-tint-val, 0.14) * 0.12)) 40%,
    transparent 85%
  );
  backdrop-filter: blur(var(--glass-blur-val, 28px)) saturate(190%);
  -webkit-backdrop-filter: blur(var(--glass-blur-val, 28px)) saturate(190%);
  border: 1px solid var(--glass-border);
  box-shadow: none;
  padding: 16px 18px;
  overflow: hidden;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
  padding: 0 6px 10px 6px;
  border-bottom: 1px solid var(--glass-border-subtle);
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: 9999px;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
  width: 220px;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.search-box:focus-within {
  border-color: var(--accent-custom);
  background: var(--glass-surface-elevated);
  box-shadow: 0 0 14px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.25);
}

.search-input {
  background: transparent;
  border: none;
  outline: none;
  font-size: 12px;
  color: var(--text-primary);
  width: 100%;
  font-family: var(--font-sans);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.clear-search-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 2px;
  display: flex;
}
.clear-search-btn:hover {
  color: var(--text-primary);
}

.count-tag {
  font-size: 10.5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 4px 10px;
  border-radius: 9999px;
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border-subtle);
  color: var(--accent-custom);
}

.table-body {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 4px 6px 12px 4px;
}

/* Floating Pill Row (Matching Sky Glass Mockup) */
.floating-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 7px 14px;
  background-color: var(--glass-surface-pill);
  background-image: linear-gradient(
    135deg,
    rgba(var(--accent-custom-rgb, 125, 211, 252), calc(var(--glass-tint-val, 0.14) * 0.35)) 0%,
    transparent 80%
  );
  backdrop-filter: blur(var(--glass-blur-val, 20px));
  -webkit-backdrop-filter: blur(var(--glass-blur-val, 20px));
  border: 1px solid var(--glass-border-subtle);
  border-radius: 9999px;
  box-shadow: var(--shadow-pill);
  cursor: pointer;
  transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}

.floating-row:hover {
  background: var(--glass-surface-elevated);
  border-color: var(--glass-border);
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.15);
}

.floating-row.is-selected {
  background: var(--glass-surface-active);
  border-color: var(--accent-custom);
  box-shadow: 0 0 20px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.35);
  transform: translateY(-1px);
}

.cell-control {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 140px;
}

.icon-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #000000;
  border: 1px solid rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

.meta-texts {
  display: flex;
  flex-direction: column;
}

.control-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

/* Center Key Mapping Capsule */
.cell-mapping {
  flex: 1;
  display: flex;
  justify-content: center;
  padding: 0 12px;
}

.key-capsule {
  padding: 4px 14px;
  border-radius: 9999px;
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-pill);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 90px;
  transition: all 0.2s ease;
}

.key-text {
  font-family: var(--font-mono);
  font-size: 11.5px;
  font-weight: 600;
  color: var(--accent-custom);
  letter-spacing: 0.02em;
}

.key-capsule.unmapped {
  background: transparent;
  border-color: var(--glass-border-subtle);
}

.key-capsule.unmapped .key-text {
  color: var(--text-muted);
  font-weight: 400;
}

/* Right Actions */
.cell-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: 9999px;
  font-size: 11.5px;
  font-weight: 500;
  cursor: pointer;
  background: var(--btn-bg);
  border: 1px solid var(--btn-border);
  color: var(--text-primary);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.action-btn:hover {
  background: var(--glass-surface-elevated);
  border-color: var(--accent-custom);
  color: var(--accent-custom);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.25);
}

.clear-icon-btn {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-icon-btn:hover {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}
</style>
