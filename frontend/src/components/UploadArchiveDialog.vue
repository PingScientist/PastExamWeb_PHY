<template>
  <div>
    <Dialog
      :visible="modelValue"
      @update:visible="$emit('update:modelValue', $event)"
      :modal="true"
      :draggable="false"
      :closeOnEscape="false"
      :style="{ width: '700px', maxWidth: '90vw' }"
      :autoFocus="false"
      :pt="{ root: { 'aria-label': '上傳考古題', 'aria-labelledby': null } }"
    >
      <template #header>
        <div class="flex align-items-center gap-2.5">
          <i class="pi pi-cloud-upload text-2xl" />
          <div class="text-xl leading-tight font-semibold">上傳考古題</div>
        </div>
      </template>
      <Stepper :value="uploadStep" @update:value="uploadStep = $event" linear>
        <StepList>
          <Step value="1">選擇課程</Step>
          <Step value="2">考試資訊</Step>
          <Step value="3">上傳檔案</Step>
          <Step value="4">確認資訊</Step>
        </StepList>

        <StepPanels>
          <StepPanel v-slot="{ activateCallback }" value="1">
            <div class="flex flex-column gap-4">
              <div class="request-mode-panel">
                <div class="flex align-items-start gap-2">
                  <Checkbox
                    v-model="form.requestNewCourse"
                    :binary="true"
                    inputId="request-new-course"
                    name="request-new-course"
                    :disabled="form.requestNewCategory"
                  />
                  <div>
                    <label for="request-new-course" class="font-semibold">申請新增課程</label>
                    <div class="text-sm text-500 mt-1">
                      勾選後，這份考古會先進入審核；管理者通過後才建立新課程並公開考古題。
                    </div>
                    <div v-if="form.requestNewCategory" class="text-sm text-500 mt-1">
                      新增分類必須同時申請新增課程。
                    </div>
                  </div>
                </div>
                <div class="flex align-items-start gap-2 mt-3">
                  <Checkbox
                    v-model="form.requestNewCategory"
                    :binary="true"
                    inputId="request-new-category"
                    name="request-new-category"
                  />
                  <div>
                    <label for="request-new-category" class="font-semibold"
                      >同時申請新增課程分類</label
                    >
                    <div class="text-sm text-500 mt-1">
                      適合現有分類都不合用的課程；勾選後會自動視為新增課程申請。
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="form.requestNewCategory" class="new-category-grid">
                <div class="flex flex-column gap-2">
                  <label>新分類 Key</label>
                  <InputText
                    id="requested-category-key"
                    name="requested-category-key"
                    v-model="form.requestedCategoryKey"
                    placeholder="例如 astrophysics"
                    class="w-full"
                    :class="{ 'p-invalid': form.requestedCategoryKey && !isCategoryKeyValid }"
                  />
                  <small
                    :class="
                      form.requestedCategoryKey && !isCategoryKeyValid ? 'p-error' : 'text-gray-500'
                    "
                  >
                    請使用小寫英文字母、數字或連字號，2 到 40 字。
                  </small>
                </div>
                <div class="flex flex-column gap-2">
                  <label>新分類名稱</label>
                  <InputText
                    id="requested-category-name"
                    name="requested-category-name"
                    v-model="form.requestedCategoryName"
                    placeholder="例如 天文物理"
                    class="w-full"
                  />
                </div>
                <div class="flex flex-column gap-2">
                  <label>科目旁小標籤</label>
                  <InputText
                    id="requested-category-label"
                    name="requested-category-label"
                    v-model="form.requestedCategoryLabel"
                    placeholder="例如 天文"
                    class="w-full"
                  />
                </div>
              </div>

              <div class="flex flex-column gap-2">
                <label>課程類別</label>
                <Select
                  inputId="upload-category"
                  name="upload-category"
                  v-model="form.category"
                  :options="categoryOptions"
                  optionLabel="name"
                  optionValue="value"
                  placeholder="選擇課程類別"
                  class="w-full"
                  :disabled="form.requestNewCategory"
                />
                <small v-if="form.requestNewCategory" class="text-gray-500">
                  已改為申請新分類，這份考古會歸到上方的新分類。
                </small>
              </div>

              <div v-if="form.requestNewCourse" class="flex flex-column gap-2">
                <label>新課程名稱</label>
                <InputText
                  id="requested-course-name"
                  name="requested-course-name"
                  v-model="form.requestedCourseName"
                  placeholder="輸入要申請的課程名稱"
                  class="w-full"
                />
              </div>

              <div v-else class="flex flex-column gap-2">
                <label>課程名稱</label>
                <Select
                  inputId="upload-subject"
                  name="upload-subject"
                  v-model="form.subject"
                  :options="subjectOptions"
                  optionLabel="name"
                  placeholder="選擇課程名稱"
                  class="w-full"
                  :disabled="!form.category"
                  filter
                  showClear
                >
                  <template #item="{ item }">
                    <div>{{ item.name }}</div>
                  </template>
                </Select>
                <small class="text-gray-500">若課程不在列表上，請勾選「申請新增課程」。</small>
              </div>

              <div class="flex flex-column gap-2">
                <label>授課教授</label>
                <AutoComplete
                  inputId="upload-professor"
                  name="upload-professor"
                  :modelValue="form.professor"
                  @update:modelValue="(val) => (form.professor = val)"
                  :suggestions="availableProfessors"
                  @complete="searchProfessor"
                  @item-select="onProfessorSelect"
                  @focus="() => searchProfessor({ query: '' })"
                  @click="() => searchProfessor({ query: '' })"
                  optionLabel="name"
                  placeholder="搜尋或輸入授課教授"
                  class="w-full"
                  :disabled="!effectiveSubject"
                  dropdown
                  completeOnFocus
                  :minLength="0"
                  autoHighlight="true"
                >
                  <template #item="{ item }">
                    <div>{{ item.name }}</div>
                  </template>
                </AutoComplete>
                <small class="text-gray-500">如果授課教授不在列表上，可自行輸入新增</small>
              </div>
            </div>
            <div class="flex pt-6 justify-end">
              <Button
                label="下一步"
                icon="pi pi-arrow-right"
                @click="activateCallback('2')"
                :disabled="!canGoToStep2"
              />
            </div>
          </StepPanel>

          <StepPanel v-slot="{ activateCallback }" value="2">
            <div class="flex flex-column gap-4">
              <div class="flex flex-column gap-2">
                <label>考試學期</label>
                <div class="semester-picker">
                  <div class="semester-picker-value">
                    {{ formatSemester(form.academicYear) || '選擇考試學期' }}
                  </div>
                  <div class="semester-grid" role="listbox" aria-label="選擇考試學期">
                    <div v-for="group in semesterGroups" :key="group.year" class="semester-row">
                      <div class="semester-year">{{ group.year }}</div>
                      <button
                        v-for="semester in group.semesters"
                        :key="semester.code"
                        type="button"
                        class="semester-option"
                        :class="{ selected: form.academicYear === semester.code }"
                        @click="form.academicYear = semester.code"
                      >
                        {{ semester.label }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="flex flex-column gap-2">
                <label>考試類型</label>
                <Select
                  inputId="upload-exam-type"
                  name="upload-exam-type"
                  v-model="form.type"
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

              <div v-if="requiresExamNumber" class="flex flex-column gap-2">
                <label>{{ form.type === 'midterm' ? '第幾次期中考' : '第幾次小考' }}</label>
                <Select
                  inputId="upload-exam-number"
                  name="upload-exam-number"
                  v-model="form.examNumber"
                  :options="examNumberOptions"
                  optionLabel="name"
                  optionValue="value"
                  placeholder="選擇次數"
                  class="w-full"
                />
                <small class="text-gray-500">
                  系統會自動建立名稱：{{ generatedFilename || '請先選擇次數' }}
                </small>
              </div>

              <div v-if="form.type === 'other'" class="flex flex-column gap-2">
                <label for="filename-input">其他考試名稱</label>
                <div class="relative w-full">
                  <InputText
                    id="filename-input"
                    name="filename-input"
                    v-model="form.otherName"
                    placeholder="例如 retake1"
                    class="w-full pr-8"
                    :class="{
                      'p-invalid': form.otherName && !isFilenameValid,
                    }"
                    :maxlength="30"
                    @input="validateFilename"
                  />
                  <i
                    v-if="isFilenameValid && form.otherName"
                    class="pi pi-check text-green-500 absolute right-3 top-1/2 -mt-2"
                  />
                  <i
                    v-else-if="form.otherName"
                    class="pi pi-times text-red-500 absolute right-3 top-1/2 -mt-2"
                  />
                </div>
                <small v-if="form.otherName && !isFilenameValid" class="p-error">
                  名稱格式必須是小寫英文字母和阿拉伯數字，數字需放在結尾（如：makeup1）
                </small>
                <small v-else class="text-gray-500">
                  請輸入小寫英文字母和阿拉伯數字，數字需放在結尾（如：makeup1）
                </small>
              </div>

              <div v-if="form.type === 'final'" class="flex flex-column gap-2">
                <label>考試名稱</label>
                <InputText
                  id="generated-filename"
                  name="generated-filename"
                  :modelValue="generatedFilename"
                  class="w-full"
                  disabled
                />
              </div>

              <div class="flex align-items-center gap-2">
                <Checkbox
                  inputId="upload-has-answers"
                  name="upload-has-answers"
                  v-model="form.hasAnswers"
                  :binary="true"
                />
                <label for="upload-has-answers">附解答</label>
              </div>
            </div>
            <div class="flex pt-6 justify-between">
              <Button
                label="上一步"
                icon="pi pi-arrow-left"
                severity="secondary"
                @click="activateCallback('1')"
              />
              <Button
                label="下一步"
                icon="pi pi-arrow-right"
                @click="activateCallback('3')"
                :disabled="!canGoToStep3"
              />
            </div>
          </StepPanel>

          <StepPanel v-slot="{ activateCallback }" value="3">
            <div class="flex flex-column gap-4">
              <FileUpload
                ref="fileUpload"
                accept="application/pdf"
                :maxFileSize="10 * 1024 * 1024"
                class="w-full"
                @select="onFileSelect"
                :multiple="false"
                :auto="false"
              >
                <template #header="{ chooseCallback }">
                  <div class="flex justify-between items-center flex-1 gap-4">
                    <div class="flex gap-2">
                      <Button
                        @click="chooseCallback()"
                        icon="pi pi-file-pdf"
                        rounded
                        outlined
                        severity="secondary"
                        label="選擇檔案"
                      ></Button>
                    </div>
                    <div v-if="form.file" class="text-sm text-500">
                      {{ formatFileSize(form.file.size) }} / 10MB
                    </div>
                  </div>
                </template>

                <template #content="{ removeFileCallback }">
                  <div v-if="form.file" class="flex flex-col gap">
                    <div class="p-4 surface-50 border-1 border-round">
                      <div class="flex align-items-center gap-3">
                        <i class="pi pi-file-pdf text-2xl"></i>
                        <div class="flex-1">
                          <div class="font-semibold text-overflow-ellipsis overflow-hidden">
                            {{ form.file.name }}
                          </div>
                          <div class="text-sm text-500">
                            {{ formatFileSize(form.file.size) }}
                          </div>
                        </div>
                        <Button
                          icon="pi pi-times"
                          @click="clearSelectedFile(removeFileCallback)"
                          outlined
                          rounded
                          severity="danger"
                          size="small"
                        />
                      </div>
                    </div>
                  </div>
                </template>

                <template #empty>
                  <div
                    v-if="!form.file"
                    class="flex align-items-center justify-content-center flex-column p-5 border-1 border-dashed border-round"
                  >
                    <i
                      class="pi pi-cloud-upload border-2 border-round p-5 text-4xl text-500 mb-3"
                    ></i>
                    <p class="m-0 text-600">將 PDF 檔案拖放至此處以上傳</p>
                    <p class="m-0 text-sm text-500 mt-2">僅接受 PDF 檔案，檔案大小最大 10MB</p>
                  </div>
                </template>
              </FileUpload>
            </div>
            <div class="flex pt-6 justify-between">
              <Button
                label="上一步"
                icon="pi pi-arrow-left"
                severity="secondary"
                @click="activateCallback('2')"
              />
              <Button
                label="下一步"
                icon="pi pi-arrow-right"
                @click="activateCallback('4')"
                :disabled="!form.file"
              />
            </div>
          </StepPanel>

          <StepPanel v-slot="{ activateCallback }" value="4">
            <div class="flex flex-column gap-4">
              <div class="flex flex-column gap-2 p-3 surface-ground border-round">
                <div>
                  <strong>投稿類型：</strong>
                  {{ submissionKindLabel }}
                </div>
                <div v-if="form.requestNewCategory">
                  <strong>申請分類：</strong>
                  {{ form.requestedCategoryName }}（{{ form.requestedCategoryKey }}）
                </div>
                <div>
                  <strong>課程類別：</strong>
                  {{ effectiveCategoryName }}
                </div>
                <div>
                  <strong>課程名稱：</strong>
                  {{ effectiveSubject || '' }}
                </div>
                <div><strong>授課教授：</strong> {{ form.professor }}</div>
                <div>
                  <strong>考試學期：</strong>
                  {{ formatSemester(form.academicYear) }}
                </div>
                <div>
                  <strong>考試類型：</strong>
                  {{ getTypeName(form.type) }}
                </div>
                <div><strong>考試名稱：</strong> {{ generatedFilename }}</div>
                <div>
                  <strong>附解答：</strong>
                  {{ form.hasAnswers ? '是' : '否' }}
                </div>
              </div>
            </div>
            <div class="flex pt-6 justify-between">
              <Button
                label="上一步"
                icon="pi pi-arrow-left"
                severity="secondary"
                @click="activateCallback('3')"
              />
              <div class="flex gap-2.5">
                <Button
                  icon="pi pi-eye"
                  label="預覽"
                  severity="secondary"
                  @click="previewUploadFile"
                />
                <Button
                  label="上傳"
                  icon="pi pi-upload"
                  severity="success"
                  @click="handleUpload"
                  :loading="uploading"
                  :disabled="!canUpload"
                />
              </div>
            </div>
          </StepPanel>
        </StepPanels>
      </Stepper>
    </Dialog>

    <PdfPreviewModal
      :visible="showUploadPreview"
      @update:visible="showUploadPreview = $event"
      :previewUrl="uploadPreviewUrl"
      :title="form.file ? form.file.name : ''"
      :academicYear="formatSemester(form.academicYear)"
      :archiveType="form.type || ''"
      :courseName="effectiveSubject || ''"
      :professorName="
        typeof form.professor === 'string' ? form.professor : form.professor?.name || ''
      "
      :loading="uploadPreviewLoading"
      :error="uploadPreviewError"
      :showDownload="false"
      @hide="closeUploadPreview"
      @error="handleUploadPreviewError"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useToast } from 'primevue/usetoast'
