<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { Profile } from '../types/keymap';
import {
  searchGames,
  fetchSteamInputDbConfig,
  fetchBestCommunityProfile,
  type DiscoveredGame,
} from '../services/gameDiscoveryService';
import CosmicIcon from './CosmicIcon.vue';

defineProps<{
  isOpen: boolean;
  profiles: Profile[];
  activeSlot: number;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'select-profile', slot: number): void;
  (e: 'add-game', entry: DiscoveredGame): void;
  (e: 'add-custom-game', name: string): void;
  (e: 'remove-profile', slot: number): void;
}>();

// View mode: 'library' | 'search' | 'detail' | 'manual'
const viewMode = ref<'library' | 'search' | 'detail' | 'manual'>('library');
const searchQuery = ref('');
const searchInputRef = ref<HTMLInputElement | null>(null);

const searchResults = ref<DiscoveredGame[]>([]);
const isSearching = ref(false);

// Selected game for preview detail sheet
const selectedGame = ref<DiscoveredGame | null>(null);

// Manual Game Creation State
const manualName = ref('');
const manualGenre = ref('Action');
const manualCoverUrl = ref('');
const manualDescription = ref('');
const manualTemplate = ref<'wasd_mouse' | 'retro_dpad' | 'blank'>('wasd_mouse');
const manualImageFailed = ref(false);

const GENRES = [
  'Action',
  'RPG',
  'Emulator',
  'Platformer',
  'Shooter',
  'Adventure',
  'Racing',
  'Strategy',
  'Indie',
  'Custom',
] as const;

const TEMPLATES = [
  {
    id: 'wasd_mouse' as const,
    title: '3D Action / FPS (WASD + Mouse Look)',
    desc: 'Left stick WASD movement, right stick smooth mouse aim, triggers for primary/secondary fire, Jump & Crouch.',
  },
  {
    id: 'retro_dpad' as const,
    title: '2D Platformer / Retro (D-Pad & Face Keys)',
    desc: 'Left stick & D-pad Arrow keys, Jump (Z/Space), Attack (X), Dash (C), Cast (A). Great for Hollow Knight & emulators.',
  },
  {
    id: 'blank' as const,
    title: 'Clean Slate (Unbound)',
    desc: 'All sticks and buttons unbound. Perfect for building a tailored layout completely from scratch.',
  },
];

const openManualAdd = () => {
  viewMode.value = 'manual';
  manualName.value = searchQuery.value.trim() || '';
  manualGenre.value = 'Action';
  manualCoverUrl.value = '';
  manualDescription.value = '';
  manualTemplate.value = 'wasd_mouse';
  manualImageFailed.value = false;
};

const handleSaveManualGame = () => {
  if (!manualName.value.trim()) return;

  let defaultProfile: Partial<Profile> | undefined;

  if (manualTemplate.value === 'wasd_mouse') {
    defaultProfile = {
      sticks: {
        left: { mode: 'digital_keys', deadzone: 80, up: 'w', down: 's', left: 'a', right: 'd' },
        right: { mode: 'mouse', deadzone: 30, sensitivity: 1.2 },
      },
      buttons: {
        a: { type: 'key', code: 'KEY_SPACE' },
        b: { type: 'key', code: 'c' },
        x: { type: 'key', code: 'e' },
        y: { type: 'key', code: 'r' },
        l1: { type: 'key', code: 'KEY_LEFT_SHIFT' },
        r1: { type: 'key', code: 'f' },
        l2: { type: 'mouse_button', code: 'MOUSE_RIGHT', threshold: 40 },
        r2: { type: 'mouse_button', code: 'MOUSE_LEFT', threshold: 40 },
        l3: { type: 'key', code: 'KEY_LEFT_SHIFT' },
        r3: { type: 'key', code: 'v' },
      },
    };
  } else if (manualTemplate.value === 'retro_dpad') {
    defaultProfile = {
      sticks: {
        left: { mode: 'digital_keys', deadzone: 100, up: 'KEY_UP_ARROW', down: 'KEY_DOWN_ARROW', left: 'KEY_LEFT_ARROW', right: 'KEY_RIGHT_ARROW' },
        right: { mode: 'none', deadzone: 100 },
      },
      buttons: {
        a: { type: 'key', code: 'KEY_SPACE' },
        b: { type: 'key', code: 'x' },
        x: { type: 'key', code: 'z' },
        y: { type: 'key', code: 'c' },
        l1: { type: 'key', code: 'KEY_LEFT_SHIFT' },
        r1: { type: 'key', code: 'a' },
      },
    };
  }

  const manualGame: DiscoveredGame = {
    id: `manual_${Date.now()}`,
    name: manualName.value.trim(),
    genre: manualGenre.value || 'Custom',
    coverUrl: manualCoverUrl.value.trim() || '',
    description: manualDescription.value.trim() || 'Custom game profile created manually.',
    source: 'custom',
    defaultProfile,
  };

  emit('add-game', manualGame);
  recentlyAddedId.value = manualGame.id;
  viewMode.value = 'library';
  showModalToast(`Created custom profile for "${manualGame.name}"!`);
};

// SteamInputDB manual link import
const steamInputDbInput = ref('');
const isImportingSidb = ref(false);
const importSidbError = ref<string | null>(null);
const isPullingCommunity = ref(false);

