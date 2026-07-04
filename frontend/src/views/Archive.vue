<template>
  <div
    class="h-full archive-screen"
    :class="{ 'archive-dark': isDarkTheme }"
    ref="archiveView"
    @toggle-sidebar="toggleSidebar"
  >
    <div class="flex h-full relative">
      <!-- Desktop/Tablet Sidebar -->
      <div class="sidebar hidden md:block" :class="{ collapsed: !sidebarVisible }">
        <div class="sidebar-shell">
          <!-- Fixed search section -->
          <div class="search-section p-3">
            <div class="relative w-full">
              <i class="pi pi-search absolute left-4 top-1/2 -mt-2 text-500"></i>
              <InputText v-model="searchQuery" placeholder="搜尋課程" class="w-full pl-6" />
            </div>
          </div>

          <!-- Scrollable content section -->
          <div class="course-list-section p-3 pt-0">
            <div v-if="searchQuery" class="search-results">
              <div v-if="filteredCategories.length === 0" class="p-3 text-center text-500">
                <i class="pi pi-search text-2xl mb-2"></i>
                <div>查無搜尋結果</div>
              </div>
              <div v-for="category in filteredCategories" :key="category.label" class="mb-2">
                <div class="text-sm mb-1" style="color: var(--text-secondary)">
                  {{ category.label }}
                </div>
                <div class="flex flex-col gap-1">
                  <Button
                    v-for="course in category.items"
                    :key="course.label"
                    :class="[
                      'p-button-text search-result-btn text-color',
                      { 'active-course-search-result': selectedCourse === course.id },
                    ]"
                    @click="filterBySubject({ label: course.label, id: course.id })"
                  >
                    <span class="ellipsis">{{ course.label }}</span>
                  </Button>
                </div>
              </div>
            </div>
            <PanelMenu
              v-else
              :model="menuItems"
              :expandedKeys="expandedMenuItems"
              @update:expandedKeys="expandedMenuItems = $event"
              class="w-full"
            />
          </div>

          <!-- Fixed upload section for desktop -->
          <div v-if="isAuthenticatedRef" class="upload-section p-3">
            <div class="upload-actions">
              <Button
                icon="pi pi-cloud-upload"
                label="上傳考古題"
                severity="success"
                @click="showUploadDialog = true"
                class="w-full"
                size="small"
              />
              <Button
                icon="pi pi-list-check"
                label="我的投稿狀態"
                severity="secondary"
                outlined
                @click="openSubmissionStatus"
                class="w-full"
                size="small"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Mobile Drawer -->
      <Drawer
        v-if="isMobile"
        :visible="sidebarVisible"
        @update:visible="sidebarVisible = $event"
        :class="['mobile-drawer', { 'mobile-drawer-dark': isDarkTheme }]"
        position="left"
        :style="{ width: 'min(100vw, 26rem)' }"
        :autoFocus="false"
        :pt="{
          mask: {
            class: isDarkTheme
              ? 'mobile-drawer-mask mobile-drawer-mask-dark'
              : 'mobile-drawer-mask',
          },
        }"
      >
        <template #header>
          <div class="flex justify-content-between align-items-center w-full">
            <span class="font-semibold">選單</span>
          </div>
        </template>
        <div class="flex flex-column h-full">
          <!-- Fixed search section -->
          <div class="search-section pb-3">
            <div class="relative w-full">
              <i class="pi pi-search absolute left-4 top-1/2 -mt-2 text-500"></i>
              <InputText v-model="searchQuery" placeholder="搜尋課程" class="w-full pl-6" />
            </div>
          </div>

          <!-- Scrollable course selection section -->
          <div class="flex-1 overflow-auto">
            <div v-if="searchQuery" class="search-results">
              <div v-if="filteredCategories.length === 0" class="p-3 text-center text-500">
                <i class="pi pi-search text-2xl mb-2"></i>
                <div>查無搜尋結果</div>
              </div>
              <div v-for="category in filteredCategories" :key="category.label" class="mb-2">
                <div class="text-sm mb-1" style="color: var(--text-secondary)">
                  {{ category.label }}
                </div>
                <div class="flex flex-col gap-1">
                  <Button
                    v-for="course in category.items"
                    :key="course.label"
                    :class="[
                      'p-button-text search-result-btn text-color',
                      { 'active-course-search-result': selectedCourse === course.id },
                    ]"
                    @click="
                      () => {
                        filterBySubject({ label: course.label, id: course.id })
                        sidebarVisible = false
                      }
                    "
                  >
                    <span class="ellipsis">{{ course.label }}</span>
                  </Button>
                </div>
              </div>
            </div>
            <PanelMenu v-else :model="mobileMenuItems" multiple class="w-full" />
          </div>

          <div v-if="isAuthenticatedRef" class="upload-section mobile-upload-section">
            <div class="upload-actions">
              <Button
                icon="pi pi-cloud-upload"
                label="上傳考古"
                severity="success"
                @click="openUploadFromMobileMenu"
                class="w-full"
                size="small"
              />
              <Button
                icon="pi pi-list-check"
                label="我的投稿狀態"
                severity="secondary"
                outlined
                @click="openSubmissionStatusFromMobileMenu"
                class="w-full"
                size="small"
              />
            </div>
          </div>
        </div>
      </Drawer>

      <div class="main-content flex-1 h-full overflow-auto">
        <div class="card h-full flex flex-col">
          <div v-if="selectedSubject" class="subject-header">
            <div class="subject-title-block">
              <Tag severity="secondary" class="subject-tag">
                {{ currentCategoryLabel }}
              </Tag>
              <div>
                <div class="subject-title">{{ selectedSubject }}</div>
                <div class="subject-subtitle">
                  <span>共 {{ archiveTotalCount }} 份考古題</span>
                  <span>最新：{{ latestAcademicTerm }}</span>
                </div>
              </div>
            </div>
          </div>
          <Toolbar v-if="selectedSubject" class="archive-filter-bar mx-3 mt-3 mb-2">
            <template #start>
              <div class="archive-filter-shell">
                <div class="filter-summary">
                  目前顯示：{{ selectedSubject }} · 共 {{ filteredArchiveCount }} 份考古題
                </div>
                <div class="archive-filter-controls">
                  <Select
                    v-model="filters.year"
                    :options="years"
                    optionLabel="name"
                    optionValue="code"
                    placeholder="學期"
                    class="filter-select"
                    showClear
                    filter
                  />
                  <Select
                    v-model="filters.professor"
                    :options="professors"
                    optionLabel="name"
                    optionValue="code"
                    placeholder="教授"
                    class="filter-select"
                    showClear
                    filter
                  />
                  <Select
                    v-model="filters.type"
                    :options="archiveTypes"
                    optionLabel="name"
                    optionValue="code"
                    placeholder="類型"
                    class="filter-select"
                    showClear
                  />
                  <div class="answer-filter">
                    <Checkbox v-model="filters.hasAnswers" :binary="true" inputId="hasAnswersFilter" />
                    <label for="hasAnswersFilter">附解答</label>
                  </div>
                </div>
              </div>
            </template>
          </Toolbar>

          <ProgressSpinner
            v-if="loading"
            class="w-full flex justify-content-center mt-4"
            strokeWidth="4"
          />

          <div v-else>
            <div v-if="selectedSubject">
              <Accordion
                v-model:value="expandedPanels"
                multiple
                class="max-w-[calc(100%-2rem)] mx-auto"
              >
                <AccordionPanel
                  v-for="group in groupedArchives"
                  :key="group.year"
                  :value="group.year.toString()"
                >
                  <AccordionHeader>
                    <div class="term-header-content">
                      <span class="term-title">{{ formatAcademicTerm(group.year) }}</span>
                      <span class="term-count">{{ group.list.length }} 份</span>
                    </div>
                  </AccordionHeader>
                  <AccordionContent>
                    <div class="archive-card-grid">
                      <article v-for="data in group.list" :key="data.id" class="archive-record-card">
                        <div class="archive-record-content">
                          <div class="archive-record-line archive-record-primary-line">
                            <div class="archive-record-title-group">
                              <Tag
                                :severity="archiveTypeConfig[data.type]?.severity || 'secondary'"
                                class="exam-type-tag"
                              >
                              {{ archiveTypeConfig[data.type]?.name || data.type }}
                              </Tag>
                              <h3>{{ data.name }}</h3>
                            </div>
                            <div class="archive-record-actions">
                              <Button
                                icon="pi pi-eye"
                                @click="previewArchive(data)"
                                size="small"
                                severity="secondary"
                                label="預覽"
                                outlined
                                class="archive-action-preview"
                              />
                              <Button
                                icon="pi pi-download"
                                @click="downloadArchive(data)"
                                size="small"
                                severity="success"
                                label="下載"
                                :loading="downloadingId === data.id"
                                class="archive-action-download"
                              />
                              <Button
                                v-if="canEditArchive(data)"
                                icon="pi pi-pencil"
                                @click="openEditDialog(data)"
                                size="small"
                                severity="secondary"
                                label="編輯"
                                outlined
                                aria-label="編輯"
                                class="archive-action-edit"
                              />
                              <Button
                                v-if="canDeleteArchive(data)"
                                icon="pi pi-trash"
                                @click="confirmDelete(data)"
                                size="small"
                                severity="danger"
                                text
                                rounded
                                aria-label="刪除"
                                class="archive-action-icon archive-action-danger"
                              />
                            </div>
                          </div>
                          <div class="archive-record-line archive-record-meta-line">
                            <span>{{ data.professor }}</span>
                            <span>{{ formatAnswerStatus(data) }}</span>
                            <span>{{ formatDownloadCount(data.downloadCount) }} 次下載</span>
                            <span v-if="isAdmin && formatSourceSubmissionIds(data)">
                              投稿編號：{{ formatSourceSubmissionIds(data) }}
                            </span>
                          </div>
                        </div>
                      </article>
                    </div>
                  </AccordionContent>
                </AccordionPanel>
              </Accordion>
            </div>
            <div
              v-else
              class="flex flex-column align-items-center justify-content-center h-full"
              style="min-height: calc(100vh - 200px)"
            >
              <i class="pi pi-book text-6xl" style="color: var(--text-secondary)"></i>
              <div class="text-xl font-medium mt-4" style="color: var(--text-secondary)">
                請從左側選單選擇課程
              </div>
              <div class="text-sm mt-2" style="color: var(--text-secondary)">
                選擇課程後即可瀏覽相關考古題
              </div>
            </div>
          </div>

          <PdfPreviewModal
            :visible="showPreview"
            @update:visible="showPreview = $event"
            :courseId="selectedCourse"
            :archiveId="selectedArchive?.id"
            :previewUrl="selectedArchive?.previewUrl"
            :title="selectedArchive?.name || ''"
            :academicYear="selectedArchive?.year"
            :archiveType="selectedArchive?.type || ''"
            :courseName="selectedSubject || ''"
            :professorName="selectedArchive?.professor || ''"
            :loading="previewLoading"
            :error="previewError"
            @hide="closePreview"
            @error="handlePreviewError"
            @download="handlePreviewDownload"
          />

          <UploadArchiveDialog
            v-model="showUploadDialog"
            :coursesList="coursesList"
            :courseCategories="courseCategories"
            @upload-success="handleUploadSuccess"
          />

          <Dialog
            v-model:visible="showSubmissionStatusDialog"
            header="我的投稿狀態"
            modal
            :draggable="false"
            :style="{ width: '760px', maxWidth: '94vw' }"
          >
            <ProgressSpinner v-if="submissionStatusLoading" class="w-full flex justify-content-center my-4" />
            <div v-else class="submission-status-list">
              <section>
                <h3>考古題投稿</h3>
                <div v-if="archiveSubmissions.length === 0" class="submission-empty">目前沒有考古題投稿</div>
                <article v-for="item in archiveSubmissions" :key="`archive-${item.id}`" class="submission-status-card">
                  <div class="submission-status-head">
                    <Tag
                      :class="['submission-status-badge', getSubmissionStatusClass(item.status)]"
                      :severity="getSubmissionSeverity(item.status)"
                    >
                      {{ getSubmissionLabel(item.status) }}
                    </Tag>
                    <Tag
                      v-if="item.is_admin_upload"
                      class="submission-admin-badge"
                      severity="secondary"
                    >
                      管理員投稿
                    </Tag>
                    <div class="submission-status-title">
                      <strong>{{ item.subject }}</strong>
                      <span>{{ item.name }}</span>
                    </div>
                  </div>
                  <div class="submission-status-meta">
                    <span><i class="pi pi-send"></i>{{ getArchiveSubmissionKind(item) }}</span>
                    <span><i class="pi pi-calendar"></i>{{ formatAcademicTerm(item.academic_year) }}</span>
                    <span><i class="pi pi-user"></i>{{ item.professor }}</span>
                  </div>
                  <div v-if="item.requested_category_name" class="submission-status-note">
                    <span>新分類</span>
                    <strong>{{ item.requested_category_name }}</strong>
                    <small>{{ item.requested_category_key }}</small>
                  </div>
                  <div v-if="shouldShowReviewNote(item)" class="submission-status-note is-review">
                    <span>審核備註</span>
                    <strong>{{ item.review_note }}</strong>
                  </div>
                </article>
              </section>
            </div>
          </Dialog>

          <Dialog
            :visible="showEditDialog"
            @update:visible="showEditDialog = $event"
            :modal="true"
            :draggable="false"
            :closeOnEscape="false"
            header="編輯考古題"
            :style="{ width: '600px', maxWidth: '90vw' }"
            :autoFocus="false"
          >
            <div class="flex flex-column">
              <div class="flex flex-column gap-2">
                <label>考試名稱</label>
                <InputText v-model="editForm.name" placeholder="輸入考試名稱" class="w-full" />
              </div>

              <div class="flex flex-column gap-2 mt-3">
                <label>授課教授</label>
                <AutoComplete
                  :modelValue="editForm.professor"
                  @update:modelValue="(val) => (editForm.professor = val)"
                  :suggestions="availableEditProfessors"
                  @complete="searchEditProfessor"
                  @item-select="onEditProfessorSelect"
                  @focus="() => searchEditProfessor({ query: '' })"
                  @click="() => searchEditProfessor({ query: '' })"
                  optionLabel="name"
                  placeholder="選擇授課教授"
                  class="w-full"
                  dropdown
                  completeOnFocus
                  :minLength="0"
                  autoHighlight="true"
                >
                  <template #item="{ item }">
                    <div>{{ item.name }}</div>
                  </template>
                </AutoComplete>
              </div>

              <div class="flex flex-column gap-2 mt-3">
                <label>考試年份</label>
                <DatePicker
                  v-model="editForm.academicYear"
                  @update:modelValue="(val) => (editForm.academicYear = val)"
                  view="year"
                  dateFormat="yy"
                  :showIcon="true"
                  placeholder="選擇考試年份"
                  class="w-full"
                  :maxDate="new Date()"
                  :minDate="new Date(2000, 0, 1)"
                />
              </div>

              <div class="flex flex-column gap-2 mt-3">
                <label>考試類型</label>
                <Select
                  v-model="editForm.type"
                  :options="[
                    { name: '期中考', value: 'midterm' },
                    { name: '期末考', value: 'final' },
                    { name: '小考', value: 'quiz' },
                    { name: '其他', value: 'other' },
                  ]"
                  optionLabel="name"
                  optionValue="value"
                  placeholder="選擇考試類型"
                  class="w-full"
                />
              </div>

              <div class="flex align-items-center gap-2 mt-3">
                <Checkbox v-model="editForm.hasAnswers" :binary="true" />
                <label>附解答</label>
              </div>

              <Divider class="mt-3" />

              <div class="flex align-items-center gap-2">
                <Checkbox v-model="editForm.shouldTransfer" :binary="true" />
                <label class="font-semibold">轉移到其他課程</label>
              </div>

              <div v-if="editForm.shouldTransfer" class="flex flex-column pl-4 mt-3">
                <div class="flex flex-column gap-2">
                  <label>目標課程類別</label>
                  <Select
                    v-model="editForm.targetCategory"
                    :options="categoryOptions"
                    optionLabel="name"
                    optionValue="value"
                    placeholder="選擇課程類別"
                    class="w-full"
                  />
                </div>

                <div class="flex flex-column gap-2 mt-3">
                  <label>目標課程名稱</label>
                  <AutoComplete
                    v-model="editForm.targetCourse"
                    :suggestions="availableCoursesForTransfer"
                    @complete="searchTargetCourse"
                    @item-select="onTargetCourseSelect"
                    @focus="() => searchTargetCourse({ query: '' })"
                    @click="() => searchTargetCourse({ query: '' })"
                    optionLabel="label"
                    placeholder="搜尋或輸入目標課程名稱"
                    class="w-full"
                    :disabled="!editForm.targetCategory"
                    dropdown
                    completeOnFocus
                    :minLength="0"
                    autoHighlight="true"
                  >
                    <template #item="{ item }">
                      <div>{{ item.label }}</div>
                    </template>
                  </AutoComplete>
                </div>
              </div>
            </div>
            <div class="flex pt-6 justify-end gap-2.5">
              <Button
                label="取消"
                icon="pi pi-times"
                severity="secondary"
                @click="closeEditDialog"
              />
              <Button
                :label="editForm.shouldTransfer ? '儲存並轉移' : '儲存'"
                :icon="editForm.shouldTransfer ? 'pi pi-arrow-right-arrow-left' : 'pi pi-check'"
                severity="success"
                @click="handleEdit"
                :loading="editLoading"
              />
            </div>
          </Dialog>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineOptions({
  name: 'ArchiveView',
})

