const FULL_TO_HALF_PARENTHESIS = {
  '（': '(',
  '）': ')',
}

const HALF_TO_FULL_PARENTHESIS = {
  '(': '（',
  ')': '）',
}

const fullToHalfRegex = new RegExp(`[${Object.keys(FULL_TO_HALF_PARENTHESIS).join('')}]`, 'g')
const halfToFullRegex = new RegExp(`[${Object.keys(HALF_TO_FULL_PARENTHESIS).join('')}]`, 'g')

export const formatCourseDisplayName = (value) => {
  if (value == null) return ''
  return String(value)
    .replace(halfToFullRegex, (char) => HALF_TO_FULL_PARENTHESIS[char])
    .trim()
}

export const normalizeCourseSearchText = (value) => {
  if (value == null) return ''
  return String(value)
    .replace(fullToHalfRegex, (char) => FULL_TO_HALF_PARENTHESIS[char])
    .replace(/\s+/g, '')
    .replace(/[()（）]/g, '')
    .toLowerCase()
    .trim()
}