import { courseService, archiveService } from '../api'
import PdfPreviewModal from './PdfPreviewModal.vue'
import { PDFDocument } from 'pdf-lib'
import { trackEvent, EVENTS } from '../utils/analytics'
import { isUnauthorizedError } from '../utils/http'
import { formatCourseDisplayName } from '../utils/courseText'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  coursesList: {
    type: Object,
    required: true,
  },
  courseCategories: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue', 'upload-success'])

const toast = useToast()
const NEW_CATEGORY_REQUIRES_COURSE_MESSAGE = '新增分類必須同時申請新增課程。'

const form = ref({
  category: null,
  subject: null,
  subjectId: null,
  requestNewCourse: false,
  requestedCourseName: '',
  requestNewCategory: false,
  requestedCategoryKey: '',
  requestedCategoryName: '',
  requestedCategoryLabel: '',
  professor: null,
  filename: '',
  examNumber: null,
  otherName: '',
  type: null,
  hasAnswers: false,
  academicYear: null,
  file: null,
})

const uploadStep = ref('1')
const uploading = ref(false)
const fileUpload = ref(null)
const uploadFormProfessors = ref([])
const isFilenameValid = ref(false)

const showUploadPreview = ref(false)
const uploadPreviewUrl = ref('')
const uploadPreviewLoading = ref(false)
const uploadPreviewError = ref(false)