import { ref, computed, onMounted, watch, inject, onBeforeUnmount } from 'vue'
import { courseService, archiveService } from '../api'
import PdfPreviewModal from '../components/PdfPreviewModal.vue'
import UploadArchiveDialog from '../components/UploadArchiveDialog.vue'
import { getCurrentUser, isAuthenticated } from '../utils/auth'
import { useTheme } from '../utils/useTheme'
import { trackEvent, EVENTS } from '../utils/analytics'
import { isUnauthorizedError } from '../utils/http'
import {
  STORAGE_KEYS,
  getLocalJson,
  setLocalJson,
  removeLocalItem,
  setSessionJson,
} from '../utils/storage'

const toast = inject('toast')
const confirm = inject('confirm')

const { isDarkTheme } = useTheme()
const sidebarVisible = inject('sidebarVisible')

// Check if we're on mobile
const isMobile = ref(false)

const checkDevice = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkDevice()
  window.addEventListener('resize', checkDevice)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkDevice)
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }
})

// Auth related data
const isAuthenticatedRef = ref(false)
const userData = ref(null)

const archives = ref([])
const loading = ref(true)
const filters = ref({
  year: '',
  professor: '',
  type: '',
  hasAnswers: false,
})

// Track filter changes
watch(
  filters,
  (newFilters, oldFilters) => {
    shouldResetPanels.value = true

    // Only track if at least one filter is active and different from old value
    const hasActiveFilter =
      newFilters.year || newFilters.professor || newFilters.type || newFilters.hasAnswers

    if (hasActiveFilter && oldFilters) {
      const changedFilters = {}
      if (newFilters.year !== oldFilters.year) changedFilters.year = !!newFilters.year
      if (newFilters.professor !== oldFilters.professor)
        changedFilters.professor = !!newFilters.professor
      if (newFilters.type !== oldFilters.type) changedFilters.type = !!newFilters.type
      if (newFilters.hasAnswers !== oldFilters.hasAnswers)
        changedFilters.hasAnswers = newFilters.hasAnswers

      if (Object.keys(changedFilters).length > 0) {
        trackEvent(EVENTS.FILTER_ARCHIVES, {
          activeFilters: {
            year: !!newFilters.year,
            professor: !!newFilters.professor,
            type: !!newFilters.type,
            hasAnswers: newFilters.hasAnswers,
          },
          changedFilters,
        })
      }
    }
  },
  { deep: true }
)

