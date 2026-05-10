import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export interface Transaction {
  id: number
  amount: string
  description: string
  date: string
  category: number | null
  category_name: string
  category_color: string
  category_icon: string
  category_type: string
  is_recurring: boolean
  recurring_interval: string
  created_at: string
  updated_at: string
}

export interface TransactionFilters {
  date_from?: string
  date_to?: string
  category?: number
  type?: string
  search?: string
  page?: number
}

export const useTransactionStore = defineStore('transactions', () => {
  const transactions = ref<Transaction[]>([])
  const totalCount = ref(0)
  const currentPage = ref(1)
  const loading = ref(false)

  async function fetchTransactions(filters: TransactionFilters = {}) {
    loading.value = true
    try {
      const params: any = { page: filters.page || 1 }
      if (filters.date_from) params.date_from = filters.date_from
      if (filters.date_to) params.date_to = filters.date_to
      if (filters.category) params.category = filters.category
      if (filters.type) params.type = filters.type
      if (filters.search) params.search = filters.search
      const { data } = await api.get('/transactions/', { params })
      transactions.value = data.results
      totalCount.value = data.count
      currentPage.value = filters.page || 1
    } finally {
      loading.value = false
    }
  }

  async function createTransaction(payload: Partial<Transaction>) {
    const { data } = await api.post('/transactions/', payload)
    await fetchTransactions({ page: currentPage.value })
    return data
  }

  async function updateTransaction(id: number, payload: Partial<Transaction>) {
    const { data } = await api.put(`/transactions/${id}/`, payload)
    await fetchTransactions({ page: currentPage.value })
    return data
  }

  async function deleteTransaction(id: number) {
    await api.delete(`/transactions/${id}/`)
    await fetchTransactions({ page: currentPage.value })
  }

  async function importCSV(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await api.post('/transactions/import-csv/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    await fetchTransactions({ page: 1 })
    return data
  }

  async function exportCSV() {
    const { data } = await api.get('/transactions/export-csv/', { responseType: 'blob' })
    downloadBlob(data, 'transactions.csv', 'text/csv')
  }

  async function exportPDF() {
    const { data } = await api.get('/transactions/export-pdf/', { responseType: 'blob' })
    downloadBlob(data, 'transactions.pdf', 'application/pdf')
  }

  function downloadBlob(blob: Blob, filename: string, type: string) {
    const url = URL.createObjectURL(new Blob([blob], { type }))
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  return {
    transactions, totalCount, currentPage, loading,
    fetchTransactions, createTransaction, updateTransaction, deleteTransaction,
    importCSV, exportCSV, exportPDF,
  }
})
