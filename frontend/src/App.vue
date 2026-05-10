<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
</script>

<template>
  <AppLayout v-if="auth.isAuthenticated && !route.meta.guest">
    <RouterView />
  </AppLayout>
  <RouterView v-else />
</template>

<style>
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background-color: #f1f5f9;
  color: #1e293b;
  min-height: 100vh;
}

a {
  text-decoration: none;
  color: inherit;
}

button {
  cursor: pointer;
  border: none;
  font-family: inherit;
}

input, select, textarea {
  font-family: inherit;
  font-size: inherit;
}
</style>
