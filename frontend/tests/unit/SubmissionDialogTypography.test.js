import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import process from 'node:process'
import { afterEach, describe, expect, it } from 'vitest'
import { actualScaleFromDisplayPercent, applyFontSizePreference } from '@/utils/fontSizePreference'

const frontendRoot = resolve(process.cwd())
const styleSource = readFileSync(`${frontendRoot}/src/style.css`, 'utf8')
const adminSource = readFileSync(`${frontendRoot}/src/views/Admin.vue`, 'utf8')
const archiveSource = readFileSync(`${frontendRoot}/src/views/Archive.vue`, 'utf8')

describe('submission dialog typography', () => {
  afterEach(() => {
    applyFontSizePreference(100)
  })

  it.each([
    [50, '0.45'],
    [100, '0.9'],
    [150, '1.35'],
  ])('applies %s%% immediately through the authoritative root scale', (percent, scale) => {
    expect(actualScaleFromDisplayPercent(percent)).toBe(Number(scale))
    applyFontSizePreference(percent)

    expect(document.documentElement.style.getPropertyValue('--app-font-scale')).toBe(scale)
    expect(document.documentElement.dataset.appFontSizeDisplayPercent).toBe(String(percent))
    expect(styleSource).toContain('--app-font-size-base: calc(1rem * var(--app-font-scale))')
  })

  it('scopes all three dialogs and the teleported Select options to the same scaled token', () => {
    expect(adminSource).toContain('header="考古題投稿詳情"')
    expect(adminSource).toContain('header="使用者資料統計"')
    expect(archiveSource).toContain('header="我的投稿狀態"')
    expect(adminSource.match(/class="[^"]*submission-typography-dialog/g)).toHaveLength(2)
    expect(archiveSource).toContain('class="submission-typography-dialog"')
    expect(adminSource.match(/overlayClass="submission-typography-overlay"/g)).toHaveLength(2)
    expect(styleSource).toMatch(
      /\.submission-typography-overlay[\s\S]*font-size: var\(--app-font-size-base\)/
    )
    expect(styleSource).not.toMatch(
      /\.submission-typography-dialog\s*\{[^}]*calc\([^)]*--app-font-scale/
    )
  })

  it('keeps the statistics footer outside the scrollable content with its own action spacing', () => {
    const contentEnd = adminSource.indexOf('</div>\n        <template #footer>')
    const footerStart = adminSource.indexOf('<template #footer>', contentEnd)
    const closeButton = adminSource.indexOf('class="user-data-stats-dialog__close"', footerStart)

    expect(contentEnd).toBeGreaterThan(-1)
    expect(footerStart).toBeGreaterThan(contentEnd)
    expect(closeButton).toBeGreaterThan(footerStart)
    expect(styleSource).toMatch(/\.user-data-stats-dialog .*__content[\s\S]*overflow-y: auto/)
    expect(styleSource).toMatch(/\.user-data-stats-dialog .*__footer[\s\S]*padding: 1rem 1\.5rem/)
    expect(styleSource).toMatch(
      /\.user-data-stats-dialog .*__footer[\s\S]*border-top: 1px solid var\(--border-color\)/
    )
  })

  it('places the online duration chart before submission data in the renamed dialog', () => {
    const dialogTitle = adminSource.indexOf('header="使用者資料統計"')
    const chart = adminSource.indexOf('<UserOnlineDurationChart', dialogTitle)
    const submissionSummary = adminSource.indexOf('class="user-submission-summary"', chart)

    expect(dialogTitle).toBeGreaterThan(-1)
    expect(chart).toBeGreaterThan(dialogTitle)
    expect(submissionSummary).toBeGreaterThan(chart)
    expect(adminSource).toContain('aria-label="查看使用者資料統計"')
    expect(adminSource).not.toContain('查看使用者投稿統計')
  })
})
