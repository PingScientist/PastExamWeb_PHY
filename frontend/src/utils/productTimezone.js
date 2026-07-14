export const PRODUCT_TIME_ZONE = import.meta.env.VITE_PRODUCT_TIME_ZONE || 'Asia/Taipei'

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
