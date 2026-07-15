export const PRODUCT_TIME_ZONE = import.meta.env.VITE_PRODUCT_TIME_ZONE || 'Asia/Taipei'
export const PRODUCT_TIME_ZONE_LABEL = 'UTC+8'

const DATE_PART_FORMATTER = new Intl.DateTimeFormat('en-CA', {
  timeZone: PRODUCT_TIME_ZONE,
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
})

export function getProductDateString(value = new Date()) {
  const parts = Object.fromEntries(
    DATE_PART_FORMATTER.formatToParts(value)
      .filter(({ type }) => type !== 'literal')
      .map(({ type, value: partValue }) => [type, partValue])
  )
  return `${parts.year}-${parts.month}-${parts.day}`
}

export function addCalendarDays(dateString, offset) {
  const [year, month, day] = dateString.split('-').map(Number)
  const date = new Date(Date.UTC(year, month - 1, day + offset))
  return date.toISOString().slice(0, 10)
}

export function formatProductDate(value, { includeYear = false } = {}) {
  return new Intl.DateTimeFormat('zh-TW', {
    timeZone: PRODUCT_TIME_ZONE,
    ...(includeYear ? { year: 'numeric' } : {}),
    month: '2-digit',
    day: '2-digit',
  }).format(new Date(value))
}

export function getProductTimeParts(value) {
  const parts = Object.fromEntries(
    new Intl.DateTimeFormat('en-GB', {
      timeZone: PRODUCT_TIME_ZONE,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hourCycle: 'h23',
    })
      .formatToParts(new Date(value))
      .filter(({ type }) => type !== 'literal')
      .map(({ type, value: partValue }) => [type, partValue])
  )
  return parts
}

export function formatProductDateTime(value) {
  const parts = getProductTimeParts(value)
  return `${parts.year}/${parts.month}/${parts.day} ${parts.hour}:${parts.minute}`
}
