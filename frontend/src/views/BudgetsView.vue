<template>
  <div class="budgets-page">
    <!-- Header -->
    <div class="page-header">
      <h1>Budgets</h1>
      <div class="header-controls">
        <div class="month-selector">
          <select v-model="selectedMonth" @change="fetchBudgetsForPeriod">
            <option v-for="m in months" :key="m.value" :value="m.value">{{ m.label }}</option>
          </select>
          <select v-model="selectedYear" @change="fetchBudgetsForPeriod">
            <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
        <button class="btn btn-primary" @click="openAddModal">Add Budget</button>
      </div>
    </div>

    <!-- Grid -->
    <div v-if="budgetStore.budgets.length" class="budget-grid">
      <div v-for="budget in budgetStore.budgets" :key="budget.id" class="budget-card">
        <div class="budget-header">
          <div class="budget-category">
            <span class="color-dot" :style="{ backgroundColor: budget.category_color }"></span>
            <h3>{{ budget.category_name }}</h3>
          </div>
        </div>

        <div class="budget-amounts">
          <span class="spent">{{ formatNumber(budget.spent) }} {{ authStore.currencySymbol }}</span>
          <span class="separator">/</span>
          <span class="total">{{ budget.amount }} {{ authStore.currencySymbol }}</span>
        </div>

        <div class="progress-bar-container">
          <div
            class="progress-bar"
            :class="percentage(budget) >= 100 ? 'progress-over' : percentage(budget) >= 80 ? 'progress-warning' : 'progress-ok'"
            :style="{ width: Math.min(percentage(budget), 100) + '%' }"
          ></div>
        </div>
        <span class="percentage-label" :class="percentage(budget) >= 100 ? 'text-over' : percentage(budget) >= 80 ? 'text-warning' : 'text-ok'">
          {{ percentage(budget).toFixed(0) }}%
        </span>
        <span v-if="percentage(budget) >= 100" class="budget-alert alert-over">Over budget!</span>
        <span v-else-if="percentage(budget) >= 80" class="budget-alert alert-warning">Approaching limit</span>

        <div class="card-actions">
          <button class="btn-action" @click="openEditModal(budget)">Edit</button>
          <button class="btn-action btn-action-danger" @click="confirmDelete(budget)">Delete</button>
        </div>
      </div>
    </div>
    <p v-else class="empty-state">No budgets set for this month.</p>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h2>{{ editingBudget ? 'Edit Budget' : 'Add Budget' }}</h2>
        <form @submit.prevent="saveBudget">
          <div class="form-group">
            <label>Category (expense only)</label>
            <select v-model="form.category" required>
              <option v-for="cat in expenseCategories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Amount</label>
            <input v-model="form.amount" type="number" step="0.01" required />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button type="submit" class="btn btn-primary">{{ editingBudget ? 'Update' : 'Create' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useBudgetStore, type Budget } from '@/stores/budgets'
import { useCategoryStore } from '@/stores/categories'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const toast = useToast()
const budgetStore = useBudgetStore()
const categoryStore = useCategoryStore()
const authStore = useAuthStore()

const now = new Date()
const selectedMonth = ref(now.getMonth() + 1)
const selectedYear = ref(now.getFullYear())

const showModal = ref(false)
const editingBudget = ref<Budget | null>(null)

const form = reactive({
  category: undefined as number | undefined,
  amount: '' as string,
})

const months = [
  { value: 1, label: 'January' },
  { value: 2, label: 'February' },
  { value: 3, label: 'March' },
  { value: 4, label: 'April' },
  { value: 5, label: 'May' },
  { value: 6, label: 'June' },
  { value: 7, label: 'July' },
  { value: 8, label: 'August' },
  { value: 9, label: 'September' },
  { value: 10, label: 'October' },
  { value: 11, label: 'November' },
  { value: 12, label: 'December' },
]

const years = computed(() => {
  const curr = new Date().getFullYear()
  return Array.from({ length: 5 }, (_, i) => curr - 2 + i)
})

const expenseCategories = computed(() =>
  categoryStore.categories.filter((c) => c.type === 'expense'),
)

onMounted(async () => {
  await Promise.all([
    categoryStore.fetchCategories(),
  ])
  fetchBudgetsForPeriod()
})

async function fetchBudgetsForPeriod() {
  await budgetStore.fetchBudgets(selectedMonth.value, selectedYear.value)
  checkBudgetAlerts()
}

function checkBudgetAlerts() {
  for (const budget of budgetStore.budgets) {
    const pct = percentage(budget)
    if (pct >= 100) {
      toast.error(`"${budget.category_name}" is over budget! (${pct.toFixed(0)}%)`)
    } else if (pct >= 80) {
      toast.warning(`"${budget.category_name}" is approaching its limit (${pct.toFixed(0)}%)`)
    }
  }
}

function percentage(budget: Budget): number {
  const amt = parseFloat(String(budget.amount))
  if (!amt) return 0
  return (budget.spent / amt) * 100
}

function formatNumber(val: number): string {
  return Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function resetForm() {
  form.category = expenseCategories.value[0]?.id
  form.amount = ''
}

function openAddModal() {
  editingBudget.value = null
  resetForm()
  showModal.value = true
}

function openEditModal(budget: Budget) {
  editingBudget.value = budget
  form.category = budget.category
  form.amount = budget.amount
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingBudget.value = null
}

async function saveBudget() {
  try {
    const payload = {
      category: form.category,
      amount: form.amount,
      month: selectedMonth.value,
      year: selectedYear.value,
    }
    if (editingBudget.value) {
      await budgetStore.updateBudget(editingBudget.value.id, payload)
      toast.success('Budget updated successfully')
    } else {
      await budgetStore.createBudget(payload)
      toast.success('Budget created successfully')
    }
    closeModal()
    fetchBudgetsForPeriod()
  } catch (err: any) {
    toast.error(err?.response?.data?.detail || 'Failed to save budget')
  }
}

async function confirmDelete(budget: Budget) {
  if (!window.confirm(`Delete budget for "${budget.category_name}"?`)) return
  try {
    await budgetStore.deleteBudget(budget.id)
    toast.success('Budget deleted')
    fetchBudgetsForPeriod()
  } catch {
    toast.error('Failed to delete budget')
  }
}
</script>

<style scoped>
.budgets-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 28px 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.page-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.month-selector {
  display: flex;
  gap: 8px;
}

.month-selector select {
  padding: 9px 14px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  background: var(--color-bg-input);
  color: var(--color-text-primary);
}

.month-selector select:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-ring);
}

