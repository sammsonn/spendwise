import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)
  let nextId = 1

  async function sendMessage(text: string) {
    messages.value.push({ id: nextId++, role: 'user', content: text, timestamp: new Date() })
    loading.value = true
    try {
      const { data } = await api.post('/ai/chat/', { message: text })
      messages.value.push({ id: nextId++, role: 'assistant', content: data.reply, timestamp: new Date() })
    } catch {
      messages.value.push({ id: nextId++, role: 'assistant', content: 'Sorry, something went wrong. Please try again.', timestamp: new Date() })
    } finally {
      loading.value = false
    }
  }

  function clearMessages() {
    messages.value = []
    nextId = 1
  }

  return { messages, loading, sendMessage, clearMessages }
})
