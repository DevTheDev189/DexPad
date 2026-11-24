import { ref, computed, watch } from 'vue';
import {
  saveMediaItem,
  getMediaItem,
  deleteMediaItem,
  MEDIA_KEY_THEME_IMAGE,
  MEDIA_KEY_THEME_VIDEO,
} from '../utils/mediaStorage';

export type ThemeMode = 'auto' | 'light' | 'dark';
export type BackgroundType = 'waves' | 'orbs' | 'shapes' | 'image' | 'video';

export interface ThemeConfig {
  mode: ThemeMode;
  accentColor: string;
  glassTint: number;
  glassBlur: number;
  backgroundType: BackgroundType;
  customImageUrl: string;
  customVideoUrl: string;
}

const STORAGE_KEY = 'controller_bridge_theme_config_v1';

export const CURATED_ACCENTS = [
  { name: 'Pastel Ice Blue', hex: '#7dd3fc', desc: 'Frosted pastel cyan with glowing specular highlights' },
  { name: 'Sky Cerulean', hex: '#0ea5e9', desc: 'Vibrant daytime sky' },
  { name: 'Electric Cyan', hex: '#06b6d4', desc: 'High-contrast glowing cyan' },
  { name: 'Ultraviolet', hex: '#a855f7', desc: 'Cosmic deep purple' },
  { name: 'Blossom Pink', hex: '#f472b6', desc: 'Pastel neon pink' },
  { name: 'Emerald Mint', hex: '#10b981', desc: 'Crisp vibrant green' },
  { name: 'Amber Gold', hex: '#f59e0b', desc: 'Warm golden glow' },
  { name: 'Crimson Rose', hex: '#f43f5e', desc: 'Striking ruby red' },
  { name: 'Obsidian Slate', hex: '#94a3b8', desc: 'Subtle titanium monochrome' },
];

const DEFAULT_CONFIG: ThemeConfig = {
  mode: 'auto',
  accentColor: '#7dd3fc',
  glassTint: 0.14,
  glassBlur: 28,
  backgroundType: 'waves',
  customImageUrl: '',
  customVideoUrl: '',
};

function hexToRgb(hex: string): string {
  try {
    const clean = hex.replace('#', '').trim();
    if (clean.length === 3) {
      const r = parseInt(clean[0] + clean[0], 16) || 125;
      const g = parseInt(clean[1] + clean[1], 16) || 211;
      const b = parseInt(clean[2] + clean[2], 16) || 252;
      return `${r}, ${g}, ${b}`;
    }
    if (clean.length >= 6) {
      const r = parseInt(clean.substring(0, 2), 16) || 125;
      const g = parseInt(clean.substring(2, 4), 16) || 211;
      const b = parseInt(clean.substring(4, 6), 16) || 252;
      return `${r}, ${g}, ${b}`;
    }
  } catch {
    // fallback
  }
  return '125, 211, 252';
}

function getContrastTextColor(hex: string): string {
  try {
    const clean = hex.replace('#', '').trim();
    let r = 125, g = 211, b = 252;
    if (clean.length === 3) {
      r = parseInt(clean[0] + clean[0], 16) || 125;
      g = parseInt(clean[1] + clean[1], 16) || 211;
      b = parseInt(clean[2] + clean[2], 16) || 252;
    } else if (clean.length >= 6) {
      r = parseInt(clean.substring(0, 2), 16) || 125;
      g = parseInt(clean.substring(2, 4), 16) || 211;
      b = parseInt(clean.substring(4, 6), 16) || 252;
    }
    const yiq = (r * 299 + g * 587 + b * 114) / 1000;
    return yiq >= 165 ? '#0b1120' : '#ffffff';
  } catch {
    return '#ffffff';
  }
}

function loadInitialConfig(): ThemeConfig {
  if (typeof window === 'undefined') return { ...DEFAULT_CONFIG };
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      // Migrate legacy background types: remove sky/cosmic stock wallpapers
      if (parsed.backgroundType === 'sky' || parsed.backgroundType === 'cosmic') {
        parsed.backgroundType = 'waves';
      } else if (parsed.backgroundType === 'abstract') {
        parsed.backgroundType = 'shapes';
      }
      if (parsed.customImageUrl === '__indexeddb__') {
        parsed.customImageUrl = '';
      }
      if (parsed.customVideoUrl === '__indexeddb__') {
        parsed.customVideoUrl = '';
      }
      return { ...DEFAULT_CONFIG, ...parsed };
    }
  } catch (err) {
    console.warn('Failed to parse saved theme config:', err);
  }
  return { ...DEFAULT_CONFIG };
}

// Global reactive state shared across all components
const config = ref<ThemeConfig>(loadInitialConfig());
const systemIsDark = ref(false);

// Asynchronously hydrate 4K/8K media from IndexedDB (no file size quota)
async function initMediaStorage() {
  if (typeof window === 'undefined') return;
  try {
    const savedImage = await getMediaItem(MEDIA_KEY_THEME_IMAGE);
    if (savedImage) {
      config.value.customImageUrl = savedImage;
    } else if (config.value.customImageUrl && config.value.customImageUrl !== '__indexeddb__') {
      await saveMediaItem(MEDIA_KEY_THEME_IMAGE, config.value.customImageUrl);
    }

    const savedVideo = await getMediaItem(MEDIA_KEY_THEME_VIDEO);
    if (savedVideo) {
      config.value.customVideoUrl = savedVideo;
    } else if (config.value.customVideoUrl && config.value.customVideoUrl !== '__indexeddb__') {
      await saveMediaItem(MEDIA_KEY_THEME_VIDEO, config.value.customVideoUrl);
    }
  } catch (err) {
    console.warn('[useTheme] Error initializing media storage:', err);
  }
}

