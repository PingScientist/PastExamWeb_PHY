export function formatDuration(value) {
  const totalSeconds = Math.max(0, Math.round(Number(value) || 0))
  if (totalSeconds === 0) return '0 秒'
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60
  const parts = []
  if (hours) parts.push(`${hours} 小時`)
  if (minutes) parts.push(`${minutes} 分鐘`)
  if (!hours && !minutes && seconds) parts.push(`${seconds} 秒`)
  return parts.join(' ')
}

export function buildOnlineDurationSummary({ points, mode, days, isToday, nowMs = Date.now() }) {
  const totalSeconds = points.reduce((sum, point) => sum + point.duration_seconds, 0)
  const peakSeconds = Math.max(0, ...points.map(({ duration_seconds }) => duration_seconds))
  if (mode === 'daily') {
    return {
      totalSeconds,
      averageSeconds: totalSeconds / days,
      peakSeconds,
    }
  }

  const elapsedSeconds = isToday
    ? points.reduce((sum, point) => {
        const start = new Date(point.start).getTime()
        const end = new Date(point.end).getTime()
        const elapsed = Math.max(0, Math.min(nowMs, end) - start)
        return sum + Math.min(end - start, elapsed) / 1000
      }, 0)
    : 24 * 3600
  return {
    totalSeconds,
    averageSeconds: elapsedSeconds > 0 ? totalSeconds / (elapsedSeconds / 3600) : 0,
    peakSeconds,
  }
}