const availableProfessors = ref([])

const categoryOptions = computed(() =>
  [...props.courseCategories]
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

const subjectOptions = computed(() =>
  (props.coursesList[form.value.category] || [])
    .filter((course) => !course.deleted_at)
    .sort((a, b) => {
      const orderDiff = (a.order_index ?? 0) - (b.order_index ?? 0)
      if (orderDiff !== 0) return orderDiff
      return (a.id ?? 0) - (b.id ?? 0)
    })
    .map((course) => ({
      name: formatCourseDisplayName(course.name),
      code: course.id,
    }))
)

const examNumberOptions = Array.from({ length: 20 }, (_, index) => ({
  name: `第 ${index + 1} 次`,
  value: index + 1,
}))

const currentSemesterCode = (() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth() + 1
  const rocYear = month >= 8 ? year - 1911 : year - 1912
  const semester = month >= 8 || month === 1 ? 1 : 2
  return rocYear * 10 + semester
})()

const semesterGroups = computed(() => {
  const groups = []
  const currentRocYear = Math.floor(currentSemesterCode / 10)
  const currentSemester = currentSemesterCode % 10

  for (let year = currentRocYear; year >= 89; year -= 1) {
    const semesters = []
    for (const semester of [1, 2]) {
      if (year === currentRocYear && semester > currentSemester) continue
      semesters.push({
        label: `${semester === 1 ? '上' : '下'}學期`,
        code: year * 10 + semester,
      })
    }
    if (semesters.length) {
      groups.push({ year, semesters })
    }
  }

  return groups
})

