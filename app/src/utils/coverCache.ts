/**
 * Caches game covers to local storage / disk for persistent offline access.
 */
export async function cacheGameCover(gameId: string, url: string): Promise<string> {
  const cacheKey = `dexpad_cover_${gameId}`;
  const existing = localStorage.getItem(cacheKey);
  if (existing) {
    return existing;
  }

  // Attempt to fetch and store as data URL
  try {
    const response = await fetch(url, { mode: 'cors' });
    if (response.ok) {
      const blob = await response.blob();
      return new Promise<string>((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64 = reader.result as string;
          try {
            localStorage.setItem(cacheKey, base64);
          } catch (e) {
            console.warn('Storage quota exceeded, preserving direct image URL:', e);
          }
          resolve(base64);
        };
        reader.onerror = () => resolve(url);
        reader.readAsDataURL(blob);
      });
    }
  } catch (err) {
    // If CORS or offline, fallback to the direct URL
    console.debug('Direct URL preserved for cover:', gameId, err);
  }

  return url;
}

export function getCachedGameCover(gameId: string, fallbackUrl?: string): string {
  const cacheKey = `dexpad_cover_${gameId}`;
  const stored = localStorage.getItem(cacheKey);
  if (stored && (stored.includes('wikimedia.org') || stored.length < 10)) {
    localStorage.removeItem(cacheKey);
    return fallbackUrl || '';
  }
  return stored || fallbackUrl || '';
}
