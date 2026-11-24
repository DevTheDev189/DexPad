<script setup lang="ts">
import { ref } from 'vue';
import { useTheme, CURATED_ACCENTS, type BackgroundType } from '../composables/useTheme';
import CosmicIcon, { type IconName } from './CosmicIcon.vue';

defineProps<{
  isOpen: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const {
  config,
  systemIsDark,
  setMode,
  setAccentColor,
  setGlassTint,
  setGlassBlur,
  setBackgroundType,
  setCustomImageUrl,
  setCustomVideoUrl,
  resetDefaults,
} = useTheme();

const imageInputRef = ref<HTMLInputElement | null>(null);
const videoInputRef = ref<HTMLInputElement | null>(null);
const isProcessingImage = ref(false);
const isProcessingVideo = ref(false);

const bgOptions: { id: BackgroundType; label: string; desc: string; icon: IconName }[] = [
  { id: 'waves', label: 'Fluid Waves', desc: 'Layered undulating liquid waves with dynamic chromatic tint', icon: 'zap' },
  { id: 'orbs', label: 'Animated Orbs', desc: 'Vibrant luminous spheres drifting smoothly across the screen', icon: 'sparkle' },
  { id: 'shapes', label: 'Animated Shapes', desc: 'Rotating 3D frosted geometric crystals & floating prisms', icon: 'diamond' },
  { id: 'image', label: 'Custom Wallpaper', desc: 'Upload your own high-resolution image (4K/8K supported)', icon: 'image' },
  { id: 'video', label: 'Video Loop', desc: 'Upload or loop an animated MP4 background', icon: 'play' },
];

const handleImageFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];
    isProcessingImage.value = true;
    const reader = new FileReader();
    reader.onload = (loadEvt) => {
      if (loadEvt.target?.result) {
        setCustomImageUrl(loadEvt.target.result as string);
      }
      isProcessingImage.value = false;
    };
    reader.onerror = () => {
      isProcessingImage.value = false;
    };
    reader.readAsDataURL(file);
  }
};

const handleVideoFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];
    isProcessingVideo.value = true;
    const reader = new FileReader();
    reader.onload = (loadEvt) => {
      if (loadEvt.target?.result) {
        setCustomVideoUrl(loadEvt.target.result as string);
      }
      isProcessingVideo.value = false;
    };
    reader.onerror = () => {
      isProcessingVideo.value = false;
    };
    reader.readAsDataURL(file);
  }
};
</script>

