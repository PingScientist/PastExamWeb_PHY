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

  it('places review submission statistics before review search and reuses chart styling', () => {
    const statisticsIndex = adminSource.indexOf('id="review-submission-insights-title"')
    const searchIndex = adminSource.indexOf('class="review-search-toolbar')

    expect(statisticsIndex).toBeGreaterThan(-1)
    expect(searchIndex).toBeGreaterThan(statisticsIndex)
    expect(adminSource).toContain('統計時區：{{ PRODUCT_TIME_ZONE_LABEL }}')
    expect(adminSource).toContain(':aria-label="reviewSubmissionChartData.ariaLabel"')
    expect(adminSource).toContain('class="user-login-column-chart__bar"')
  })

  it('centers shared summaries and keeps the mobile controls above one three-column row', () => {
    expect(adminSource).toMatch(
      /\.admin-insights-card \.chart-summary-item\s*\{[^}]*justify-items: center;[^}]*text-align: center;/s
    )
    expect(adminSource).toMatch(
      /@media \(max-width: 640px\)[\s\S]*?\.admin-insights-card \.chart-summary-control-row\s*\{[^}]*grid-template-areas:[^}]*'controls'[^}]*'summary'[^}]*'timezone'/
    )
    expect(adminSource).toMatch(
      /\.admin-insights-card \.chart-summary-group\s*\{[^}]*grid-template-columns: repeat\(3, minmax\(0, 1fr\)\)/s
    )
    expect(adminSource).toMatch(
      /\.admin-insights-card \.chart-control-stack \.user-insights__range\s*\{[^}]*width: max-content;[^}]*justify-self: end;/s
    )
  })

  it('right-aligns only the mobile statistics controls and observes the effective x-axis', () => {
    expect(adminSource).toMatch(
      /@media \(max-width: 640px\)[\s\S]*?\.user-insights__actions\s*\{[^}]*justify-content: flex-end;/
    )
    expect(adminSource).toMatch(
      /@media \(max-width: 640px\)[\s\S]*?\.user-insights__switch\s*\{[^}]*margin-inline-start: auto;[^}]*justify-content: flex-end;/
    )
    expect(adminSource).toContain(
      'ref="userStatisticsChartElement"\n                          class="user-login-column-chart__x-axis"'
    )
    expect(adminSource).toContain(
      'ref="reviewSubmissionChartElement"\n                          class="user-login-column-chart__x-axis"'
    )
  })

  it('uses a simple mobile-only level tag without changing the desktop level cell', () => {
    expect(adminSource).toContain('Lv{{ user.contributorLevel.level }}')
    expect(adminSource).toContain('class="user-card-contributor-badge"')
    expect(adminSource).toMatch(
      /\.mobile-user-level-tag\s*\{[^}]*display: none;[\s\S]*?@media \(max-width: 640px\)[\s\S]*?\.admin-mobile-list--users \.mobile-user-level-tag\s*\{[^}]*display: inline-flex;/
    )
    expect(adminSource).toMatch(
      /@media \(max-width: 640px\)[\s\S]*?\.admin-mobile-list--users \.user-card-contributor-badge\s*\{[^}]*display: none;/
    )
    expect(adminSource).toContain('Lv. {{ data.contributorLevel.level }}')
  })
})