// In-modal toast feedback
const toastMessage = ref<string | null>(null);
let toastTimer: any = null;
const recentlyAddedId = ref<string | number | null>(null);

const showModalToast = (msg: string) => {
  toastMessage.value = msg;
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toastMessage.value = null;
  }, 3500);
};

// Categories for quick discovery
const CATEGORIES = ['All', 'RPG', 'Action', 'Indie', 'Adventure', 'Shooter'] as const;
const selectedCategory = ref<string>('All');

const selectCategory = (cat: string) => {
  selectedCategory.value = cat;
  if (cat === 'All') {
    searchQuery.value = '';
    executeSearch('');
  } else {
    searchQuery.value = cat;
    executeSearch(cat);
  }
};

const executeSearch = async (query: string) => {
  isSearching.value = true;
  try {
    const list = await searchGames(query);
    searchResults.value = list;
  } catch (err) {
    console.error('Failed to search games:', err);
  } finally {
    isSearching.value = false;
  }
};

const openSearch = () => {
  viewMode.value = 'search';
  searchQuery.value = '';
  executeSearch('');
  setTimeout(() => {
    searchInputRef.value?.focus();
  }, 100);
};

const backToLibrary = () => {
  viewMode.value = 'library';
  searchQuery.value = '';
};

const openGameDetail = (game: DiscoveredGame) => {
  selectedGame.value = game;
  viewMode.value = 'detail';
  steamInputDbInput.value = '';
  importSidbError.value = null;
};

const backToSearch = () => {
  viewMode.value = 'search';
};

const handleAutoPullCommunity = async () => {
  if (!selectedGame.value?.steamAppId) return;
  isPullingCommunity.value = true;
  try {
    const profile = await fetchBestCommunityProfile(selectedGame.value.steamAppId);
    if (profile && profile.buttons && Object.keys(profile.buttons).length > 0) {
      selectedGame.value.defaultProfile = profile;
      showModalToast(`Pulled community keyboard mapping from SteamInput!`);
    } else {
      showModalToast(`No community keyboard mappings found; using smart archetype.`);
    }
  } catch (err) {
    showModalToast(`Error pulling SteamInput layout.`);
  } finally {
    isPullingCommunity.value = false;
  }
};

const handleAddSelectedGame = async () => {
  if (!selectedGame.value) return;
  const game = selectedGame.value;

  // Auto-pull community mapping if Steam game has no preset yet
  if (game.steamAppId && !game.defaultProfile) {
    try {
      const commProfile = await fetchBestCommunityProfile(game.steamAppId);
      if (commProfile) {
        game.defaultProfile = commProfile;
      }
    } catch {
      // fallback
    }
  }

  emit('add-game', game);
  recentlyAddedId.value = game.id;
  viewMode.value = 'library';
  showModalToast(`Added "${game.name}" to your library!`);
};

const handleImportSteamInputDb = async () => {
  if (!steamInputDbInput.value.trim()) return;
  isImportingSidb.value = true;
  importSidbError.value = null;
  try {
    const imported = await fetchSteamInputDbConfig(steamInputDbInput.value.trim());
    if (imported) {
      selectedGame.value = imported;
      emit('add-game', imported);
      recentlyAddedId.value = imported.id;
      viewMode.value = 'library';
      showModalToast(`Imported layout from SteamInputDB!`);
    } else {
      importSidbError.value = 'Could not find a valid config for that URL or ID.';
    }
  } catch (err) {
    importSidbError.value = 'Error fetching SteamInputDB config.';
  } finally {
    isImportingSidb.value = false;
  }
};

const triggerSearch = () => {
  executeSearch(searchQuery.value);
};

const handleClearSearch = () => {
  searchQuery.value = '';
  selectedCategory.value = 'All';
  executeSearch('');
};

onMounted(() => {
  executeSearch('');
});

const handleImageError = (game: DiscoveredGame) => {
  // If Steam 600x900 fails, swap to RAWG background art fallback
  if (game.fallbackCoverUrl && game.coverUrl !== game.fallbackCoverUrl) {
    game.coverUrl = game.fallbackCoverUrl;
  }
};

const handleProfileImageError = (prof: Profile) => {
  if (prof.name.toLowerCase().includes('minecraft')) {
    prof.coverUrl = 'https://media.rawg.io/media/games/b4e/b4e4c73d5aa4ec66bbf75375c4847a2b.jpg';
  } else {
    prof.coverUrl = '';
  }
};

const handleSelectSavedGame = (slot: number) => {
  emit('select-profile', slot);
  emit('close');
};

const handleCreateCustom = () => {
  if (!searchQuery.value.trim()) return;
  emit('add-custom-game', searchQuery.value.trim());
  emit('close');
};

const handleDeleteSavedGame = (e: Event, slot: number) => {
  e.stopPropagation();
  emit('remove-profile', slot);
};
</script>