<template>
  <div v-if="isOpen" class="modal-backdrop" @click="emit('close')">
    <div class="modal-card glass-panel-elevated" @click.stop>
      <!-- Modal Header -->
      <header class="modal-header">
        <div class="modal-title-group">
          <div class="title-glyph" :style="{ backgroundColor: config.accentColor }">
            <CosmicIcon name="brush" size="18" />
          </div>
          <div>
            <h2 class="modal-title">Style</h2>
            <p class="modal-subtitle">Theme mode, glassmorphism, accent glow, and custom backgrounds</p>
          </div>
        </div>
        <button class="close-btn glass-btn" @click="emit('close')">
          <CosmicIcon name="close" size="14" />
        </button>
      </header>

      <!-- Scrollable Settings Body -->
      <div class="modal-body custom-scroll">
        <!-- 1. Theme Base Mode Selection -->
        <section class="settings-section">
          <h4 class="section-title">Theme Mode (OS Auto-Detection)</h4>
          <p class="section-desc">
            Automatically follow system appearance or pin to clean white or obsidian dark glass.
          </p>

          <div class="segmented-control">
            <button
              class="segment-btn"
              :class="{ active: config.mode === 'auto' }"
              @click="setMode('auto')"
            >
              <CosmicIcon name="monitor" size="14" />
              <span>Auto (System: {{ systemIsDark ? 'Dark' : 'Light' }})</span>
            </button>
            <button
              class="segment-btn"
              :class="{ active: config.mode === 'light' }"
              @click="setMode('light')"
            >
              <CosmicIcon name="sun" size="14" />
              <span>Light (Pure White Glass)</span>
            </button>
            <button
              class="segment-btn"
              :class="{ active: config.mode === 'dark' }"
              @click="setMode('dark')"
            >
              <CosmicIcon name="moon" size="14" />
              <span>Dark (Obsidian Glass)</span>
            </button>
          </div>
        </section>

        <!-- 2. Accent Color Palette -->
        <section class="settings-section">
          <h4 class="section-title">Accent Color & Glowing Rim</h4>
          <p class="section-desc">
            Tints the glass borders, button halo highlights, DualSense lightbar, and telemetry pulses.
          </p>

          <div class="palette-grid">
            <div
              v-for="swatch in CURATED_ACCENTS"
              :key="swatch.hex"
              class="swatch-item"
              :class="{ active: config.accentColor.toLowerCase() === swatch.hex.toLowerCase() }"
              @click="setAccentColor(swatch.hex)"
            >
              <span class="swatch-circle" :style="{ backgroundColor: swatch.hex }"></span>
              <div class="swatch-meta">
                <span class="swatch-name">{{ swatch.name }}</span>
                <span class="swatch-hex">{{ swatch.hex }}</span>
              </div>
            </div>

            <!-- Custom Hex Picker Card -->
            <div class="swatch-item custom-picker-item">
              <input
                type="color"
                :value="config.accentColor"
                class="native-color-picker"
                @input="setAccentColor(($event.target as HTMLInputElement).value)"
              />
              <div class="swatch-meta">
                <span class="swatch-name">Custom Hex</span>
                <span class="swatch-hex">{{ config.accentColor }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- 3. Glassmorphism Fine Tuning -->
        <section class="settings-section">
          <h4 class="section-title">Glassmorphism Intensity</h4>
          <p class="section-desc">
            Adjust the frosting depth and translucent tint of all application panels.
          </p>

          <div class="slider-group">
            <div class="slider-row">
              <div class="slider-label">
                <span>Glass Tint Opacity</span>
                <span class="slider-val">{{ Math.round(config.glassTint * 100) }}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="0.45"
                step="0.02"
                :value="config.glassTint"
                class="glass-slider"
                @input="setGlassTint(parseFloat(($event.target as HTMLInputElement).value))"
              />
            </div>

            <div class="slider-row">
              <div class="slider-label">
                <span>Frosting Blur Depth</span>
                <span class="slider-val">{{ config.glassBlur }}px</span>
              </div>
              <input
                type="range"
                min="12"
                max="48"
                step="2"
                :value="config.glassBlur"
                class="glass-slider"
                @input="setGlassBlur(parseInt(($event.target as HTMLInputElement).value))"
              />
            </div>
          </div>
        </section>

        <!-- 4. Background Engine Selection -->
        <section class="settings-section">
          <h4 class="section-title">Background Engine</h4>
          <p class="section-desc">
            Select a live procedural animation, photo atmosphere, or upload custom media.
          </p>

          <div class="bg-options-grid">
            <div
              v-for="bg in bgOptions"
              :key="bg.id"
              class="bg-card"
              :class="{ active: config.backgroundType === bg.id }"
              @click="setBackgroundType(bg.id)"
            >
              <div class="bg-card-icon" :style="{ color: config.backgroundType === bg.id ? config.accentColor : undefined }">
                <CosmicIcon :name="bg.icon" size="20" />
              </div>
              <div class="bg-card-text">
                <span class="bg-card-title">{{ bg.label }}</span>
                <span class="bg-card-desc">{{ bg.desc }}</span>
              </div>
            </div>
          </div>

          <!-- Upload Controls for Image / Video -->
          <div v-if="config.backgroundType === 'image'" class="media-uploader-box">
            <div class="uploader-header">
              <span class="uploader-title">Custom Wallpaper Image</span>
              <button class="glass-btn" :disabled="isProcessingImage" @click="imageInputRef?.click()">
                <CosmicIcon name="upload" size="14" />
                <span>{{ isProcessingImage ? 'Loading 4K Image...' : 'Choose Image (PNG, JPG, WebP)' }}</span>
              </button>
              <input
                ref="imageInputRef"
                type="file"
                accept="image/*"
                style="display: none"
                @change="handleImageFileChange"
              />
            </div>
            <div v-if="config.customImageUrl" class="media-preview-container">
              <img :src="config.customImageUrl" alt="Wallpaper Preview" class="media-thumb" />
              <button class="glass-btn remove-btn" @click="setCustomImageUrl('')">Clear Image</button>
            </div>
          </div>

          <div v-if="config.backgroundType === 'video'" class="media-uploader-box">
            <div class="uploader-header">
              <span class="uploader-title">Custom Video Loop (MP4)</span>
              <button class="glass-btn" :disabled="isProcessingVideo" @click="videoInputRef?.click()">
                <CosmicIcon name="upload" size="14" />
                <span>{{ isProcessingVideo ? 'Loading Video...' : 'Choose Video (MP4, WebM)' }}</span>
              </button>
              <input
                ref="videoInputRef"
                type="file"
                accept="video/*"
                style="display: none"
                @change="handleVideoFileChange"
              />
            </div>
            <div v-if="config.customVideoUrl" class="media-preview-container">
              <video :src="config.customVideoUrl" autoplay loop muted class="media-thumb"></video>
              <button class="glass-btn remove-btn" @click="setCustomVideoUrl('')">Clear Video</button>
            </div>
          </div>
        </section>
      </div>

      <!-- Modal Footer -->
      <footer class="modal-footer">
        <button class="glass-btn" @click="resetDefaults">
          <CosmicIcon name="refresh" size="12" />
          <span>Reset Defaults</span>
        </button>
        <button class="glass-btn-primary" @click="emit('close')">
          Done
        </button>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(3, 7, 18, 0.35);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 24px;
}

