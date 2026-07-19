<template>
  <main class="comment-report-page" aria-labelledby="comment-report-title">
    <section class="comment-report-shell">
      <Button
        icon="pi pi-arrow-left"
        label="返回原畫面"
        severity="secondary"
        outlined
        class="comment-report-back"
        @click="goBack"
      />

      <Card class="comment-report-card">
        <template #title>
          <div class="comment-report-heading">
            <i class="pi pi-flag" aria-hidden="true" />
            <h1 id="comment-report-title">回報留言</h1>
          </div>
        </template>
        <template #content>
          <Message severity="info" :closable="false" class="comment-report-notice">
            回報功能尚在建置中。目前不會送出回報，也不會通知管理員。
          </Message>

          <div v-if="loading" class="comment-report-state" aria-live="polite">
            <ProgressSpinner strokeWidth="4" />
            <span>正在載入留言摘要…</span>
          </div>

          <div v-else-if="error" class="comment-report-state is-error" role="alert">
            <i class="pi pi-exclamation-circle" aria-hidden="true" />
            <span>{{ error }}</span>
          </div>

          <article v-else-if="message" class="comment-report-summary">
            <div class="comment-report-summary__label">被回報留言摘要</div>
            <dl class="comment-report-details">
              <div>
                <dt>留言者名稱</dt>
                <dd>{{ message.user_name }}</dd>
              </div>
              <div>
                <dt>留言時間</dt>
                <dd>{{ formatTime(message.created_at) }}</dd>
              </div>
              <div class="is-content">
                <dt>留言內容預覽</dt>
                <dd>{{ contentPreview }}</dd>
              </div>
            </dl>
          </article>
        </template>
      </Card>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { discussionService } from '../api'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const error = ref('')
const message = ref(null)

const contentPreview = computed(() => {
  if (message.value?.is_deleted) return '此留言已刪除'
  const content = String(message.value?.content || '').trim()
  return content.length > 240 ? `${content.slice(0, 240)}…` : content
})

function findMessage(messages, messageId) {
  for (const root of messages) {
    if (Number(root.id) === messageId) return root
    const reply = (root.replies || []).find((item) => Number(item.id) === messageId)
    if (reply) return reply
  }
  return null
}

function formatTime(value) {
  if (!value) return '未知時間'
  return new Intl.DateTimeFormat('zh-TW', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

async function loadMessage() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await discussionService.listArchiveMessages(
      route.params.courseId,
      route.params.archiveId,
      { limit: 100 }
    )
    message.value = findMessage(Array.isArray(data) ? data : [], Number(route.params.messageId))
    if (!message.value) error.value = '找不到這則留言，留言可能已被移除。'
  } catch (loadError) {
    console.error('Load comment report summary error:', loadError)
    error.value = '無法載入留言摘要，請返回原畫面後再試。'
  } finally {
    loading.value = false
  }
}

function goBack() {
  const returnTo = Array.isArray(route.query.returnTo)
    ? route.query.returnTo[0]
    : route.query.returnTo
  if (typeof returnTo === 'string' && returnTo.startsWith('/') && !returnTo.startsWith('//')) {
    router.push(returnTo)
    return
  }
  if (window.history.length > 1) {
    router.back()
    return
  }
  router.push({ name: 'Archive' })
}

onMounted(loadMessage)
</script>

<style scoped>
.comment-report-page {
  min-height: 100%;
  padding: clamp(1rem, 3vw, 2.5rem);
  background: var(--bg-primary);
  color: var(--text-primary);
}

.comment-report-shell {
  display: flex;
  width: min(100%, 760px);
  margin: 0 auto;
  flex-direction: column;
  gap: 1rem;
}

.comment-report-back {
  align-self: flex-start;
}

:deep(.comment-report-card.p-card) {
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-primary);
  box-shadow: 0 8px 24px color-mix(in srgb, var(--text-primary) 8%, transparent);
}

.comment-report-heading {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.comment-report-heading h1 {
  margin: 0;
  font-size: var(--app-font-size-lg);
}

.comment-report-notice {
  margin-bottom: 1.25rem;
}

.comment-report-state {
  display: flex;
  min-height: 9rem;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: var(--text-secondary);
}

.comment-report-state.is-error {
  color: var(--p-red-500, var(--text-primary));
}

.comment-report-summary {
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.comment-report-summary__label {
  margin-bottom: 0.8rem;
  font-weight: 700;
}

.comment-report-details {
  display: grid;
  gap: 0.9rem;
  margin: 0;
}

.comment-report-details > div {
  display: grid;
  grid-template-columns: minmax(7rem, 0.3fr) minmax(0, 1fr);
  gap: 0.5rem 1rem;
}

.comment-report-details dt {
  color: var(--text-secondary);
  font-size: var(--app-font-size-sm);
  font-weight: 600;
}

.comment-report-details dd {
  min-width: 0;
  margin: 0;
  line-height: 1.55;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}

@media (max-width: 520px) {
  .comment-report-page {
    padding: 0.75rem;
  }

  .comment-report-details > div {
    grid-template-columns: minmax(0, 1fr);
    gap: 0.2rem;
  }
}
</style>
