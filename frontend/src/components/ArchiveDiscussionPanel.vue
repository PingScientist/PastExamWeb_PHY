<template>
  <div class="discussion-panel flex flex-column" :style="{ width }">
    <div
      v-if="showHeader"
      class="discussion-header p-3 flex align-items-center justify-content-between"
    >
      <div class="font-semibold">討論區</div>
      <Button
        v-if="showSettings"
        icon="pi pi-cog"
        severity="secondary"
        text
        rounded
        size="small"
        aria-label="暱稱設定"
        class="discussion-settings-btn"
        @click="openNicknameDialog"
      />
    </div>

    <div ref="messagesRef" class="flex-1 overflow-auto p-3 flex flex-column gap-2">
      <div v-if="loading" class="flex-1 flex align-items-center justify-content-center">
        <ProgressSpinner strokeWidth="4" />
      </div>
      <div v-else-if="messages.length === 0" class="text-sm" style="color: var(--text-secondary)">
        還沒有人發起討論，來當第一個吧！
      </div>

      <div
        v-for="msg in sortedMessages"
        :key="msg.id"
        class="message p-2.5"
        :class="{ 'is-pinned': msg.is_pinned }"
      >
        <div class="flex align-items-center justify-content-between gap-3">
          <div class="discussion-author flex align-items-center gap-2 min-w-0">
            <Tag v-if="msg.is_pinned" value="置頂" severity="warning" class="discussion-pin-tag" />
            <div class="discussion-author-name text-sm font-semibold">{{ msg.user_name }}</div>
            <ContributorLevelBadge
              v-if="shouldShowLevelTitle(msg)"
              :level="getMessageLevel(msg).level"
              :title="getMessageLevel(msg).name"
              size="compact"
            />
          </div>
          <div class="flex align-items-center gap-2">
            <div class="text-xs" style="color: var(--text-secondary)">
              {{ formatTime(msg.created_at) }}
            </div>
            <Button
              v-if="canPin"
              :icon="msg.is_pinned ? 'pi pi-bookmark-fill' : 'pi pi-bookmark'"
              severity="warning"
              text
              size="small"
              rounded
              :aria-label="msg.is_pinned ? '取消置頂' : '置頂'"
              class="discussion-pin-btn"
              @click="togglePin(msg)"
            />
            <Button
              v-if="canDelete(msg)"
              icon="pi pi-trash"
              severity="danger"
              text
              size="small"
              rounded
              aria-label="刪除"
              class="discussion-delete-btn"
              @click="confirmDelete(msg)"
            />
          </div>
        </div>
        <div class="text-sm mt-1 whitespace-pre-wrap break-words">
          <div>{{ getMessageText(msg) }}</div>
          <div v-if="shouldShowToggle(msg)" class="flex justify-content-end mt-1">
            <button
              type="button"
              class="discussion-more-btn"
              @click="toggleExpanded(msg.id)"
              :aria-label="isExpanded(msg.id) ? '收合訊息' : '顯示更多訊息'"
            >
              {{ isExpanded(msg.id) ? '顯示較少' : '顯示更多' }}
              <i :class="`pi ${isExpanded(msg.id) ? 'pi-angle-up' : 'pi-angle-down'}`" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="discussion-footer p-3 flex gap-2">
      <div class="flex-1 flex flex-column gap-1 min-w-0">
        <Textarea
          name="discussion-message"
          v-model="draft"
          placeholder="輸入訊息"
          class="w-full"
          :maxlength="MESSAGE_MAX_LENGTH"
          :disabled="!canSend"
          rows="1"
          style="resize: vertical"
          @keydown.enter.ctrl.exact.prevent="send"
          @keydown.enter.meta.exact.prevent="send"
        />
        <div class="text-xs flex justify-content-end" :style="{ color: messageLengthColor }">
          {{ messageLengthLabel }}
        </div>
      </div>
      <Button
        icon="pi pi-send"
        label="送出"
        severity="secondary"
        :disabled="!canSend || !draft.trim() || draft.length > MESSAGE_MAX_LENGTH"
        @click="send"
      />
    </div>

    <Dialog
      :visible="showNicknameDialog"
      @update:visible="(val) => !val && closeNicknameDialog()"
      :modal="true"
      :draggable="false"
      :style="{ width: '420px', maxWidth: '92vw' }"
      :autoFocus="false"
      :pt="{ root: { 'aria-label': '討論區設定', 'aria-labelledby': null } }"
    >
      <template #header>
        <div class="flex align-items-center gap-2.5">
          <i class="pi pi-cog text-2xl" />
          <div class="text-xl leading-tight font-semibold">討論區設定</div>
        </div>
      </template>
      <div class="flex flex-column gap-3">
        <div class="flex flex-column gap-2">
          <label for="discussion-nickname" class="font-semibold">暱稱</label>
          <InputText
            id="discussion-nickname"
            name="discussion-nickname"
            v-model="nicknameDraft"
            placeholder="輸入暱稱"
            maxlength="15"
            class="w-full"
          />
          <small class="text-xs" style="color: var(--text-secondary)">{{ nicknameHint }}</small>
        </div>
        <div class="flex flex-column gap-2">
          <label class="font-semibold">其他</label>
          <label for="discussion-desktop-default-open" class="flex align-items-center gap-2">
            <Checkbox
              inputId="discussion-desktop-default-open"
              name="discussion-desktop-default-open"
              v-model="desktopDefaultOpen"
              :binary="true"
              @change="handleDesktopDefaultOpenChange"
            />
            <span>預設開啟討論區</span>
          </label>
          <label for="discussion-show-level-title" class="discussion-setting-option">
            <Checkbox
              inputId="discussion-show-level-title"
              name="discussion-show-level-title"
              v-model="showLevelTitleDraft"
              :binary="true"
            />
            <span>
              <span>顯示我的等級稱號</span>
              <small>開啟後，留言名稱旁會顯示目前的 Lv. 與投稿稱號</small>
            </span>
          </label>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-content-end gap-2">
          <Button
            label="取消"
            severity="secondary"
            @click="closeNicknameDialog"
            :disabled="nicknameSaving"
          />
          <Button
            label="儲存"
            severity="success"
            :loading="nicknameSaving"
            :disabled="!canSaveNickname"
            @click="saveNickname"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, inject, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { discussionService, userService } from '../api'
