<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Profile } from '../types/keymap';
import CosmicIcon from './CosmicIcon.vue';

const props = defineProps<{
  profiles: Profile[];
  activeSlot: number;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'select-profile', slot: number): void;
  (e: 'add-profile', profile: Profile, targetSlot: number): void;
  (e: 'update-cover', slot: number, coverUrl: string): void;
}>();

const searchQuery = ref('');
const customGameName = ref('');
const customCoverUrl = ref('');
const targetSlotSelection = ref(props.activeSlot);

// Built-in curated community game templates with high-res artwork
const CURATED_GAME_PRESETS: Array<{
  name: string;
  genre: string;
  coverUrl: string;
  description: string;
  profile: Profile;
}> = [
  {
    name: 'Minecraft',
    genre: 'Sandbox / Survival',
    coverUrl: 'https://images.unsplash.com/photo-1627856013091-fed6e4e30025?w=600&auto=format&fit=crop&q=80',
    description: 'WASD movement, 125Hz mouse camera, space jump, shift sneak, L2 place, R2 mine.',
    profile: {
      slot: 0,
      name: 'Minecraft',
      gameTitle: 'Minecraft',
      coverUrl: 'https://images.unsplash.com/photo-1627856013091-fed6e4e30025?w=600&auto=format&fit=crop&q=80',
      genre: 'Sandbox',
      sticks: {
        left: { mode: 'digital_keys', deadzone: 180, up: 'w', down: 's', left: 'a', right: 'd' },
        right: { mode: 'mouse', deadzone: 45, sensitivity: 1.35, curve: 'exponential' },
      },
      buttons: {
        a: { type: 'key', code: 'KEY_SPACE' },
        b: { type: 'key', code: 'KEY_LEFT_SHIFT' },
        x: { type: 'key', code: 'q' },
        y: { type: 'key', code: 'e' },
        l1: { type: 'mouse_scroll', delta: 1, repeat_ms: 120 },
        r1: { type: 'mouse_scroll', delta: -1, repeat_ms: 120 },
        l2: { type: 'mouse_button', code: 'MOUSE_RIGHT', threshold: 40 },
        r2: { type: 'mouse_button', code: 'MOUSE_LEFT', threshold: 40 },
        l3: { type: 'key', code: 'KEY_LEFT_CTRL' },
        r3: { type: 'key', code: 'f' },
        dpad_up: { type: 'key', code: 'KEY_F5' },
        dpad_down: { type: 'key', code: 'KEY_F3' },
        dpad_left: { type: 'key', code: '1' },
        dpad_right: { type: 'key', code: 't' },
        menu: { type: 'key', code: 'KEY_ESC' },
        options: { type: 'key', code: 'KEY_RETURN' },
        home: { type: 'key', code: 'KEY_TAB' },
      },
    },
  },
  {
    name: 'Hollow Knight',
    genre: 'Metroidvania',
    coverUrl: 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=600&auto=format&fit=crop&q=80',
    description: 'Arrow navigation, Z jump, X nail slash, A cast/focus, C dash, Shift super dash.',
    profile: {
      slot: 1,
      name: 'Hollow Knight',
      gameTitle: 'Hollow Knight',
      coverUrl: 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=600&auto=format&fit=crop&q=80',
      genre: 'Metroidvania',
      sticks: {
        left: { mode: 'digital_keys', deadzone: 150, up: 'KEY_UP_ARROW', down: 'KEY_DOWN_ARROW', left: 'KEY_LEFT_ARROW', right: 'KEY_RIGHT_ARROW' },
        right: { mode: 'none', deadzone: 45 },
      },
      buttons: {
        a: { type: 'key', code: 'z' },
        x: { type: 'key', code: 'x' },
        y: { type: 'key', code: 'a' },
        b: { type: 'key', code: 'c' },
        r2: { type: 'key', code: 'KEY_LEFT_SHIFT', threshold: 40 },
        menu: { type: 'key', code: 'KEY_ESC' },
        home: { type: 'key', code: 'KEY_TAB' },
      },
    },
  },
  {
    name: 'Hades',
    genre: 'Action Roguelike',
    coverUrl: 'https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&auto=format&fit=crop&q=80',
    description: 'Fast-paced isometric combat: WASD dash, J attack, K special, Space dash, Q call.',
    profile: {
      slot: 2,
      name: 'Hades',
      gameTitle: 'Hades',
      coverUrl: 'https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&auto=format&fit=crop&q=80',
      genre: 'Roguelike',
      sticks: {
        left: { mode: 'digital_keys', deadzone: 140, up: 'w', down: 's', left: 'a', right: 'd' },
        right: { mode: 'mouse', deadzone: 40, sensitivity: 1.4, curve: 'linear' },
      },
      buttons: {
        a: { type: 'key', code: 'KEY_SPACE' },
        x: { type: 'key', code: 'j' },
        y: { type: 'key', code: 'k' },
        b: { type: 'key', code: 'l' },
        r1: { type: 'key', code: 'q' },
        l1: { type: 'key', code: 'e' },
        menu: { type: 'key', code: 'KEY_ESC' },
      },
    },
  },
  {
    name: 'Desktop Productivity Mode',
    genre: 'macOS Utility',
    coverUrl: 'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=600&auto=format&fit=crop&q=80',
    description: 'Precision mouse cursor on right stick, Left/Right click, Scroll wheel, Cmd for Mission Control.',
    profile: {
      slot: 3,
      name: 'Desktop Mouse',
      gameTitle: 'macOS Desktop',
      coverUrl: 'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=600&auto=format&fit=crop&q=80',
      genre: 'Utility',
      sticks: {
        left: { mode: 'none', deadzone: 100 },
        right: { mode: 'mouse', deadzone: 30, sensitivity: 1.6, curve: 'exponential' },
      },
      buttons: {
        a: { type: 'mouse_button', code: 'MOUSE_LEFT' },
        b: { type: 'mouse_button', code: 'MOUSE_RIGHT' },
        x: { type: 'mouse_button', code: 'MOUSE_MIDDLE' },
        l1: { type: 'mouse_scroll', delta: 1, repeat_ms: 100 },
        r1: { type: 'mouse_scroll', delta: -1, repeat_ms: 100 },
        home: { type: 'key', code: 'KEY_LEFT_GUI' },
      },
    },
  },
  {
    name: 'Cyberpunk 2077',
    genre: 'RPG / Action',
    coverUrl: 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=600&auto=format&fit=crop&q=80',
    description: 'FPS camera, Aim down sights (L2), Shoot (R2), Crouch (B), Jump (A), Reload (X), Interact (Y).',
    profile: {
      slot: 0,
      name: 'Cyberpunk 2077',
      gameTitle: 'Cyberpunk 2077',
      coverUrl: 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=600&auto=format&fit=crop&q=80',
      genre: 'Action RPG',
      sticks: {
        left: { mode: 'digital_keys', deadzone: 160, up: 'w', down: 's', left: 'a', right: 'd' },
        right: { mode: 'mouse', deadzone: 40, sensitivity: 1.5, curve: 'linear' },
      },
      buttons: {
        a: { type: 'key', code: 'KEY_SPACE' },
        b: { type: 'key', code: 'c' },
        x: { type: 'key', code: 'r' },
        y: { type: 'key', code: 'f' },
        l2: { type: 'mouse_button', code: 'MOUSE_RIGHT', threshold: 40 },
        r2: { type: 'mouse_button', code: 'MOUSE_LEFT', threshold: 40 },
        l3: { type: 'key', code: 'KEY_LEFT_SHIFT' },
      },
    },
  },
];