const showPreview = ref(false)
const selectedArchive = ref(null)
const selectedSubject = ref(null)
const selectedCourse = ref(null)
const showUploadDialog = ref(false)
const showSubmissionStatusDialog = ref(false)
const submissionStatusLoading = ref(false)
const archiveSubmissions = ref([])
const uploadFormProfessors = ref([])
const expandedPanels = ref([])
const expandedMenuItems = ref({})
const shouldResetPanels = ref(true)

const fallbackCategories = [
  { key: 'freshman', name: '基礎必修', icon: 'pi pi-fw pi-book', label: '基礎' },
  { key: 'sophomore', name: '專業必修', icon: 'pi pi-fw pi-compass', label: '必修' },
  { key: 'junior', name: '實驗課程', icon: 'pi pi-fw pi-sparkles', label: '實驗' },
  { key: 'senior', name: '專業選修', icon: 'pi pi-fw pi-book', label: '選修' },
  { key: 'graduate', name: '研究所', icon: 'pi pi-fw pi-graduation-cap', label: '研究所' },
  { key: 'interdisciplinary', name: '戳戳數學系', icon: 'pi pi-fw pi-calculator', label: '數學' },
]

const courseCategories = ref([...fallbackCategories])
const coursesList = ref({})
const categoryMap = computed(() =>
  courseCategories.value.reduce((acc, category) => {
    acc[category.key] = category
    return acc
  }, {})
)

const archiveTypeConfig = {
  midterm: {
    name: '期中考',
    severity: 'secondary',
  },
  final: {
    name: '期末考',
    severity: 'secondary',
  },
  quiz: {
    name: '小考',
    severity: 'secondary',
  },
  other: {
    name: '其他',
    severity: 'secondary',
  },
}

const years = ref([])
const professors = ref([])
const archiveTypes = ref([])

const searchQuery = ref('')

// Track search query changes with debounce
let searchDebounceTimer = null
watch(searchQuery, (newValue) => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }

  if (newValue && newValue.trim().length > 0) {
    searchDebounceTimer = setTimeout(() => {
      trackEvent(EVENTS.SEARCH_COURSE, {
        query: newValue,
        queryLength: newValue.length,
      })
    }, 1000) // 1 second debounce
  }
})

const ISSUE_CONTEXT_STORAGE_KEY = STORAGE_KEYS.session.ISSUE_CONTEXT

function persistIssueContext() {
  try {
    if (typeof window === 'undefined') return

    const selectedSubjectStored = getLocalJson(STORAGE_KEYS.local.SELECTED_SUBJECT)

    const payload = {
      page: 'archive',
      timestamp: new Date().toISOString(),
      course: {
        id: selectedCourse.value ?? selectedSubjectStored?.id ?? null,
        name: selectedSubject.value ?? selectedSubjectStored?.label ?? null,
      },
      filters: {
        year: filters.value?.year || null,
        professor: filters.value?.professor || null,
        type: filters.value?.type || null,
        hasAnswers: Boolean(filters.value?.hasAnswers),
        searchQuery: searchQuery.value || null,
      },
      preview: {
        open: Boolean(showPreview.value),
        archiveId: selectedArchive.value?.id ?? null,
        name: selectedArchive.value?.name ?? null,
        year: selectedArchive.value?.year ?? null,
        professor: selectedArchive.value?.professor ?? null,
        type: selectedArchive.value?.type ?? null,
        hasAnswers: selectedArchive.value?.hasAnswers ?? null,
      },
    }

    setSessionJson(ISSUE_CONTEXT_STORAGE_KEY, payload)
  } catch {
    // ignore
  }
}

watch(
  () => [
    selectedCourse.value,
    selectedSubject.value,
    showPreview.value,
    selectedArchive.value?.id,
    filters.value?.year,
    filters.value?.professor,
    filters.value?.type,
    filters.value?.hasAnswers,
    searchQuery.value,
  ],
  () => persistIssueContext(),
  { immediate: true }
)

const menuItems = computed(() => {
  if (!coursesList.value) return []

  return courseCategories.value.map((category) => ({
    key: category.key,
    label: category.name,
    icon: category.icon || 'pi pi-fw pi-book',
    items: (coursesList.value[category.key] || [])
      .map((course) => ({
        label: course.name,
        class: selectedCourse.value === course.id ? 'active-course-menu-item' : undefined,
        command: () => filterBySubject({ label: course.name, id: course.id }),
      }))
  }))
})

const filteredCategories = computed(() => {
  if (!searchQuery.value) {
    return []
  }

  const query = searchQuery.value.trim().toLowerCase().normalize('NFKC')
  const filtered = []

  menuItems.value.forEach((category) => {
    const filteredItems = category.items.filter((item) => {
      const itemLabelLower = item.label.toLowerCase().normalize('NFKC')
      const isIncluded = itemLabelLower.includes(query)
      return isIncluded
    })

    if (filteredItems.length > 0) {
      filtered.push({
        ...category,
        items: filteredItems
          .map((item) => {
            const course = (coursesList.value[getCategoryKey(category.label)] || []).find(
              (c) => c.name === item.label
            )
            return {
              label: item.label,
              id: course?.id,
            }
          })
      })
    }
  })

  return filtered
})

function getCategoryKey(categoryLabel) {
  return courseCategories.value.find((category) => category.name === categoryLabel)?.key || ''
}

function getCategoryKeyForCourse(courseId) {
  for (const [categoryKey, courses] of Object.entries(coursesList.value)) {
    if (courses.some((course) => course.id === courseId)) {
      return categoryKey
    }
  }
  return null
}

const groupedArchives = computed(() => {
  if (!archives.value) return []

  const filteredArchives = archives.value.filter((archive) => {
    if (filters.value.year && archive.year.toString() !== filters.value.year) return false
    if (filters.value.professor && archive.professor !== filters.value.professor) return false
    if (filters.value.type && archive.type !== filters.value.type) return false
    if (filters.value.hasAnswers && !archive.hasAnswers) return false
    return true
  })

  const groups = {}
  filteredArchives.forEach((archive) => {
    if (!groups[archive.year]) {
      groups[archive.year] = {
        year: archive.year,
        list: [],
      }
    }
    groups[archive.year].list.push(archive)
  })

  Object.values(groups).forEach((group) => {
    group.list.sort((a, b) => {
      // Define exam type priority
      const typePriority = {
        midterm: 1,
        final: 2,
        quiz: 3,
        other: 4,
      }

      const aPriority = typePriority[a.type] || 4
      const bPriority = typePriority[b.type] || 4

      if (aPriority !== bPriority) {
        return aPriority - bPriority
      }

      return a.name.localeCompare(b.name, 'en')
    })
  })

  return Object.values(groups).sort((a, b) => b.year - a.year)
})

const archiveTotalCount = computed(() => archives.value.length)

const filteredArchiveCount = computed(() =>
  groupedArchives.value.reduce((total, group) => total + group.list.length, 0)
)

const latestAcademicTerm = computed(() => {
  const latestYear = archives.value
    .map((archive) => Number(archive.year))
    .filter(Boolean)
    .sort((a, b) => b - a)[0]

  return latestYear ? formatAcademicTerm(latestYear) : '尚無資料'
})

function formatAcademicTerm(value) {
  const numericValue = Number(value)
  if (!numericValue) return ''
  if (numericValue >= 1000 && numericValue < 2000) {
    const year = Math.floor(numericValue / 10)
    const semester = numericValue % 10
    return `${year}${semester === 1 ? '上' : '下'}學期`
  }
  return `${numericValue} 年`
}

function formatSourceSubmissionIds(archive) {
  const ids = Array.isArray(archive?.sourceSubmissionIds)
    ? archive.sourceSubmissionIds.filter((id) => id !== null && id !== undefined)
    : []
  if (!ids.length) return ''
  return ids.map((id) => `#${id}`).join(', ')
}

async function fetchCourses() {
  try {
    loading.value = true
    const [categoriesResponse, coursesResponse] = await Promise.all([
      courseService.listCategories(),
      courseService.listCourses(),
    ])
    const categories = Array.isArray(categoriesResponse.data) && categoriesResponse.data.length
      ? categoriesResponse.data
      : fallbackCategories

    // Only update coursesList if the data has actually changed to prevent unnecessary re-renders
    const newData = coursesResponse.data || {}
    const currentData = coursesList.value
    const hasChanged = JSON.stringify(currentData) !== JSON.stringify(newData)

    courseCategories.value = categories.map((category, index) => ({
      key: category.key,
      name: category.name,
      label: category.label || category.name,
      icon: category.icon || 'pi pi-fw pi-book',
      order_index: category.order_index ?? index,
    }))

    if (hasChanged) {
      coursesList.value = newData
    }
  } catch (error) {
    console.error('Error fetching courses:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '載入失敗',
      detail: '無法載入課程資料',
      life: 3000,
    })
  } finally {
    loading.value = false
  }
}

function getSubmissionLabel(status) {
  const labels = {
    pending: '待審核',
    approved: '已通過',
    rejected: '未通過',
    deleted: '已刪除',
    takedown: '已下架',
    PENDING: '待審核',
    APPROVED: '已通過',
    REJECTED: '未通過',
    DELETED: '已刪除',
    TAKEDOWN: '已下架',
  }
  return labels[status] || status
}

function getNormalizedSubmissionStatus(status) {
  return String(status || '').toLowerCase()
}

function getSubmissionSeverity(status) {
  const normalized = getNormalizedSubmissionStatus(status)
  if (normalized === 'approved') return 'success'
  if (normalized === 'rejected') return 'danger'
  if (normalized === 'deleted') return 'danger'
  if (normalized === 'takedown') return 'secondary'
  return 'warning'
}

function getSubmissionStatusClass(status) {
  const normalized = getNormalizedSubmissionStatus(status)
  if (normalized === 'approved') return 'submission-status-approved'
  if (normalized === 'rejected') return 'submission-status-rejected'
  if (normalized === 'deleted') return 'submission-status-deleted'
  if (normalized === 'takedown') return 'submission-status-takedown'
  return 'submission-status-pending'
}

function getArchiveSubmissionKind(item) {
  if (item?.is_admin_upload) return '管理員投稿'
  if (item?.requested_category_key) return '新分類與新課程申請'
  if (item?.requested_course_name) return '新課程申請'
  return '既有課程投稿'
}