<template>
  <div v-if="isOpen" class="modal-backdrop" @click="emit('close')">
    <div class="modal-card" @click.stop>
      <!-- Modal Header -->
      <header class="modal-header">
        <div class="header-left">
          <button
            v-if="viewMode === 'search' || viewMode === 'manual'"
            class="glass-btn back-btn"
            title="Back to Library"
            @click="backToLibrary"
          >
            <CosmicIcon name="chevron-down" size="14" class="back-icon" />
            <span>Library</span>
          </button>

          <button
            v-if="viewMode === 'detail'"
            class="glass-btn back-btn"
            title="Back to Search"
            @click="backToSearch"
          >
            <CosmicIcon name="chevron-down" size="14" class="back-icon" />
            <span>Search</span>
          </button>

          <div class="title-meta">
            <h2 class="modal-title">
              {{
                viewMode === 'library'
                  ? 'Game Library'
                  : viewMode === 'detail'
                  ? selectedGame?.name || 'Game Details'
                  : viewMode === 'manual'
                  ? 'Add Game Manually'
                  : 'Add Game from Database'
              }}
            </h2>
            <p class="modal-subtitle">
              {{
                viewMode === 'library'
                  ? 'Select a game profile to switch controller mappings or add new titles.'
                  : viewMode === 'detail'
                  ? 'Review controller mappings and SteamInput community layouts.'
                  : viewMode === 'manual'
                  ? 'Create a custom controller profile for emulators, indie games, or non-Steam titles.'
                  : 'Search games with authentic Steam Store posters & RAWG database coverage.'
              }}
            </p>
          </div>
        </div>

        <div class="header-actions">
          <button
            v-if="viewMode === 'library'"
            class="glass-btn add-manual-header-btn"
            title="Create custom profile manually"
            @click="openManualAdd"
          >
            <CosmicIcon name="sparkles" size="13" />
            <span>Add Manually</span>
          </button>

          <button
            v-if="viewMode === 'library'"
            class="glass-btn-primary add-header-btn"
            title="Search online database"
            @click="openSearch"
          >
            <CosmicIcon name="search" size="13" />
            <span>Search Database</span>
          </button>

          <button class="glass-btn close-btn" @click="emit('close')">
            <CosmicIcon name="close" size="14" />
          </button>
        </div>
      </header>

      <!-- In-Modal Notification Toast -->
      <transition name="toast-fade">
        <div v-if="toastMessage" class="modal-toast-banner">
          <CosmicIcon name="check" size="13" />
          <span>{{ toastMessage }}</span>
        </div>
      </transition>

      <!-- Search Toolbar & Category Filter Chips (Shown in Search Mode) -->
      <div v-if="viewMode === 'search'" class="search-toolbar">
        <div class="search-input-wrapper">
          <CosmicIcon name="search" size="15" class="search-glyph" />
          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            class="search-input"
            placeholder="Type game title and press Enter to search..."
            @keydown.enter="triggerSearch"
          />
          <button
            v-if="searchQuery"
            class="clear-search-btn"
            title="Clear"
            @click="handleClearSearch"
          >
            <CosmicIcon name="close" size="12" />
          </button>
          <button
            class="glass-btn-primary search-submit-btn"
            :disabled="isSearching || !searchQuery.trim()"
            @click="triggerSearch"
          >
            <span v-if="isSearching" class="search-spinner-sm"></span>
            <span v-else>Search</span>
          </button>

          <button
            class="glass-btn manual-search-btn"
            title="Create a custom profile manually"
            @click="openManualAdd"
          >
            <CosmicIcon name="sparkles" size="12" />
            <span>Add Manually</span>
          </button>
        </div>

        <div class="category-chips">
          <button
            v-for="cat in CATEGORIES"
            :key="cat"
            class="category-chip"
            :class="{ active: selectedCategory === cat }"
            @click="selectCategory(cat)"
          >
            {{ cat }}
          </button>
        </div>
      </div>

      <!-- Modal Body -->
      <div class="modal-body custom-scroll">
        <!-- 1. Saved Library Grid (Playnite / Console Box-Art Style) -->
        <div v-if="viewMode === 'library'" class="game-grid">
          <!-- Saved Profile Cards -->
          <div
            v-for="(prof, idx) in profiles"
            :key="prof.slot"
            class="game-card"
            :class="{ 'is-active': activeSlot === idx }"
            @click="handleSelectSavedGame(idx)"
          >
            <!-- Box Art Poster -->
            <div class="poster-container">
              <img
                v-if="prof.coverUrl"
                :src="prof.coverUrl"
                :alt="prof.name"
                class="poster-img"
                loading="lazy"
                @error="handleProfileImageError(prof)"
              />
              <div v-else class="poster-fallback">
                <CosmicIcon name="gamepad" size="32" />
              </div>

              <!-- Frosted Bottom Gradient -->
              <div class="poster-gradient"></div>

              <!-- Active Badge -->
              <span v-if="activeSlot === idx" class="active-badge">
                <CosmicIcon name="check" size="11" />
                <span>Active</span>
              </span>

              <!-- Delete Button on Hover -->
              <button
                v-if="profiles.length > 1"
                class="delete-card-btn"
                title="Remove game from library"
                @click="handleDeleteSavedGame($event, idx)"
              >
                <CosmicIcon name="trash" size="12" />
              </button>
            </div>

            <!-- Card Meta -->
            <div class="card-meta">
              <h4 class="game-name" :title="prof.name">{{ prof.name }}</h4>
              <span class="game-genre">{{ prof.genre || 'Controller Profile' }}</span>
            </div>
          </div>

          <!-- Search Online Database Grid Tile -->
          <div class="add-tile-card" title="Search online database" @click="openSearch">
            <div class="add-tile-inner">
              <div class="add-icon-circle">
                <CosmicIcon name="search" size="20" />
              </div>
              <span class="add-tile-title">Search Database</span>
              <span class="add-tile-sub">Online RAWG / Steam</span>
            </div>
          </div>

          <!-- Add Game Manually Grid Tile -->
          <div class="add-tile-card" title="Create a custom profile from scratch" @click="openManualAdd">
            <div class="add-tile-inner">
              <div class="add-icon-circle">
                <CosmicIcon name="sparkles" size="20" />
              </div>
              <span class="add-tile-title">Add Manually</span>
              <span class="add-tile-sub">Emulators & Custom</span>
            </div>
          </div>
        </div>

        <!-- 4. Manual Game Profile Creation View -->
        <div v-else-if="viewMode === 'manual'" class="manual-add-view">
          <div class="manual-add-layout">
            <!-- Left Column: Live Card Poster Preview -->
            <div class="manual-preview-col">
              <span class="section-heading">Live Preview</span>
              <div class="game-card manual-preview-card">
                <div class="poster-container">
                  <img
                    v-if="manualCoverUrl.trim() && !manualImageFailed"
                    :src="manualCoverUrl.trim()"
                    :alt="manualName || 'Game Cover'"
                    class="poster-img"
                    @error="manualImageFailed = true"
                  />
                  <div v-else class="poster-fallback manual-fallback">
                    <CosmicIcon name="gamepad" size="38" class="manual-fallback-icon" />
                    <span class="manual-fallback-text">{{ manualName || 'Custom Title' }}</span>
                  </div>
                  <div class="poster-gradient"></div>
                  <span class="genre-tag">{{ manualGenre || 'Custom' }}</span>
                </div>
                <div class="card-meta">
                  <h4 class="game-name" :title="manualName || 'Custom Game Title'">
                    {{ manualName || 'Custom Game Title' }}
                  </h4>
                  <p class="game-description">
                    {{ manualDescription || 'Custom controller profile ready for key and stick mapping.' }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Right Column: Form Inputs -->
            <div class="manual-form-col">
              <!-- Game Title Input -->
              <div class="form-field-group">
                <label class="form-field-label">
                  <span>Game Title</span>
                  <span class="required-star">*</span>
                </label>
                <input
                  v-model="manualName"
                  type="text"
                  class="glass-form-input"
                  placeholder="e.g. Dolphin Emulator, Hollow Knight Silksong, Mario 64"
                  autofocus
                  @keydown.enter="handleSaveManualGame"
                />
              </div>

              <!-- Genre & Category Selection -->
              <div class="form-field-group">
                <label class="form-field-label">Genre / Category</label>
                <div class="manual-genre-chips">
                  <button
                    v-for="g in GENRES"
                    :key="g"
                    type="button"
                    class="category-chip"
                    :class="{ active: manualGenre === g }"
                    @click="manualGenre = g"
                  >
                    {{ g }}
                  </button>
                </div>
              </div>

              <!-- Cover Image URL -->
              <div class="form-field-group">
                <div class="label-row-meta">
                  <label class="form-field-label">Cover Image URL (Optional)</label>
                  <span class="hint-text">Paste Steam 600×900, RAWG, or Web image link</span>
                </div>
                <div class="input-with-clear">
                  <input
                    v-model="manualCoverUrl"
                    type="text"
                    class="glass-form-input"
                    placeholder="https://.../cover.jpg"
                    @input="manualImageFailed = false"
                  />
                  <button
                    v-if="manualCoverUrl"
                    type="button"
                    class="clear-url-btn"
                    @click="manualCoverUrl = ''"
                  >
                    <CosmicIcon name="close" size="12" />
                  </button>
                </div>
              </div>

              <!-- Starting Layout Template -->
              <div class="form-field-group">
                <label class="form-field-label">Starter Controller Template</label>
                <div class="template-selector-grid">
                  <div
                    v-for="tpl in TEMPLATES"
                    :key="tpl.id"
                    class="template-card-option"
                    :class="{ active: manualTemplate === tpl.id }"
                    @click="manualTemplate = tpl.id"
                  >
                    <div class="tpl-radio-circle">
                      <div v-if="manualTemplate === tpl.id" class="tpl-radio-dot"></div>
                    </div>
                    <div class="tpl-text-meta">
                      <span class="tpl-card-title">{{ tpl.title }}</span>
                      <p class="tpl-card-desc">{{ tpl.desc }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Description / Notes -->
              <div class="form-field-group">
                <label class="form-field-label">Notes / Description (Optional)</label>
                <input
                  v-model="manualDescription"
                  type="text"
                  class="glass-form-input"
                  placeholder="e.g. Gamecube controller emulator bindings"
                  @keydown.enter="handleSaveManualGame"
                />
              </div>

              <!-- Form Action Buttons -->
              <div class="manual-form-actions">
                <button type="button" class="glass-btn back-browse-btn" @click="backToLibrary">
                  <span>Cancel</span>
                </button>
                <button
                  type="button"
                  class="glass-btn-primary add-to-lib-btn"
                  :disabled="!manualName.trim()"
                  @click="handleSaveManualGame"
                >
                  <CosmicIcon name="plus" size="14" />
                  <span>Create Game Profile</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. Search Results Grid -->
        <div v-else-if="viewMode === 'search'" class="search-view">
          <div v-if="searchResults.length > 0" class="game-grid">
            <div
              v-for="game in searchResults"
              :key="game.id"
              class="game-card search-card"
              @click="openGameDetail(game)"
            >
              <div class="poster-container">
                <img
                  :src="game.coverUrl"
                  :alt="game.name"
                  class="poster-img"
                  loading="lazy"
                  @error="handleImageError(game)"
                />
                <div class="poster-gradient"></div>
                <span class="genre-tag">{{ game.genre }}</span>
                <span v-if="game.formattedRelease" class="release-tag">{{ game.formattedRelease }}</span>
                <span v-else-if="game.steamAppId" class="steam-link-tag">Steam 600×900</span>
                <span v-else class="fallback-tag">Metadata Cover</span>
              </div>
              <div class="card-meta">
                <h4 class="game-name" :title="game.name">{{ game.name }}</h4>
                <p class="game-description">{{ game.description }}</p>
                <div class="card-bottom-row">
                  <span
                    v-if="game.defaultProfile"
                    class="preset-available-tag"
                  >
                    Preset Mapping Included
                  </span>
                  <span v-else class="blank-mapping-tag">
                    Universal Gamepad
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Custom Game Fallback -->
          <div v-if="searchQuery.trim()" class="custom-game-cta">
            <div class="custom-cta-info">
              <div class="custom-cta-icon">
                <CosmicIcon name="sparkles" size="18" />
              </div>
              <div>
                <h4 class="custom-cta-title">Add "{{ searchQuery.trim() }}" as Custom Game</h4>
                <p class="custom-cta-sub">
                  Creates a new blank profile ready for key and stick mapping.
                </p>
              </div>
            </div>
            <button class="glass-btn-primary add-custom-btn" @click="handleCreateCustom">
              <CosmicIcon name="plus" size="12" />
              <span>Add to Library</span>
            </button>
          </div>

          <!-- Empty State -->
          <div v-if="searchResults.length === 0 && !isSearching" class="empty-state">
            <CosmicIcon name="search" size="28" />
            <p>No games found for "{{ searchQuery }}". Add it as a custom game above!</p>
          </div>
        </div>

        <!-- 3. Game Detail & SteamInputDB Preview View -->
        <div v-else-if="viewMode === 'detail' && selectedGame" class="detail-view">
          <div
            class="detail-backdrop"
            :style="{ backgroundImage: `url(${selectedGame.coverUrl})` }"
          ></div>

          <div class="detail-container">
            <!-- Left Poster Column -->
            <div class="detail-poster-col">
              <div class="detail-poster-wrapper">
                <img
                  :src="selectedGame.coverUrl"
                  :alt="selectedGame.name"
                  class="detail-poster-img"
                  @error="handleImageError(selectedGame)"
                />
              </div>
            </div>

            <!-- Right Info Column -->
            <div class="detail-info-col">
              <div class="detail-header-meta">
                <h3 class="detail-game-title">{{ selectedGame.name }}</h3>

                <div class="detail-meta-pills">
                  <span class="meta-pill genre-pill">{{ selectedGame.genre }}</span>
                  <span v-if="selectedGame.formattedRelease" class="meta-pill release-pill">
                    Released {{ selectedGame.formattedRelease }}
                  </span>
                  <span v-if="selectedGame.metacritic" class="meta-pill meta-score-pill">
                    Metascore {{ selectedGame.metacritic }}
                  </span>
                  <span v-else-if="selectedGame.rating" class="meta-pill rating-pill">
                    ★ {{ selectedGame.rating.toFixed(1) }} / 5
                  </span>
                </div>
              </div>

              <!-- Synopsis / Description -->
              <div class="detail-synopsis-box">
                <h4 class="section-heading">Overview</h4>
                <p class="synopsis-text">{{ selectedGame.description }}</p>
              </div>

              <!-- Controller Mapping Status Card -->
              <div class="detail-controller-section">
                <h4 class="section-heading">Controller Configuration</h4>

                <div class="controller-status-card">
                  <div
                    class="status-icon-badge"
                    :class="selectedGame.defaultProfile ? 'is-preset' : 'is-generic'"
                  >
                    <CosmicIcon :name="selectedGame.defaultProfile ? 'check' : 'gamepad'" size="16" />
                  </div>
                  <div class="status-text">
                    <span class="status-title">
                      {{
                        selectedGame.defaultProfile
                          ? 'Curated DexPad Profile Ready'
                          : 'Universal Gamepad Passthrough'
                      }}
                    </span>
                    <span class="status-sub">
                      {{
                        selectedGame.defaultProfile
                          ? 'Hand-tuned sticks, analog triggers, and action button rebindings ready to play.'
                          : 'Standard 1:1 controller passthrough. Ready for full customization in DexPad.'
                      }}
                    </span>
                  </div>
                </div>

                <!-- SteamInputDB Direct Linkout & Auto-Pull -->
                <div v-if="selectedGame.steamInputDbUrl" class="steaminput-hub-card">
                  <div class="hub-info">
                    <div class="hub-title-row">
                      <span class="hub-title">SteamInputDB Community Layouts</span>
                      <span class="hub-badge">Live Index</span>
                    </div>
                    <span class="hub-desc">
                      Cross-reference Steam App ID ({{ selectedGame.steamAppId }}) with SteamInputDB to pull community controller-to-keyboard mappings.
                    </span>
                  </div>
                  <div class="hub-actions">
                    <button
                      class="glass-btn-primary auto-pull-btn"
                      :disabled="isPullingCommunity"
                      @click="handleAutoPullCommunity"
                    >
                      <CosmicIcon name="sparkles" size="13" />
                      <span>{{ isPullingCommunity ? 'Pulling...' : 'Auto-Pull Mapping' }}</span>
                    </button>
                    <a
                      :href="selectedGame.steamInputDbUrl"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="glass-btn steaminput-link-btn"
                    >
                      <span>Browse on Web</span>
                      <CosmicIcon name="chevron-down" size="12" class="linkout-arrow" />
                    </a>
                  </div>
                </div>

                <!-- SteamInputDB Config Import Box -->
                <div class="sidb-import-box">
                  <label class="sidb-import-label">Import Layout from SteamInputDB URL</label>
                  <div class="sidb-input-row">
                    <input
                      v-model="steamInputDbInput"
                      type="text"
                      class="sidb-text-input"
                      placeholder="Paste link (e.g. steaminputdb.com/config/3660748856)..."
                      @keydown.enter="handleImportSteamInputDb"
                    />
                    <button
                      class="glass-btn-primary sidb-import-btn"
                      :disabled="isImportingSidb || !steamInputDbInput.trim()"
                      @click="handleImportSteamInputDb"
                    >
                      <span v-if="isImportingSidb">Importing...</span>
                      <span v-else>Import</span>
                    </button>
                  </div>
                  <span v-if="importSidbError" class="sidb-error-msg">{{ importSidbError }}</span>
                </div>
              </div>

              <!-- Action Bar Footer -->
              <div class="detail-action-footer">
                <button class="glass-btn back-browse-btn" @click="backToSearch">
                  <span>Back to Browse</span>
                </button>
                <button class="glass-btn-primary add-to-lib-btn" @click="handleAddSelectedGame">
                  <CosmicIcon name="plus" size="14" />
                  <span>Add to DexPad Library</span>
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
  width: 100vw;
  height: 100vh;
  background: rgba(3, 7, 18, 0.45);
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
  max-width: 960px;
  max-height: 88vh;
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
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.back-icon {
  transform: rotate(90deg);
}

.title-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.2;
}

.modal-subtitle {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Search Toolbar */
.search-toolbar {
  padding: 14px 28px;
  border-bottom: 1px solid var(--glass-border-subtle);
  background: var(--glass-surface-pill);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.category-chips {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.category-chip {
  padding: 5px 12px;
  border-radius: 9999px;
  font-size: 11.5px;
  font-weight: 500;
  background: var(--glass-surface-elevated);
  border: 1px solid var(--glass-border);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.category-chip:hover {
  color: var(--text-primary);
  border-color: var(--accent-custom);
  background: var(--glass-surface-pill);
}

.category-chip.active {
  color: var(--accent-custom);
  border-color: var(--accent-custom);
  background: rgba(var(--accent-custom-rgb, 125, 211, 252), 0.12);
  box-shadow: 0 0 10px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.2);
  font-weight: 600;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--glass-surface-elevated);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  padding: 8px 14px;
  transition: all 0.2s ease;
}

.search-input-wrapper:focus-within {
  border-color: var(--accent-custom);
  box-shadow: 0 0 14px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.35);
}

.search-glyph {
  color: var(--text-muted);
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 13.5px;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-top-color: var(--accent-custom);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.clear-search-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
}

.clear-search-btn:hover {
  color: var(--text-primary);
}

.search-submit-btn {
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.search-spinner-sm {
  width: 13px;
  height: 13px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Modal Body */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px 28px;
}

/* Game Grid (Console Box-Art / Playnite Style) */
.game-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 18px;
}

.game-card {
  position: relative;
  display: flex;
  flex-direction: column;
  border-radius: 18px;
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border-subtle);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.game-card:hover {
  transform: translateY(-4px);
  border-color: var(--accent-custom);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.35), 0 0 16px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.2);
}

