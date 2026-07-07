<template>
  <main class="personal-settings-page">
    <section class="personal-settings-shell">
      <header class="settings-header">
        <h1>個人化設定</h1>
      </header>

      <div class="settings-layout">
        <aside class="settings-nav" aria-label="個人化設定目錄">
          <button
            v-for="item in navItems"
            :key="item.id"
            type="button"
            class="settings-nav-item"
            :class="[`settings-nav-item--${item.level}`, { active: activeSection === item.id }]"
            @click="scrollToSection(item.id)"
          >
            {{ item.label }}
          </button>
        </aside>

        <div class="settings-content">
          <section id="display-settings" class="settings-group settings-anchor">
            <div class="settings-group-header">
              <h2>顯示設定</h2>
              <p>調整網站閱讀與顯示偏好。</p>
            </div>

            <Card class="settings-section">
              <template #title>顯示設定</template>
              <template #content>
                <form class="settings-form" @submit.prevent="saveDisplaySettings">
                  <div class="settings-grid">
                    <div id="font-size-setting" class="field settings-anchor font-size-setting">
                      <div class="font-size-controls">
                        <label id="font-size-label">字體大小</label>
                        <div class="font-size-slider-row">
                          <Slider
                            v-model="fontSizeIndex"
                            :min="0"
                            :max="fontSizeOptions.length - 1"
                            :step="1"
                            class="font-size-slider"
                            aria-labelledby="font-size-label"
                          />
                          <span class="font-size-current">{{ currentFontSizeOption.label }}</span>
                        </div>
                        <small>偏好值會保存於此裝置，重新整理後仍會保留。</small>
                      </div>

                      <div class="font-size-preview" :style="fontSizePreviewStyle">
                        <h3>清大物理考古系統</h3>
                        <p>這是一段用來預覽目前字體大小的文字。</p>
                        <small>篩選、預覽、下載等操作文字會依設定調整。</small>
                      </div>
                    </div>

                    <div id="language-setting" class="field settings-anchor">
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

          <section id="account-settings" class="settings-group settings-anchor">
            <div class="settings-group-header">
              <h2>帳號設定</h2>
              <p>管理名稱、電子郵件與密碼。</p>
            </div>

            <Card id="profile-setting" class="settings-section settings-anchor">
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

            <Card id="password-setting" class="settings-section settings-anchor">
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
                    <small v-if="passwordMismatch" class="field-error">{{
                      passwordMismatch
                    }}</small>
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
          </section>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
import { userService } from '../api'
import { getCurrentUser } from '../utils/auth'
import { getLocalItem, setLocalItem } from '../utils/storage'
import {
  FONT_SIZE_OPTIONS,
  getFontSizePreference,
  setFontSizePreference,
} from '../utils/fontSizePreference'
import { useToast } from 'primevue/usetoast'

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
        fontSize: getFontSizePreference(),
        language: getLocalItem(LANGUAGE_KEY) || 'zh-TW',
      },
      fontSizeIndex: FONT_SIZE_OPTIONS.findIndex(
        (option) => option.value === getFontSizePreference()
      ),
      activeSection: 'display-settings',
      sectionObserver: null,
      navItems: [
        { id: 'display-settings', label: '顯示設定', level: 'group' },
        { id: 'font-size-setting', label: '字體大小', level: 'item' },
        { id: 'language-setting', label: '語言', level: 'item' },
        { id: 'account-settings', label: '帳號設定', level: 'group' },
        { id: 'profile-setting', label: '基本資料', level: 'item' },
        { id: 'password-setting', label: '密碼設定', level: 'item' },
      ],
      fontSizeOptions: FONT_SIZE_OPTIONS,
      languageOptions: [
        { label: '繁體中文', value: 'zh-TW' },
        { label: 'English', value: 'en' },
      ],
    }
  },
  computed: {
    currentFontSizeOption() {
      return this.fontSizeOptions[this.fontSizeIndex] || this.fontSizeOptions[1]
    },
    fontSizePreviewStyle() {
      return {
        '--preview-font-scale': this.currentFontSizeOption.scale,
      }
    },
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
  watch: {
    fontSizeIndex() {
      const option = this.currentFontSizeOption
      this.displayForm.fontSize = option.value
      setFontSizePreference(option.value)
    },
  },
  mounted() {
    void this.loadProfile()
    this.$nextTick(() => {
      this.setupSectionObserver()
    })
  },
  beforeUnmount() {
    this.teardownSectionObserver()
  },
  methods: {
    scrollToSection(sectionId) {
      const target = document.getElementById(sectionId)
      if (!target) {
        return
      }

      target.scrollIntoView({ behavior: 'smooth', block: 'start' })
      this.activeSection = sectionId
    },

    setupSectionObserver() {
      this.teardownSectionObserver()

      if (typeof IntersectionObserver === 'undefined') {
        return
      }

      const targets = this.navItems.map((item) => document.getElementById(item.id)).filter(Boolean)
      const root = document.querySelector('.content-container')

      this.sectionObserver = new IntersectionObserver(
        (entries) => {
          const visible = entries
            .filter((entry) => entry.isIntersecting)
            .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)

          if (visible[0]?.target?.id) {
            this.activeSection = visible[0].target.id
          }
        },
        {
          root,
          rootMargin: '-16% 0px -68% 0px',
          threshold: [0, 0.2, 0.6],
        }
      )

      targets.forEach((target) => this.sectionObserver.observe(target))
    },

    teardownSectionObserver() {
      if (this.sectionObserver) {
        this.sectionObserver.disconnect()
        this.sectionObserver = null
      }
    },

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
      // TODO: Sync font-size preference with backend profile settings when the API is available.
      setFontSizePreference(this.displayForm.fontSize)
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
  width: min(100%, 1040px);
  margin: 0 auto;
  padding: 2.25rem 1.5rem 3.5rem;
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

.settings-layout {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr);
  gap: 2rem;
  align-items: start;
}

