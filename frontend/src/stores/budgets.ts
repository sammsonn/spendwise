import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export interface Budget {
  id: number
  category: number
  category_name: string
  category_color: string
  amount: string
  month: number
  year: number
  spent: number
}

export const useBudgetStore = defineStore('budgets', () => {
  const budgets = ref<Budget[]>([])
  const loading = ref(false)

  async function fetchBudgets(month?: number, year?: number) {
    loading.value = true
    try {
      const params: any = {}
      if (month) params.month = month
      if (year) params.year = year
      const { data } = await api.get('/budgets/', { params })
      budgets.value = data.results || data
    } finally {
      loading.value = false
    }
  }

  async function createBudget(payload: Partial<Budget>) {
    const { data } = await api.post('/budgets/', payload)
    await fetchBudgets()
    return data
  }

  async function updateBudget(id: number, payload: Partial<Budget>) {
    const { data } = await api.put(`/budgets/${id}/`, payload)
    await fetchBudgets()
    return data
  }

  async function deleteBudget(id: number) {
    await api.delete(`/budgets/${id}/`)
    await fetchBudgets()
  }

  return { budgets, loading, fetchBudgets, createBudget, updateBudget, deleteBudget }
})
