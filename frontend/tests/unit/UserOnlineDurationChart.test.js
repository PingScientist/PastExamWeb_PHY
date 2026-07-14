import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import process from 'node:process'
import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import UserOnlineDurationChart from '@/components/UserOnlineDurationChart.vue'
import { applyFontSizePreference } from '@/utils/fontSizePreference'

const getUserOnlineDurationMock = vi.hoisted(() => vi.fn())

vi.mock('@/api', () => ({
  getUserOnlineDuration: getUserOnlineDurationMock,
}))

const componentSource = readFileSync(
  resolve(process.cwd(), 'src/components/UserOnlineDurationChart.vue'),
  'utf8'
)

const makeResponse = ({ mode = 'hourly', days = 7, history = true } = {}) => {
  const count = mode === 'hourly' ? 24 : days
  const bucketMs = mode === 'hourly' ? 3_600_000 : 86_400_000
  const rangeStart = Date.UTC(2026, 6, 15) - (mode === 'daily' ? (days - 1) * bucketMs : 0)
  const points = Array.from({ length: count }, (_, index) => ({
    start: new Date(rangeStart + index * bucketMs).toISOString(),
    end: new Date(rangeStart + (index + 1) * bucketMs).toISOString(),
    duration_seconds: index === 13 ? (mode === 'hourly' ? 1920 : 9300) : 0,
    has_data: history,
  }))
  return {
    user_id: 7,
    mode,
    timezone: 'UTC',
    online_timeout_seconds: 300,
    range_start: points[0].start,
    range_end: points.at(-1).end,
    history_started_at: history ? points[0].start : null,
    points,
  }
}

const stubs = {
  Select: {
    props: ['modelValue', 'options'],
    template: '<select aria-label="選擇最近七日日期"><option>{{ modelValue }}</option></select>',
  },
  ProgressSpinner: { template: '<span class="spinner" />' },
  Message: { template: '<div class="message"><slot /></div>' },
  Button: { props: ['label'], template: '<button>{{ label }}</button>' },
}

const mountChart = () =>
  mount(UserOnlineDurationChart, {
    props: { userId: 7, active: true },
    global: { stubs },
  })

describe('UserOnlineDurationChart', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-07-15T15:30:00Z'))
    getUserOnlineDurationMock.mockReset()
    getUserOnlineDurationMock.mockImplementation((_userId, options) =>
      Promise.resolve({ data: makeResponse({ mode: options.mode, days: options.days }) })
    )
  })

  afterEach(() => {
    applyFontSizePreference(100)
    vi.useRealTimers()
  })

  it('defaults to today hourly mode and renders exactly 24 accessible bars before submission data', async () => {
    const wrapper = mountChart()
    await flushPromises()

    expect(getUserOnlineDurationMock).toHaveBeenCalledWith(
      7,
      expect.objectContaining({ mode: 'hourly', date: '2026-07-15' })
    )
    expect(wrapper.text()).toContain('當日在線時長紀錄')
    expect(wrapper.text()).toContain('每日在線時長紀錄')
    expect(wrapper.findAll('.user-duration-chart__item')).toHaveLength(24)
    expect(wrapper.find('[aria-label="選擇最近七日日期"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('在線時長：32 分鐘')
    expect(wrapper.find('canvas').exists()).toBe(false)
    expect(componentSource).not.toContain('收合')
  })

  it.each([7, 30, 90])(
    'loads and renders %s daily points without horizontal data padding',
    async (days) => {
      const wrapper = mountChart()
      await flushPromises()
      await wrapper.findAll('.user-duration-switch button')[1].trigger('click')
      await flushPromises()
      const rangeButton = wrapper
        .findAll('.user-duration-range button')
        .find((button) => button.text() === `${days} 日`)
      if (days !== 7) {
        await rangeButton.trigger('click')
        await flushPromises()
      }

      expect(getUserOnlineDurationMock).toHaveBeenLastCalledWith(
        7,
        expect.objectContaining({ mode: 'daily', days })
      )
      expect(wrapper.findAll('.user-duration-chart__item')).toHaveLength(days)
    }
  )

  it('keeps loading, empty, malformed and request failure states distinct', async () => {
    let resolveRequest
    getUserOnlineDurationMock.mockReturnValueOnce(
      new Promise((resolve) => {
        resolveRequest = resolve
      })
    )
    const wrapper = mountChart()
    expect(wrapper.text()).toContain('載入在線時長紀錄')
    resolveRequest({ data: makeResponse({ history: false }) })
    await flushPromises()
    expect(wrapper.text()).toContain('目前尚無紀錄')

    getUserOnlineDurationMock.mockResolvedValueOnce({ data: { points: [] } })
    await wrapper.findAll('.user-duration-switch button')[1].trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('在線時長載入失敗')
    expect(wrapper.findAll('.user-duration-chart__item')).toHaveLength(0)
  })

  it('uses the authoritative font tokens at 50, 100 and 150 percent without a chart instance', async () => {
    const wrapper = mountChart()
    await flushPromises()

    for (const [percent, scale] of [
      [50, '0.45'],
      [100, '0.9'],
      [150, '1.35'],
    ]) {
      applyFontSizePreference(percent)
      expect(document.documentElement.style.getPropertyValue('--app-font-scale')).toBe(scale)
      expect(wrapper.findAll('.user-duration-chart')).toHaveLength(1)
    }

    expect(componentSource).toMatch(/user-duration-chart__y-axis[\s\S]*var\(--app-font-size-xs\)/)
    expect(componentSource).toMatch(/user-duration-chart__tooltip[\s\S]*var\(--app-font-size-xs\)/)
    expect(componentSource).toMatch(/user-duration-switch button[\s\S]*var\(--app-font-size-xs\)/)
    expect(componentSource).not.toMatch(/font-size:\s*(11|12)px/)
    expect(componentSource).not.toContain('overflow-x: auto')
  })
})
