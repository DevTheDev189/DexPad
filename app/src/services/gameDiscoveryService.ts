import { GAMES_DATABASE } from '../data/gamesDatabase';
import type { Profile } from '../types/keymap';
import { parseSteamVdfToProfile } from '../utils/steamVdfParser';

export interface DiscoveredGame {
  id: string | number;
  name: string;
  genre: string;
  coverUrl: string;
  fallbackCoverUrl?: string;
  description: string;
  steamAppId?: string;
  source: 'rawg' | 'steam' | 'curated' | 'custom' | 'steaminputdb';
  defaultProfile?: Partial<Profile>;
  released?: string;
  formattedRelease?: string;
  rating?: number;
  metacritic?: number;
  developer?: string;
  steamInputDbUrl?: string;
}

/**
 * Format raw ISO dates (e.g. 2020-12-10) into human readable formats (e.g. "Dec 2020")
 */
export function formatReleaseDate(rawDate?: string): string {
  if (!rawDate) return '';
  const match = rawDate.match(/^(\d{4})(?:-(\d{2}))?/);
  if (!match) return rawDate;
  const year = match[1];
  const month = match[2];
  if (!month) return year;
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const monthIdx = parseInt(month, 10) - 1;
  if (monthIdx >= 0 && monthIdx < 12) {
    return `${months[monthIdx]} ${year}`;
  }
  return year;
}

/**
 * Extract config file ID from a steaminputdb.com URL or raw ID string
 * e.g. "https://steaminputdb.com/config/3660748856" -> "3660748856"
 */
export function parseSteamInputDbUrl(input: string): string | null {
  const clean = input.trim();
  const match = clean.match(/(?:steaminputdb\.com\/config\/|config\/|^)(\d{6,12})/i);
  return match ? match[1] : null;
}

/**
 * Automatically cross-references Steam App ID to pull community controller-to-keyboard mappings
 */
export async function fetchBestCommunityProfile(steamAppId: string): Promise<Partial<Profile> | null> {
  if (!steamAppId) return null;

  try {
    const res = await fetch(`https://steaminputdb.com/app/${steamAppId}/__data.json`, { mode: 'cors' });
    if (!res.ok) return null;
    const json = await res.json();
    const table = json.nodes?.[1]?.data;
    if (!table || !Array.isArray(table)) return null;

    // Find config objects that have file_url
    const configItems = table.filter((item: any) => item && typeof item === 'object' && 'file_url' in item);
    if (configItems.length === 0) return null;

    // Resolve first config's file_url
    const firstConfig = configItems[0];
    const fileUrlRef = firstConfig.file_url;
    const fileUrl = typeof fileUrlRef === 'number' ? table[fileUrlRef] : fileUrlRef;

    if (fileUrl && typeof fileUrl === 'string' && fileUrl.includes('steamusercontent.com')) {
      const vdfRes = await fetch(fileUrl, { mode: 'cors' });
      if (vdfRes.ok) {
        const vdfText = await vdfRes.text();
        return parseSteamVdfToProfile(vdfText);
      }
    }
  } catch (err) {
    console.debug('Failed to auto-pull community mapping from SteamInputDB:', err);
  }
  return null;
}

/**
 * Fetches config and game details from SteamInputDB's data endpoint
 */
export async function fetchSteamInputDbConfig(urlOrId: string): Promise<DiscoveredGame | null> {
  const fileId = parseSteamInputDbUrl(urlOrId);
  if (!fileId) return null;

  try {
    const res = await fetch(`https://steaminputdb.com/config/${fileId}/__data.json`, { mode: 'cors' });
    if (!res.ok) return null;
    const json = await res.json();

    // SvelteKit data de-serialization
    const node = json.nodes?.[1]?.data;
    if (!node || !Array.isArray(node)) return null;

    // Find strings in the de-serialized table
    const strings = node.filter((item: any) => typeof item === 'string');
    const title = strings.find((s: string) => s.length > 3 && !s.startsWith('http') && !s.includes('/') && !s.includes('Steamdeck')) || `SteamInput Layout #${fileId}`;
    const desc = strings.find((s: string) => s.length > 20 && !s.startsWith('http')) || 'Community controller layout imported from SteamInputDB.';

    // Look for app_id in numbers
    const appIdNum = node.find((item: any) => typeof item === 'number' && item > 1000 && item < 40000000);
    const appIdStr = appIdNum ? String(appIdNum) : undefined;

    // Look for cover assets
    const heroAsset = strings.find((s: string) => s.includes('capsule_616x353') || s.includes('header'));
    const coverUrl = appIdStr
      ? `https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/${appIdStr}/library_600x900.jpg`
      : heroAsset
      ? `https://shared.fastly.steamstatic.com/store_item_assets/${heroAsset}`
      : 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop&q=80';

    // Game title
    const gameName = strings.find((s: string) => s.length > 2 && s.length < 50 && !s.includes('http') && !s.includes('layout') && !s.includes('config')) || title;

    // Look for file_url and fetch/parse raw VDF
    const fileUrl = strings.find((s: string) => s.includes('cdn.steamusercontent.com'));
    let defaultProfile: Partial<Profile> | undefined;
    if (fileUrl) {
      try {
        const vdfRes = await fetch(fileUrl, { mode: 'cors' });
        if (vdfRes.ok) {
          const vdfText = await vdfRes.text();
          defaultProfile = parseSteamVdfToProfile(vdfText);
        }
      } catch (e) {
        console.debug('Failed to fetch raw VDF:', e);
      }
    }

    return {
      id: `sidb-${fileId}`,
      name: `${gameName} (${title})`,
      genre: 'Steam Community Layout',
      coverUrl,
      fallbackCoverUrl: coverUrl,
      description: `${desc}\n\nImported from SteamInputDB (Config #${fileId})`,
      steamAppId: appIdStr,
      source: 'steaminputdb',
      steamInputDbUrl: `https://steaminputdb.com/config/${fileId}`,
      defaultProfile,
    };
  } catch (err) {
    console.warn('Failed to fetch SteamInputDB config:', err);
    return null;
  }
}

