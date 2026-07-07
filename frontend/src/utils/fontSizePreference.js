import { getLocalItem, setLocalItem } from './storage'

export const FONT_SIZE_STORAGE_KEY = 'personal-settings-font-size'

export const FONT_SIZE_MIN = 0.85
export const FONT_SIZE_MAX = 1.25
export const FONT_SIZE_STEP = 0.01
export const FONT_SIZE_DEFAULT = 1

const LEGACY_FONT_SIZE_SCALE = {
  small: 0.9,
  default: 1,
  large: 1.1,
  'x-large': 1.2,
}

function normalizeFontSizeScale(value) {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) {
    return FONT_SIZE_DEFAULT
  }

  const clamped = Math.min(FONT_SIZE_MAX, Math.max(FONT_SIZE_MIN, numeric))
  return Number(clamped.toFixed(2))
}

export function getFontSizePreference() {
  const stored = getLocalItem(FONT_SIZE_STORAGE_KEY)
  return normalizeFontSizeScale(LEGACY_FONT_SIZE_SCALE[stored] ?? stored)
}

export function applyFontSizePreference(value = getFontSizePreference()) {
  const scale = normalizeFontSizeScale(value)

  if (typeof document !== 'undefined') {
    document.documentElement.style.setProperty('--app-font-scale', String(scale))
    document.documentElement.dataset.appFontSize = String(scale)
  }

  return scale
}

export function setFontSizePreference(value) {
  const scale = normalizeFontSizeScale(value)
  setLocalItem(FONT_SIZE_STORAGE_KEY, String(scale))
  applyFontSizePreference(scale)
  return scale
}