.budget-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.budget-card {
  background: var(--color-bg-card);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--color-shadow);
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: box-shadow 0.15s;
}

.budget-card:hover {
  box-shadow: var(--color-shadow-hover);
}

.budget-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.budget-category {
  display: flex;
  align-items: center;
  gap: 8px;
}

.budget-category h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.color-dot {
  width: 10px;
  height: 10px;
  border-radius: 6px;
  flex-shrink: 0;
}

.budget-amounts {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  font-variant-numeric: tabular-nums;
}

.spent {
  color: var(--color-text-secondary);
}

.separator {
  margin: 0 4px;
  color: var(--color-text-placeholder);
}

.total {
  color: var(--color-text-placeholder);
  font-weight: 500;
}

.progress-bar-container {
  width: 100%;
  height: 8px;
  background: var(--color-border-light);
  border-radius: 9999px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.3s ease;
}

.progress-ok {
  background: var(--color-income);
}

.progress-warning {
  background: var(--color-warning);
}

.progress-over {
  background: var(--color-expense);
}

.percentage-label {
  font-size: 0.8125rem;
  font-weight: 600;
}

.text-ok {
  color: var(--color-income);
}

.text-warning {
  color: var(--color-warning);
}

.text-over {
  color: var(--color-expense);
}

.budget-alert {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 9999px;
  display: inline-block;
}

.alert-warning {
  background: var(--color-badge-warning-bg);
  color: var(--color-warning);
}

.alert-over {
  background: var(--color-badge-expense-bg);
  color: var(--color-expense);
}

.card-actions {
  display: flex;
  gap: 6px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border-light);
  margin-top: auto;
}

.btn-action {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  transition: background 0.15s, border-color 0.15s;
}

.btn-action:hover {
  background: var(--color-bg-secondary);
}

.btn-action-danger:hover {
  background: var(--color-btn-danger-hover-bg);
  border-color: var(--color-btn-danger-hover-border);
  color: var(--color-expense);
}

.empty-state {
  text-align: center;
  padding: 48px 16px;
  color: var(--color-text-placeholder);
  font-size: 0.875rem;
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

.btn-secondary {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-border);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--color-modal-overlay);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 16px;
}

.modal {
  background: var(--color-bg-card);
  border-radius: 16px;
  padding: 28px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--color-shadow-lg);
}

.modal h2 {
  margin: 0 0 24px;
  font-size: 1.25rem;
  font-weight: 700;
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

.form-group input[type='number'],
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

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 24px;
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-controls {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