import { getCurrentUser } from '../utils/auth'
import { formatRelativeTime } from '../utils/time'
import { trackEvent, EVENTS } from '../utils/analytics'
import { getBooleanPreference, setBooleanPreference } from '../utils/usePreferences'
import { STORAGE_KEYS } from '../utils/storage'
import { resolveSubmissionLevel } from '../utils/submissionLevel'
import ContributorLevelBadge from './ContributorLevelBadge.vue'

const DESKTOP_DEFAULT_OPEN_KEY = STORAGE_KEYS.local.DISCUSSION_DESKTOP_DEFAULT_OPEN

const props = defineProps({
  courseId: {
    type: [Number, String],
    required: true,
  },
  archiveId: {
    type: [Number, String],
    required: true,
  },
  width: {
    type: String,
    default: '360px',
  },
  enabled: {
    type: Boolean,
    default: true,
  },
  showHeader: {
    type: Boolean,
    default: true,
  },
  showSettings: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['desktop-default-open-change'])

const messages = ref([])
const loading = ref(false)
const connected = ref(false)
const connecting = ref(false)
const draft = ref('')

const toast = inject('toast', null)
const confirm = inject('confirm', null)

let socket = null
let reconnectTimer = null
let connectSeq = 0

const currentUser = computed(() => getCurrentUser())
const canSend = computed(() => props.enabled && connected.value && Boolean(currentUser.value))
const canPin = computed(() => Boolean(currentUser.value?.is_admin))
const messagesRef = ref(null)

const profile = ref({ nickname: '', name: '', showLevelTitle: true })
const showNicknameDialog = ref(false)
const nicknameDraft = ref('')
const showLevelTitleDraft = ref(true)
const nicknameSaving = ref(false)
const desktopDefaultOpen = ref(getBooleanPreference(DESKTOP_DEFAULT_OPEN_KEY, true))

const MESSAGE_MAX_LENGTH = 200
const MESSAGE_PREVIEW_LENGTH = 100
const WS_RECONNECT_MAX_ATTEMPTS = 6

const expandedById = ref({})
const reconnectAttempts = ref(0)

const sortedMessages = computed(() => {
  return [...messages.value].sort((a, b) => {
    if (Boolean(a.is_pinned) !== Boolean(b.is_pinned)) {
      return a.is_pinned ? -1 : 1
    }
    return Number(a.id || 0) - Number(b.id || 0)
  })
})

const nicknameHint = computed(() => {
  const trimmed = (nicknameDraft.value || '').trim()
  return `設定後，討論區會以暱稱顯示，留空以清除暱稱（${trimmed.length}/15）`
})

const canSaveNickname = computed(() => {
  return Boolean(currentUser.value) && !nicknameSaving.value
})

const messageLengthLabel = computed(() => {
  return `${String(draft.value ?? '').length}/${MESSAGE_MAX_LENGTH}`
})

const messageLengthColor = computed(() => {
  const len = (draft.value || '').length
  return len > MESSAGE_MAX_LENGTH ? 'var(--red-500)' : 'var(--text-secondary)'
})

function isExpanded(messageId) {
  return Boolean(expandedById.value?.[messageId])
}

function toggleExpanded(messageId) {
  expandedById.value = {
    ...(expandedById.value || {}),
    [messageId]: !isExpanded(messageId),
  }
}

function shouldShowToggle(msg) {
  const content = String(msg?.content ?? '')
  return content.length > MESSAGE_PREVIEW_LENGTH
}

function getMessageText(msg) {
  const content = String(msg?.content ?? '')
  if (isExpanded(msg?.id)) return content
  if (content.length <= MESSAGE_PREVIEW_LENGTH) return content
  return `${content.slice(0, MESSAGE_PREVIEW_LENGTH)}…`
}

function normalizeId(raw) {
  if (raw === null || raw === undefined) return null
  const n = typeof raw === 'string' ? Number(raw) : raw
  return Number.isFinite(n) ? n : null
}

function formatTime(val) {
  return formatRelativeTime(val)
}

function shouldShowLevelTitle(message) {
  return message?.author_show_level_title === true && Number.isFinite(message?.author_experience)
}

function getMessageLevel(message) {
  return resolveSubmissionLevel(message?.author_experience)
}

function scrollToBottom() {
  const el = messagesRef.value
  if (!el) return
  el.scrollTop = el.scrollHeight
}

function closeSocket() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
  if (!socket) return
  try {
    socket.__manualClose = true
    socket.close()
  } catch {
    // ignore
  }
  socket = null
  connected.value = false
  connecting.value = false
}

