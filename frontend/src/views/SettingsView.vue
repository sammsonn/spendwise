<template>
  <div class="settings-page">
    <h1>Settings</h1>

    <div class="settings-card">
      <h2>Profile Information</h2>
      <form @submit.prevent="saveProfile">
        <div class="form-group">
          <label>Username</label>
          <input :value="authStore.user?.username" type="text" disabled class="input-disabled" />
        </div>
        <div class="form-group">
          <label>First Name</label>
          <input v-model="form.first_name" type="text" />
        </div>
        <div class="form-group">
          <label>Last Name</label>
          <input v-model="form.last_name" type="text" />
        </div>
        <div class="form-group">
          <label>Email</label>
          <input v-model="form.email" type="email" />
        </div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </form>
    </div>

    <div class="settings-card">
      <h2>Preferences</h2>
      <form @submit.prevent="saveCurrency">
        <div class="form-group">
          <label>Preferred Currency</label>
          <select v-model="selectedCurrency">
            <option v-for="cur in currencyStore.currencies" :key="cur.id" :value="cur.id">
              {{ cur.code }} ({{ cur.symbol }})
            </option>
          </select>
        </div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="savingCurrency">
            {{ savingCurrency ? 'Saving...' : 'Save Currency' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCurrencyStore } from '@/stores/currencies'
import api from '@/api'
import { useToast } from 'vue-toastification'

const toast = useToast()
const authStore = useAuthStore()
const currencyStore = useCurrencyStore()
const saving = ref(false)
const savingCurrency = ref(false)
const selectedCurrency = ref<number | undefined>(undefined)

const form = reactive({
  first_name: '',
  last_name: '',
  email: '',
})

onMounted(async () => {
  await Promise.all([
    authStore.fetchProfile(),
    currencyStore.fetchCurrencies(),
  ])
  if (authStore.user) {
    form.first_name = authStore.user.first_name || ''
    form.last_name = authStore.user.last_name || ''
    form.email = authStore.user.email || ''
    selectedCurrency.value = authStore.user.preferred_currency
  }
})

async function saveProfile() {
  saving.value = true
  try {
    await api.put('/auth/profile/', {
      first_name: form.first_name,
      last_name: form.last_name,
      email: form.email,
      preferred_currency: selectedCurrency.value,
    })
    await authStore.fetchProfile()
    toast.success('Profile updated successfully')
  } catch (err: any) {
    toast.error(err?.response?.data?.detail || 'Failed to update profile')
  } finally {
    saving.value = false
  }
}

async function saveCurrency() {
  savingCurrency.value = true
  try {
    await api.put('/auth/profile/', {
      first_name: form.first_name,
      last_name: form.last_name,
      email: form.email,
      preferred_currency: selectedCurrency.value,
    })
    await authStore.fetchProfile()
    toast.success('Currency preference updated')
  } catch (err: any) {
    toast.error(err?.response?.data?.detail || 'Failed to update currency')
  } finally {
    savingCurrency.value = false
  }
}
</script>

<style scoped>
.settings-page {
  max-width: 560px;
  margin: 0 auto;
  padding: 28px 20px;
}

.settings-page h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 24px;
}

.settings-card {
  background: #fff;
  border-radius: 12px;
  padding: 28px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04);
  margin-bottom: 20px;
}

.settings-card h2 {
  margin: 0 0 24px;
  font-size: 1.125rem;
  font-weight: 600;
  color: #0f172a;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #475569;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 9px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.15s, box-shadow 0.15s;
  background: #fff;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #0d9488;
  box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.1);
}

.input-disabled {
  background: #f8fafc;
  color: #94a3b8;
  cursor: not-allowed;
}

.form-actions {
  margin-top: 24px;
}

.btn {
  padding: 9px 18px;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, opacity 0.15s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #0d9488;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #0f766e;
}
</style>
