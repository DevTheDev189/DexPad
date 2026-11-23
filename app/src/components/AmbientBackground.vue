<script setup lang="ts">
import { useTheme } from '../composables/useTheme';

const { config, effectiveTheme } = useTheme();
</script>

<template>
  <div class="ambient-canvas-root" :class="[`bg-${config.backgroundType}`, `theme-${effectiveTheme}`]" aria-hidden="true">
    <!-- ====================================================================
         1. Animated Glowing Orbs Engine (Active Dynamic Orbital Movement)
         ==================================================================== -->
    <div v-if="config.backgroundType === 'orbs'" class="engine-layer orbs-engine">
      <div class="orb orb-1" :style="{ backgroundColor: config.accentColor }"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3" :style="{ borderColor: config.accentColor }"></div>
      <div class="orb orb-4"></div>
      <div class="orb orb-5" :style="{ backgroundColor: config.accentColor }"></div>
      <div class="orb orb-6"></div>
      <div class="orb orb-center-glow" :style="{ backgroundColor: config.accentColor }"></div>
    </div>

    <!-- ====================================================================
         2. Animated Fluid Waves Engine (Full-Screen Continuous Liquid Flow)
         ==================================================================== -->
    <div v-else-if="config.backgroundType === 'waves'" class="engine-layer waves-engine">
      <!-- Ambient Backing Glow Orbs to illuminate waves from behind -->
      <div class="wave-ambient-glow glow-1" :style="{ backgroundColor: config.accentColor }"></div>
      <div class="wave-ambient-glow glow-2"></div>
      <div class="wave-ambient-glow glow-3" :style="{ borderColor: config.accentColor }"></div>

      <!-- Top Fluid Wave Ribbon -->
      <svg class="wave-svg wave-top" viewBox="0 0 2880 500" preserveAspectRatio="none">
        <defs>
          <linearGradient id="waveGradTop" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="rgba(var(--accent-custom-rgb, 125, 211, 252), 0.35)" />
            <stop offset="45%" stop-color="rgba(99, 102, 241, 0.22)" />
            <stop offset="100%" stop-color="rgba(6, 182, 212, 0.12)" />
          </linearGradient>
        </defs>
        <path
          fill="url(#waveGradTop)"
          d="M0,0 L2880,0 L2880,180 C2400,280 2160,100 1920,200 C1680,300 1440,120 1200,220 C960,320 720,110 480,210 C240,310 120,130 0,230 Z"
        ></path>
      </svg>

      <!-- Mid Screen Flowing Wave Ribbon -->
      <svg class="wave-svg wave-mid" viewBox="0 0 2880 500" preserveAspectRatio="none">
        <defs>
          <linearGradient id="waveGradMid" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="rgba(6, 182, 212, 0.28)" />
            <stop offset="50%" stop-color="rgba(var(--accent-custom-rgb, 125, 211, 252), 0.32)" />
            <stop offset="100%" stop-color="rgba(99, 102, 241, 0.18)" />
          </linearGradient>
        </defs>
        <path
          fill="url(#waveGradMid)"
          d="M0,160 C360,300 720,90 1080,220 C1440,350 1800,110 2160,250 C2520,380 2700,160 2880,260 L2880,500 L0,500 Z"
        ></path>
      </svg>

      <!-- Bottom Crest Wave 1 -->
      <svg class="wave-svg wave-bottom-1" viewBox="0 0 2880 440" preserveAspectRatio="none">
        <defs>
          <linearGradient id="waveGradBtm1" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="rgba(var(--accent-custom-rgb, 125, 211, 252), 0.38)" />
            <stop offset="60%" stop-color="rgba(6, 182, 212, 0.24)" />
            <stop offset="100%" stop-color="rgba(var(--accent-custom-rgb, 125, 211, 252), 0.10)" />
          </linearGradient>
        </defs>
        <path
          fill="url(#waveGradBtm1)"
          d="M0,210 C320,330 640,130 960,250 C1280,370 1600,150 1920,280 C2240,400 2560,160 2880,270 L2880,440 L0,440 Z"
        ></path>
      </svg>

      <!-- Bottom Crest Wave 2 -->
      <svg class="wave-svg wave-bottom-2" viewBox="0 0 2880 400" preserveAspectRatio="none">
        <defs>
          <linearGradient id="waveGradBtm2" x1="100%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stop-color="rgba(99, 102, 241, 0.34)" />
            <stop offset="50%" stop-color="rgba(var(--accent-custom-rgb, 125, 211, 252), 0.28)" />
            <stop offset="100%" stop-color="rgba(6, 182, 212, 0.16)" />
          </linearGradient>
        </defs>
        <path
          fill="url(#waveGradBtm2)"
          d="M0,240 C280,120 560,290 840,210 C1120,130 1400,280 1680,200 C1960,120 2240,300 2520,210 C2700,150 2800,230 2880,240 L2880,400 L0,400 Z"
        ></path>
      </svg>
    </div>

    <!-- ====================================================================
         3. Dynamic Animated Shapes Engine (3D Frosted Crystals & Prisms)
         ==================================================================== -->
    <div v-else-if="config.backgroundType === 'shapes'" class="engine-layer shapes-engine">
      <!-- Floating Frosted Prisms & Geometric Crystals -->
      <div class="crystal-prism prism-1" :style="{ borderColor: config.accentColor }"></div>
      <div class="crystal-prism prism-2"></div>
      <div class="crystal-prism prism-3" :style="{ backgroundColor: config.accentColor }"></div>
      <div class="geometric-diamond diamond-1" :style="{ borderColor: config.accentColor }"></div>
      <div class="geometric-diamond diamond-2"></div>
      <div class="orbital-ring ring-1"></div>
      <div class="orbital-ring ring-2" :style="{ borderColor: config.accentColor }"></div>
      <div class="floating-capsule capsule-1"></div>
      <div class="floating-capsule capsule-2" :style="{ borderColor: config.accentColor }"></div>
    </div>

    <!-- ====================================================================
         4. Custom Wallpaper Image Engine
         ==================================================================== -->
    <div v-else-if="config.backgroundType === 'image'" class="engine-layer image-engine">
      <div
        v-if="config.customImageUrl"
        class="custom-photo-layer"
        :style="{ backgroundImage: `url(${config.customImageUrl})` }"
      ></div>
      <div v-else class="empty-media-fallback">
        <p>No custom wallpaper uploaded yet. Configure in Appearance Settings.</p>
      </div>
    </div>

    <!-- ====================================================================
         5. Custom Video Wallpaper Engine
         ==================================================================== -->
    <div v-else-if="config.backgroundType === 'video'" class="engine-layer video-engine">
      <video
        v-if="config.customVideoUrl"
        class="custom-video-layer"
        :src="config.customVideoUrl"
        autoplay
        loop
        muted
        playsinline
      ></video>
      <div v-else class="empty-media-fallback">
        <p>No video loop specified. Provide an MP4 URL or file in Appearance Settings.</p>
      </div>
    </div>

    <!-- ====================================================================
         Minimalist Specular Vignette Overlay (Leaves waves & glass crisp)
         ==================================================================== -->
    <div class="glass-ambient-veil"></div>
  </div>
