<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const username = computed(() => authStore.user?.first_name || authStore.user?.username || 'User')

function logout() {
  authStore.logout()
}
</script>

<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <img src="/media/logo_big.png" alt="SpendWise" class="app-logo" />
      </div>

      <nav class="sidebar-nav">
        <RouterLink to="/" class="nav-link" :class="{ active: route.path === '/' }">
          Dashboard
        </RouterLink>
        <RouterLink to="/transactions" class="nav-link" :class="{ active: route.path.startsWith('/transactions') }">
          Transactions
        </RouterLink>
        <RouterLink to="/categories" class="nav-link" :class="{ active: route.path.startsWith('/categories') }">
          Categories
        </RouterLink>
        <RouterLink to="/budgets" class="nav-link" :class="{ active: route.path.startsWith('/budgets') }">
          Budgets
        </RouterLink>
        <RouterLink to="/goals" class="nav-link" :class="{ active: route.path.startsWith('/goals') }">
          Goals
        </RouterLink>
        <RouterLink to="/reports" class="nav-link" :class="{ active: route.path.startsWith('/reports') }">
          Reports
        </RouterLink>
        <RouterLink to="/settings" class="nav-link" :class="{ active: route.path.startsWith('/settings') }">
          Settings
        </RouterLink>
      </nav>

      <div class="sidebar-footer">
        <button class="logout-btn" @click="logout">
          Logout
        </button>
      </div>
    </aside>

    <div class="main-wrapper">
      <header class="top-bar">
        <div class="top-bar-content">
          <span class="greeting">Hello, {{ username }}</span>
          <button class="dark-mode-toggle" @click="authStore.toggleDarkMode()" :title="authStore.darkMode ? 'Switch to light mode' : 'Switch to dark mode'">
            <svg v-if="authStore.darkMode" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
          </button>
        </div>
      </header>

      <main class="page-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 240px;
  min-width: 240px;
  height: 100vh;
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg-sidebar);
  color: var(--color-text-sidebar);
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  align-items: center;
  padding: 24px 20px;
  border-bottom: 1px solid var(--color-border-sidebar);
}

.app-logo {
  max-width: 100%;
  height: auto;
  max-height: 120px;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 16px 0;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  border-left: 3px solid transparent;
  color: var(--color-text-sidebar);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: color 150ms, background-color 150ms, border-color 150ms;
}

.nav-link:hover {
  background-color: var(--color-bg-sidebar-hover);
  color: var(--color-text-sidebar-hover);
}

.nav-link.active {
  border-left-color: var(--color-accent);
  background-color: var(--color-bg-sidebar-hover);
  color: var(--color-text-sidebar-active);
  font-weight: 600;
}

.sidebar-footer {
  padding: 16px 0;
  border-top: 1px solid var(--color-border-sidebar);
}

.logout-btn {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 10px 23px;
  border: none;
  background: transparent;
  color: var(--color-text-sidebar);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: color 150ms;
}

.logout-btn:hover {
  color: var(--color-logout-hover);
}

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  overflow-y: auto;
  background-color: var(--color-bg-primary);
}

.top-bar {
  background-color: var(--color-bg-topbar);
  border-bottom: 1px solid var(--color-border);
  padding: 0 32px;
  height: 56px;
  display: flex;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 10;
}

.top-bar-content {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.greeting {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.dark-mode-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  cursor: pointer;
  margin-left: 12px;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}

.dark-mode-toggle:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.page-content {
  flex: 1;
  padding: 32px;
}
</style>
