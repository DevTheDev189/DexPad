/**
 * Media Storage Utility powered by IndexedDB
 * Bypasses the 5MB browser localStorage quota limit, allowing persistent
 * storage of 4K/8K images, animated videos, and media assets with zero file-size restrictions.
 */

const DB_NAME = 'dexpad_media_db_v1';
const DB_VERSION = 1;
const STORE_NAME = 'media_blobs';

export const MEDIA_KEY_THEME_IMAGE = 'theme_custom_image';
export const MEDIA_KEY_THEME_VIDEO = 'theme_custom_video';

let dbPromise: Promise<IDBDatabase> | null = null;

function getDatabase(): Promise<IDBDatabase> {
  if (dbPromise) return dbPromise;

  dbPromise = new Promise<IDBDatabase>((resolve, reject) => {
    if (typeof window === 'undefined' || !window.indexedDB) {
      reject(new Error('IndexedDB not supported in this environment'));
      return;
    }

    const request = window.indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME);
      }
    };

    request.onsuccess = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;
      db.onclose = () => {
        dbPromise = null;
      };
      resolve(db);
    };

    request.onerror = (event) => {
      dbPromise = null;
      reject((event.target as IDBOpenDBRequest).error);
    };
  });

  return dbPromise;
}

/**
 * Persist a media string (data URL, base64, or blob URL) into IndexedDB.
 */
export async function saveMediaItem(key: string, data: string): Promise<void> {
  try {
    const db = await getDatabase();
    return new Promise<void>((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readwrite');
      const store = tx.objectStore(STORE_NAME);
      const req = store.put(data, key);

      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  } catch (err) {
    console.warn(`[mediaStorage] Failed to save media '${key}':`, err);
  }
}

/**
 * Retrieve a media item from IndexedDB by key.
 */
export async function getMediaItem(key: string): Promise<string | null> {
  try {
    const db = await getDatabase();
    return new Promise<string | null>((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readonly');
      const store = tx.objectStore(STORE_NAME);
      const req = store.get(key);

      req.onsuccess = () => {
        resolve((req.result as string) || null);
      };
      req.onerror = () => reject(req.error);
    });
  } catch (err) {
    console.warn(`[mediaStorage] Failed to load media '${key}':`, err);
    return null;
  }
}

/**
 * Remove a media item from IndexedDB.
 */
export async function deleteMediaItem(key: string): Promise<void> {
  try {
    const db = await getDatabase();
    return new Promise<void>((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readwrite');
      const store = tx.objectStore(STORE_NAME);
      const req = store.delete(key);

      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  } catch (err) {
    console.warn(`[mediaStorage] Failed to delete media '${key}':`, err);
  }
}
