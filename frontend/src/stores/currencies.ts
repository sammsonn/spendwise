import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export interface Currency {
  id: number
  code: string
  name: string
  symbol: string
}

export const useCurrencyStore = defineStore('currencies', () => {
  const currencies = ref<Currency[]>([])

  async function fetchCurrencies() {
    const { data } = await api.get('/currencies/')
    currencies.value = data.results || data
  }

  return { currencies, fetchCurrencies }
})