function isBoilerplateReviewNote(note) {
  const normalized = String(note || '').trim().toLowerCase()
  return !normalized || normalized === '管理員上傳' || normalized === 'admin upload' || normalized.startsWith('takedown_target:')
}

function shouldShowReviewNote(item) {
  return Boolean(item?.review_note) && !isBoilerplateReviewNote(item.review_note)
}

async function loadSubmissionStatus() {
  submissionStatusLoading.value = true
  try {
    const archiveResponse = await archiveService.listMySubmissions()
    archiveSubmissions.value = Array.isArray(archiveResponse.data) ? archiveResponse.data : []
  } catch (error) {
    console.error('Load submission status error:', error)
    if (isUnauthorizedError(error)) return
    toast.add({
      severity: 'error',
      summary: '載入失敗',
      detail: '無法載入投稿狀態',
      life: 3000,
    })
  } finally {
    submissionStatusLoading.value = false
  }
}

async function openSubmissionStatus() {
  showSubmissionStatusDialog.value = true
  await loadSubmissionStatus()
}

function openUploadFromMobileMenu() {
  sidebarVisible.value = false
  showUploadDialog.value = true
}

async function openSubmissionStatusFromMobileMenu() {
  sidebarVisible.value = false
  await openSubmissionStatus()
}

function filterBySubject(course) {
  trackEvent(EVENTS.SELECT_COURSE, {
    courseName: course.label,
    courseId: course.id,
  })

  selectedSubject.value = course.label
  selectedCourse.value = course.id
  filters.value.professor = ''
  filters.value.year = ''
  filters.value.type = ''
  expandedPanels.value = []
  shouldResetPanels.value = true

  const categoryKey = getCategoryKeyForCourse(course.id)
  if (categoryKey) {
    expandedMenuItems.value = { [categoryKey]: true }
    // console.log("Expanding category:", categoryKey, expandedMenuItems.value);
  }

  setLocalJson(STORAGE_KEYS.local.SELECTED_SUBJECT, { label: course.label, id: course.id })

  fetchArchives()
}

async function fetchArchives() {
  try {
    loading.value = true
    const response = await courseService.getCourseArchives(selectedCourse.value)
    const archiveRows = Array.isArray(response.data) ? response.data : []
    if (!Array.isArray(response.data)) {
      throw new Error('Archive list response is not an array')
    }
    archives.value = archiveRows
      .filter((archive) => archive && archive.id !== null && archive.id !== undefined)
      .map((archive) => ({
        id: archive.id,
        year: archive.academic_year || '',
        name: archive.name || '未命名考古題',
        type: archive.archive_type || 'other',
        professor: archive.professor || '—',
        hasAnswers: Boolean(archive.has_answers),
        subject: selectedSubject.value,
        uploader_id: archive.uploader_id || null,
        downloadCount: Number(archive.download_count || 0),
        sourceSubmissionIds: Array.isArray(archive.source_submission_ids) ? archive.source_submission_ids : [],
      }))

    const uniqueYears = new Set()
    const uniqueProfessors = new Set()
    const uniqueTypes = new Set()

    archives.value.forEach((archive) => {
      if (archive.year) uniqueYears.add(archive.year.toString())
      if (archive.professor) uniqueProfessors.add(archive.professor)
      if (archive.type) uniqueTypes.add(archive.type)
    })

    years.value = Array.from(uniqueYears)
      .sort((a, b) => b - a)
      .map((year) => ({
        name: formatAcademicTerm(year),
        code: year,
      }))

    professors.value = Array.from(uniqueProfessors)
      .sort()
      .map((professor) => ({
        name: professor,
        code: professor,
      }))

    archiveTypes.value = Array.from(uniqueTypes)
      .sort()
      .map((type) => ({
        name: archiveTypeConfig[type]?.name || type,
        code: type,
      }))
  } catch (error) {
    console.error('Error fetching archives:', error)
    archives.value = []
    years.value = []
    professors.value = []
    archiveTypes.value = []
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '載入失敗',
      detail: '無法載入考古題資料',
      life: 3000,
    })
  } finally {
    loading.value = false
  }
}

const downloadingId = ref(null)

async function syncArchiveDownloadCount(archiveId) {
  if (!selectedCourse.value) return

  const previousExpandedPanels = [...expandedPanels.value]
  const resetRequested = shouldResetPanels.value

  try {
    const response = await courseService.getCourseArchives(selectedCourse.value)
    const serverMap = new Map(response.data.map((item) => [item.id, item]))

    archives.value = archives.value.map((archive) => {
      const serverArchive = serverMap.get(archive.id)
      if (!serverArchive || serverArchive.download_count === archive.downloadCount) {
        return archive
      }
      return {
        ...archive,
        downloadCount: serverArchive.download_count,
      }
    })

    const serverArchive = serverMap.get(archiveId)
    if (serverArchive && selectedArchive.value?.id === archiveId) {
      selectedArchive.value = {
        ...selectedArchive.value,
        downloadCount: serverArchive.download_count,
      }
    }

    if (!resetRequested) {
      const availableYears = Array.from(
        new Set(
          archives.value
            .map((item) =>
              item.year !== undefined && item.year !== null ? item.year.toString() : null
            )
            .filter((year) => year !== null)
        )
      )

      const preservedPanels = previousExpandedPanels.filter((year) => availableYears.includes(year))
      expandedPanels.value = preservedPanels
    }
  } catch (error) {
    console.error('Sync download count error:', error)
  }
}

async function downloadArchive(archive) {
  try {
    downloadingId.value = archive.id

    const { data } = await archiveService.getArchiveDownloadUrl(selectedCourse.value, archive.id)

    const response = await fetch(data.url)
    if (!response.ok) {
      throw new Error(`Download failed with status ${response.status}`)
    }
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url

    const fileName = `${archive.year}_${selectedSubject.value}_${archive.professor}_${archive.name}.pdf`
    link.download = fileName
    link.style.display = 'none'

    document.body.appendChild(link)
    link.click()
    setTimeout(() => {
      window.URL.revokeObjectURL(url)
      link.remove()
    }, 100)

    trackEvent(EVENTS.DOWNLOAD_ARCHIVE, {
      archiveName: archive.name,
      year: archive.year,
      professor: archive.professor,
      type: archive.type,
      courseName: selectedSubject.value,
      source: 'archive-list',
    })

    toast.add({
      severity: 'success',
      summary: '下載成功',
      detail: `已下載 ${fileName}`,
      life: 3000,
    })

    await syncArchiveDownloadCount(archive.id)
  } catch (error) {
    console.error('Download error:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '下載失敗',
      detail: '無法取得下載連結',
      life: 3000,
    })
  } finally {
    downloadingId.value = null
  }
}

const previewLoading = ref(false)
const previewError = ref(false)

async function previewArchive(archive) {
  try {
    previewLoading.value = true
    previewError.value = false
    showPreview.value = true

    const { data } = await archiveService.getArchivePreviewFile(selectedCourse.value, archive.id)
    const previewUrl = URL.createObjectURL(new Blob([data], { type: 'application/pdf' }))

    selectedArchive.value = {
      ...archive,
      previewUrl,
    }

    trackEvent(EVENTS.PREVIEW_ARCHIVE, {
      archiveName: archive.name,
      year: archive.year,
      professor: archive.professor,
      type: archive.type,
      courseName: selectedSubject.value,
    })
  } catch (error) {
    console.error('Preview error:', error)
    previewError.value = true
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '預覽失敗',
      detail: '無法取得預覽連結',
      life: 3000,
    })
  } finally {
    previewLoading.value = false
  }
}

function handlePreviewError() {
  previewError.value = true
}

function closePreview() {
  if (selectedArchive.value?.previewUrl?.startsWith('blob:')) {
    URL.revokeObjectURL(selectedArchive.value.previewUrl)
  }
  showPreview.value = false
  selectedArchive.value = null
  previewError.value = false
}

function getCategoryName(code) {
  return categoryMap.value[code]?.name || code
}

const availableEditProfessors = ref([])

const categoryOptions = computed(() =>
  [...courseCategories.value]
    .sort((a, b) => {
      const orderDiff = (a.order_index ?? 0) - (b.order_index ?? 0)
      if (orderDiff !== 0) return orderDiff
      return (a.id ?? 0) - (b.id ?? 0)
    })
    .map((category) => ({
      name: category.name,
      value: category.key,
    }))
)

const sortCourseOptionsByManagementOrder = (courseList) => {
  return [...courseList].sort((a, b) => {
    const orderDiff = (a.order_index ?? 0) - (b.order_index ?? 0)
    if (orderDiff !== 0) return orderDiff
    return (a.id ?? 0) - (b.id ?? 0)
  })
}

watch(
  () => groupedArchives.value,
  (newGroups) => {
    if (!newGroups.length) {
      // Clear expanded panels if no groups available
      expandedPanels.value = []
      shouldResetPanels.value = true
      return
    }

    const availableYears = newGroups.map((group) => group.year.toString())
    const preservedPanels = expandedPanels.value.filter((year) => availableYears.includes(year))

    if (shouldResetPanels.value) {
      // Default to expanding the most recent three years when reset is requested
      expandedPanels.value = newGroups.slice(0, 3).map((group) => group.year.toString())
    } else {
      expandedPanels.value = preservedPanels
    }

    shouldResetPanels.value = false
  },
  { immediate: true }
)

const isAdmin = ref(false)
const showEditDialog = ref(false)
const editForm = ref({
  id: null,
  name: '',
  professor: '',
  type: '',
  hasAnswers: false,
  academicYear: null,
  shouldTransfer: false,
  targetCategory: null,
  targetCourse: null,
  targetCourseId: null,
})

const editLoading = ref(false)

const allAvailableCoursesForTransfer = computed(() => {
  if (!editForm.value.targetCategory || !coursesList.value) {
    return []
  }

  const categoryData = coursesList.value[editForm.value.targetCategory]
  if (!categoryData) {
    return []
  }

  return sortCourseOptionsByManagementOrder(categoryData)
    .filter((course) => course.id !== selectedCourse.value)
    .map((course) => ({
      id: course.id,
      label: course.name,
    }))
})