const filteredPresets = computed(() => {
  if (!searchQuery.value) return CURATED_GAME_PRESETS;
  const q = searchQuery.value.toLowerCase();
  return CURATED_GAME_PRESETS.filter(
    (p) =>
      p.name.toLowerCase().includes(q) ||
      p.genre.toLowerCase().includes(q) ||
      p.description.toLowerCase().includes(q)
  );
});

const applyPreset = (preset: (typeof CURATED_GAME_PRESETS)[0]) => {
  const newProf: Profile = {
    ...JSON.parse(JSON.stringify(preset.profile)),
    slot: targetSlotSelection.value,
    coverUrl: preset.coverUrl,
    gameTitle: preset.name,
  };
  emit('add-profile', newProf, targetSlotSelection.value);
};

const createCustomGame = () => {
  if (!customGameName.value.trim()) return;
  const targetSlot = targetSlotSelection.value;
  const baseProfile = JSON.parse(JSON.stringify(props.profiles[targetSlot] || props.profiles[0]));
  baseProfile.name = customGameName.value.trim();
  baseProfile.gameTitle = customGameName.value.trim();
  baseProfile.coverUrl = customCoverUrl.value.trim() || undefined;
  baseProfile.slot = targetSlot;

  emit('add-profile', baseProfile, targetSlot);
  customGameName.value = '';
  customCoverUrl.value = '';
};
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="manager-card glass-panel-elevated">
      <!-- Header -->
      <div class="modal-header">
        <div class="header-title-row">
          <div class="header-icon-box">
            <CosmicIcon name="gamepad" size="18" />
          </div>
          <div>
            <h2 class="modal-title">Game Profiles & Community Presets Hub</h2>
            <p class="modal-subtitle">
              Browse pre-configured games, custom artwork covers, and assign layouts to ESP32 Flash memory slots.
            </p>
          </div>
        </div>
        <button class="close-btn" @click="emit('close')">
          <CosmicIcon name="x" size="16" />
        </button>
      </div>

      <!-- Target Hardware Slot Selector -->
      <div class="target-slot-bar glass-panel">
        <div class="slot-bar-label">
          <CosmicIcon name="chip" size="14" class="chip-icon" />
          <span>Assign Layout into Hardware Dongle Slot:</span>
        </div>
        <div class="slot-pills">
          <button
            v-for="s in 4"
            :key="s"
            class="slot-btn"
            :class="{ active: targetSlotSelection === s - 1 }"
            @click="targetSlotSelection = s - 1"
          >
            <span>Slot {{ s }}</span>
            <span class="slot-current-name">({{ profiles[s - 1]?.name || 'Empty' }})</span>
          </button>
        </div>
      </div>

      <!-- Search & Custom Adder Bar -->
      <div class="hub-toolbar">
        <div class="search-box">
          <CosmicIcon name="search" size="14" class="search-icon" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search game presets database..."
            class="search-input"
          />
        </div>

        <!-- Custom Game Quick-Add -->
        <div class="custom-add-group">
          <input
            v-model="customGameName"
            type="text"
            placeholder="Custom Game Title..."
            class="custom-name-input"
          />
          <input
            v-model="customCoverUrl"
            type="text"
            placeholder="Cover URL (optional)..."
            class="custom-url-input"
          />
          <button
            class="btn-cosmic add-btn"
            :disabled="!customGameName.trim()"
            @click="createCustomGame"
          >
            <CosmicIcon name="plus" size="12" />
            <span>Create Profile</span>
          </button>
        </div>
      </div>

      <!-- Presets Gallery Grid -->
      <div class="gallery-scroll-area">
        <div class="presets-grid">
          <div
            v-for="preset in filteredPresets"
            :key="preset.name"
            class="preset-card glass-panel"
          >
            <!-- Game Cover Banner -->
            <div class="cover-image-box">
              <img :src="preset.coverUrl" :alt="preset.name" class="cover-img" />
              <div class="cover-gradient-overlay"></div>
              <span class="genre-badge">{{ preset.genre }}</span>
            </div>

            <!-- Content -->
            <div class="preset-card-body">
              <h3 class="preset-name">{{ preset.name }}</h3>
              <p class="preset-desc">{{ preset.description }}</p>

              <div class="preset-actions">
                <button
                  class="btn-cosmic apply-btn"
                  @click="applyPreset(preset)"
                >
                  <CosmicIcon name="bolt" size="12" />
                  <span>Apply to Slot {{ targetSlotSelection + 1 }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(3, 5, 10, 0.78);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  padding: 24px;
  animation: fadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.manager-card {
  width: 900px;
  max-width: 95vw;
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  padding: 22px;
  border-radius: 20px;
  overflow: hidden;
  gap: 16px;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.header-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon-box {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(56, 189, 248, 0.15);
  border: 1px solid rgba(56, 189, 248, 0.4);
  color: var(--accent-cyan);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 16px rgba(56, 189, 248, 0.25);
}

.modal-title {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}

.modal-subtitle {
  font-size: 11.5px;
  color: var(--text-muted);
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: all 0.2s ease;
}
.close-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

/* Target Slot Selector */
.target-slot-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px;
  border-radius: 12px;
  gap: 12px;
  background: rgba(15, 23, 42, 0.5);
}

.slot-bar-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.chip-icon {
  color: var(--accent-cyan);
}

.slot-pills {
  display: flex;
  gap: 6px;
}

.slot-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  color: var(--text-muted);
  font-family: var(--font-sans);
  font-size: 11.5px;
  font-weight: 600;
  padding: 5px 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.slot-btn.active {
  background: rgba(56, 189, 248, 0.2);
  border-color: var(--accent-cyan);
  color: #fff;
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.25);
}