.game-card.is-active {
  border-color: var(--accent-custom);
  box-shadow: 0 0 20px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.45);
}

/* Poster Container (2:3 Aspect Ratio) */
.poster-container {
  position: relative;
  width: 100%;
  aspect-ratio: 2 / 3;
  overflow: hidden;
  background: #000000;
}

.poster-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.35s ease;
}

.game-card:hover .poster-img {
  transform: scale(1.05);
}

.poster-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  background: #111827;
}

.poster-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8) 0%, transparent 60%);
  pointer-events: none;
}

.active-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px 9px;
  border-radius: 9999px;
  background: var(--accent-custom);
  color: var(--text-on-accent);
  font-size: 10.5px;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.6);
  z-index: 2;
}

.genre-tag {
  position: absolute;
  bottom: 8px;
  left: 10px;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(8px);
  color: #f1f5f9;
  z-index: 2;
}

.steam-link-tag {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 9.5px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 6px;
  background: rgba(14, 165, 233, 0.85);
  color: #ffffff;
  z-index: 2;
}

.fallback-tag {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 9.5px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.65);
  color: var(--text-muted);
  z-index: 2;
}

.delete-card-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ef4444;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transform: scale(0.9);
  transition: all 0.2s ease;
  z-index: 2;
}

.game-card:hover .delete-card-btn {
  opacity: 1;
  transform: scale(1);
}