const requiresExamNumber = computed(() => ['midterm', 'quiz'].includes(form.value.type))

const isCategoryKeyValid = computed(() =>
  /^[a-z0-9-]{2,40}$/.test((form.value.requestedCategoryKey || '').trim())
)

const effectiveSubject = computed(() => {
  if (form.value.requestNewCourse) return formatCourseDisplayName(form.value.requestedCourseName)
  if (typeof form.value.subject === 'string') return formatCourseDisplayName(form.value.subject)
  return formatCourseDisplayName(form.value.subject?.name)
})

const effectiveCategory = computed(() => {
  if (form.value.requestNewCategory)
    return (form.value.requestedCategoryKey || '').trim().toLowerCase()
  return form.value.category
})

const effectiveCategoryName = computed(() => {
  if (form.value.requestNewCategory) return (form.value.requestedCategoryName || '').trim()
  return getCategoryName(form.value.category)
})

const submissionKindLabel = computed(() => {
  if (form.value.requestNewCategory) return '新分類與新課程申請'
  if (form.value.requestNewCourse) return '新課程申請'
  return '既有課程投稿'
})

const generatedFilename = computed(() => {
  if (form.value.type === 'midterm' && form.value.examNumber) {
    return `midterm${form.value.examNumber}`
  }
  if (form.value.type === 'quiz' && form.value.examNumber) {
    return `quiz${form.value.examNumber}`
  }
  if (form.value.type === 'final') return 'final'
  if (form.value.type === 'other') return form.value.otherName
  return ''
})