.slot-current-name {
  font-size: 10px;
  opacity: 0.7;
}

/* Toolbar */
.hub-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 220px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 10px;
  padding: 7px 12px;
}

.search-icon {
  color: var(--text-muted);
}

.search-input {
  background: transparent;
  border: none;
  outline: none;
  color: #fff;
  font-family: var(--font-sans);
  font-size: 12px;
  width: 100%;
}

.custom-add-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.custom-name-input,
.custom-url-input {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 11.5px;
  color: #fff;
  outline: none;
  font-family: var(--font-sans);
}

.custom-name-input {
  width: 140px;
}

.custom-url-input {
  width: 160px;
}

.add-btn {
  padding: 6px 12px;
  font-size: 11.5px;
}

/* Gallery */
.gallery-scroll-area {
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
}

.presets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 14px;
}

.preset-card {
  border-radius: 14px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.preset-card:hover {
  transform: translateY(-2px);
  border-color: rgba(56, 189, 248, 0.45);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6), 0 0 20px rgba(56, 189, 248, 0.2);
}

.cover-image-box {
  position: relative;
  height: 120px;
  overflow: hidden;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.preset-card:hover .cover-img {
  transform: scale(1.06);
}

.cover-gradient-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(12, 18, 36, 0.95) 0%, rgba(12, 18, 36, 0.2) 60%, transparent 100%);
}

.genre-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  font-family: var(--font-mono);
  font-size: 9px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 6px;
  background: rgba(12, 18, 36, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: var(--accent-cyan);
}

.preset-card-body {
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.preset-name {
  font-size: 13.5px;
  font-weight: 700;
  color: #fff;
}

.preset-desc {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.4;
  flex: 1;
}

.preset-actions {
  display: flex;
  margin-top: 4px;
}

.apply-btn {
  width: 100%;
  padding: 7px 10px;
  font-size: 11.5px;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
