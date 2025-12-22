/**
 * Locale detection and management utilities
 */

import type { Locale } from '../i18n';

const LOCALE_STORAGE_KEY = 'todo-locale';
const LOCALE_COOKIE_KEY = 'todo-locale';

/**
 * Get locale from cookie or localStorage
 */
export function getStoredLocale(): Locale | null {
  // Try cookie first
  if (typeof document !== 'undefined') {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === LOCALE_COOKIE_KEY) {
        return value as Locale;
      }
    }
  }

  // Try localStorage
  if (typeof localStorage !== 'undefined') {
    const stored = localStorage.getItem(LOCALE_STORAGE_KEY);
    if (stored && ['en', 'ur'].includes(stored)) {
      return stored as Locale;
    }
  }

  return null;
}

/**
 * Detect locale from browser settings
 */
export function detectLocale(): Locale {
  // Check stored preference
  const stored = getStoredLocale();
  if (stored) return stored;

  // Detect from browser
  if (typeof navigator !== 'undefined') {
    const browserLang = navigator.language.toLowerCase();

    // Check for Urdu (ur, ur-PK, ur-IN, etc.)
    if (browserLang.startsWith('ur')) {
      return 'ur';
    }

    // Default to English
    return 'en';
  }

  return 'en';
}

/**
 * Set locale preference
 */
export function setLocale(locale: Locale): void {
  if (typeof document !== 'undefined') {
    // Set cookie
    document.cookie = `${LOCALE_COOKIE_KEY}=${locale}; path=/; max-age=31536000; sameSite=lax`;
  }

  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(LOCALE_STORAGE_KEY, locale);
  }
}