</template>

<style scoped>
.ambient-canvas-root {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
  transition: background-color 0.4s ease;
}

.engine-layer {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

/* ====================================================================
   1. Animated Glowing Orbs Engine Styles
   ==================================================================== */
.orbs-engine {
  background: radial-gradient(circle at 30% 20%, #0d1e38 0%, #060b14 65%, #03060c 100%);
}

.theme-light .orbs-engine {
  background: radial-gradient(circle at 30% 20%, #dbeafe 0%, #eff6ff 50%, #f0fdf4 100%);
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(75px);
  will-change: transform;
}

.orb-1 {
  width: 520px;
  height: 520px;
  top: 5%;
  left: 10%;
  opacity: 0.45;
  animation: orb-drift-1 16s ease-in-out infinite alternate;
}

.orb-2 {
  width: 600px;
  height: 600px;
  bottom: 5%;
  right: 8%;
  background-color: #6366f1;
  opacity: 0.32;
  animation: orb-drift-2 20s ease-in-out infinite alternate;
}

.orb-3 {
  width: 440px;
  height: 440px;
  top: 35%;
  right: 20%;
  border-width: 70px;
  border-style: solid;
  opacity: 0.35;
  animation: orb-drift-3 18s ease-in-out infinite alternate;
}

.orb-4 {
  width: 480px;
  height: 480px;
  bottom: 12%;
  left: 5%;
  background-color: #06b6d4;
  opacity: 0.32;
  animation: orb-drift-4 22s ease-in-out infinite alternate;
}

.orb-5 {
  width: 360px;
  height: 360px;
  top: 60%;
  left: 45%;
  opacity: 0.30;
  animation: orb-drift-5 14s ease-in-out infinite alternate;
}

.orb-6 {
  width: 420px;
  height: 420px;
  top: 15%;
  right: 40%;
  background-color: #a855f7;
  opacity: 0.28;
  animation: orb-drift-6 19s ease-in-out infinite alternate;
}

.orb-center-glow {
  width: 750px;
  height: 750px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0.16;
  filter: blur(130px);
}

@keyframes orb-drift-1 {
  0% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(140px, 80px) scale(1.12); }
  66% { transform: translate(-80px, 120px) scale(0.92); }
  100% { transform: translate(60px, -40px) scale(1.05); }
}

@keyframes orb-drift-2 {
  0% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(-120px, -70px) scale(1.15); }
  66% { transform: translate(90px, -50px) scale(0.90); }
  100% { transform: translate(-60px, 60px) scale(1.08); }
}

@keyframes orb-drift-3 {
  0% { transform: translate(0, 0) rotate(0deg) scale(1); }
  50% { transform: translate(120px, -90px) rotate(120deg) scale(1.1); }
  100% { transform: translate(-100px, 60px) rotate(240deg) scale(0.95); }
}

@keyframes orb-drift-4 {
  0% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(110px, -100px) scale(1.14); }
  100% { transform: translate(-70px, -60px) scale(0.94); }
}