const canGoToStep2 = computed(() => {
  if (form.value.requestNewCategory && !form.value.requestNewCourse) return false
  const hasCategory = form.value.requestNewCategory
    ? isCategoryKeyValid.value && form.value.requestedCategoryName.trim()
    : form.value.category
  return hasCategory && effectiveSubject.value && form.value.professor
})

const canGoToStep3 = computed(() => {
  return (
    form.value.academicYear && form.value.type && generatedFilename.value && isFilenameValid.value
  )
})

const canUpload = computed(() => {
  return (
    form.value.file &&
    effectiveCategory.value &&
    effectiveSubject.value &&
    form.value.professor &&
    form.value.academicYear &&
    form.value.type &&
    generatedFilename.value
  )
})

function validateFilename() {
  const regex = /^[a-z]+[0-9]*$/
  isFilenameValid.value = regex.test(generatedFilename.value)
}

function formatSemester(value) {
  const numericValue = Number(value)
  if (!numericValue) return ''
  if (numericValue >= 1000 && numericValue < 2000) {
    const year = Math.floor(numericValue / 10)
    const semester = numericValue % 10
    return `${year}${semester === 1 ? '上' : '下'}學期`
  }
  return `${numericValue}`
}

function getCategoryName(code) {
  return props.courseCategories.find((category) => category.key === code)?.name || code
}

