<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const username = ref('')
const email = ref('')
const firstName = ref('')
const lastName = ref('')
const password = ref('')
const passwordConfirm = ref('')
const loading = ref(false)

async function handleRegister() {
  if (password.value !== passwordConfirm.value) {
    toast.error('Passwords do not match.')
    return
  }

  loading.value = true
  try {
    await authStore.register({
      username: username.value,
      email: email.value,
      first_name: firstName.value,
      last_name: lastName.value,
      password: password.value,
      password_confirm: passwordConfirm.value,
    })
    toast.success('Account created successfully!')
    router.push('/')
  } catch (err: any) {
    const data = err?.response?.data
    if (data && typeof data === 'object') {
      const messages = Object.entries(data)
        .map(([field, errors]) => {
          const msg = Array.isArray(errors) ? errors.join(' ') : errors
          return `${field}: ${msg}`
        })
        .join('\n')
      toast.error(messages || 'Registration failed.')
    } else {
      toast.error('Registration failed. Please try again.')
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-wrapper">
    <div class="register-card">
      <h1 class="app-title">SpendWise</h1>
      <p class="app-subtitle">Create your account</p>

      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="Choose a username"
            required
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="you@example.com"
            required
            autocomplete="email"
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="first_name">First Name</label>
            <input
              id="first_name"
              v-model="firstName"
              type="text"
              placeholder="First name"
              required
            />
          </div>

          <div class="form-group">
            <label for="last_name">Last Name</label>
            <input
              id="last_name"
              v-model="lastName"
              type="text"
              placeholder="Last name"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Create a password"
            required
            autocomplete="new-password"
          />
        </div>

        <div class="form-group">
          <label for="password_confirm">Confirm Password</label>
          <input
            id="password_confirm"
            v-model="passwordConfirm"
            type="password"
            placeholder="Repeat your password"
            required
            autocomplete="new-password"
          />
        </div>

        <button type="submit" class="btn-submit" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          {{ loading ? 'Creating account...' : 'Create account' }}
        </button>
      </form>

      <p class="form-footer">
        Already have an account?
        <router-link to="/login" class="form-link">Sign in</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.register-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg-primary);
  padding: 1rem;
}

.register-card {
  width: 100%;
  max-width: 400px;
  background-color: var(--color-bg-card);
  border-radius: 16px;
  box-shadow: var(--color-shadow);
  padding: 32px;
}

.app-title {
  text-align: center;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px;
}

.app-subtitle {
  text-align: center;
  color: var(--color-text-muted);
  margin: 0 0 2rem;
  font-size: 0.9rem;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-row .form-group {
  flex: 1;
  min-width: 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-group label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.form-group input {
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.95rem;
  color: var(--color-text-primary);
  background: var(--color-bg-input);
  transition: border-color 0.2s, box-shadow 0.2s;
  outline: none;
}

.form-group input:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-ring);
}

.btn-submit {
  margin-top: 0.5rem;
  height: 42px;
  background-color: var(--color-accent);
  color: #ffffff;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: background-color 0.2s;
}

.btn-submit:hover:not(:disabled) {
  background-color: var(--color-accent-hover);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.form-footer {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.form-link {
  color: var(--color-accent);
  font-weight: 600;
  text-decoration: none;
}

.form-link:hover {
  text-decoration: underline;
}

@media (max-width: 480px) {
  .form-row {
    flex-direction: column;
    gap: 1.25rem;
  }

  .register-card {
    padding: 2rem 1.25rem;
  }
}
</style>