.delete-card-btn:hover {
  background: #ef4444;
  color: #ffffff;
  border-color: #ef4444;
}

/* Card Meta */
.card-meta {
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.game-name {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.game-genre {
  font-size: 11px;
  color: var(--text-muted);
}

.game-description {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 2px 0 6px;
}

.card-bottom-row {
  margin-top: 4px;
}

.preset-available-tag {
  font-size: 10px;
  font-weight: 600;
  color: #10b981;
}

.blank-mapping-tag {
  font-size: 10px;
  color: var(--text-muted);
}

/* Add Tile Card */
.add-tile-card {
  border-radius: 18px;
  border: 2px dashed var(--glass-border);
  background: var(--glass-surface-pill);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.25s ease;
  min-height: 280px;
}

.add-tile-card:hover {
  border-color: var(--accent-custom);
  background: var(--glass-surface-elevated);
  transform: translateY(-4px);
  box-shadow: 0 0 18px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.25);
}

.add-tile-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px;
  text-align: center;
}

.add-icon-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--glass-surface-elevated);
  border: 1px solid var(--glass-border);
  color: var(--accent-custom);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.add-tile-card:hover .add-icon-circle {
  background: var(--accent-custom);
  color: var(--text-on-accent);
  box-shadow: 0 0 14px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.5);
}

