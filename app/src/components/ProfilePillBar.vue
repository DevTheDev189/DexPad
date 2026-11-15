<script setup lang="ts">
import { ref } from 'vue';
import type { Profile } from '../types/keymap';

defineProps<{
  profiles: Profile[];
  activeSlot: number;
  isDirty: boolean;
  isConnected: boolean;
}>();

const emit = defineEmits<{
  (e: 'select-slot', slot: number): void;
  (e: 'rename-slot', slot: number, name: string): void;
  (e: 'save-to-device'): void;
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
          <span class="slot-index-badge">P{{ idx + 1 }}</span>
          
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
              title="Double click to rename"
              @click.stop="startRenaming(idx, prof.name)"
            >
              ✎
            </button>
          </template>
        </div>
      </div>
    </div>

    <!-- Sync Action / Status Badge -->
    <div class="sync-actions">
      <div class="sync-status" :class="{ synced: isConnected && !isDirty, unsaved: isDirty }">
        <span class="status-dot"></span>
        <span class="status-label">
          {{ !isConnected ? 'Local Mode' : (isDirty ? 'Unsaved Changes' : 'Synced with ESP32') }}
        </span>
      </div>

      <button
        class="btn-cosmic sync-btn"
        :disabled="!isConnected && false"
        title="Write active profile to ESP32 Flash Memory (NVS)"
        @click="emit('save-to-device')"
      >
        <span class="btn-icon">⚡</span>
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
  height: 54px;
  border-radius: 14px;
}

.slots-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.slot-tab {
  position: relative;
  display: flex;
  align-items: center;
  padding: 6px 14px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s ease;
  user-select: none;
}

.slot-tab:hover:not(.active) {
  background: rgba(147, 197, 253, 0.08);
}

.active-metaball-pill {
  position: absolute;
  inset: 0;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.22) 0%, rgba(139, 92, 246, 0.25) 100%);
  border: 1px solid rgba(56, 189, 248, 0.4);
  box-shadow: 0 0 16px rgba(56, 189, 248, 0.25), inset 0 0 8px rgba(255, 255, 255, 0.1);
  pointer-events: none;
}

.slot-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.slot-index-badge {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  padding: 2px 5px;
  border-radius: 4px;
  background: rgba(15, 23, 42, 0.6);
  color: var(--accent-cyan);
  border: 1px solid rgba(56, 189, 248, 0.3);
}

.slot-name {
  font-weight: 600;
  font-size: 13px;
  color: var(--text-secondary);
  transition: color 0.2s ease;
}

.slot-tab.active .slot-name {
  color: #ffffff;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

.edit-icon-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 11px;
  opacity: 0;
  transition: opacity 0.2s ease, color 0.2s ease;
  padding: 0 2px;
}

.slot-tab:hover .edit-icon-btn {
  opacity: 0.7;
}

.edit-icon-btn:hover {
  color: var(--accent-cyan);
  opacity: 1;
}

.rename-input {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid var(--accent-cyan);
  border-radius: 6px;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  padding: 2px 6px;
  outline: none;
  font-family: var(--font-sans);
  width: 110px;
}

/* Sync Actions */
.sync-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.sync-status {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
}

.status-dot {
  width: 8px;
  height: 8px;
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

.btn-icon {
  font-size: 13px;
}
</style>
