import { formatProductDate, getProductTimeParts } from './productTimezone'

export function resolveTemporalLabelEvery({
  baseLabelEvery,
  chartWidth,
  pointCount,
  mode,
  fontScale = 1,
}) {
  const base = Math.max(1, Math.floor(Number(baseLabelEvery) || 1))
  const width = Number(chartWidth)
  const count = Math.max(0, Math.floor(Number(pointCount) || 0))
  if (!Number.isFinite(width) || width <= 0 || count <= 2) return base

  const scale = Math.min(1.5, Math.max(0.5, Number(fontScale) || 1))
  const minimumLabelWidth = (mode === 'hour' ? 44 : 48) * scale
  const visibleLabelCapacity = Math.max(2, Math.floor(width / minimumLabelWidth))
  const responsiveEvery = Math.ceil((count - 1) / Math.max(1, visibleLabelCapacity - 1))

  return Math.max(base, responsiveEvery)
}

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