initMediaStorage();

if (typeof window !== 'undefined') {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  systemIsDark.value = mediaQuery.matches;

  mediaQuery.addEventListener('change', (e) => {
    systemIsDark.value = e.matches;
    applyThemeToDOM();
  });
}

const effectiveTheme = computed<'light' | 'dark'>(() => {
  if (config.value.mode === 'auto') {
    return systemIsDark.value ? 'dark' : 'light';
  }
  return config.value.mode;
});

function applyThemeToDOM() {
  if (typeof document === 'undefined') return;

  const root = document.documentElement;
  const theme = effectiveTheme.value;

  // Toggle class names on root
  root.classList.remove('theme-light', 'theme-dark');
  root.classList.add(`theme-${theme}`);

  // Dynamic CSS variables
  const rgb = hexToRgb(config.value.accentColor);
  root.style.setProperty('--accent-custom', config.value.accentColor);
  root.style.setProperty('--accent-custom-rgb', rgb);
  root.style.setProperty('--text-on-accent', getContrastTextColor(config.value.accentColor));
  root.style.setProperty('--glass-tint-val', config.value.glassTint.toString());
  root.style.setProperty('--glass-blur-val', `${config.value.glassBlur}px`);
}

// Save & apply on every modification
watch(
  config,
  (newVal) => {
    if (typeof window !== 'undefined') {
      // 1. Persist large media to IndexedDB with zero file size limits
      if (newVal.customImageUrl && newVal.customImageUrl !== '__indexeddb__') {
        saveMediaItem(MEDIA_KEY_THEME_IMAGE, newVal.customImageUrl);
      } else if (!newVal.customImageUrl) {
        deleteMediaItem(MEDIA_KEY_THEME_IMAGE);
      }

      if (newVal.customVideoUrl && newVal.customVideoUrl !== '__indexeddb__') {
        saveMediaItem(MEDIA_KEY_THEME_VIDEO, newVal.customVideoUrl);
      } else if (!newVal.customVideoUrl) {
        deleteMediaItem(MEDIA_KEY_THEME_VIDEO);
      }

      // 2. Persist clean theme metadata to localStorage without payload
      try {
        const cleanConfig = {
          ...newVal,
          customImageUrl: newVal.customImageUrl ? '__indexeddb__' : '',
          customVideoUrl: newVal.customVideoUrl ? '__indexeddb__' : '',
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(cleanConfig));
      } catch (err) {
        console.warn('Could not save theme config to localStorage:', err);
      }
    }
    applyThemeToDOM();
  },
  { deep: true, immediate: true }
);

watch(effectiveTheme, () => {
  applyThemeToDOM();
});

export function useTheme() {
  const setMode = (mode: ThemeMode) => {
    config.value.mode = mode;
  };

  const setAccentColor = (hex: string) => {
    config.value.accentColor = hex;
  };

  const setGlassTint = (val: number) => {
    config.value.glassTint = Math.max(0, Math.min(0.5, val));
  };

  const setGlassBlur = (val: number) => {
    config.value.glassBlur = Math.max(8, Math.min(60, val));
  };

  const setBackgroundType = (type: BackgroundType) => {
    config.value.backgroundType = type;
  };

  const setCustomImageUrl = (url: string) => {
    config.value.customImageUrl = url;
    config.value.backgroundType = 'image';
    if (url) {
      saveMediaItem(MEDIA_KEY_THEME_IMAGE, url);
    } else {
      deleteMediaItem(MEDIA_KEY_THEME_IMAGE);
    }
  };

  const setCustomVideoUrl = (url: string) => {
    config.value.customVideoUrl = url;
    config.value.backgroundType = 'video';
    if (url) {
      saveMediaItem(MEDIA_KEY_THEME_VIDEO, url);
    } else {
      deleteMediaItem(MEDIA_KEY_THEME_VIDEO);
    }
  };

  const applyGlassPreset = () => {
    deleteMediaItem(MEDIA_KEY_THEME_IMAGE);
    deleteMediaItem(MEDIA_KEY_THEME_VIDEO);
    config.value = {
      mode: 'dark',
      accentColor: '#7dd3fc',
      glassTint: 0.16,
      glassBlur: 28,
      backgroundType: 'waves',
      customImageUrl: '',
      customVideoUrl: '',
    };
  };

  const resetDefaults = () => {
    deleteMediaItem(MEDIA_KEY_THEME_IMAGE);
    deleteMediaItem(MEDIA_KEY_THEME_VIDEO);
    config.value = { ...DEFAULT_CONFIG };
  };

  return {
    config,
    effectiveTheme,
    systemIsDark,
    setMode,
    setAccentColor,
    setGlassTint,
    setGlassBlur,
    setBackgroundType,
    setCustomImageUrl,
    setCustomVideoUrl,
    applyGlassPreset,
    resetDefaults,
    applyThemeToDOM,
  };
}
