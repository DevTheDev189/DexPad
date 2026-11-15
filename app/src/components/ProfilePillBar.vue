<script setup lang="ts">
import { ref } from 'vue';
import type { Profile } from '../types/keymap';
import CosmicIcon from './CosmicIcon.vue';

defineProps<{
  profiles: Profile[];
  activeSlot: number;
  isDirty: boolean;
  isConnected: boolean;
  currentView: 'controller' | 'table';
}>();

const emit = defineEmits<{
  (e: 'select-slot', slot: number): void;
  (e: 'rename-slot', slot: number, name: string): void;
  (e: 'save-to-device'): void;
  (e: 'open-manager'): void;
  (e: 'toggle-view', view: 'controller' | 'table'): void;
}>();

const editingSlot = ref<number | null>(null);
const editNameInput = ref('');

const startRenaming = (slot: number, currentName: string) => {
  editingSlot.value = slot;
  editNameInput.value = currentName;
};

const commitRename = (slot: number) => {
  if (editNameInput.value.trim()) {
    emit('rename-slot', slot, editNameInput.value.trim());
  }
  editingSlot.value = null;
};
</script>

<template>
  <div class="profile-bar-wrapper glass-panel">
    <!-- Preset Slots -->
    <div class="slots-container">
      <div
        v-for="(prof, idx) in profiles"
        :key="prof.slot"
        class="slot-tab"
        :class="{ active: activeSlot === idx }"
        @click="emit('select-slot', idx)"
      >
        <!-- Sliding active liquid indicator pill -->
        <div v-if="activeSlot === idx" class="active-metaball-pill"></div>

        <div class="slot-content">
          <!-- Game Cover Avatar or Slot Badge -->
          <div v-if="prof.coverUrl" class="slot-cover-avatar">
            <img :src="prof.coverUrl" :alt="prof.name" class="avatar-img" />
          </div>
          <span v-else class="slot-index-badge">P{{ idx + 1 }}</span>
          
          <template v-if="editingSlot === idx">
            <input
              v-model="editNameInput"
              class="rename-input"
              autofocus
              @blur="commitRename(idx)"
              @keydown.enter="commitRename(idx)"
              @click.stop
            />
          </template>
          <template v-else>
            <span class="slot-name" @dblclick.stop="startRenaming(idx, prof.name)">
              {{ prof.name }}
            </span>
            <button
              class="edit-icon-btn"
              title="Rename profile"
              @click.stop="startRenaming(idx, prof.name)"
            >
              <CosmicIcon name="edit" size="11" />
            </button>
          </template>
        </div>
      </div>

      <!-- Open Game Hub & Presets Button -->
      <button
        class="btn-glass-secondary presets-hub-btn"
        title="Open Game Profiles & Community Presets Hub"
        @click="emit('open-manager')"
      >
        <CosmicIcon name="gamepad" size="13" />
        <span>Game Hub</span>
      </button>
    </div>

    <!-- Right Controls: View Switcher & Hardware Sync Action -->
    <div class="right-actions-group">
      <!-- Controller vs Table View Switcher -->
      <div class="view-switcher-pill glass-pill">
        <button
          class="view-btn"
          :class="{ active: currentView === 'controller' }"
          title="Interactive 3D Controller View"
          @click="emit('toggle-view', 'controller')"
        >
          <CosmicIcon name="gamepad" size="13" />
          <span>Controller</span>
        </button>
        <button
          class="view-btn"
          :class="{ active: currentView === 'table' }"
          title="Controller to Keybind Table View"
          @click="emit('toggle-view', 'table')"
        >
          <CosmicIcon name="table" size="13" />
          <span>Keybind Table</span>
        </button>
      </div>

      <!-- Sync Status Badge -->
      <div class="sync-status" :class="{ synced: isConnected && !isDirty, unsaved: isDirty }">
        <span class="status-dot"></span>
        <span class="status-label">
          {{ !isConnected ? 'Local Mode' : (isDirty ? 'Unsaved' : 'Synced') }}
        </span>
      </div>

      <!-- Save to Dongle Action -->
      <button
        class="btn-cosmic sync-btn"
        title="Write active profile into ESP32 Flash Memory (NVS)"
        @click="emit('save-to-device')"
      >
        <CosmicIcon name="bolt" size="13" />
        <span>Save to Dongle</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.profile-bar-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 14px;
  width: 100%;
  height: 52px;
  border-radius: 14px;
  gap: 12px;
  flex-wrap: wrap;
}

.slots-container {
  display: flex;
  align-items: center;
  gap: 6px;
}

.slot-tab {
  position: relative;
  display: flex;
  align-items: center;
  padding: 5px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  user-select: none;
}

.slot-tab:hover:not(.active) {
  background: rgba(255, 255, 255, 0.06);
}

.active-metaball-pill {
  position: absolute;
  inset: 0;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.25) 0%, rgba(139, 92, 246, 0.3) 100%);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 0 20px rgba(56, 189, 248, 0.3), inset 0 1px 1.5px rgba(255, 255, 255, 0.35);
  pointer-events: none;
}

.slot-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.slot-cover-avatar {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.slot-index-badge {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  padding: 2px 5px;
  border-radius: 4px;
  background: rgba(12, 18, 36, 0.7);
  color: var(--accent-cyan);
  border: 1px solid rgba(56, 189, 248, 0.35);
}

.slot-name {
  font-weight: 600;
  font-size: 12.5px;
  color: var(--text-secondary);
  transition: color 0.2s ease;
}

.slot-tab.active .slot-name {
  color: #ffffff;
  text-shadow: 0 0 12px rgba(255, 255, 255, 0.6);
}

.edit-icon-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  opacity: 0;
  transition: all 0.2s ease;
  padding: 2px;
}

.slot-tab:hover .edit-icon-btn {
  opacity: 0.8;
}

.edit-icon-btn:hover {
  color: var(--accent-cyan);
  opacity: 1;
}

.rename-input {
  background: rgba(12, 18, 36, 0.95);
  border: 1px solid var(--accent-cyan);
  border-radius: 6px;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  padding: 2px 6px;
  outline: none;
  font-family: var(--font-sans);
  width: 100px;
}

.presets-hub-btn {
  padding: 5px 10px;
  font-size: 11.5px;
  margin-left: 4px;
}

/* Right Actions */
.right-actions-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* View Switcher */
.view-switcher-pill {
  display: flex;
  padding: 2px;
  gap: 2px;
}

.view-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  background: transparent;
  border: none;
  border-radius: 9999px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-btn:hover:not(.active) {
  color: #fff;
}

.view-btn.active {
  background: rgba(56, 189, 248, 0.25);
  color: #fff;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.2);
}

/* Sync Status */
.sync-status {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 11.5px;
  font-weight: 500;
  color: var(--text-muted);
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #64748b;
  transition: all 0.3s ease;
}

.sync-status.synced .status-dot {
  background: #10b981;
  box-shadow: 0 0 10px #10b981;
}
.sync-status.synced .status-label {
  color: #34d399;
}

.sync-status.unsaved .status-dot {
  background: #f59e0b;
  box-shadow: 0 0 10px #f59e0b;
}
.sync-status.unsaved .status-label {
  color: #fbbf24;
}

.sync-btn {
  padding: 6px 14px;
  font-size: 12px;
}
</style>