@keyframes orb-drift-5 {
  0% { transform: translate(0, 0) scale(0.95); }
  50% { transform: translate(-100px, 90px) scale(1.12); }
  100% { transform: translate(80px, -70px) scale(1.02); }
}

@keyframes orb-drift-6 {
  0% { transform: translate(0, 0) scale(1.05); }
  50% { transform: translate(90px, 110px) scale(0.92); }
  100% { transform: translate(-110px, -80px) scale(1.1); }
}

/* ====================================================================
   2. Animated Fluid Waves Engine Styles (Full-Screen Undulating Ribbons)
   ==================================================================== */
.waves-engine {
  background: radial-gradient(circle at 50% 10%, #0d1b32 0%, #060b14 60%, #040810 100%);
  overflow: hidden;
}

.theme-light .waves-engine {
  background: radial-gradient(circle at 50% 10%, #e0f2fe 0%, #bae6fd 60%, #93c5fd 100%);
}

.wave-svg {
  position: absolute;
  left: -20%;
  width: 140%;
  will-change: transform;
  pointer-events: none;
}

.wave-top {
  top: -8%;
  height: 52%;
  animation: wave-flow-top 12s ease-in-out infinite alternate;
  filter: blur(1.5px);
}

.wave-mid {
  top: 18%;
  height: 60%;
  animation: wave-flow-mid 16s ease-in-out infinite alternate;
  filter: blur(2px);
}

.wave-bottom-1 {
  bottom: -6%;
  height: 64%;
  animation: wave-flow-btm1 11s ease-in-out infinite alternate;
}

.wave-bottom-2 {
  bottom: 0%;
  height: 54%;
  animation: wave-flow-btm2 14s ease-in-out infinite alternate;
}

@keyframes wave-flow-top {
  0% { transform: translateX(0) translateY(0) scaleY(1); }
  50% { transform: translateX(-60px) translateY(18px) scaleY(1.1); }
  100% { transform: translateX(50px) translateY(-14px) scaleY(0.92); }
}

@keyframes wave-flow-mid {
  0% { transform: translateX(40px) translateY(-12px) scaleY(0.94); }
  50% { transform: translateX(-55px) translateY(22px) scaleY(1.08); }
  100% { transform: translateX(-20px) translateY(-10px) scaleY(1); }
}

@keyframes wave-flow-btm1 {
  0% { transform: translateX(0) translateY(0) scaleY(1); }
  50% { transform: translateX(-80px) translateY(-25px) scaleY(1.18); }
  100% { transform: translateX(40px) translateY(15px) scaleY(0.94); }
}

@keyframes wave-flow-btm2 {
  0% { transform: translateX(-50px) translateY(12px) scaleY(1.08); }
  50% { transform: translateX(60px) translateY(-20px) scaleY(0.92); }
  100% { transform: translateX(10px) translateY(8px) scaleY(1.04); }
}

.wave-ambient-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(110px);
  will-change: transform;
}

.glow-1 {
  top: 10%;
  left: 20%;
  width: 580px;
  height: 580px;
  opacity: 0.35;
  animation: wave-glow-drift 15s ease-in-out infinite alternate;
}

.glow-2 {
  bottom: 15%;
  right: 15%;
  width: 680px;
  height: 680px;
  background-color: #6366f1;
  opacity: 0.28;
  animation: wave-glow-drift 19s ease-in-out infinite alternate-reverse;
}

.glow-3 {
  top: 45%;
  right: 35%;
  width: 440px;
  height: 440px;
  border-width: 80px;
  border-style: solid;
  opacity: 0.30;
  animation: wave-glow-drift 17s ease-in-out infinite alternate;
}

@keyframes wave-glow-drift {
  0% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(80px, -45px) scale(1.15); }
  100% { transform: translate(-60px, 50px) scale(0.92); }
}