function getTypeName(code) {
  const types = {
    midterm: '期中考',
    final: '期末考',
    quiz: '小考',
    other: '其他',
  }
  return types[code] || code
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

async function fetchProfessorsForSubject(subjectId) {
  if (!subjectId) return

  try {
    const response = await courseService.getCourseArchives(subjectId)
    const archiveData = response.data

    const uniqueProfessors = new Set()
    archiveData.forEach((archive) => {
      if (archive.professor) uniqueProfessors.add(archive.professor)
    })

    uploadFormProfessors.value = Array.from(uniqueProfessors)
      .sort()
      .map((professor) => ({
        name: professor,
        code: professor,
      }))
  } catch (error) {
    console.error('Error fetching professors for subject:', error)
    uploadFormProfessors.value = []
  }
}

const handleUpload = async () => {
  if (form.value.requestNewCategory && !form.value.requestNewCourse) {
    toast.add({
      severity: 'error',
      summary: '無法送出',
      detail: NEW_CATEGORY_REQUIRES_COURSE_MESSAGE,
      life: 3000,
    })
    return
  }

  try {
    uploading.value = true

    const fileArrayBuffer = await form.value.file.arrayBuffer()
    const pdfDoc = await PDFDocument.load(fileArrayBuffer)

    pdfDoc.setTitle('')
    pdfDoc.setAuthor('')
    pdfDoc.setSubject('')
    pdfDoc.setKeywords([])
    pdfDoc.setProducer('')
    pdfDoc.setCreator('')
    pdfDoc.setCreationDate(new Date())
    pdfDoc.setModificationDate(new Date())
    const pdfBytes = await pdfDoc.save()
    const cleanFile = new Blob([pdfBytes], { type: 'application/pdf' })
    const cleanFileWithName = new File([cleanFile], form.value.file.name, {
      type: 'application/pdf',
    })

    const formData = new FormData()
    formData.append('file', cleanFileWithName)
    formData.append('subject', effectiveSubject.value)
    formData.append('category', effectiveCategory.value)
    formData.append('professor', form.value.professor)
    formData.append('archive_type', form.value.type)
    formData.append('has_answers', form.value.hasAnswers)
    formData.append('filename', generatedFilename.value)
    formData.append('academic_year', form.value.academicYear)
    formData.append('request_new_course', form.value.requestNewCourse)
    formData.append('request_new_category', form.value.requestNewCategory)
    if (form.value.requestNewCourse) {
      formData.append('requested_course_name', effectiveSubject.value)
    }
    if (form.value.requestNewCategory) {
      formData.append('requested_category_key', effectiveCategory.value)
      formData.append('requested_category_name', form.value.requestedCategoryName.trim())
      formData.append(
        'requested_category_label',
        (form.value.requestedCategoryLabel || form.value.requestedCategoryName).trim()
      )
      formData.append('requested_category_icon', 'pi pi-fw pi-book')
    }

    const response = await archiveService.uploadArchive(formData)
    const uploadResult = response?.data || {}
    const uploadedSubmission = uploadResult.submission || {}
    const isAdminUpload =
      uploadResult.is_admin_upload === true || uploadedSubmission.is_admin_upload === true

    emit('update:modelValue', false)
    emit('upload-success')

    toast.add({
      severity: 'success',
      summary: isAdminUpload ? '管理員投稿成功' : '已送出審核',
      detail: isAdminUpload
        ? '考古題已直接建立，不需再經審核。'
        : '考古題投稿已送至管理者審核，通過後才會公開',
      life: 3000,
    })
  } catch (error) {
    console.error('Upload error:', error)
    if (isUnauthorizedError(error)) {
      return
    }

    toast.add({
      severity: 'error',
      summary: '上傳失敗',
      detail: '發生錯誤，請稍後再試',
      life: 3000,
    })
  } finally {
    uploading.value = false
  }
}

const onFileSelect = (event) => {
  const newFile = event.files[0]

  if (fileUpload.value) {
    fileUpload.value.clear()
  }
  form.value.file = null

  nextTick(() => {
    form.value.file = newFile
  })
}

function clearSelectedFile(removeFileCallback) {
  if (removeFileCallback) removeFileCallback(0)
  form.value.file = null
  if (fileUpload.value) {
    fileUpload.value.clear()
  }
}

function previewUploadFile() {
  if (!form.value.file) return

  uploadPreviewLoading.value = true
  uploadPreviewError.value = false

  try {
    const fileUrl = URL.createObjectURL(new Blob([form.value.file], { type: 'application/pdf' }))
    uploadPreviewUrl.value = fileUrl
    showUploadPreview.value = true

    trackEvent(EVENTS.PREVIEW_ARCHIVE, {
      context: 'upload-dialog',
      fileName: generatedFilename.value,
      fileSize: form.value.file.size,
    })
  } catch (error) {
    console.error('Preview error:', error)
    uploadPreviewError.value = true
    toast.add({
      severity: 'error',
      summary: '預覽失敗',
      detail: '無法預覽檔案',
      life: 3000,
    })
  } finally {
    uploadPreviewLoading.value = false
  }
}

function handleUploadPreviewError() {
  uploadPreviewError.value = true
}

function closeUploadPreview() {
  showUploadPreview.value = false
  if (uploadPreviewUrl.value) {
    URL.revokeObjectURL(uploadPreviewUrl.value)
    uploadPreviewUrl.value = ''
  }
  uploadPreviewError.value = false
}

const searchProfessor = (event) => {
  const query = event?.query?.toLowerCase() || ''
  const filteredProfessors = uploadFormProfessors.value
    .filter((professor) => professor.name.toLowerCase().includes(query))
    .sort((a, b) => a.name.localeCompare(b.name))

  availableProfessors.value = filteredProfessors
}

const onProfessorSelect = (event) => {
  if (event.value && typeof event.value === 'object') {
    form.value.professor = event.value.name
  }
}

watch(
  () => form.value.category,
  () => {
    if (form.value.requestNewCategory) return
    form.value.subject = null
    form.value.subjectId = null
    form.value.professor = null
  }
)

watch(
  () => form.value.subject,
  (subject) => {
    form.value.subjectId = subject && typeof subject === 'object' ? subject.code : null
  }
)

watch(
  () => effectiveSubject.value,
  (newSubject) => {
    form.value.professor = null
    if (newSubject && !form.value.requestNewCourse) {
      fetchProfessorsForSubject(form.value.subjectId)
    } else {
      uploadFormProfessors.value = []
    }
  }
)

watch(
  () => form.value.requestNewCategory,
  (enabled) => {
    if (enabled) {
      form.value.requestNewCourse = true
      form.value.category = null
      form.value.subject = null
      form.value.subjectId = null
    } else {
      form.value.requestedCategoryKey = ''
      form.value.requestedCategoryName = ''
      form.value.requestedCategoryLabel = ''
    }
  }
)

watch(
  () => form.value.requestNewCourse,
  (enabled) => {
    if (!enabled && form.value.requestNewCategory) {
      form.value.requestNewCourse = true
      return
    }
    form.value.subject = null
    form.value.subjectId = null
    form.value.requestedCourseName = ''
    form.value.professor = null
  }
)

watch(
  () => form.value.type,
  (type) => {
    form.value.examNumber = null
    form.value.otherName = ''
    if (type === 'final') {
      form.value.filename = 'final'
    } else {
      form.value.filename = ''
    }
    validateFilename()
  }
)

watch(generatedFilename, (filename) => {
  form.value.filename = filename
  validateFilename()
})

watch(
  () => props.modelValue,
  (newValue, oldValue) => {
    if (oldValue === true && newValue === false) {
      resetForm()
    }
  }
)

function resetForm() {
  form.value = {
    category: null,
    subject: null,
    subjectId: null,
    requestNewCourse: false,
    requestedCourseName: '',
    requestNewCategory: false,
    requestedCategoryKey: '',
    requestedCategoryName: '',
    requestedCategoryLabel: '',
    professor: null,
    filename: '',
    examNumber: null,
    otherName: '',
    type: null,
    hasAnswers: false,
    academicYear: null,
    file: null,
  }
  uploadStep.value = '1'
  isFilenameValid.value = false
  availableProfessors.value = []
  uploadFormProfessors.value = []

  if (fileUpload.value) {
    fileUpload.value.clear()
  }

  closeUploadPreview()
}
</script>

<style scoped>
.flex-wrap {
  flex-wrap: wrap;
}

.ellipsis {
  display: inline-block;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: middle;
}

.request-mode-panel,
.new-category-grid {
  border: 1px solid var(--p-content-border-color);
  border-radius: 8px;
  padding: 0.9rem;
  background: color-mix(in srgb, var(--p-content-background) 92%, var(--p-primary-color) 8%);
}

.new-category-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.new-category-grid > :first-child {
  grid-column: 1 / -1;
}

@media (max-width: 640px) {
  .new-category-grid {
    grid-template-columns: 1fr;
  }
}

.semester-picker {
  border: 1px solid var(--p-inputtext-border-color);
  border-radius: 8px;
  background: var(--p-inputtext-background);
  overflow: hidden;
}

.semester-picker-value {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--p-content-border-color);
  color: var(--text-primary);
  font-weight: 600;
}

