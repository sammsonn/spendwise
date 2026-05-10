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

/* ---- Sidebar ---- */
.sidebar {
  width: 240px;
  min-width: 240px;
  height: 100vh;
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  background-color: #0f172a;
  color: #94a3b8;
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  align-items: center;
  padding: 24px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.app-logo {
  max-width: 100%;
  height: auto;
  max-height: 120px;
}

/* ---- Navigation ---- */
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
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: color 150ms, background-color 150ms, border-color 150ms;
}

.nav-link:hover {
  background-color: #1e293b;
  color: #f1f5f9;
}

.nav-link.active {
  border-left-color: #0d9488;
  background-color: #1e293b;
  color: #ffffff;
  font-weight: 600;
}

/* ---- Sidebar Footer ---- */
.sidebar-footer {
  padding: 16px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.logout-btn {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 10px 23px;
  border: none;
  background: transparent;
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: color 150ms;
}

.logout-btn:hover {
  color: #fca5a5;
}

/* ---- Main Content Area ---- */
.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  overflow-y: auto;
  background-color: #f8fafc;
}

.top-bar {
  background-color: #ffffff;
  border-bottom: 1px solid #e2e8f0;
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
  color: #475569;
}

.page-content {
  flex: 1;
  padding: 32px;
}
</style>
