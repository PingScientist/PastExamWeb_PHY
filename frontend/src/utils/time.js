import { formatProductDateTime } from './productTimezone'

export function formatExactDateTime24h(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'

  return formatProductDateTime(date)
}

export function formatRelativeOrAbsoluteDateTime(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'

  const now = new Date()
  const diffInMs = Math.max(now - date, 0)
  const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60))
  const diffInDays = Math.floor(diffInHours / 24)

  if (diffInDays === 0) {
    if (diffInHours === 0) {
      const diffInMinutes = Math.floor(diffInMs / (1000 * 60))
      if (diffInMinutes < 1) {
        return '剛剛'
      } else if (diffInMinutes < 60) {
        return `${diffInMinutes} 分鐘前`
      }
    }
    return `${diffInHours} 小時前`
  } else if (diffInDays === 1) {
    return '昨天'
  } else if (diffInDays < 7) {
    return `${diffInDays} 天前`
  }

  return formatExactDateTime24h(date)
}

export function formatRelativeTime(value) {
  return formatRelativeOrAbsoluteDateTime(value)
}
