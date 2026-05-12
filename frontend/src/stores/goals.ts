import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export interface SavingsGoal {
  id: number
  name: string
  target_amount: string
  current_amount: string
  deadline: string | null
  percentage: number
  created_at: string
  updated_at: string
}

export const useGoalStore = defineStore('goals', () => {
  const goals = ref<SavingsGoal[]>([])
  const loading = ref(false)

  async function fetchGoals() {
    loading.value = true
    try {
      const { data } = await api.get('/goals/')
      goals.value = data.results ?? data
    } finally {
      loading.value = false
    }
  }

  async function createGoal(payload: Partial<SavingsGoal>) {
    const { data } = await api.post('/goals/', payload)
    await fetchGoals()
    return data
  }

  async function updateGoal(id: number, payload: Partial<SavingsGoal>) {
    const { data } = await api.put(`/goals/${id}/`, payload)
    await fetchGoals()
    return data
  }

  async function deleteGoal(id: number) {
    await api.delete(`/goals/${id}/`)
    await fetchGoals()
  }

  return { goals, loading, fetchGoals, createGoal, updateGoal, deleteGoal }
})