const availableCoursesForTransfer = ref([])

const canDeleteArchive = (archive) => {
  const currentUser = getCurrentUser()
  if (!currentUser) return false

  return isAdmin.value || (archive.uploader_id && archive.uploader_id === currentUser.id)
}

const canEditArchive = () => {
  return isAdmin.value
}

const confirmDelete = (archive) => {
  confirm.require({
    message: '確定要刪除此考古題嗎？',
    header: '確認刪除',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      deleteArchive(archive)
    },
  })
}

const deleteArchive = async (archive) => {
  try {
    await archiveService.deleteArchive(selectedCourse.value, archive.id)

    trackEvent(EVENTS.DELETE_ARCHIVE, {
      archiveName: archive.name,
      year: archive.year,
      professor: archive.professor,
      type: archive.type,
      courseName: selectedSubject.value,
    })

    shouldResetPanels.value = true
    await fetchArchives()
    toast.add({
      severity: 'success',
      summary: '刪除成功',
      detail: '考古題已成功刪除',
      life: 3000,
    })
  } catch (error) {
    console.error('Delete error:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '刪除失敗',
      detail: '發生錯誤，請稍後再試',
      life: 3000,
    })
  }
}

const openEditDialog = async (archive) => {
  try {
    const response = await courseService.getCourseArchives(selectedCourse.value)
    const archiveData = response.data

    const uniqueProfessors = new Set()
    archiveData.forEach((item) => {
      if (item.professor) uniqueProfessors.add(item.professor)
    })

    uploadFormProfessors.value = Array.from(uniqueProfessors)
      .sort()
      .map((professor) => ({
        name: professor,
        code: professor,
      }))

    editForm.value = {
      id: archive.id,
      name: archive.name,
      professor: archive.professor,
      type: archive.type,
      hasAnswers: archive.hasAnswers,
      academicYear: archive.year ? new Date(parseInt(archive.year), 0, 1) : null,
      shouldTransfer: false,
      targetCategory: null,
      targetCourse: null,
      targetCourseId: null,
    }

    availableEditProfessors.value = uploadFormProfessors.value

    trackEvent(EVENTS.EDIT_ARCHIVE, {
      action: 'open-dialog',
      archiveName: archive.name,
      year: archive.year,
    })

    showEditDialog.value = true
  } catch (error) {
    console.error('Error fetching professors:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '載入失敗',
      detail: '無法載入教授清單',
      life: 3000,
    })
  }
}

const handleEdit = async () => {
  try {
    editLoading.value = true

    await archiveService.updateArchive(selectedCourse.value, editForm.value.id, {
      name: editForm.value.name,
      professor: editForm.value.professor,
      archive_type: editForm.value.type,
      has_answers: editForm.value.hasAnswers,
      academic_year: editForm.value.academicYear ? editForm.value.academicYear.getFullYear() : null,
    })

    if (editForm.value.shouldTransfer && editForm.value.targetCategory) {
      if (editForm.value.targetCourseId) {
        // Transfer to existing course
        await archiveService.updateArchiveCourse(
          selectedCourse.value,
          editForm.value.id,
          editForm.value.targetCourseId
        )
      } else if (editForm.value.targetCourse) {
        // Transfer to new course (create if not exists)
        await archiveService.updateArchiveCourseByCategoryAndName(
          selectedCourse.value,
          editForm.value.id,
          editForm.value.targetCourse,
          editForm.value.targetCategory
        )
      }
    }

    trackEvent(EVENTS.EDIT_ARCHIVE, {
      action: 'submit',
      transferred: editForm.value.shouldTransfer,
      targetCategory: editForm.value.shouldTransfer ? editForm.value.targetCategory : null,
    })

    shouldResetPanels.value = true
    await fetchArchives()

    // If transfer was performed, refresh the course list to show the new course
    if (editForm.value.shouldTransfer) {
      await fetchCourses()
    }

    closeEditDialog()

    const successMessage = editForm.value.shouldTransfer
      ? '考古題已更新並轉移到新課程'
      : '考古題資訊已更新'

    toast.add({
      severity: 'success',
      summary: '更新成功',
      detail: successMessage,
      life: 3000,
    })
  } catch (error) {
    console.error('Update error:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '更新失敗',
      detail: '發生錯誤，請稍後再試',
      life: 3000,
    })
  } finally {
    editLoading.value = false
  }
}

onMounted(async () => {
  const user = getCurrentUser()
  isAdmin.value = user?.is_admin || false
  checkAuthentication()
  await fetchCourses()

  const subjectData = getLocalJson(STORAGE_KEYS.local.SELECTED_SUBJECT)
  if (subjectData) {
    try {
      // Verify the course still exists in the current course list
      const courseExists = Object.values(coursesList.value).some((category) =>
        category.some((course) => course.id === subjectData.id && course.name === subjectData.label)
      )

      if (courseExists) {
        selectedSubject.value = subjectData.label
        selectedCourse.value = subjectData.id

        const categoryKey = getCategoryKeyForCourse(subjectData.id)
        if (categoryKey) {
          expandedMenuItems.value = { [categoryKey]: true }
        }

        await fetchArchives()
      } else {
        removeLocalItem(STORAGE_KEYS.local.SELECTED_SUBJECT)
      }
    } catch (error) {
      console.error('Error parsing saved subject:', error)
      removeLocalItem(STORAGE_KEYS.local.SELECTED_SUBJECT)
    }
  }
})

watch(isDarkTheme, () => {})

async function handleUploadSuccess() {
  trackEvent(EVENTS.UPLOAD_ARCHIVE, {
    courseName: selectedSubject.value,
  })

  await fetchCourses()
  await loadSubmissionStatus()
  shouldResetPanels.value = true
  if (selectedCourse.value) {
    await fetchArchives()
  }
}

function getCategoryTag(categoryLabel) {
  const category = courseCategories.value.find((cat) => cat.name === categoryLabel)
  return category?.label || categoryLabel
}

function formatDownloadCount(count) {
  if (count === 0 || count === null || count === undefined) {
    return '0'
  }
  return count.toString()
}

function formatAnswerStatus(archive) {
  return archive?.hasAnswers ? '含解答' : '僅題目'
}

function toggleSidebar() {
  trackEvent(EVENTS.TOGGLE_SIDEBAR, { visible: !sidebarVisible.value })
  sidebarVisible.value = !sidebarVisible.value
}

async function handlePreviewDownload(onComplete) {
  if (!selectedArchive.value) return

  try {
    const { data } = await archiveService.getArchiveDownloadUrl(
      selectedCourse.value,
      selectedArchive.value.id
    )

    const response = await fetch(data.url)
    if (!response.ok) {
      throw new Error(`Download failed with status ${response.status}`)
    }
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url

    const fileName = `${selectedArchive.value.year}_${selectedSubject.value}_${selectedArchive.value.professor}_${selectedArchive.value.name}.pdf`
    link.download = fileName
    link.style.display = 'none'

    document.body.appendChild(link)
    link.click()
    setTimeout(() => {
      window.URL.revokeObjectURL(url)
      link.remove()
    }, 100)

    trackEvent(EVENTS.DOWNLOAD_ARCHIVE, {
      archiveName: selectedArchive.value.name,
      year: selectedArchive.value.year,
      professor: selectedArchive.value.professor,
      type: selectedArchive.value.type,
      courseName: selectedSubject.value,
      source: 'preview-modal',
    })

    toast.add({
      severity: 'success',
      summary: '下載成功',
      detail: `已下載 ${fileName}`,
      life: 3000,
    })

    await syncArchiveDownloadCount(selectedArchive.value.id)
  } catch (error) {
    console.error('Download error:', error)
    if (isUnauthorizedError(error)) {
      return
    }
    toast.add({
      severity: 'error',
      summary: '下載失敗',
      detail: '無法取得下載連結',
      life: 3000,
    })
  } finally {
    onComplete()
  }
}

const getCurrentCategory = computed(() => {
  if (!selectedCourse.value) return ''

  for (const [category, courses] of Object.entries(coursesList.value)) {
    const course = courses.find((c) => c.id === selectedCourse.value)
    if (course) return category
  }
  return ''
})

const currentCategoryName = computed(() => getCategoryName(getCurrentCategory.value))
const currentCategoryLabel = computed(() => getCategoryTag(currentCategoryName.value))

const searchEditProfessor = (event) => {
  const query = event?.query?.toLowerCase() || ''
  const filteredProfessors = uploadFormProfessors.value
    .filter((professor) => professor.name.toLowerCase().includes(query))
    .sort((a, b) => a.name.localeCompare(b.name))

  availableEditProfessors.value = filteredProfessors
}

const onEditProfessorSelect = (event) => {
  if (event.value && typeof event.value === 'object') {
    editForm.value.professor = event.value.name
  }
}

const closeEditDialog = () => {
  showEditDialog.value = false
  editForm.value = {
    id: null,
    name: '',
    professor: '',
    type: '',
    hasAnswers: false,
    academicYear: null,
    shouldTransfer: false,
    targetCategory: null,
    targetCourse: null,
    targetCourseId: null,
  }
}

const searchTargetCourse = (event) => {
  const query = event?.query?.toLowerCase() || ''
  const filteredCourses = allAvailableCoursesForTransfer.value
    .filter((course) => course.label.toLowerCase().includes(query))
    .sort((a, b) => a.label.localeCompare(b.label))

  availableCoursesForTransfer.value = filteredCourses
}

const onTargetCourseSelect = (event) => {
  if (event.value && typeof event.value === 'object') {
    editForm.value.targetCourse = event.value.label
    editForm.value.targetCourseId = event.value.id
  } else if (typeof event.value === 'string') {
    // User typed a new course name
    editForm.value.targetCourse = event.value
    editForm.value.targetCourseId = null
  }
}

// Handle direct input of course name
watch(
  () => editForm.value.targetCourse,
  (newValue) => {
    if (typeof newValue === 'string' && newValue) {
      // Check if it's an existing course
      const existingCourse = allAvailableCoursesForTransfer.value.find(
        (course) => course.label === newValue
      )
      if (existingCourse) {
        editForm.value.targetCourseId = existingCourse.id
      } else {
        editForm.value.targetCourseId = null
      }
    }
  }
)

