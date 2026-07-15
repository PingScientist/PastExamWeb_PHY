import { describe, expect, it } from 'vitest'
import { buildOnlineDurationSummary, formatDuration } from '@/utils/onlineDurationSummary'
import { buildTemporalTicks } from '@/utils/temporalChart'
import { buildDurationAxis, formatDurationAxisTick } from '@/utils/durationAxis'

const makePoints = ({ start, count, bucketMinutes, durations = {} }) =>
  Array.from({ length: count }, (_, index) => {
    const pointStart = new Date(new Date(start).getTime() + index * bucketMinutes * 60_000)
    return {
      start: pointStart.toISOString(),
      end: new Date(pointStart.getTime() + bucketMinutes * 60_000).toISOString(),
      duration_seconds: durations[index] ?? 0,
    }
  })

describe('temporal chart helpers', () => {
  it.each([
    [24, 10, 12],
    [48, 20, 18],
    [72, 30, 18],
  ])(
    'keeps %s-hour data intact and renders midnight ticks on separate lines',
    (hours, minutes, every) => {
      const points = makePoints({
        start: '2026-07-12T18:00:00Z',
        count: 144,
        bucketMinutes: minutes,
      })
      const ticks = buildTemporalTicks(points, {
        mode: 'hour',
        labelEvery: every,
        minGap: Math.max(6, Math.floor(every / 2)),
      })

      expect(ticks).toHaveLength(144)
      expect(ticks[0].showLabel).toBe(true)
      expect(ticks.at(-1).showLabel).toBe(true)
      const midnight = ticks.find((tick) => tick.isMultiline)
      expect(midnight.labelLines).toHaveLength(2)
      expect(midnight.labelLines[0]).toBe('00 時')
      expect(midnight.labelLines[1]).toMatch(/^\d{2}\/\d{2}$/)
      expect(midnight.labelLines.join('')).not.toMatch(/23 時\d{2}/)
    }
  )

  it.each([
    [7, 1],
    [30, 5],
    [90, 15],
  ])('preserves %s daily points and complete first/last date ticks', (days, every) => {
    const points = makePoints({
      start: '2026-04-16T16:00:00Z',
      count: days,
      bucketMinutes: 24 * 60,
    })
    const ticks = buildTemporalTicks(points, { mode: 'date', labelEvery: every })

    expect(ticks).toHaveLength(days)
    expect(ticks[0]).toMatchObject({ showLabel: true, labelLines: ['04/17'] })
    expect(ticks.at(-1).showLabel).toBe(true)
    expect(ticks.at(-1).labelLines[0]).toMatch(/^\d{2}\/\d{2}$/)
    expect(ticks.every(({ labelLines }) => labelLines.length === 1)).toBe(true)
    expect(ticks.filter(({ showLabel }) => showLabel).length).toBeLessThanOrEqual(
      Math.ceil((days - 1) / every) + 1
    )
  })
})

describe('online duration summaries', () => {
  it('uses 24 hours for a completed historical day', () => {
    const points = makePoints({
      start: '2026-07-13T16:00:00Z',
      count: 24,
      bucketMinutes: 60,
      durations: { 1: 3600, 2: 900 },
    })
    expect(buildOnlineDurationSummary({ points, mode: 'hourly', days: 7, isToday: false })).toEqual(
      { totalSeconds: 4500, averageSeconds: 187.5, peakSeconds: 3600 }
    )
  })

  it('uses elapsed partial hours today without counting future zero buckets', () => {
    const points = makePoints({
      start: '2026-07-14T16:00:00Z',
      count: 24,
      bucketMinutes: 60,
      durations: { 1: 3600, 4: 900 },
    })
    const summary = buildOnlineDurationSummary({
      points,
      mode: 'hourly',
      days: 7,
      isToday: true,
      nowMs: new Date('2026-07-14T20:20:00Z').getTime(),
    })
    expect(summary.totalSeconds).toBe(4500)
    expect(summary.averageSeconds).toBeCloseTo(4500 / (4 + 20 / 60))
    expect(summary.peakSeconds).toBe(3600)
  })

  it.each([7, 30, 90])('includes zero days in the %s-day average', (days) => {
    const points = makePoints({
      start: '2026-04-16T16:00:00Z',
      count: days,
      bucketMinutes: 24 * 60,
      durations: { 0: 3600, 1: 1800 },
    })
    expect(buildOnlineDurationSummary({ points, mode: 'daily', days, isToday: true })).toEqual({
      totalSeconds: 5400,
      averageSeconds: 5400 / days,
      peakSeconds: 3600,
    })
  })

  it('formats seconds, minutes and hours without excessive decimals', () => {
    expect(formatDuration(0)).toBe('0 秒')
    expect(formatDuration(45)).toBe('45 秒')
    expect(formatDuration(480)).toBe('8 分鐘')
    expect(formatDuration(3900)).toBe('1 小時 5 分鐘')
  })
})

describe('duration chart axis', () => {
  it('keeps fractional daily-hour ticks distinguishable', () => {
    const values = [0, 0.5, 1, 1.5, 2, 2.5, 3]
    const labels = values.map((value) => formatDurationAxisTick(value, 'hours'))

    expect(labels).toEqual([
      '0 分鐘',
      '30 分鐘',
      '1 小時',
      '1 小時 30 分鐘',
      '2 小時',
      '2 小時 30 分鐘',
      '3 小時',
    ])
    expect(new Set(labels).size).toBe(labels.length)
    expect(buildDurationAxis({ mode: 'daily', maxValue: 2.5 })).toEqual({
      yMax: 3,
      yTicks: [3, 2.5, 2, 1.5, 1, 0.5, 0],
    })
  })

  it('preserves the current-day minute axis', () => {
    expect(buildDurationAxis({ mode: 'hourly', maxValue: 19 })).toEqual({
      yMax: 60,
      yTicks: [60, 45, 30, 15, 0],
    })
    expect(formatDurationAxisTick(30, 'minutes')).toBe('30 分')
  })
})