.modal-card {
  width: 100%;
  max-width: 680px;
  max-height: 86vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 24px;
  background-color: var(--glass-surface-elevated);
  background-image: linear-gradient(
    135deg,
    rgba(var(--accent-custom-rgb, 125, 211, 252), calc(var(--glass-tint-val, 0.14) * 0.45)) 0%,
    transparent 80%
  );
  backdrop-filter: blur(var(--glass-blur-val, 28px)) saturate(190%);
  -webkit-backdrop-filter: blur(var(--glass-blur-val, 28px)) saturate(190%);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-glass-elevated);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 28px;
  border-bottom: 1px solid var(--glass-border-subtle);
}

.modal-title-group {
  display: flex;
  align-items: center;
  gap: 14px;
}

.title-glyph {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-on-accent);
  box-shadow: 0 4px 14px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.4);
}

.modal-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
}

.modal-subtitle {
  font-size: 12px;
  color: var(--text-muted);
}

.close-btn {
  width: 34px;
  height: 34px;
  padding: 0;
  border-radius: 50%;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px 28px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

/* Settings Sections */
.settings-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.section-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 6px;
}

/* Segmented Control */
.segmented-control {
  display: flex;
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border-subtle);
  border-radius: 12px;
  padding: 4px;
  gap: 4px;
}

.segment-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 9px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.segment-btn:hover {
  color: var(--text-primary);
}

.segment-btn.active {
  background: var(--glass-surface-elevated);
  border: 1px solid var(--glass-border);
  color: var(--accent-custom);
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

/* Palette Grid */
.palette-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 10px;
}

.swatch-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 12px;
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border-subtle);
  cursor: pointer;
  transition: all 0.2s ease;
}

.swatch-item:hover {
  border-color: var(--glass-border);
  transform: translateY(-1px);
}

.swatch-item.active {
  background: var(--glass-surface-elevated);
  border-color: var(--accent-custom);
  box-shadow: 0 0 14px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.35);
}

.swatch-circle {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.swatch-meta {
  display: flex;
  flex-direction: column;
}

.swatch-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.swatch-hex {
  font-size: 10.5px;
  font-family: var(--font-mono);
  color: var(--text-muted);
}

.custom-picker-item {
  position: relative;
}

.native-color-picker {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  background: none;
}

/* Sliders */
.slider-group {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.slider-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.slider-label {
  display: flex;
  justify-content: space-between;
  font-size: 12.5px;
  color: var(--text-secondary);
}

.slider-val {
  font-family: var(--font-mono);
  font-weight: 600;
  color: var(--accent-custom);
}

.glass-slider {
  width: 100%;
  accent-color: var(--accent-custom);
  height: 6px;
  border-radius: 3px;
  cursor: pointer;
}

/* Background Options Grid */
.bg-options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}

.bg-card {
  display: flex;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border-subtle);
  cursor: pointer;
  transition: all 0.2s ease;
}

.bg-card:hover {
  border-color: var(--glass-border);
  transform: translateY(-1px);
}

.bg-card.active {
  background: var(--glass-surface-elevated);
  border-color: var(--accent-custom);
  box-shadow: 0 0 16px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.35);
}

.bg-card-icon {
  margin-top: 2px;
}

.bg-card-text {
  display: flex;
  flex-direction: column;
}

.bg-card-title {
  font-size: 12.5px;
  font-weight: 700;
  color: var(--text-primary);
}

.bg-card-desc {
  font-size: 10.5px;
  color: var(--text-muted);
  line-height: 1.3;
}

/* Media Uploader */
.media-uploader-box {
  margin-top: 10px;
  padding: 16px;
  border-radius: 14px;
  background: var(--glass-surface-pill);
  border: 1px dashed var(--glass-border);
}

.uploader-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.uploader-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.media-preview-container {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 14px;
}

.media-thumb {
  width: 140px;
  height: 80px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid var(--glass-border);
}

.remove-btn {
  color: #ef4444;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 28px;
  border-top: 1px solid var(--glass-border-subtle);
}
</style>