/* ====================================================================
   3. Animated Geometric Shapes Engine Styles
   ==================================================================== */
.shapes-engine {
  background: radial-gradient(circle at 65% 25%, #131b2e 0%, #080d16 100%);
  overflow: hidden;
  perspective: 1200px;
}

.theme-light .shapes-engine {
  background: radial-gradient(circle at 65% 25%, #e0f2fe 0%, #f8fafc 100%);
}

.crystal-prism,
.geometric-diamond,
.orbital-ring,
.floating-capsule {
  position: absolute;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  will-change: transform;
}

.prism-1 {
  width: 320px;
  height: 320px;
  top: 12%;
  right: 10%;
  border-width: 2.5px;
  border-style: solid;
  border-radius: 46px;
  background: rgba(255, 255, 255, 0.04);
  box-shadow: 0 16px 45px rgba(0, 0, 0, 0.25), inset 0 2px 3px rgba(255, 255, 255, 0.4);
  animation: prism-rotate-3d 24s ease-in-out infinite alternate;
}

.prism-2 {
  width: 420px;
  height: 420px;
  bottom: 8%;
  left: 8%;
  border: 2px solid rgba(255, 255, 255, 0.14);
  border-radius: 64px;
  background: rgba(255, 255, 255, 0.03);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3), inset 0 1.5px 2px rgba(255, 255, 255, 0.3);
  animation: prism-rotate-alt 28s ease-in-out infinite alternate;
}

.prism-3 {
  width: 240px;
  height: 240px;
  top: 48%;
  left: 28%;
  border-radius: 38px;
  opacity: 0.18;
  filter: blur(35px);
  animation: shape-float 16s ease-in-out infinite alternate;
}

.diamond-1 {
  width: 200px;
  height: 200px;
  top: 25%;
  left: 18%;
  border-width: 2px;
  border-style: solid;
  border-radius: 28px;
  transform: rotate(45deg);
  background: rgba(255, 255, 255, 0.05);
  box-shadow: 0 10px 30px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.25);
  animation: diamond-hover 18s ease-in-out infinite alternate;
}

.diamond-2 {
  width: 160px;
  height: 160px;
  bottom: 25%;
  right: 22%;
  border: 2px solid rgba(255, 255, 255, 0.18);
  border-radius: 24px;
  transform: rotate(45deg);
  background: rgba(255, 255, 255, 0.03);
  animation: diamond-hover-2 22s ease-in-out infinite alternate;
}