watch(
  () => editForm.value.targetCategory,
  () => {
    editForm.value.targetCourseId = null
    editForm.value.targetCourse = null
    availableCoursesForTransfer.value = allAvailableCoursesForTransfer.value
  }
)

const checkAuthentication = () => {
  isAuthenticatedRef.value = isAuthenticated()
  if (isAuthenticatedRef.value) {
    const user = getCurrentUser()
    if (user) {
      userData.value = user
    } else {
      isAuthenticatedRef.value = false
      userData.value = null
    }
  } else {
    isAuthenticatedRef.value = false
    userData.value = null
  }
}

const mobileMenuItems = computed(() => {
  return menuItems.value.map((item) => ({
    ...item,
    items: item.items?.map((subItem) => ({
      ...subItem,
      command: () => {
        subItem.command()
        sidebarVisible.value = false
      },
    })),
  }))
})
</script>

<style scoped>
.card {
  position: relative;
  z-index: 1;
  background: var(--bg-primary);
}

.archive-screen,
.archive-screen > .flex {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  overflow-x: hidden;
}

:deep(.p-sidebar),
:deep(.p-drawer) {
  padding: 0;
  background-color: var(--bg-primary);
  z-index: 2;
  border-right: 1px solid var(--border-color);
  max-width: 100vw;
}

:deep(.p-sidebar-header),
:deep(.p-drawer-header) {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  background-color: var(--bg-primary);
}

:deep(.p-sidebar-content),
:deep(.p-drawer-content) {
  padding: 1rem;
  background-color: var(--bg-primary);
}

:deep(.p-accordioncontent),
:deep(.p-accordioncontent-wrapper),
:deep(.p-accordioncontent-content) {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  overflow-x: hidden;
}

:deep(.p-input-icon-left) {
  width: 100%;
}

:deep(.p-input-icon-left i) {
  left: 0.75rem;
}

:deep(.p-input-icon-left input) {
  padding-left: 2.5rem;
  background: var(--bg-primary);
  border-color: var(--border-color);
  color: var(--text-color);
}

:deep(.p-input-icon-left input:focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 1px var(--primary-color);
}

.sidebar {
  width: 318px;
  min-width: 0;
  max-width: min(318px, 100vw);
  background: #e4eee9;
  border: 0;
  border-right: 1px solid #c7d8d0;
  transition: width 0.2s ease-in-out;
  overflow: hidden;
  position: relative;
  z-index: 1;
  height: calc(100% - 0.25rem);
  margin-left: 0.25rem;
  margin-bottom: 0.25rem;
  display: flex;
  flex-direction: column;
  box-shadow: none;
}

.archive-dark .sidebar {
  background: #0e1b18;
  border-right-color: #22342f;
}

.upload-section {
  flex-shrink: 0;
  border-top: 1px solid #c7d8d0;
  background: #d8e8e0;
}