function scheduleReconnect() {
  if (!props.enabled) return
  if (!currentUser.value) return
  if (reconnectTimer) return
  if (reconnectAttempts.value >= WS_RECONNECT_MAX_ATTEMPTS) {
    toast?.add?.({
      severity: 'warn',
      summary: '連線中斷',
      detail: '討論區已斷線，請重新整理後再試',
      life: 4000,
    })
    return
  }

  reconnectAttempts.value += 1
  const baseDelayMs = 500
  const maxDelayMs = 10_000
  const delay = Math.min(maxDelayMs, baseDelayMs * 2 ** (reconnectAttempts.value - 1))
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null
    connect()
  }, delay)
}

async function connect() {
  const seq = (connectSeq += 1)
  closeSocket()
  if (!props.enabled) return
  const courseId = normalizeId(props.courseId)
  const archiveId = normalizeId(props.archiveId)
  if (!courseId || !archiveId) return
  if (!currentUser.value) return

  connecting.value = true
  connected.value = false
  loading.value = true

  const ws = discussionService.openArchiveDiscussionWebSocket(courseId, archiveId)
  if (!ws) {
    loading.value = false
    connecting.value = false
    return
  }
  socket = ws

  ws.onopen = () => {
    if (seq !== connectSeq) return
    connecting.value = false
    connected.value = true
    reconnectAttempts.value = 0
  }

  ws.onmessage = async (event) => {
    try {
      if (seq !== connectSeq) return
      const data = JSON.parse(event.data)
      if (!data || typeof data !== 'object') return
      if (data.type === 'history' && Array.isArray(data.messages)) {
        messages.value = data.messages
        loading.value = false
        await nextTick()
        scrollToBottom()
        return
      }
      if (data.type === 'error') {
        toast?.add?.({
          severity: 'error',
          summary: '送出失敗',
          detail: data.detail || '無法送出訊息，請稍後再試',
          life: 3000,
        })
        return
      }
      if (data.type === 'message' && data.message) {
        const incoming = data.message
        const user = currentUser.value
        const preferredName = (profile.value.nickname || profile.value.name || '').trim()
        const normalized =
          user && preferredName && incoming.user_id === user.id
            ? {
                ...incoming,
                user_name: preferredName,
                author_show_level_title: profile.value.showLevelTitle,
              }
            : incoming

        messages.value = [...messages.value, normalized]
        await nextTick()
        scrollToBottom()
        return
      }
      if (data.type === 'delete' && data.message_id) {
        messages.value = messages.value.filter((m) => m.id !== data.message_id)
      }
      if (data.type === 'pin' && data.message_id) {
        messages.value = messages.value.map((m) =>
          m.id === data.message_id ? { ...m, is_pinned: Boolean(data.is_pinned) } : m
        )
      }
    } catch {
      // ignore
    } finally {
      loading.value = false
    }
  }

  ws.onerror = () => {
    if (seq !== connectSeq) return
    if (ws.__manualClose) return
    connected.value = false
    connecting.value = false
    loading.value = false
    scheduleReconnect()
  }

  ws.onclose = (event) => {
    if (seq !== connectSeq) return
    if (ws.__manualClose) return
    connected.value = false
    connecting.value = false
    loading.value = false
    if (event?.code === 4401) return
    scheduleReconnect()
  }
}

