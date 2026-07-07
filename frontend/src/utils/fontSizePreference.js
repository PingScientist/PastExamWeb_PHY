import { getLocalItem, setLocalItem } from './storage'

export const FONT_SIZE_STORAGE_KEY = 'personal-settings-font-size'

export const FONT_SIZE_OPTIONS = [
  { label: '小', value: 'small', scale: 0.9 },
  { label: '預設', value: 'default', scale: 1 },
  { label: '大', value: 'large', scale: 1.1 },
  { label: '特大', value: 'x-large', scale: 1.2 },
]

export function getFontSizePreference() {
  const stored = getLocalItem(FONT_SIZE_STORAGE_KEY)
  return FONT_SIZE_OPTIONS.some((option) => option.value === stored) ? stored : 'default'
}

export function getFontSizeOption(value) {
  return FONT_SIZE_OPTIONS.find((option) => option.value === value) || FONT_SIZE_OPTIONS[1]
}

export function applyFontSizePreference(value = getFontSizePreference()) {
  const option = getFontSizeOption(value)

  if (typeof document !== 'undefined') {
    document.documentElement.style.setProperty('--app-font-scale', String(option.scale))
    document.documentElement.dataset.appFontSize = option.value
  }

  return option
}

export function setFontSizePreference(value) {
  const option = getFontSizeOption(value)
  setLocalItem(FONT_SIZE_STORAGE_KEY, option.value)
  applyFontSizePreference(option.value)
  return option
}