.upload-actions {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.archive-dark .upload-section {
  background: #0b1714;
  border-top-color: #22342f;
}

.sidebar-shell {
  width: 100%;
  opacity: 1;
  white-space: nowrap;
  height: 100%;
  transition: opacity 0.2s ease-in-out;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.sidebar .search-section {
  flex-shrink: 0;
}

.course-list-section {
  flex: 1 1 auto;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
}

.sidebar.collapsed {
  width: 0;
  min-width: 0;
  margin-left: 0;
  margin-bottom: 0;
  height: 100%;
  border-right: none;
}

.sidebar.collapsed .sidebar-shell {
  opacity: 0;
  pointer-events: none;
}

.main-content {
  flex: 1 1 0%;
  min-width: 0;
  max-width: 100%;
  background: transparent;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.subject-header {
  border-bottom: 1px solid var(--border-color);
  background: #eef6f2;
  position: relative;
  z-index: 1;
  padding: 0.9rem 1.35rem;
}

.archive-dark .subject-header {
  background: #14211d;
}

.subject-title-block {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.subject-tag {
  flex: 0 0 auto;
}

.subject-title {
  color: var(--text-primary);
  font-size: clamp(1.25rem, 2vw, 1.75rem);
  font-weight: 800;
  line-height: 1.12;
}

.subject-subtitle {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem 0.75rem;
  margin-top: 0.28rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 650;
}

.subject-subtitle span + span::before {
  content: '';
  display: inline-block;
  width: 0.24rem;
  height: 0.24rem;
  margin-right: 0.75rem;
  border-radius: 50%;
  vertical-align: middle;
  background: #8aa49a;
}

.archive-filter-bar {
  border: 1px solid #d7e4df !important;
  border-radius: 8px;
  background: rgba(247, 251, 249, 0.84) !important;
  box-shadow: none;
}

.archive-filter-bar :deep(.p-toolbar-start) {
  width: 100%;
}

.archive-filter-shell {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  gap: 0.85rem;
}

.filter-summary {
  flex: 1 1 16rem;
  min-width: 12rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 650;
}

.archive-filter-controls {
  display: flex;
  flex: 1 1 auto;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.5rem;
}

.filter-select {
  width: min(11rem, 100%);
}

.answer-filter {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  min-height: 2.35rem;
  padding: 0 0.25rem;
  color: var(--text-secondary);
  font-size: 0.92rem;
  font-weight: 650;
}

.ellipsis {
  display: inline-block;
  max-width: 90%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: middle;
}

.search-result-btn {
  width: 100%;
  justify-content: flex-start;
  text-align: left;
  padding: 0.5rem;
  border-radius: 4px;
}

.active-course-search-result {
  background: #dcebe4 !important;
  box-shadow: inset 3px 0 0 #176a5a;
  color: #17382f !important;
  font-weight: 800;
}

:deep(.p-panelmenu) {
  display: grid;
  gap: 0.7rem;
}

:deep(.p-panelmenu-panel) {
  overflow: hidden;
  border: 1px solid #cadbd4;
  border-radius: 8px;
  background: #f8fbfa;
}

.archive-dark :deep(.p-panelmenu-panel) {
  border-color: #22342f;
  background: #121b18;
}

:deep(.p-panelmenu-header-content),
:deep(.p-panelmenu-content) {
  border: 0;
  background: transparent;
}

:deep(.p-panelmenu-header-link) {
  padding: 0.85rem 1rem;
  font-weight: 800;
}

:deep(.p-panelmenu-item-link) {
  border-radius: 7px;
  margin: 0.15rem 0.45rem;
  padding: 0.55rem 0.75rem;
}

:deep(.active-course-menu-item .p-panelmenu-item-link),
:deep(.active-course-menu-item > .p-panelmenu-item-link) {
  background: #dcebe4;
  box-shadow: inset 3px 0 0 #176a5a;
  color: #17382f;
  font-weight: 800;
}

.archive-dark :deep(.active-course-menu-item .p-panelmenu-item-link),
.archive-dark :deep(.active-course-menu-item > .p-panelmenu-item-link) {
  background: #172c26;
  color: #edf8f3;
  box-shadow: inset 3px 0 0 #49b692;
}

:deep(.p-accordion) {
  display: grid;
  gap: 0.85rem;
}

:deep(.p-accordionpanel) {
  overflow: hidden;
  border: 1px solid var(--border-color);
  border-left: 4px solid #176a5a;
  border-radius: 8px;
  background: #fbfdfc;
}

:deep(.p-accordionheader) {
  padding: 0.82rem 1rem;
  border: 0;
  background: #f0f7f4;
  font-size: 1rem;
  font-weight: 800;
}

:deep(.p-accordioncontent-content) {
  padding: 0.75rem;
  background: transparent;
}

.term-header-content {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.term-title {
  color: var(--text-primary);
  font-weight: 850;
}

.term-count {
  color: #60776f;
  font-size: 0.86rem;
  font-weight: 750;
}

.archive-card-grid {
  display: grid;
  gap: 0.5rem;
}

.archive-record-card {
  padding: 0.65rem 0.75rem;
  border: 1px solid #d8e4df;
  border-left: 3px solid #6da48f;
  border-radius: 8px;
  background: #ffffff;
}

.archive-dark .archive-record-card {
  background: #0d1a17;
  border-color: #22342f;
  border-left-color: #35d39a;
}

.archive-record-content {
  display: grid;
  gap: 0.38rem;
  min-width: 0;
}

.archive-record-line,
.archive-record-title-group,
.archive-record-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.archive-record-primary-line {
  justify-content: space-between;
  gap: 0.75rem;
}

.archive-record-title-group {
  flex: 1 1 16rem;
  min-width: 0;
  gap: 0.55rem;
}

.archive-record-card h3 {
  min-width: 0;
  margin: 0;
  color: var(--text-primary);
  font-size: 1.02rem;
  font-weight: 800;
  line-height: 1.28;
  overflow-wrap: anywhere;
}

.exam-type-tag {
  background: #edf5f1 !important;
  border-color: #c5d8d0 !important;
  color: #1d5f52 !important;
  font-weight: 800;
}

.archive-record-meta-line {
  gap: 0.35rem 0.65rem;
  color: var(--text-secondary);
  font-size: 0.86rem;
  font-weight: 560;
}

.archive-record-meta-line span + span::before {
  content: '';
  display: inline-block;
  width: 0.2rem;
  height: 0.2rem;
  margin-right: 0.65rem;
  border-radius: 50%;
  vertical-align: middle;
  background: #91a9a0;
}

.archive-record-actions {
  flex: 0 0 auto;
  justify-content: flex-end;
  gap: 0.35rem;
}

.archive-record-actions :deep(.p-button) {
  min-height: 2.05rem;
  padding-top: 0.36rem;
  padding-bottom: 0.36rem;
}

.archive-record-actions :deep(.archive-action-icon.p-button) {
  width: 2.05rem;
  padding-right: 0;
  padding-left: 0;
}

.archive-record-actions :deep(.archive-action-edit.p-button) {
  color: #426b61;
  border-color: #c5d8d0;
  background: #fbfdfc;
}

.archive-record-actions :deep(.archive-action-danger.p-button) {
  color: #9b3a35;
}

.archive-dark .archive-filter-bar {
  border-color: #22342f !important;
  background: rgba(18, 31, 27, 0.86) !important;
}

.archive-dark :deep(.p-accordionpanel) {
  border-left-color: #49b692;
  background: #0f1a17;
}

.archive-dark :deep(.p-accordionheader) {
  background: #14231f;
}

.archive-dark .term-count {
  color: #9db8ae;
}

.archive-dark .exam-type-tag {
  background: #172c26 !important;
  border-color: #29483f !important;
  color: #9ee8c7 !important;
}

.archive-dark .archive-record-actions :deep(.archive-action-edit.p-button) {
  color: #b4cbc3;
  border-color: #29483f;
  background: #0f1a17;
}

.search-results .text-sm {
  font-size: 0.875rem;
}

/* Mobile sidebar specific styles */
.mobile-drawer {
  display: none;
}

@media (max-width: 768px) {
  .mobile-drawer {
    display: block;
  }
}

:deep(.mobile-drawer.p-drawer),
:deep(.mobile-drawer .p-sidebar),
:deep(.mobile-drawer .p-drawer) {
  z-index: 1000;
  width: min(100vw, 26rem) !important;
  max-width: 100vw;
  background: #f5f8f1;
  border-right: 1px solid rgba(88, 126, 106, 0.22);
}

:global(.mobile-drawer.p-drawer),
:global(.mobile-drawer .p-drawer),
:global(.mobile-drawer .p-sidebar) {
  width: min(100vw, 26rem) !important;
  max-width: 100vw;
  background: #f5f8f1 !important;
  color: #17382f !important;
  border-right: 1px solid rgba(88, 126, 106, 0.22);
  box-shadow: 0 1.5rem 3.5rem rgba(42, 68, 54, 0.18);
}

:global(.mobile-drawer.mobile-drawer-dark.p-drawer),
:global(.mobile-drawer.mobile-drawer-dark .p-drawer),
:global(.mobile-drawer.mobile-drawer-dark .p-sidebar) {
  background: #101916 !important;
  color: rgba(239, 247, 238, 0.94) !important;
  border-right-color: rgba(214, 230, 223, 0.16);
  box-shadow: 0 1.5rem 3.5rem rgba(0, 0, 0, 0.38);
}

:global(.mobile-drawer-mask) {
  background: rgba(31, 54, 45, 0.2) !important;
  backdrop-filter: blur(2px);
}

:global(.mobile-drawer-mask-dark) {
  background: rgba(2, 8, 7, 0.54) !important;
}

:deep(.mobile-drawer .p-sidebar-content),
:deep(.mobile-drawer .p-drawer-content) {
  padding: 0.9rem;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-x: hidden;
  background:
    radial-gradient(circle at 78% 8%, rgba(202, 179, 111, 0.14), transparent 9rem),
    linear-gradient(180deg, #fbfaf3 0%, #eef6f1 100%);
}

:global(.mobile-drawer .p-drawer-content),
:global(.mobile-drawer .p-sidebar-content) {
  padding: 0.9rem !important;
  overflow-x: hidden;
  background:
    radial-gradient(circle at 78% 8%, rgba(202, 179, 111, 0.14), transparent 9rem),
    linear-gradient(180deg, #fbfaf3 0%, #eef6f1 100%) !important;
}

:global(.mobile-drawer.mobile-drawer-dark .p-drawer-content),
:global(.mobile-drawer.mobile-drawer-dark .p-sidebar-content) {
  background:
    radial-gradient(circle at 78% 8%, rgba(202, 179, 111, 0.12), transparent 9rem),
    linear-gradient(180deg, #101916 0%, #0b1512 100%) !important;
}

:deep(.mobile-drawer .p-sidebar-header),
:deep(.mobile-drawer .p-drawer-header) {
  padding: 1rem;
  border-bottom: 1px solid rgba(88, 126, 106, 0.2);
  background-color: #fbfaf3;
  position: relative;
}

:global(.mobile-drawer .p-drawer-header),
:global(.mobile-drawer .p-sidebar-header) {
  background: #fbfaf3 !important;
  border-bottom: 1px solid rgba(88, 126, 106, 0.2);
  color: #17382f !important;
}

:global(.mobile-drawer.mobile-drawer-dark .p-drawer-header),
:global(.mobile-drawer.mobile-drawer-dark .p-sidebar-header) {
  background: #101916 !important;
  border-bottom-color: rgba(214, 230, 223, 0.16);
  color: rgba(239, 247, 238, 0.94) !important;
}

:deep(.mobile-drawer .p-sidebar-close),
:deep(.mobile-drawer .p-drawer-close-button) {
  position: absolute;
  top: 50%;
  right: 1rem;
  transform: translateY(-50%);
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.58);
  border: 1px solid rgba(88, 126, 106, 0.24);
  color: #17382f;
  cursor: pointer;
  transition: all 0.2s;
}

:deep(.mobile-drawer .p-sidebar-close:hover),
:deep(.mobile-drawer .p-drawer-close-button:hover) {
  background: rgba(225, 238, 229, 0.86);
}

:global(.mobile-drawer.mobile-drawer-dark .p-drawer-close-button),
:global(.mobile-drawer.mobile-drawer-dark .p-sidebar-close) {
  background: rgba(214, 230, 223, 0.06);
  border-color: rgba(214, 230, 223, 0.16);
  color: rgba(239, 247, 238, 0.94);
}

:global(.mobile-drawer.mobile-drawer-dark .p-drawer-close-button:hover),
:global(.mobile-drawer.mobile-drawer-dark .p-sidebar-close:hover) {
  background: rgba(214, 230, 223, 0.12);
}

.mobile-upload-section {
  margin: 0 -0.9rem -0.9rem;
  padding: 0.9rem;
  padding-bottom: max(0.9rem, env(safe-area-inset-bottom));
}

:global(.mobile-drawer.mobile-drawer-dark .mobile-upload-section) {
  background: #0b1714 !important;
  border-top: 1px solid #22342f !important;
  box-shadow: 0 -1px 0 rgba(214, 230, 223, 0.04);
}

:global(.mobile-drawer.mobile-drawer-dark .mobile-upload-section .p-button.p-button-secondary.p-button-outlined) {
  background: rgba(214, 230, 223, 0.06) !important;
  border-color: rgba(214, 230, 223, 0.28) !important;
  color: rgba(239, 247, 238, 0.92) !important;
}

:global(.mobile-drawer.mobile-drawer-dark .mobile-upload-section .p-button.p-button-secondary.p-button-outlined:hover) {
  background: rgba(214, 230, 223, 0.12) !important;
  border-color: rgba(214, 230, 223, 0.4) !important;
  color: #f4fbf4 !important;
}

/* Ensure proper mobile responsiveness */
@media (max-width: 768px) {
  .main-content {
    width: 100%;
    min-width: 0;
    overflow-x: hidden;
  }

  .subject-header {
    padding: 0.85rem 1rem;
  }

  .archive-filter-shell {
    align-items: flex-start;
    flex-direction: column;
    gap: 0.55rem;
  }

  .archive-filter-controls {
    width: 100%;
    justify-content: flex-start;
  }

  .filter-select {
    flex: 1 1 9.5rem;
    min-width: min(100%, 9.5rem);
  }

  .archive-record-primary-line {
    align-items: flex-start;
  }

  .archive-record-actions {
    min-width: 0;
    justify-content: flex-start;
  }

  .archive-record-actions :deep(.p-button) {
    flex: 0 0 auto;
  }

  .archive-record-actions :deep(.archive-action-preview.p-button),
  .archive-record-actions :deep(.archive-action-download.p-button) {
    flex: 1 1 6.5rem;
  }

  /* Dialog font size adjustments for mobile */
  :deep(.p-dialog .p-dialog-content) {
    font-size: 0.875rem;
  }

  :deep(.p-dialog .p-dialog-header) {
    font-size: 1rem;
  }

  :deep(.p-dialog label) {
    font-size: 0.875rem;
  }

  :deep(.p-dialog .p-inputtext) {
    font-size: 0.875rem;
  }

  :deep(.p-dialog .p-button) {
    font-size: 0.875rem;
    padding: 0.5rem 0.75rem;
  }

  :deep(.p-dialog .p-dropdown-label),
  :deep(.p-dialog .p-autocomplete-input),
  :deep(.p-dialog .p-calendar-input) {
    font-size: 0.875rem;
  }

  :deep(.p-dialog .p-checkbox-label) {
    font-size: 0.875rem;
  }

  /* Table responsive design for mobile */
  :deep(.p-accordioncontent-content .p-datatable) {
    font-size: 0.75rem;
    width: 100%;
    max-width: 100%;
  }

  :deep(.p-accordioncontent-content .p-datatable-table-container) {
    width: 100%;
    max-width: 100%;
    overflow-x: auto;
  }

  :deep(.p-datatable-table) {
    font-size: 0.75rem;
    min-width: 600px;
    width: 100%;
  }

  :deep(.p-datatable .p-datatable-thead > tr > th) {
    font-size: 0.75rem;
    padding: 0.5rem 0.25rem;
    white-space: nowrap;
  }

  :deep(.p-datatable .p-datatable-tbody > tr > td) {
    font-size: 0.75rem;
    padding: 0.5rem 0.25rem;
    white-space: nowrap;
  }

  :deep(.p-datatable .p-button) {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    white-space: nowrap;
  }

  :deep(.p-tag) {
    font-size: 0.625rem;
    padding: 0.125rem 0.375rem;
    white-space: nowrap;
  }

  /* Make table container scrollable on mobile */
  :deep(.p-accordion-content) {
    padding: 0.5rem;
    overflow-x: auto;
  }

  /* Adjust button groups for mobile */
  :deep(.p-datatable .p-column-header-content) {
    justify-content: center;
  }

  /* Ensure buttons don't wrap */
  :deep(.p-datatable .flex.gap-2\.5) {
    flex-wrap: nowrap;
    gap: 0.25rem;
  }

  /* Accordion adjustments for mobile */
  :deep(.p-accordion .p-accordion-header) {
    font-size: 0.875rem;
  }

  :deep(.p-accordion .p-accordion-content) {
    padding: 0.5rem;
  }
}

@media (max-width: 768px) {
  :deep(.mobile-drawer .p-panelmenu),
  :deep(.mobile-drawer .p-panelmenu-panel),
  :deep(.mobile-drawer .p-panelmenu-header-content),
  :deep(.mobile-drawer .p-panelmenu-header),
  :deep(.mobile-drawer .p-panelmenu-item-content),
  :deep(.mobile-drawer .p-panelmenu-content) {
    width: 100%;
    max-width: 100%;
    overflow: hidden;
    border-color: rgba(88, 126, 106, 0.2);
    background: #f8fbf6 !important;
  }

  :global(.mobile-drawer .p-panelmenu),
  :global(.mobile-drawer .p-panelmenu-panel),
  :global(.mobile-drawer .p-panelmenu-header),
  :global(.mobile-drawer .p-panelmenu-header-content),
  :global(.mobile-drawer .p-panelmenu-item-content),
  :global(.mobile-drawer .p-panelmenu-content) {
    width: 100%;
    max-width: 100%;
    overflow: hidden;
    border-color: rgba(88, 126, 106, 0.2) !important;
    background: #f8fbf6 !important;
  }

  :deep(.mobile-drawer .p-panelmenu-panel) {
    margin-bottom: 0.75rem;
    border-radius: 8px;
  }

  :global(.mobile-drawer .p-panelmenu-panel) {
    margin-bottom: 0.75rem;
    border-radius: 8px;
    box-shadow: none !important;
  }

  :deep(.mobile-drawer .p-panelmenu-header-link),
  :deep(.mobile-drawer .p-panelmenu-item-link) {
    min-height: 3rem;
    color: #17382f !important;
    background: #f8fbf6 !important;
  }

  :global(.mobile-drawer .p-panelmenu-header-link),
  :global(.mobile-drawer .p-panelmenu-item-link) {
    min-height: 3rem;
    color: #17382f !important;
    background: #f8fbf6 !important;
  }

  :deep(.mobile-drawer .p-panelmenu-header-link:hover),
  :deep(.mobile-drawer .p-panelmenu-item-link:hover) {
    background: #edf6f1 !important;
  }

  :deep(.mobile-drawer .p-panelmenu-header-label),
  :deep(.mobile-drawer .p-panelmenu-item-label),
  :deep(.mobile-drawer .p-panelmenu-header-icon),
  :deep(.mobile-drawer .p-panelmenu-submenu-icon) {
    color: #17382f !important;
  }

  :global(.mobile-drawer .p-panelmenu-header-label),
  :global(.mobile-drawer .p-panelmenu-item-label),
  :global(.mobile-drawer .p-panelmenu-header-icon),
  :global(.mobile-drawer .p-panelmenu-submenu-icon),
  :global(.mobile-drawer .p-panelmenu-item-icon) {
    color: #17382f !important;
  }

  :deep(.mobile-drawer .p-inputtext) {
    min-height: 3rem;
    background: rgba(255, 255, 255, 0.82);
    color: #17382f;
    border-color: rgba(88, 126, 106, 0.24);
  }

  :global(.mobile-drawer.mobile-drawer-dark .p-panelmenu),
  :global(.mobile-drawer.mobile-drawer-dark .p-panelmenu-panel),
  :global(.mobile-drawer.mobile-drawer-dark .p-panelmenu-header),
  :global(.mobile-drawer.mobile-drawer-dark .p-panelmenu-header-content),
  :global(.mobile-drawer.mobile-drawer-dark .p-panelmenu-item-content),
  :global(.mobile-drawer.mobile-drawer-dark .p-panelmenu-content) {
    border-color: rgba(214, 230, 223, 0.16) !important;
    background: #111816 !important;
  }

  :global(.mobile-drawer.mobile-drawer-dark .p-panelmenu-header-link),
  :global(.mobile-drawer.mobile-drawer-dark .p-panelmenu-item-link) {
    color: rgba(239, 247, 238, 0.92) !important;
    background: #111816 !important;
  }

  :global(.mobile-drawer.mobile-drawer-dark .p-panelmenu-header-link:hover),
  :global(.mobile-drawer.mobile-drawer-dark .p-panelmenu-item-link:hover) {
    background: #172522 !important;
  }

  :global(.mobile-drawer.mobile-drawer-dark .p-panelmenu-header-label),
  :global(.mobile-drawer.mobile-drawer-dark .p-panelmenu-item-label),
  :global(.mobile-drawer.mobile-drawer-dark .p-panelmenu-header-icon),
  :global(.mobile-drawer.mobile-drawer-dark .p-panelmenu-submenu-icon),
  :global(.mobile-drawer.mobile-drawer-dark .p-panelmenu-item-icon) {
    color: rgba(239, 247, 238, 0.92) !important;
  }

  :global(.mobile-drawer.mobile-drawer-dark .p-inputtext) {
    background: #080a0b !important;
    color: rgba(239, 247, 238, 0.94) !important;
    border-color: rgba(214, 230, 223, 0.22) !important;
  }

  .upload-section,
  .admin-section {
    padding-bottom: max(1rem, env(safe-area-inset-bottom));
  }
}

/* Desktop table overflow handling */
@media (min-width: 769px) {
  :deep(.p-accordioncontent-content .p-datatable) {
    width: 100%;
    max-width: 100%;
  }

  :deep(.p-accordioncontent-content .p-datatable-table-container) {
    width: 100%;
    max-width: 100%;
    overflow-x: auto;
  }

  :deep(.p-datatable-table) {
    min-width: 800px;
    width: 100%;
  }

  :deep(.p-datatable .p-datatable-thead > tr > th),
  :deep(.p-datatable .p-datatable-tbody > tr > td) {
    white-space: nowrap;
  }

  :deep(.p-datatable .p-button) {
    white-space: nowrap;
  }

  :deep(.p-tag) {
    white-space: nowrap;
  }

  /* Make accordion content scrollable on desktop too */
  :deep(.p-accordion-content) {
    overflow-x: auto;
  }

  /* Ensure buttons don't wrap on desktop */
  :deep(.p-datatable .flex.gap-2\.5) {
    flex-wrap: nowrap;
    gap: 0.5rem;
  }
}

/* Search section styles */
.search-section {
  flex-shrink: 0;
}

/* Scrollable content styles */
.sidebar .search-results,
.mobile-drawer .search-results {
  padding: 0.5rem;
}

.sidebar .search-results {
  white-space: nowrap;
  overflow: hidden;
}

.sidebar .search-results .p-button {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar :deep(.p-panelmenu) {
  white-space: nowrap;
}

.sidebar :deep(.p-panelmenu .p-panelmenu-content) {
  overflow: hidden;
}

.admin-section {
  flex-shrink: 0;
}

.submission-status-list h3 {
  margin: 0 0 0.75rem;
  font-size: 1.1rem;
}

.submission-empty {
  color: var(--text-secondary);
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.submission-status-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.submission-status-card + .submission-status-card {
  margin-top: 0.75rem;
}

.submission-status-head {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

:deep(.submission-status-badge.submission-status-pending) {
  background: #fef3c7;
  color: #92400e;
  border-color: #f59e0b;
  font-weight: 700;
}

:deep(.submission-status-badge.submission-status-approved) {
  background: #dcfce7;
  color: #166534;
  border-color: #22c55e;
  font-weight: 700;
}

:deep(.submission-status-badge.submission-status-rejected) {
  background: #fee2e2;
  color: #991b1b;
  border-color: #ef4444;
  font-weight: 700;
}

:deep(.submission-status-badge.submission-status-deleted) {
  background: #ffe4e6;
  color: #9f1239;
  border-color: #f43f5e;
  font-weight: 700;
}

:deep(.submission-status-badge.submission-status-takedown) {
  background: #e2e8f0;
  color: #334155;
  border-color: #64748b;
  font-weight: 700;
}

:deep(.submission-admin-badge) {
  background: #dbeafe;
  color: #1d4ed8;
  border-color: #3b82f6;
  font-weight: 700;
}

.archive-dark :deep(.submission-status-badge.submission-status-pending) {
  background: rgba(245, 158, 11, 0.22);
  color: #fcd34d;
  border-color: rgba(251, 191, 36, 0.55);
}

.archive-dark :deep(.submission-status-badge.submission-status-approved) {
  background: rgba(34, 197, 94, 0.2);
  color: #86efac;
  border-color: rgba(74, 222, 128, 0.52);
}

.archive-dark :deep(.submission-status-badge.submission-status-rejected) {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
  border-color: rgba(248, 113, 113, 0.54);
}

.archive-dark :deep(.submission-status-badge.submission-status-deleted) {
  background: rgba(244, 63, 94, 0.2);
  color: #fda4af;
  border-color: rgba(251, 113, 133, 0.54);
}

.archive-dark :deep(.submission-status-badge.submission-status-takedown) {
  background: rgba(100, 116, 139, 0.24);
  color: #cbd5e1;
  border-color: rgba(148, 163, 184, 0.5);
}

.archive-dark :deep(.submission-admin-badge) {
  background: rgba(59, 130, 246, 0.22);
  color: #bfdbfe;
  border-color: rgba(96, 165, 250, 0.56);
}

.submission-status-title {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
}

.submission-status-title strong {
  font-size: 1rem;
  line-height: 1.3;
  overflow-wrap: anywhere;
}

.submission-status-title span {
  color: var(--text-secondary);
  overflow-wrap: anywhere;
}

.submission-status-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.submission-status-meta span,
.submission-status-note {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.6rem;
  border-radius: 8px;
  color: var(--text-color);
  background: color-mix(in srgb, var(--bg-primary) 82%, var(--border-color));
  border: 1px solid var(--border-color);
}

.submission-status-note {
  align-self: flex-start;
}

.submission-status-note span {
  color: var(--text-secondary);
}

.submission-status-note small {
  color: var(--text-secondary);
}

.submission-status-note.is-review {
  align-items: flex-start;
  flex-direction: column;
}
</style>
