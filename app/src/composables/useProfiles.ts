import { ref, computed, watch } from 'vue';
import type { Profile, ControllerControlId, ButtonBinding, StickConfig } from '../types/keymap';
import { cacheGameCover, getCachedGameCover } from '../utils/coverCache';

const STORAGE_KEY = 'dexpad_profiles_v1';
const ACTIVE_SLOT_KEY = 'dexpad_active_slot_v1';

const INITIAL_PROFILES: Profile[] = [
  // 0: Minecraft
  {
    slot: 0,
    name: 'Minecraft',
    gameTitle: 'Minecraft',
    coverUrl: 'https://media.rawg.io/media/games/b4e/b4e4c73d5aa4ec66bbf75375c4847a2b.jpg',
    genre: 'Sandbox / Survival',
    description: 'WASD walking, mouse camera, space jump, shift sneak, Q drop item, E inventory.',
    sticks: {
      left: {
        mode: 'digital_keys',
        deadzone: 180,
        up: 'w',
        down: 's',
        left: 'a',
        right: 'd',
      },
      right: {
        mode: 'mouse',
        deadzone: 45,
        sensitivity: 1.35,
        curve: 'exponential',
        invert_y: false,
      },
    },
    buttons: {
      a: { type: 'key', code: 'KEY_SPACE' },
      b: { type: 'key', code: 'KEY_LEFT_SHIFT' },
      x: { type: 'key', code: 'q' },
      y: { type: 'key', code: 'e' },
      l1: { type: 'mouse_scroll', delta: 1, repeat_ms: 120 },
      r1: { type: 'mouse_scroll', delta: -1, repeat_ms: 120 },
      l4: { type: 'key', code: 'KEY_LEFT_CTRL' },
      r4: { type: 'key', code: 'KEY_SPACE' },
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
  // 1: Cyberpunk 2077
  {
    slot: 1,
    name: 'Cyberpunk 2077',
    gameTitle: 'Cyberpunk 2077',
    coverUrl: 'https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1091500/library_600x900.jpg',
    genre: 'Action RPG / Sci-Fi',
    description: 'WASD movement, responsive camera, Space jump, C crouch, R reload, F interact, L4 Gyro Aim.',
    sticks: {
      left: {
        mode: 'digital_keys',
        deadzone: 160,
        up: 'w',
        down: 's',
        left: 'a',
        right: 'd',
      },
      right: {
        mode: 'mouse',
        deadzone: 40,
        sensitivity: 1.5,
        curve: 'linear',
        invert_y: false,
      },
    },
    buttons: {
      a: { type: 'key', code: 'KEY_SPACE' },
      b: { type: 'key', code: 'c' },
      x: { type: 'key', code: 'r' },
      y: { type: 'key', code: 'f' },
      l1: { type: 'key', code: 'g' },
      r1: { type: 'key', code: 'KEY_LEFT_CONTROL' },
      l4: { type: 'gyro_aim', gyro_axis: 'pitch_yaw', gyro_sensitivity: 1.2 },
      r4: { type: 'key', code: 'KEY_LEFT_SHIFT' },
      l2: { type: 'mouse_button', code: 'MOUSE_RIGHT', threshold: 40 },
      r2: { type: 'mouse_button', code: 'MOUSE_LEFT', threshold: 40 },
      l3: { type: 'key', code: 'KEY_LEFT_SHIFT' },
      r3: { type: 'key', code: 'v' },
    },
  },
  // 2: Hollow Knight
  {
    slot: 2,
    name: 'Hollow Knight',
    gameTitle: 'Hollow Knight',
    coverUrl: 'https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/367520/library_600x900.jpg',
    genre: 'Metroidvania',
    description: 'Arrow key movement, Z jump, X slash, A cast/heal, C dash.',
    sticks: {
      left: {
        mode: 'digital_keys',
        deadzone: 150,
        up: 'KEY_UP_ARROW',
        down: 'KEY_DOWN_ARROW',
        left: 'KEY_LEFT_ARROW',
        right: 'KEY_RIGHT_ARROW',
      },
      right: {
        mode: 'none',
        deadzone: 45,
        sensitivity: 1.0,
      },
    },
    buttons: {
      a: { type: 'key', code: 'z' },
      x: { type: 'key', code: 'x' },
      y: { type: 'key', code: 'a' },
      b: { type: 'key', code: 'c' },
      l1: { type: 'key', code: 'KEY_TAB' },
      r1: { type: 'key', code: 's' },
      l4: { type: 'key', code: 'c' },
      r4: { type: 'key', code: 'a' },
      l2: { type: 'key', code: 'a', threshold: 40 },
      r2: { type: 'key', code: 'KEY_LEFT_SHIFT', threshold: 40 },
      menu: { type: 'key', code: 'KEY_ESC' },
      home: { type: 'key', code: 'KEY_TAB' },
    },
  },
  // 3: Desktop Mouse
  {
    slot: 3,
    name: 'Desktop Mouse',
    gameTitle: 'Desktop Utility',
    coverUrl: 'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=600&auto=format&fit=crop&q=80',
    genre: 'Productivity',
    description: 'Silky smooth cursor control, left/right clicks, wheel scrolling, volume and media controls.',
    sticks: {
      left: {
        mode: 'none',
        deadzone: 100,
      },
      right: {
        mode: 'mouse',
        deadzone: 30,
        sensitivity: 1.6,
        curve: 'exponential',
        invert_y: false,
      },
    },
    buttons: {
      a: { type: 'mouse_button', code: 'MOUSE_LEFT' },
      b: { type: 'mouse_button', code: 'MOUSE_RIGHT' },
      x: { type: 'mouse_button', code: 'MOUSE_MIDDLE' },
      y: { type: 'consumer_control', code: 'MEDIA_PLAY_PAUSE' },
      l1: { type: 'mouse_scroll', delta: 1, repeat_ms: 100 },
      r1: { type: 'mouse_scroll', delta: -1, repeat_ms: 100 },
      l4: { type: 'consumer_control', code: 'MEDIA_VOLUME_DOWN' },
      r4: { type: 'consumer_control', code: 'MEDIA_VOLUME_UP' },
      l2: { type: 'consumer_control', code: 'MEDIA_PREV_TRACK' },
      r2: { type: 'consumer_control', code: 'MEDIA_NEXT_TRACK' },
      home: { type: 'key', code: 'KEY_LEFT_GUI' },
    },
  },
];

function loadSavedProfiles(): Profile[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length > 0) {
        // Hydrate any cached covers & migrate broken legacy links
        return parsed.map((p: Profile, i: number) => {
          let cover = p.coverUrl;
          if (!cover || cover.includes('wikimedia.org')) {
            const defaultGame = INITIAL_PROFILES.find((init) => init.name.toLowerCase() === p.name.toLowerCase());
            if (defaultGame) {
              cover = defaultGame.coverUrl;
            } else if (p.name.toLowerCase().includes('minecraft')) {
              cover = 'https://media.rawg.io/media/games/b4e/b4e4c73d5aa4ec66bbf75375c4847a2b.jpg';
            }
          }
          return {
            ...p,
            slot: i,
            coverUrl: getCachedGameCover(p.name, cover),
          };
        });
      }
    }
  } catch (e) {
    console.warn('Failed to load profiles from disk:', e);
  }
  return JSON.parse(JSON.stringify(INITIAL_PROFILES));
}

