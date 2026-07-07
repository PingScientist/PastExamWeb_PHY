<template>
  <main class="personal-settings-page">
    <section class="personal-settings-shell">
      <h1>個人化設定</h1>
    </section>
  </main>
</template>

<script>
export default {
  name: 'PersonalSettings',
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
  padding: 2rem 1rem;
}

h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.75rem;
  font-weight: 760;
  letter-spacing: 0;
}
</style>