.add-tile-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.add-tile-sub {
  font-size: 11.5px;
  color: var(--text-muted);
}

/* Custom Game CTA */
.custom-game-cta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 20px;
  border-radius: 16px;
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border);
  margin-top: 20px;
}

.custom-cta-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.custom-cta-icon {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: var(--accent-custom);
  color: var(--text-on-accent);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.custom-cta-title {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.custom-cta-sub {
  font-size: 11.5px;
  color: var(--text-muted);
  margin: 2px 0 0;
}

.add-custom-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px 20px;
  color: var(--text-muted);
  font-size: 13px;
}
/* Toast Banner */
.modal-toast-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(16, 185, 129, 0.15);
  border-bottom: 1px solid rgba(16, 185, 129, 0.3);
  color: #10b981;
  font-size: 12.5px;
  font-weight: 600;
  backdrop-filter: blur(12px);
  animation: slideDown 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: all 0.25s ease;
}

.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.release-tag {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 10.5px;
  font-weight: 600;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: var(--text-primary);
  z-index: 1;
}

/* Detail View */
.detail-view {
  position: relative;
  overflow: hidden;
  border-radius: 20px;
  padding: 28px;
  min-height: 480px;
  display: flex;
}

.detail-backdrop {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  filter: blur(54px) brightness(0.22);
  opacity: 0.7;
  transform: scale(1.1);
  pointer-events: none;
}

