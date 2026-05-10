import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const user = ref<any>(null)

  const isAuthenticated = computed(() => !!accessToken.value)
  const currencySymbol = computed(() => user.value?.preferred_currency_symbol || 'lei')

  async function login(username: string, password: string) {
    const { data } = await api.post('/auth/login/', { username, password })
    accessToken.value = data.access
    refreshToken.value = data.refresh
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    await fetchProfile()
  }

  async function register(payload: { username: string; email: string; password: string; password_confirm: string; first_name?: string; last_name?: string }) {
    await api.post('/auth/register/', payload)
    await login(payload.username, payload.password)
  }

  async function refresh(): Promise<boolean> {
    if (!refreshToken.value) return false
    try {
      const { data } = await api.post('/auth/refresh/', { refresh: refreshToken.value })
      accessToken.value = data.access
      if (data.refresh) refreshToken.value = data.refresh
      localStorage.setItem('access_token', data.access)
      if (data.refresh) localStorage.setItem('refresh_token', data.refresh)
      return true
    } catch {
      return false
    }
  }

  async function fetchProfile() {
    try {
      const { data } = await api.get('/auth/profile/')
      user.value = data
    } catch {
      // ignore
    }
  }

  function logout() {
    accessToken.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    router.push('/login')
  }

  return { accessToken, refreshToken, user, isAuthenticated, currencySymbol, login, register, refresh, fetchProfile, logout }
})
