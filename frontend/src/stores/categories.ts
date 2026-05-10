import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export interface Category {
  id: number
  name: string
  icon: string
  color: string
  type: 'income' | 'expense'
}

export const useCategoryStore = defineStore('categories', () => {
  const categories = ref<Category[]>([])
  const loading = ref(false)

  async function fetchCategories() {
    loading.value = true
    try {
      const { data } = await api.get('/categories/')
      categories.value = data.results || data
    } finally {
      loading.value = false
    }
  }

  async function createCategory(payload: Partial<Category>) {
    const { data } = await api.post('/categories/', payload)
    await fetchCategories()
    return data
  }

  async function updateCategory(id: number, payload: Partial<Category>) {
    const { data } = await api.put(`/categories/${id}/`, payload)
    await fetchCategories()
    return data
  }

  async function deleteCategory(id: number) {
    await api.delete(`/categories/${id}/`)
    await fetchCategories()
  }

  return { categories, loading, fetchCategories, createCategory, updateCategory, deleteCategory }
})
