import { adminTest as test, expect } from '../support/adminTest'
import { JSON_HEADERS } from '../support/constants'
import { clickWhenVisible } from '../support/ui'

const COURSES_FIXTURE = {
  freshman: [
    { id: 101, name: '普通物理(一)' },
    { id: 102, name: '電磁學(一)' },
  ],
  sophomore: [],
  junior: [],
  senior: [],
  graduate: [],
  interdisciplinary: [],
}

const ARCHIVES_FIXTURE: Record<number, Array<Record<string, unknown>>> = {
  101: [
    {
      id: 201,
      academic_year: 2024,
      name: '期末考',
      archive_type: 'final',
      professor: '王教授',
      has_answers: true,
      download_count: 12,
      uploader_id: 9,
    },
  ],
  102: [
    {
      id: 301,
      academic_year: 2023,
      name: '期中考',
      archive_type: 'midterm',
      professor: '李教授',
      has_answers: false,
      download_count: 7,
      uploader_id: 10,
    },
  ],
}

test.describe('Admin › Archive management', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/notifications/active', async (route) => {
      await route.fulfill({
        status: 200,
        headers: JSON_HEADERS,
        body: JSON.stringify([]),
      })
    })

    await page.route('**/api/courses', async (route) => {
      if (route.request().method() !== 'GET') {
        await route.continue()
        return
      }

      await route.fulfill({
        status: 200,
        headers: JSON_HEADERS,
        body: JSON.stringify(COURSES_FIXTURE),
      })
    })

    await page.route('**/api/courses/*/archives', async (route) => {
      if (route.request().method() !== 'GET') {
        await route.continue()
        return
      }

      const courseIdMatch = route
        .request()
        .url()
        .match(/courses\/(\d+)\/archives/)
      const courseId = courseIdMatch ? Number(courseIdMatch[1]) : null
      const responseBody = courseId ? (ARCHIVES_FIXTURE[courseId] ?? []) : []

      await route.fulfill({
        status: 200,
        headers: JSON_HEADERS,
        body: JSON.stringify(responseBody),
      })
    })
  })

  test('allows searching courses and opening upload dialog', async ({ page }) => {
    await page.goto('/archive')
    await expect(page).toHaveURL(/\/archive$/)

    const uploadButton = page.getByRole('button', { name: '上傳考古題' })
    await expect(uploadButton).toBeVisible({ timeout: 15000 })

    const searchInput = page.getByPlaceholder('搜尋課程')
    await expect(searchInput).toBeVisible({ timeout: 15000 })
    await searchInput.fill('普通物理')

    const courseButton = page.getByRole('button', { name: '普通物理(一)' }).first()
    await expect(courseButton).toBeVisible({ timeout: 15000 })
    await Promise.all([
      page.waitForResponse((response) => {
        return (
          response.url().includes('/api/courses/') &&
          response.url().endsWith('/archives') &&
          response.request().method() === 'GET'
        )
      }),
      clickWhenVisible(courseButton),
    ])

    const selectedSubject = page.locator('span.font-medium', {
      hasText: '普通物理(一)',
    })
    await expect(selectedSubject).toBeVisible({ timeout: 15000 })

    await clickWhenVisible(uploadButton)

    const uploadDialog = page.getByRole('dialog', { name: '上傳考古題' })
    await expect(uploadDialog).toBeVisible({ timeout: 10000 })
    await expect(uploadDialog.getByRole('tab', { name: '選擇課程' })).toBeVisible()
    await expect(uploadDialog.getByRole('tab', { name: '考試資訊' })).toBeVisible()
  })

  test('persists last selected course across reloads', async ({ page }) => {
    await page.goto('/archive')

    const searchInput = page.getByPlaceholder('搜尋課程')
    await searchInput.fill('電磁學')

    const courseButton = page.getByRole('button', { name: '電磁學(一)' }).first()
    await Promise.all([
      page.waitForResponse((response) => {
        return (
          response.url().includes('/api/courses/') &&
          response.url().endsWith('/archives') &&
          response.request().method() === 'GET'
        )
      }),
      clickWhenVisible(courseButton),
    ])

    const selectionTag = page.locator('span.font-medium', { hasText: '電磁學(一)' })
    await expect(selectionTag).toBeVisible({ timeout: 15000 })

    await page.reload()

    await expect(page).toHaveURL(/\/archive$/)
    await expect(selectionTag).toBeVisible({ timeout: 15000 })
  })
})
