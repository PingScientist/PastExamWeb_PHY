import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import process from 'node:process'
import { describe, expect, it } from 'vitest'

const adminSource = readFileSync(resolve(process.cwd(), 'src/views/Admin.vue'), 'utf8')
const durationChartSource = readFileSync(
  resolve(process.cwd(), 'src/components/UserOnlineDurationChart.vue'),
  'utf8'
)

const getRule = (source, selector) => {
  const escapedSelector = selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const matches = [
    ...source.matchAll(new RegExp(`(?:^|\\n)${escapedSelector}\\s*\\{([^}]+)\\}`, 'g')),
  ]
  return matches.at(-1)?.[1] || ''
}

describe('user statistics chart layout styles', () => {
  it('keeps the primary and secondary control rows compact without changing card padding', () => {
    const cardRule = getRule(adminSource, '.admin-insights-card')
    const userCardRule = getRule(adminSource, '.user-insights.admin-insights-card')

    expect(cardRule).toContain('padding: 0.85rem')
    expect(userCardRule).toContain('row-gap: 0.5rem')
    expect(adminSource).not.toContain(
      '<p class="user-insights__description">{{ loginDistributionDescription }}</p>'
    )
  })

  it('matches the user data statistics bar gap without changing either data grid', () => {
    const userStatisticsBars = getRule(adminSource, '.user-login-column-chart__bars')
    const durationBars = getRule(durationChartSource, '.user-duration-chart__bars')

    expect(userStatisticsBars).toContain('gap: clamp(1px, 0.25vw, 3px)')
    expect(durationBars).toContain('gap: clamp(1px, 0.25vw, 3px)')
    expect(adminSource).toContain(
      'grid-template-columns: repeat(var(--login-chart-columns), minmax(0, 1fr))'
    )
  })
})