.settings-nav {
  position: sticky;
  top: 1rem;
  display: grid;
  gap: 0.2rem;
  padding: 0.35rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: color-mix(in srgb, var(--bg-secondary) 82%, transparent);
}

.settings-nav-item {
  width: 100%;
  min-height: 2rem;
  padding: 0.35rem 0.6rem;
  border: 0;
  border-radius: 6px;
  color: var(--text-secondary);
  background: transparent;
  font: inherit;
  font-size: 0.92rem;
  line-height: 1.35;
  text-align: left;
  cursor: pointer;
}

.settings-nav-item:hover,
.settings-nav-item.active {
  color: var(--text-primary);
  background: color-mix(in srgb, var(--text-primary) 9%, transparent);
}

.settings-nav-item--item {
  padding-left: 1.25rem;
  font-size: 0.86rem;
}

.settings-content {
  min-width: 0;
}

.settings-anchor {
  scroll-margin-top: 1rem;
}

.settings-group {
  padding-top: 0.5rem;
}

.settings-group + .settings-group {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-color);
}

.settings-group-header {
  max-width: 640px;
  margin-bottom: 0.85rem;
}

.settings-group-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.18rem;
  font-weight: 760;
  letter-spacing: 0;
}

.settings-group-header p {
  margin: 0.35rem 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.settings-section {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
}

.settings-section + .settings-section {
  margin-top: 1.25rem;
}

.settings-form {
  display: grid;
  gap: 1.25rem;
  width: min(100%, 640px);
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

.font-size-setting {
  grid-column: 1 / -1;
  grid-template-columns: minmax(0, 320px) minmax(240px, 1fr);
  gap: 1rem;
  align-items: start;
}

.font-size-controls {
  display: grid;
  gap: 0.8rem;
}

.font-size-slider-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 4rem;
  gap: 1rem;
  align-items: center;
}

.font-size-slider {
  min-width: 0;
}

.font-size-current {
  color: var(--text-primary);
  font-weight: 700;
  text-align: right;
}

.font-size-preview {
  display: grid;
  gap: 0.35rem;
  padding: 1rem;
  border: 1px solid color-mix(in srgb, var(--border-color) 82%, transparent);
  border-radius: 8px;
  background: color-mix(in srgb, var(--bg-primary) 72%, var(--bg-secondary));
  font-size: calc(1rem * var(--preview-font-scale));
}

.font-size-preview h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.05em;
  font-weight: 760;
  letter-spacing: 0;
}

.font-size-preview p {
  margin: 0;
  color: var(--text-primary);
  line-height: 1.65;
}

.font-size-preview small {
  font-size: 0.86em;
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
  justify-content: flex-start;
}

@media (max-width: 640px) {
  .personal-settings-shell {
    padding: 1.25rem 0.75rem 2rem;
  }

  .settings-layout {
    display: grid;
    gap: 1rem;
  }

  .settings-nav {
    position: static;
    display: flex;
    gap: 0.35rem;
    padding: 0.35rem;
    overflow-x: auto;
  }

  .settings-nav-item {
    width: auto;
    flex: 0 0 auto;
    white-space: nowrap;
  }

  .settings-nav-item--item {
    padding-left: 0.6rem;
  }

  .form-actions {
    justify-content: stretch;
  }

  .settings-grid {
    grid-template-columns: 1fr;
  }

  .font-size-setting {
    grid-template-columns: 1fr;
  }

  .font-size-slider-row {
    grid-template-columns: minmax(0, 1fr) 3.5rem;
  }

  .form-actions :deep(.p-button) {
    width: 100%;
  }
}
</style>