.detail-container {
  display: flex;
  gap: 32px;
  width: 100%;
  position: relative;
  z-index: 1;
}

.detail-poster-col {
  width: 220px;
  flex-shrink: 0;
}

.detail-poster-wrapper {
  width: 100%;
  aspect-ratio: 2 / 3;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.65);
}

.detail-poster-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.detail-info-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}

.detail-header-meta {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.detail-game-title {
  font-size: 24px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
  margin: 0;
  line-height: 1.2;
}

.detail-meta-pills {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.meta-pill {
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 600;
}

.genre-pill {
  background: rgba(var(--accent-custom-rgb, 125, 211, 252), 0.15);
  color: var(--accent-custom);
  border: 1px solid rgba(var(--accent-custom-rgb, 125, 211, 252), 0.3);
}

.release-pill {
  background: var(--glass-surface-elevated);
  color: var(--text-secondary);
  border: 1px solid var(--glass-border);
}

.meta-score-pill {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.35);
  font-weight: 700;
}

.rating-pill {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.35);
}

.section-heading {
  font-size: 11.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  margin: 0 0 8px;
}

.detail-synopsis-box {
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border-subtle);
  border-radius: 14px;
  padding: 14px 18px;
}

.synopsis-text {
  font-size: 12.5px;
  line-height: 1.55;
  color: var(--text-secondary);
  margin: 0;
  max-height: 85px;
  overflow-y: auto;
}

.detail-controller-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.controller-status-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  border-radius: 12px;
  background: var(--glass-surface-elevated);
  border: 1px solid var(--glass-border);
}

.status-icon-badge {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.status-icon-badge.is-preset {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.4);
}

.status-icon-badge.is-generic {
  background: var(--glass-surface-pill);
  color: var(--text-secondary);
  border: 1px solid var(--glass-border);
}

.status-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.status-title {
  font-size: 12.5px;
  font-weight: 700;
  color: var(--text-primary);
}

.status-sub {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.35;
}

/* SteamInputDB Hub Card */
.steaminput-hub-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.45) 0%, rgba(15, 23, 42, 0.6) 100%);
  border: 1px solid rgba(148, 163, 184, 0.25);
}