.ring-1 {
  width: 360px;
  height: 360px;
  top: 15%;
  left: 8%;
  border-radius: 50%;
  border: 2px dashed rgba(255, 255, 255, 0.22);
  animation: ring-spin 32s linear infinite;
}

.ring-2 {
  width: 440px;
  height: 440px;
  bottom: 12%;
  right: 12%;
  border-radius: 50%;
  border-width: 3px;
  border-style: solid;
  opacity: 0.32;
  filter: blur(28px);
  animation: ring-spin 40s linear infinite reverse;
}

.capsule-1 {
  width: 380px;
  height: 130px;
  top: 62%;
  right: 5%;
  border-radius: 9999px;
  background: linear-gradient(90deg, rgba(var(--accent-custom-rgb, 125, 211, 252), 0.2) 0%, transparent 100%);
  border: 1.5px solid rgba(255, 255, 255, 0.12);
  transform: rotate(-28deg);
  animation: capsule-drift 20s ease-in-out infinite alternate;
}

.capsule-2 {
  width: 300px;
  height: 100px;
  top: 18%;
  right: 32%;
  border-radius: 9999px;
  border-width: 1.5px;
  border-style: solid;
  background: rgba(255, 255, 255, 0.03);
  transform: rotate(35deg);
  animation: capsule-drift-2 24s ease-in-out infinite alternate;
}

@keyframes prism-rotate-3d {
  0% { transform: rotate3d(1, 1, 0, 15deg) translateY(0); }
  50% { transform: rotate3d(1, 1, 1, 45deg) translateY(-40px); }
  100% { transform: rotate3d(0, 1, 1, 25deg) translateY(30px); }
}

@keyframes prism-rotate-alt {
  0% { transform: rotate3d(1, 0, 1, -15deg) translateY(0); }
  50% { transform: rotate3d(0, 1, 1, -40deg) translateY(50px); }
  100% { transform: rotate3d(1, 1, 0, -20deg) translateY(-30px); }
}

@keyframes diamond-hover {
  0% { transform: rotate(45deg) translate(0, 0) scale(1); }
  50% { transform: rotate(65deg) translate(50px, -40px) scale(1.12); }
  100% { transform: rotate(35deg) translate(-40px, 30px) scale(0.94); }
}

@keyframes diamond-hover-2 {
  0% { transform: rotate(45deg) translate(0, 0); }
  50% { transform: rotate(25deg) translate(-60px, -50px) scale(1.08); }
  100% { transform: rotate(55deg) translate(40px, 40px) scale(0.95); }
}

@keyframes ring-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes shape-float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(70px, -60px) scale(1.2); }
}

@keyframes capsule-drift {
  0% { transform: rotate(-28deg) translate(0, 0); }
  50% { transform: rotate(-20deg) translate(-60px, 40px); }
  100% { transform: rotate(-35deg) translate(40px, -30px); }
}

@keyframes capsule-drift-2 {
  0% { transform: rotate(35deg) translate(0, 0); }
  50% { transform: rotate(45deg) translate(50px, -35px); }
  100% { transform: rotate(25deg) translate(-45px, 30px); }
}

/* ====================================================================
   4 & 5. Custom Image & Video Engines
   ==================================================================== */
.image-engine,
.video-engine {
  background: #0b0f19;
}

.custom-photo-layer {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.custom-video-layer {
  position: absolute;
  top: 50%;
  left: 50%;
  min-width: 100%;
  min-height: 100%;
  width: auto;
  height: auto;
  transform: translate(-50%, -50%);
  object-fit: cover;
}

.empty-media-fallback {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
  padding: 16px 24px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px dashed rgba(255, 255, 255, 0.2);
}

/* Ultra-light ambient veil to keep background visible through frosted glass */
.glass-ambient-veil {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(
    circle at 50% 50%,
    transparent 55%,
    rgba(6, 11, 20, 0.35) 100%
  );
}

.theme-light .glass-ambient-veil {
  background: radial-gradient(
    circle at 50% 50%,
    transparent 65%,
    rgba(255, 255, 255, 0.25) 100%
  );
}
</style>
