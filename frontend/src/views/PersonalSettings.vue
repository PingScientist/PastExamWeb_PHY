<template>
  <main class="personal-settings-page">
    <section class="personal-settings-shell">
      <header class="settings-header">
        <h1>個人化設定</h1>
      </header>

      <Card class="settings-section">
        <template #title>基本資料</template>
        <template #content>
          <form class="settings-form" @submit.prevent="saveProfile">
            <div class="field">
              <label for="display-name">名稱</label>
              <InputText
                id="display-name"
                v-model="profileForm.name"
                class="w-full"
                maxlength="15"
                :disabled="profileLoading"
              />
              <small>最多 15 字，會優先作為站內顯示名稱。</small>
            </div>

            <div class="field">
              <label for="email">電子郵件</label>
              <InputText id="email" v-model="profileForm.email" class="w-full" readonly />
            </div>

            <div class="form-actions">
              <Button
                label="儲存基本資料"
                icon="pi pi-save"
                type="submit"
                :loading="profileSaving"
                :disabled="profileLoading || !canSaveProfile"
              />
            </div>
          </form>
        </template>
      </Card>

      <Card class="settings-section">
        <template #title>密碼設定</template>
        <template #content>
          <form class="settings-form" @submit.prevent="savePassword">
            <div class="field">
              <label for="current-password">目前密碼</label>
              <Password
                id="current-password"
                v-model="passwordForm.currentPassword"
                class="w-full"
                inputClass="w-full"
                toggleMask
                :feedback="false"
              />
            </div>

            <div class="field">
              <label for="new-password">新密碼</label>
              <Password
                id="new-password"
                v-model="passwordForm.newPassword"
                class="w-full"
                inputClass="w-full"
                toggleMask
              />
            </div>

            <div class="field">
              <label for="confirm-password">確認新密碼</label>
              <Password
                id="confirm-password"
                v-model="passwordForm.confirmPassword"
                class="w-full"
                inputClass="w-full"
                toggleMask
                :feedback="false"
                :invalid="Boolean(passwordMismatch)"
              />
              <small v-if="passwordMismatch" class="field-error">{{ passwordMismatch }}</small>
            </div>

            <div class="form-actions">
              <Button
                label="儲存密碼"
                icon="pi pi-key"
                type="submit"
                :disabled="!canSubmitPassword"
              />
            </div>
          </form>
        </template>
      </Card>

      <Card class="settings-section">
        <template #title>顯示設定</template>
        <template #content>
          <form class="settings-form" @submit.prevent="saveDisplaySettings">
            <div class="settings-grid">
              <div class="field">
                <label for="font-size">字體大小</label>
                <Select
                  id="font-size"
                  v-model="displayForm.fontSize"
                  :options="fontSizeOptions"
                  optionLabel="label"
                  optionValue="value"
                  class="w-full"
                />
                <small>已先保存偏好值，之後可接入全域字體大小機制。</small>
              </div>

              <div class="field">
                <label for="language">語言</label>
                <Select
                  id="language"
                  v-model="displayForm.language"
                  :options="languageOptions"
                  optionLabel="label"
                  optionValue="value"
                  class="w-full"
                />
                <small>語言功能目前僅為 UI placeholder，正式英文翻譯表之後才會提供。</small>
              </div>
            </div>

            <div class="form-actions">
              <Button label="儲存顯示設定" icon="pi pi-save" type="submit" />
            </div>
          </form>
        </template>
      </Card>
    </section>
  </main>
</template>

<script>
import { userService } from '../api'
import { getCurrentUser } from '../utils/auth'
import { getLocalItem, setLocalItem } from '../utils/storage'
import { useToast } from 'primevue/usetoast'

const FONT_SIZE_KEY = 'personal-settings-font-size'
const LANGUAGE_KEY = 'personal-settings-language'

