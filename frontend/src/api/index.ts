import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const auth = useAuthStore()
      const refreshed = await auth.refresh()
      if (refreshed) {
        originalRequest.headers.Authorization = `Bearer ${auth.accessToken}`
        return api(originalRequest)
      }
      auth.logout()
      router.push('/login')
    }
    return Promise.reject(error)
  },
)

export default api