.hub-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.hub-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.hub-title {
  font-size: 12.5px;
  font-weight: 700;
  color: #f1f5f9;
}

.hub-badge {
  font-size: 9.5px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(56, 189, 248, 0.2);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.35);
  text-transform: uppercase;
}

.hub-desc {
  font-size: 11px;
  color: #94a3b8;
  line-height: 1.35;
}

.hub-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.auto-pull-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 8px;
  font-size: 11.5px;
  font-weight: 600;
  white-space: nowrap;
}

.steaminput-link-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 8px;
  font-size: 11.5px;
  font-weight: 600;
  color: #f8fafc;
  text-decoration: none;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.steaminput-link-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: #38bdf8;
  transform: translateY(-1px);
}

.linkout-arrow {
  transform: rotate(-90deg);
}

/* SteamInputDB Import Box */
.sidb-import-box {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 16px;
  border-radius: 12px;
  background: var(--glass-surface-pill);
  border: 1px solid var(--glass-border);
}

.sidb-import-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
}

.sidb-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sidb-text-input {
  flex: 1;
  background: var(--glass-surface-elevated);
  border: 1px solid var(--glass-border);
  color: var(--text-primary);
  font-size: 11.5px;
  padding: 7px 12px;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.2s ease;
}

.sidb-text-input:focus {
  border-color: var(--accent-custom);
}

.sidb-import-btn {
  padding: 7px 16px;
  font-size: 11.5px;
  border-radius: 8px;
  font-weight: 600;
  flex-shrink: 0;
}

.sidb-error-msg {
  font-size: 11px;
  color: #ef4444;
}

/* Detail Action Footer */
.detail-action-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  margin-top: auto;
  padding-top: 14px;
  border-top: 1px solid var(--glass-border-subtle);
}

.back-browse-btn {
  padding: 9px 18px;
  border-radius: 12px;
  font-size: 12.5px;
  font-weight: 600;
}

.add-to-lib-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 22px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 700;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ==========================================================================
   Manual Game Profile Creation Form Styles
   ========================================================================== */
.add-manual-header-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 14px;
  border-radius: 12px;
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-primary);
  background: var(--glass-surface-elevated);
  border: 1px solid var(--glass-border);
  transition: all 0.2s ease;
}

.add-manual-header-btn:hover {
  border-color: var(--accent-custom);
  transform: translateY(-1px);
}

.manual-search-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 14px;
  height: 38px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  background: var(--glass-surface-elevated);
  border: 1px solid var(--glass-border);
  white-space: nowrap;
  transition: all 0.2s ease;
}

.manual-search-btn:hover {
  border-color: var(--accent-custom);
  color: var(--accent-custom);
}

.manual-add-view {
  padding: 12px 10px 24px;
  animation: slideDown 0.25s ease-out;
}

.manual-add-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 32px;
  align-items: start;
}

.manual-preview-col {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.manual-preview-card {
  width: 100%;
  pointer-events: none;
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.25);
}

.manual-fallback {
  background: #111827 !important;
  color: var(--text-muted);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.manual-fallback-icon {
  color: var(--text-muted);
  opacity: 0.8;
}

.manual-fallback-text {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-secondary);
  text-align: center;
  padding: 0 12px;
}

.manual-form-col {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-field-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-field-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-primary);
}

.required-star {
  color: #ef4444;
}

.label-row-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.hint-text {
  font-size: 11px;
  color: var(--text-muted);
}

.glass-form-input {
  width: 100%;
  padding: 11px 16px;
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 13px;
  font-family: inherit;
  outline: none;
  transition: all 0.2s ease;
}

.glass-form-input:focus {
  border-color: var(--accent-custom);
  box-shadow: 0 0 0 3px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.18);
}

.manual-genre-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.input-with-clear {
  position: relative;
  display: flex;
  align-items: center;
}

.clear-url-btn {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
}

.clear-url-btn:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.1);
}

.template-selector-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.template-card-option {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 16px;
  background: var(--glass-surface-elevated);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.template-card-option:hover {
  border-color: rgba(var(--accent-custom-rgb, 125, 211, 252), 0.5);
  background: rgba(var(--accent-custom-rgb, 125, 211, 252), 0.06);
}

.template-card-option.active {
  border-color: var(--accent-custom);
  background: rgba(var(--accent-custom-rgb, 125, 211, 252), 0.12);
  box-shadow: 0 0 16px rgba(var(--accent-custom-rgb, 125, 211, 252), 0.15);
}

.tpl-radio-circle {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
  transition: all 0.2s ease;
}

.template-card-option.active .tpl-radio-circle {
  border-color: var(--accent-custom);
}

.tpl-radio-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-custom);
}

.tpl-text-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tpl-card-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
}

.tpl-card-desc {
  font-size: 11.5px;
  line-height: 1.45;
  color: var(--text-muted);
  margin: 0;
}

.manual-form-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 14px;
  border-top: 1px solid var(--glass-border-subtle);
  margin-top: 8px;
}

.submit-manual-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 700;
}

@media (max-width: 820px) {
  .manual-add-layout {
    grid-template-columns: 1fr;
  }
  .manual-preview-card {
    max-width: 220px;
    margin: 0 auto;
  }
}
</style>