export default {
  name: 'PersonalSettings',
  setup() {
    const toast = useToast()

    return {
      toast,
    }
  },
  data() {
    const currentUser = getCurrentUser()

    return {
      profileLoading: false,
      profileSaving: false,
      originalName: (currentUser?.name || '').trim(),
      profileForm: {
        name: (currentUser?.name || '').trim(),
        email: (currentUser?.email || '').trim(),
      },
      passwordForm: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      },
      displayForm: {
        fontSize: getLocalItem(FONT_SIZE_KEY) || 'default',
        language: getLocalItem(LANGUAGE_KEY) || 'zh-TW',
      },
      fontSizeOptions: [
        { label: '小', value: 'small' },
        { label: '預設', value: 'default' },
        { label: '大', value: 'large' },
        { label: '特大', value: 'x-large' },
      ],
      languageOptions: [
        { label: '繁體中文', value: 'zh-TW' },
        { label: 'English', value: 'en' },
      ],
    }
  },
  computed: {
    canSaveProfile() {
      return (
        Boolean(this.profileForm.name.trim()) && this.profileForm.name.trim() !== this.originalName
      )
    },
    passwordMismatch() {
      if (!this.passwordForm.confirmPassword) {
        return ''
      }

      return this.passwordForm.newPassword === this.passwordForm.confirmPassword
        ? ''
        : '兩次輸入的新密碼不一致'
    },
    canSubmitPassword() {
      return (
        Boolean(this.passwordForm.currentPassword) &&
        Boolean(this.passwordForm.newPassword) &&
        Boolean(this.passwordForm.confirmPassword) &&
        !this.passwordMismatch
      )
    },
  },
  mounted() {
    void this.loadProfile()
  },
  methods: {
    async loadProfile() {
      this.profileLoading = true

      try {
        const { data } = await userService.getMe()
        const displayName = (data?.nickname || data?.name || '').trim()
        this.originalName = displayName
        this.profileForm.name = displayName
        this.profileForm.email = (data?.email || this.profileForm.email || '').trim()
      } catch (error) {
        console.error('Load profile failed:', error)
      } finally {
        this.profileLoading = false
      }
    },

    async saveProfile() {
      const nextName = this.profileForm.name.trim()
      if (!nextName || nextName === this.originalName) {
        return
      }

      this.profileSaving = true
      try {
        const { data } = await userService.updateMyNickname(nextName)
        const savedName = (data?.nickname || data?.name || nextName).trim()
        this.originalName = savedName
        this.profileForm.name = savedName
        this.profileForm.email = (data?.email || this.profileForm.email || '').trim()
        this.toast.add({
          severity: 'success',
          summary: '儲存成功',
          detail: '基本資料已更新',
          life: 2500,
        })
      } catch (error) {
        console.error('Save profile failed:', error)
        const detail = error?.response?.data?.detail
        this.toast.add({
          severity: 'error',
          summary: '更新失敗',
          detail:
            typeof detail === 'string' && detail.trim() ? detail : '無法更新基本資料，請稍後再試',
          life: 3000,
        })
      } finally {
        this.profileSaving = false
      }
    },

    savePassword() {
      if (!this.canSubmitPassword) {
        return
      }

      // TODO: Connect to a password update API when the backend endpoint is available.
      console.info('Password update is a UI placeholder until the backend API is ready.')
      this.passwordForm = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      }
      this.toast.add({
        severity: 'info',
        summary: '尚未送出',
        detail: '密碼 API 尚未接入，已先保留前端表單。',
        life: 3000,
      })
    },

    saveDisplaySettings() {
      // TODO: Apply font-size preference through a centralized global display setting.
      setLocalItem(FONT_SIZE_KEY, this.displayForm.fontSize)
      // TODO: Language selection is UI-only until the English translation table is provided.
      setLocalItem(LANGUAGE_KEY, this.displayForm.language)
      this.toast.add({
        severity: 'success',
        summary: '儲存成功',
        detail: '顯示設定偏好已保存',
        life: 2500,
      })
    },
  },
}
</script>

<style scoped>
.personal-settings-page {
  min-height: 100%;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.personal-settings-shell {
  width: min(100%, 960px);
  margin: 0 auto;
  padding: 2rem 1rem 3rem;
}

.settings-header {
  margin-bottom: 1.25rem;
}

h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.75rem;
  font-weight: 760;
  letter-spacing: 0;
}

.settings-section {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.settings-section + .settings-section {
  margin-top: 1rem;
}

.settings-form {
  display: grid;
  gap: 1.25rem;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.field {
  display: grid;
  gap: 0.45rem;
  margin: 0;
}

label {
  color: var(--text-primary);
  font-weight: 650;
}

small {
  color: var(--text-secondary);
}

.field-error {
  color: #dc2626;
}

.dark .field-error {
  color: #fca5a5;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 640px) {
  .personal-settings-shell {
    padding: 1.25rem 0.75rem 2rem;
  }

  .form-actions {
    justify-content: stretch;
  }

  .settings-grid {
    grid-template-columns: 1fr;
  }

  .form-actions :deep(.p-button) {
    width: 100%;
  }
}
</style>