const RAWG_STORAGE_KEY = 'dexpad_rawg_key_v1';
// Public developer key for RAWG to work out-of-the-box
export const DEFAULT_RAWG_KEY = '53fcca8a79254f09b99257fc5e2bf2ba';

export function getRawgApiKey(): string {
  const envKey = (import.meta as any).env?.VITE_RAWG_API_KEY;
  if (envKey && envKey.trim()) {
    return envKey.trim();
  }
  return localStorage.getItem(RAWG_STORAGE_KEY) || DEFAULT_RAWG_KEY;
}

export function setRawgApiKey(key: string): void {
  if (key.trim()) {
    localStorage.setItem(RAWG_STORAGE_KEY, key.trim());
  } else {
    localStorage.removeItem(RAWG_STORAGE_KEY);
  }
}

/**
 * Generate smart controller archetype based on detected genres
 */
function generateArchetypeByGenre(genres: string[]): Partial<Profile> | undefined {
  const gLower = genres.map((g) => g.toLowerCase());

  if (gLower.some((g) => g.includes('shooter') || g.includes('fps'))) {
    return {
      sticks: {
        left: { mode: 'digital_keys', deadzone: 160, up: 'w', down: 's', left: 'a', right: 'd' },
        right: { mode: 'mouse', deadzone: 40, sensitivity: 1.5, curve: 'linear' },
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
    };
  }

  if (gLower.some((g) => g.includes('platformer') || g.includes('metroidvania') || g.includes('fighting'))) {
    return {
      sticks: {
        left: {
          mode: 'digital_keys',
          deadzone: 150,
          up: 'KEY_UP_ARROW',
          down: 'KEY_DOWN_ARROW',
          left: 'KEY_LEFT_ARROW',
          right: 'KEY_RIGHT_ARROW',
        },
        right: { mode: 'none', deadzone: 50 },
      },
      buttons: {
        a: { type: 'key', code: 'z' },
        b: { type: 'key', code: 'c' },
        x: { type: 'key', code: 'x' },
        y: { type: 'key', code: 'a' },
        l1: { type: 'key', code: 'KEY_TAB' },
        r1: { type: 'key', code: 's' },
        l4: { type: 'key', code: 'c' },
        r4: { type: 'key', code: 'a' },
        r2: { type: 'key', code: 'KEY_LEFT_SHIFT', threshold: 40 },
        menu: { type: 'key', code: 'KEY_ESC' },
        home: { type: 'key', code: 'KEY_TAB' },
      },
    };
  }

  if (gLower.some((g) => g.includes('racing') || g.includes('driving'))) {
    return {
      sticks: {
        left: { mode: 'digital_keys', deadzone: 120, up: 'w', down: 's', left: 'a', right: 'd' },
        right: { mode: 'mouse', deadzone: 50, sensitivity: 1.2 },
      },
      buttons: {
        a: { type: 'key', code: 'KEY_SPACE' }, // Handbrake
        b: { type: 'key', code: 'b' },
        x: { type: 'key', code: 'KEY_LEFT_SHIFT' }, // Shift Up
        y: { type: 'key', code: 'KEY_LEFT_CTRL' },  // Shift Down
        l2: { type: 'key', code: 's', threshold: 40 }, // Brake / Reverse
        r2: { type: 'key', code: 'w', threshold: 40 }, // Throttle
      },
    };
  }

  // Blank mapping by default for general/unknown games
  return undefined;
}

/**
 * Searches games using RAWG API, extracting Steam App IDs for 600x900 vertical art,
 * with graceful fallback to RAWG background images and our curated offline database.
 */
export async function searchGames(query: string): Promise<DiscoveredGame[]> {
  const cleanQ = query.trim().toLowerCase();

  // 1. Check curated local matches first
  const localMatches = GAMES_DATABASE.filter((g) => {
    if (!cleanQ) return true;
    return (
      g.name.toLowerCase().includes(cleanQ) ||
      g.keywords.some((k) => k.toLowerCase().includes(cleanQ)) ||
      g.genre.toLowerCase().includes(cleanQ)
    );
  }).map((g): DiscoveredGame => {
    const steamMatch = g.coverUrl.match(/steam\/apps\/(\d+)/);
    const steamAppId = steamMatch ? steamMatch[1] : undefined;
    return {
      id: g.id,
      name: g.name,
      genre: g.genre,
      coverUrl: g.coverUrl,
      fallbackCoverUrl: g.coverUrl,
      description: g.description,
      steamAppId,
      steamInputDbUrl: steamAppId ? `https://steaminputdb.com/app/${steamAppId}` : undefined,
      source: 'curated',
      defaultProfile: g.defaultProfile,
    };
  });

  if (!cleanQ) {
    return localMatches.slice(0, 16);
  }

  // 2. Query RAWG API
  try {
    // 2. Query RAWG API (Filtered strictly to PC, macOS, PS5, Xbox Series, Switch to eliminate mobile/shovelware)
    const apiKey = getRawgApiKey();
    const url = `https://api.rawg.io/api/games?key=${apiKey}&search=${encodeURIComponent(cleanQ)}&platforms=4,5,187,186,7&page_size=16`;
    const res = await fetch(url, { mode: 'cors' });

    if (res.ok) {
      const data = await res.json();
      if (data && Array.isArray(data.results)) {
        const rawgGames: DiscoveredGame[] = data.results.map((rawgItem: any): DiscoveredGame => {
          // Check for Steam store connection
          let steamAppId: string | undefined;
          if (Array.isArray(rawgItem.stores)) {
            const steamStore = rawgItem.stores.find(
              (s: any) =>
                s.store?.slug === 'steam' ||
                s.store?.id === 1 ||
                (s.url && s.url.includes('store.steampowered.com/app/'))
            );
            if (steamStore?.url) {
              const match = steamStore.url.match(/\/app\/(\d+)/);
              if (match) {
                steamAppId = match[1];
              }
            }
          }

          // Build genre list
          const genresList = Array.isArray(rawgItem.genres)
            ? rawgItem.genres.map((g: any) => g.name)
            : [];
          const genreStr = genresList.slice(0, 2).join(' / ') || 'Action';

          // Authentic Box Art resolution:
          // If Steam App ID exists, use official 600x900 vertical Steam library poster;
          // otherwise fallback to RAWG high-res background art.
          const steamCover = steamAppId
            ? `https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/${steamAppId}/library_600x900.jpg`
            : undefined;
          const rawgCover = rawgItem.background_image || '';

          // Look for curated preset mapping
          const curated = GAMES_DATABASE.find(
            (g) => g.name.toLowerCase() === rawgItem.name.toLowerCase()
          );

          const rawRelease = rawgItem.released || '';
          const formattedRel = formatReleaseDate(rawRelease);
          const dev = Array.isArray(rawgItem.developers) && rawgItem.developers.length > 0
            ? rawgItem.developers.map((d: any) => d.name).join(', ')
            : undefined;

          return {
            id: rawgItem.id,
            name: rawgItem.name,
            genre: genreStr,
            coverUrl: steamCover || curated?.coverUrl || rawgCover,
            fallbackCoverUrl: rawgCover || curated?.coverUrl || '',
            description: rawgItem.description_raw || `Released: ${formattedRel || 'N/A'} • Rating: ${rawgItem.rating || 'N/A'}/5`,
            steamAppId,
            steamInputDbUrl: steamAppId ? `https://steaminputdb.com/app/${steamAppId}` : undefined,
            source: 'rawg',
            defaultProfile: curated?.defaultProfile || generateArchetypeByGenre(genresList),
            released: rawRelease,
            formattedRelease: formattedRel,
            rating: typeof rawgItem.rating === 'number' ? rawgItem.rating : undefined,
            metacritic: typeof rawgItem.metacritic === 'number' ? rawgItem.metacritic : undefined,
            developer: dev,
          };
        });

        // Merge RAWG results with local curated matches (deduping by lowercase name)
        const seen = new Set<string>();
        const merged: DiscoveredGame[] = [];

        // Put exact local curated matches first
        for (const loc of localMatches) {
          const key = loc.name.toLowerCase();
          if (!seen.has(key)) {
            seen.add(key);
            merged.push(loc);
          }
        }

        // Then add online RAWG results
        for (const rg of rawgGames) {
          const key = rg.name.toLowerCase();
          if (!seen.has(key)) {
            seen.add(key);
            merged.push(rg);
          }
        }

        return merged;
      }
    }
  } catch (err) {
    console.warn('RAWG API query failed or offline, falling back to local database:', err);
  }

  // 3. Fallback when RAWG fails or is offline
  return localMatches;
}