async function send() {
  const rawContent = String(draft.value ?? '')
  if (!rawContent.trim()) return
  if (!socket || socket.readyState !== WebSocket.OPEN) return

  try {
    socket.send(
      JSON.stringify({
        type: 'send',
        content: rawContent,
      })
    )
    trackEvent(EVENTS.DISCUSSION_SEND_MESSAGE, {
      courseId: normalizeId(props.courseId),
      archiveId: normalizeId(props.archiveId),
      length: rawContent.length,
    })
    draft.value = ''
  } catch {
    // ignore
  }
}

function canDelete(msg) {
  const user = currentUser.value
  if (!user) return false
  return Boolean(user.is_admin || msg.user_id === user.id)
}

async function deleteMessage(msg) {
  const courseId = normalizeId(props.courseId)
  const archiveId = normalizeId(props.archiveId)
  if (!courseId || !archiveId) return

  try {
    await discussionService.deleteArchiveMessage(courseId, archiveId, msg.id)
    // optimistic; server will also broadcast delete
    messages.value = messages.value.filter((m) => m.id !== msg.id)
  } catch (error) {
    console.error('Delete message error:', error)
    toast?.add?.({
      severity: 'error',
      summary: '刪除失敗',
      detail: '無法刪除訊息，請稍後再試',
      life: 3000,
    })
  }
}

async function togglePin(msg) {
  if (!canPin.value) return
  const courseId = normalizeId(props.courseId)
  const archiveId = normalizeId(props.archiveId)
  if (!courseId || !archiveId) return
  const nextPinned = !msg.is_pinned

  messages.value = messages.value.map((m) =>
    m.id === msg.id ? { ...m, is_pinned: nextPinned } : m
  )

  try {
    await discussionService.pinArchiveMessage(courseId, archiveId, msg.id, nextPinned)
  } catch (error) {
    console.error('Pin message error:', error)
    messages.value = messages.value.map((m) =>
      m.id === msg.id ? { ...m, is_pinned: !nextPinned } : m
    )
    toast?.add?.({
      severity: 'error',
      summary: '置頂失敗',
      detail: '無法更新留言置頂狀態，請稍後再試',
      life: 3000,
    })
  }
}

function confirmDelete(msg) {
  if (!confirm?.require) {
    deleteMessage(msg)
    return
  }
  confirm.require({
    message: '確定要刪除這則訊息嗎？',
    header: '確認刪除',
    icon: 'pi pi-exclamation-triangle',
    accept: () => deleteMessage(msg),
  })
}

watch(
  () => [props.courseId, props.archiveId, props.enabled],
  () => {
    connect()
  }
)

onMounted(() => {
  loadMe()
  connect()
})

onBeforeUnmount(() => {
  closeSocket()
})

async function loadMe() {
  if (!currentUser.value) return
  try {
    const { data } = await userService.getMe()
    profile.value = {
      nickname: (data?.nickname || data?.name || '').trim(),
      name: (data?.name || '').trim(),
      showLevelTitle: data?.show_level_title !== false,
    }
  } catch {
    // ignore
  }
}

