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
    </section>
  </main>
</template>

<script>
import { userService } from '../api'
import { getCurrentUser } from '../utils/auth'
import { useToast } from 'primevue/usetoast'

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
    }
  },
  computed: {
    canSaveProfile() {
      return (
        Boolean(this.profileForm.name.trim()) && this.profileForm.name.trim() !== this.originalName
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

.settings-form {
  display: grid;
  gap: 1.25rem;
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

  .form-actions :deep(.p-button) {
    width: 100%;
  }
}
</style>
