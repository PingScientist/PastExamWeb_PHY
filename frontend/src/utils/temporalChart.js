import { formatProductDate, getProductTimeParts } from './productTimezone'

function selectVisibleTicks(points, { labelEvery, includeMidnights, minGap }) {
  if (points.length === 0) return new Set()
  const lastIndex = points.length - 1
  const priorityIndexes = new Set([0, lastIndex])
  if (includeMidnights) {
    points.forEach((point, index) => {
      const { hour, minute } = getProductTimeParts(point.start)
      if (hour === '00' && minute === '00') priorityIndexes.add(index)
    })
  }

  const visibleIndexes = new Set(priorityIndexes)
  points.forEach((_point, index) => {
    if (index % labelEvery !== 0 || visibleIndexes.has(index)) return
    if ([...priorityIndexes].every((priorityIndex) => Math.abs(priorityIndex - index) >= minGap)) {
      visibleIndexes.add(index)
    }
  })
  return visibleIndexes
}

export function buildTemporalTicks(points, { mode, labelEvery, minGap = mode === 'hour' ? 8 : 1 }) {
  const includeMidnights = mode === 'hour'
  const visibleIndexes = selectVisibleTicks(points, {
    labelEvery,
    includeMidnights,
    minGap,
  })

  return points.map((point, index) => {
    const parts = getProductTimeParts(point.start)
    const isMidnight = parts.hour === '00' && parts.minute === '00'
    const labelLines =
      mode === 'date'
        ? [formatProductDate(point.start)]
        : isMidnight
          ? [`${parts.hour} 時`, formatProductDate(point.start)]
          : [`${parts.hour} 時`]
    return {
      labelLines,
      showLabel: visibleIndexes.has(index),
      isMultiline: labelLines.length > 1,
    }
  })
}