function openNicknameDialog() {
  nicknameDraft.value = (profile.value.nickname || profile.value.name || '').trim()
  showLevelTitleDraft.value = profile.value.showLevelTitle
  desktopDefaultOpen.value = getBooleanPreference(DESKTOP_DEFAULT_OPEN_KEY, true)
  showNicknameDialog.value = true
}

function closeNicknameDialog() {
  showNicknameDialog.value = false
}

defineExpose({
  openNicknameDialog,
})

async function saveNickname() {
  if (!currentUser.value) return
  const nextNickname = (nicknameDraft.value || '').trim()

  nicknameSaving.value = true
  try {
    const { data } = await userService.updateMyDiscussionSettings(
      nextNickname,
      showLevelTitleDraft.value
    )
    const newNickname = (data?.nickname || data?.name || '').trim()
    const newShowLevelTitle = data?.show_level_title !== false
    profile.value.nickname = newNickname
    profile.value.name = (data?.name || profile.value.name || '').trim()
    profile.value.showLevelTitle = newShowLevelTitle

    messages.value = messages.value.map((m) =>
      m.user_id === currentUser.value.id
        ? { ...m, user_name: newNickname, author_show_level_title: newShowLevelTitle }
        : m
    )

    trackEvent(EVENTS.DISCUSSION_UPDATE_NICKNAME, {
      cleared: !nextNickname,
      length: nextNickname.length,
    })

    toast?.add?.({
      severity: 'success',
      summary: '儲存成功',
      detail: '討論區設定已儲存',
      life: 2500,
    })
    closeNicknameDialog()
  } catch (error) {
    console.error('Update nickname error:', error)
    const detail = error?.response?.data?.detail
    toast?.add?.({
      severity: 'error',
      summary: '更新失敗',
      detail: typeof detail === 'string' && detail.trim() ? detail : '無法更新暱稱，請稍後再試',
      life: 3000,
    })
  } finally {
    nicknameSaving.value = false
  }
}

function handleDesktopDefaultOpenChange() {
  const next = Boolean(desktopDefaultOpen.value)
  setBooleanPreference(DESKTOP_DEFAULT_OPEN_KEY, next)
  emit('desktop-default-open-change', next)
  trackEvent(EVENTS.DISCUSSION_SET_DEFAULT_OPEN, { enabled: next })
}
</script>

<style scoped>
.discussion-panel {
  min-width: 280px;
  max-width: 420px;
  overflow: hidden;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.discussion-header {
  border-bottom: 1px solid var(--border-color);
}

.discussion-footer {
  border-top: 1px solid var(--border-color);
}

.message {
  border-radius: 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
}

.message.is-pinned {
  border-color: color-mix(in srgb, var(--brand-gold) 58%, var(--border-color));
  background: color-mix(in srgb, var(--brand-gold) 10%, var(--bg-secondary));
}

.discussion-author {
  flex-wrap: wrap;
}

.discussion-author-name {
  min-width: 0;
  overflow-wrap: anywhere;
}

.discussion-setting-option {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.discussion-setting-option > span {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 0.15rem;
}

.discussion-setting-option small {
  color: var(--text-secondary);
  line-height: 1.35;
  overflow-wrap: anywhere;
}

:deep(.discussion-pin-tag.p-tag) {
  padding: 0.1rem 0.45rem;
  font-size: 0.7rem;
  line-height: 1rem;
}

:deep(.discussion-pin-btn.p-button) {
  width: 1.25rem;
  height: 1.25rem;
  padding: 0;
  min-width: 1.25rem;
  flex: 0 0 auto;
}

:deep(.discussion-pin-btn.p-button .p-button-icon) {
  font-size: 0.75rem;
}

:deep(.discussion-delete-btn.p-button) {
  width: 1.25rem;
  height: 1.25rem;
  padding: 0;
  min-width: 1.25rem;
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

:deep(.discussion-delete-btn.p-button .p-button-icon) {
  font-size: 0.75rem;
}

:deep(.discussion-settings-btn.p-button) {
  width: 1.5rem;
  height: 1.5rem;
  padding: 0;
  min-width: 1.5rem;
}

.discussion-more-btn {
  margin-left: 0.25rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  padding: 0.15rem 0.6rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: var(--bg-primary);
  color: var(--text-color);
  cursor: pointer;
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.discussion-more-btn:hover {
  background: var(--bg-secondary);
}
</style>