.semester-grid {
  display: grid;
  gap: 0.45rem;
  max-height: 15.5rem;
  padding: 0.75rem;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.semester-row {
  display: grid;
  grid-template-columns: 4.5rem repeat(2, minmax(0, 1fr));
  align-items: center;
  gap: 0.5rem;
}

.semester-year {
  color: var(--text-secondary);
  font-weight: 700;
}

.semester-option {
  min-height: 2.65rem;
  border: 1px solid rgba(167, 176, 190, 0.34);
  border-radius: 7px;
  background: rgba(21, 38, 33, 0.88);
  color: rgba(242, 248, 244, 0.96);
  font: inherit;
  font-weight: 650;
  cursor: pointer;
  transition:
    background 0.16s ease,
    border-color 0.16s ease,
    color 0.16s ease;
}

.semester-option:hover {
  border-color: #35d39a;
  background: rgba(30, 58, 49, 0.94);
}

.semester-option.selected {
  border-color: #42dca4;
  background: #36d399;
  color: #04130e;
  box-shadow: 0 0 0 1px rgba(54, 211, 153, 0.26);
}

.semester-option:disabled {
  opacity: 0.38;
  cursor: not-allowed;
}

@media (max-width: 520px) {
  .semester-row {
    grid-template-columns: 1fr;
  }
}
</style>