function loadSavedActiveSlot(): number {
  try {
    const raw = localStorage.getItem(ACTIVE_SLOT_KEY);
    if (raw !== null) {
      const num = parseInt(raw, 10);
      if (!isNaN(num) && num >= 0) return num;
    }
  } catch {
    // fallback
  }
  return 0;
}

export function useProfiles() {
  const profiles = ref<Profile[]>(loadSavedProfiles());
  const activeSlot = ref(loadSavedActiveSlot());
  const selectedControl = ref<ControllerControlId | null>('a');
  const hoveredControl = ref<ControllerControlId | null>(null);
  const isDirty = ref(false);

  // Keep active slot safely within bounds
  if (activeSlot.value >= profiles.value.length) {
    activeSlot.value = 0;
  }

  // Persistent disk sync
  watch(
    profiles,
    (updated) => {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      } catch (e) {
        console.warn('Failed to save profiles to disk:', e);
      }
    },
    { deep: true }
  );

  watch(activeSlot, (newSlot) => {
    try {
      localStorage.setItem(ACTIVE_SLOT_KEY, String(newSlot));
    } catch (e) {
      console.warn('Failed to save active slot to disk:', e);
    }
  });

  const activeProfile = computed<Profile>(() => {
    return profiles.value[activeSlot.value] || profiles.value[0];
  });

  const selectSlot = (slot: number) => {
    if (slot >= 0 && slot < profiles.value.length) {
      activeSlot.value = slot;
    }
  };

  const addGameProfile = (entry: {
    name: string;
    gameTitle?: string;
    coverUrl?: string;
    genre?: string;
    description?: string;
    defaultProfile?: Partial<Profile>;
  }): number => {
    // Check if game is already in library
    const existingIndex = profiles.value.findIndex(
      (p) => p.name.toLowerCase() === entry.name.toLowerCase() ||
             (entry.gameTitle && p.gameTitle?.toLowerCase() === entry.gameTitle.toLowerCase())
    );

    if (existingIndex !== -1) {
      // Game already in library, just select it!
      activeSlot.value = existingIndex;
      return existingIndex;
    }

    const newSlot = profiles.value.length;
    let newProfile: Profile;

    if (entry.defaultProfile && entry.defaultProfile.buttons && entry.defaultProfile.sticks) {
      // Use pre-configured layout
      newProfile = {
        slot: newSlot,
        name: entry.name,
        gameTitle: entry.gameTitle || entry.name,
        coverUrl: entry.coverUrl,
        genre: entry.genre || 'Action',
        description: entry.description || '',
        sticks: JSON.parse(JSON.stringify(entry.defaultProfile.sticks)),
        buttons: JSON.parse(JSON.stringify(entry.defaultProfile.buttons)),
      };
    } else {
      // Blank mapping by default as requested
      newProfile = {
        slot: newSlot,
        name: entry.name,
        gameTitle: entry.gameTitle || entry.name,
        coverUrl: entry.coverUrl,
        genre: entry.genre || 'General',
        description: entry.description || 'Blank controller mapping ready for custom configuration.',
        sticks: {
          left: { mode: 'none', deadzone: 100 },
          right: { mode: 'none', deadzone: 100 },
        },
        buttons: {},
      };
    }

    profiles.value.push(newProfile);
    activeSlot.value = newSlot;
    isDirty.value = true;

    // Cache cover image to disk asynchronously
    if (entry.coverUrl) {
      cacheGameCover(entry.name, entry.coverUrl).then((cached) => {
        newProfile.coverUrl = cached;
      });
    }

    return newSlot;
  };

  const removeProfile = (slot: number) => {
    if (profiles.value.length <= 1) return; // keep at least 1
    profiles.value.splice(slot, 1);
    profiles.value.forEach((p, idx) => {
      p.slot = idx;
    });
    if (activeSlot.value >= profiles.value.length) {
      activeSlot.value = profiles.value.length - 1;
    }
    isDirty.value = true;
  };

  const renameProfile = (slot: number, name: string) => {
    if (profiles.value[slot]) {
      profiles.value[slot].name = name;
      isDirty.value = true;
    }
  };

  const setProfileInSlot = (slot: number, profile: Profile) => {
    profiles.value[slot] = {
      ...profile,
      slot,
    };
    isDirty.value = true;
  };

  const updateButtonBinding = (controlId: string, binding: ButtonBinding) => {
    if (!activeProfile.value.buttons) {
      activeProfile.value.buttons = {};
    }
    activeProfile.value.buttons[controlId] = { ...binding };
    isDirty.value = true;
  };

  const updateStickConfig = (stick: 'left' | 'right', config: StickConfig) => {
    activeProfile.value.sticks[stick] = { ...config };
    isDirty.value = true;
  };

  const markClean = () => {
    isDirty.value = false;
  };

  const exportCurrentProfileJson = (): string => {
    return JSON.stringify(activeProfile.value, null, 2);
  };

  const importProfileJson = (jsonStr: string): boolean => {
    try {
      const parsed = JSON.parse(jsonStr);
      if (parsed && typeof parsed.name === 'string' && parsed.sticks && parsed.buttons) {
        profiles.value[activeSlot.value] = {
          ...parsed,
          slot: activeSlot.value,
        };
        isDirty.value = true;
        return true;
      }
      return false;
    } catch {
      return false;
    }
  };

  return {
    profiles,
    activeSlot,
    activeProfile,
    selectedControl,
    hoveredControl,
    isDirty,
    selectSlot,
    addGameProfile,
    removeProfile,
    renameProfile,
    setProfileInSlot,
    updateButtonBinding,
    updateStickConfig,
    markClean,
    exportCurrentProfileJson,
    importProfileJson,
  };
}
