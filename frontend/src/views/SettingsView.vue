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

    <div class="settings-card">
      <h2>Appearance</h2>
      <div class="theme-toggle">
        <span class="theme-toggle-label">Dark Mode</span>
        <button
          class="toggle-switch"
          :class="{ active: authStore.darkMode }"
          @click="authStore.toggleDarkMode()"
          type="button"
        >
          <span class="toggle-knob"></span>
        </button>
      </div>
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
      dark_mode: authStore.darkMode,
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
      dark_mode: authStore.darkMode,
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
  color: var(--color-text-primary);
  margin: 0 0 24px;
}

.settings-card {
  background: var(--color-bg-card);
  border-radius: 12px;
  padding: 28px;
  box-shadow: var(--color-shadow);
  margin-bottom: 20px;
}

.settings-card h2 {
  margin: 0 0 24px;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 9px 14px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.875rem;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.15s, box-shadow 0.15s;
  background: var(--color-bg-input);
  color: var(--color-text-primary);
}

.form-group input:focus,
.form-group select:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-ring);
}

.input-disabled {
  background: var(--color-input-disabled-bg);
  color: var(--color-input-disabled-text);
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
  background: var(--color-accent);
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-accent-hover);
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 0;
}

.theme-toggle-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
}

.toggle-switch {
  position: relative;
  width: 48px;
  height: 26px;
  background: var(--color-border);
  border-radius: 9999px;
  cursor: pointer;
  transition: background 0.2s;
  border: none;
  padding: 0;
}

.toggle-switch.active {
  background: var(--color-accent);
}

.toggle-knob {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  transition: transform 0.2s;
}

.toggle-switch.active .toggle-knob {
  transform: translateX(22px);
}
</style>
