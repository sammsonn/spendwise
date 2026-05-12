<template>
  <div class="transactions-page">
    <!-- Header -->
    <div class="page-header">
      <h1>Transactions</h1>
      <button class="btn btn-primary" @click="openAddModal">Add Transaction</button>
    </div>

    <!-- Date Presets + Import/Export -->
    <div class="date-presets">
      <div class="preset-buttons">
        <button class="btn btn-preset" :class="{ active: activePreset === 'week' }" @click="setPreset('week')">This Week</button>
        <button class="btn btn-preset" :class="{ active: activePreset === '7days' }" @click="setPreset('7days')">Last 7 Days</button>
        <button class="btn btn-preset" :class="{ active: activePreset === 'month' }" @click="setPreset('month')">This Month</button>
        <button class="btn btn-preset" :class="{ active: activePreset === '30days' }" @click="setPreset('30days')">Last 30 Days</button>
        <button class="btn btn-preset" :class="{ active: activePreset === 'year' }" @click="setPreset('year')">This Year</button>
        <button v-if="activePreset" class="btn btn-preset" @click="clearPreset">Clear</button>
      </div>
      <div class="toolbar-buttons">
        <button class="btn btn-secondary" @click="triggerImportCSV">Import CSV</button>
        <input
          ref="csvFileInput"
          type="file"
          accept=".csv"
          style="display: none"
          @change="handleImportCSV"
        />
        <button class="btn btn-secondary" @click="transactionStore.exportCSV()">Export CSV</button>
        <button class="btn btn-secondary" @click="transactionStore.exportPDF()">Export PDF</button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filter-bar">
      <div class="filter-group">
        <label>From</label>
        <input v-model="filters.date_from" type="date" @change="activePreset = ''; applyFilters()" />
      </div>
      <div class="filter-group">
        <label>To</label>
        <input v-model="filters.date_to" type="date" @change="activePreset = ''; applyFilters()" />
      </div>
      <div class="filter-group">
        <label>Category</label>
        <select v-model="filters.category" @change="applyFilters">
          <option :value="undefined">All</option>
          <option v-for="cat in categoryStore.categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <label>Type</label>
        <select v-model="filters.type" @change="applyFilters">
          <option value="">All</option>
          <option value="income">Income</option>
          <option value="expense">Expense</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Min Amount</label>
        <input v-model="filters.amount_min" type="number" step="0.01" placeholder="0.00" @change="applyFilters" />
      </div>
      <div class="filter-group">
        <label>Max Amount</label>
        <input v-model="filters.amount_max" type="number" step="0.01" placeholder="0.00" @change="applyFilters" />
      </div>
      <div class="filter-group">
        <label>Search</label>
        <input v-model="filters.search" type="text" placeholder="Search..." @input="applyFilters" />
      </div>
    </div>

    <!-- Table -->
    <div class="table-container">
      <table v-if="transactionStore.transactions.length">
        <thead>
          <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Category</th>
            <th>Type</th>
            <th>Amount</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tx in transactionStore.transactions" :key="tx.id">
            <td>{{ tx.date }}</td>
            <td>{{ tx.description }}</td>
            <td>
              <span class="category-cell">
                <span class="color-dot" :style="{ backgroundColor: tx.category_color }"></span>
                {{ tx.category_name || '---' }}
              </span>
            </td>
            <td>
              <span class="badge" :class="tx.category_type === 'income' ? 'badge-income' : 'badge-expense'">
                {{ tx.category_type || '---' }}
              </span>
              <span v-if="tx.is_recurring" class="badge badge-recurring">
                {{ tx.recurring_interval }}
              </span>
            </td>
            <td class="amount">{{ tx.amount }} {{ authStore.currencySymbol }}</td>
            <td class="actions">
              <button class="btn-action" @click="openEditModal(tx)">Edit</button>
              <button class="btn-action btn-action-danger" @click="confirmDelete(tx)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty-state">No transactions found.</p>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        class="btn btn-secondary"
        :disabled="transactionStore.currentPage <= 1"
        @click="changePage(transactionStore.currentPage - 1)"
      >
        Previous
      </button>
      <span class="page-info">Page {{ transactionStore.currentPage }} of {{ totalPages }}</span>
      <button
        class="btn btn-secondary"
        :disabled="transactionStore.currentPage >= totalPages"
        @click="changePage(transactionStore.currentPage + 1)"
      >
        Next
      </button>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h2>{{ editingTransaction ? 'Edit Transaction' : 'Add Transaction' }}</h2>
        <form @submit.prevent="saveTransaction">
          <div class="form-group">
            <label>Amount</label>
            <input v-model="form.amount" type="number" step="0.01" required />
          </div>
          <div class="form-group">
            <label>Category</label>
            <select v-model="form.category">
              <option :value="null">None</option>
              <option v-for="cat in categoryStore.categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Date</label>
            <input v-model="form.date" type="date" required />
          </div>
          <div class="form-group">
            <label>Description</label>
            <input v-model="form.description" type="text" />
          </div>
          <div class="form-group checkbox-group">
            <label>
              <input v-model="form.is_recurring" type="checkbox" />
              Recurring
            </label>
          </div>
          <div v-if="form.is_recurring" class="form-group">
            <label>Interval</label>
            <select v-model="form.recurring_interval">
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button type="submit" class="btn btn-primary">{{ editingTransaction ? 'Update' : 'Create' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { useTransactionStore, type Transaction } from '@/stores/transactions'
import { useCategoryStore } from '@/stores/categories'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const toast = useToast()
const route = useRoute()
const transactionStore = useTransactionStore()
const categoryStore = useCategoryStore()
const authStore = useAuthStore()

const PAGE_SIZE = 10

const filters = reactive<{
  date_from?: string
  date_to?: string
  category?: number
  type?: string
  search?: string
  amount_min?: string
  amount_max?: string
}>({})

const activePreset = ref('')

const showModal = ref(false)
const editingTransaction = ref<Transaction | null>(null)
const csvFileInput = ref<HTMLInputElement | null>(null)

const form = reactive({
  amount: '' as string,
  category: undefined as number | undefined,
  date: '',
  description: '',
  is_recurring: false,
  recurring_interval: 'monthly',
})

const totalPages = computed(() => Math.max(1, Math.ceil(transactionStore.totalCount / PAGE_SIZE)))

onMounted(async () => {
  if (route.query.category) {
    filters.category = Number(route.query.category)
  }
  await Promise.all([
    transactionStore.fetchTransactions(filters.category ? { category: filters.category } : undefined),
    categoryStore.fetchCategories(),
  ])
})

function applyFilters() {
  transactionStore.fetchTransactions({ ...filters, page: 1 })
}

function formatDate(d: Date): string {
  return d.toISOString().slice(0, 10)
}

function setPreset(preset: string) {
  activePreset.value = preset
  const today = new Date()
  switch (preset) {
    case 'week': {
      const day = today.getDay()
      const monday = new Date(today)
      monday.setDate(today.getDate() - ((day + 6) % 7))
      filters.date_from = formatDate(monday)
      filters.date_to = formatDate(today)
      break
    }
    case '7days': {
      const d = new Date(today)
      d.setDate(today.getDate() - 6)
      filters.date_from = formatDate(d)
      filters.date_to = formatDate(today)
      break
    }
    case 'month': {
      filters.date_from = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-01`
      filters.date_to = formatDate(today)
      break
    }
    case '30days': {
      const d = new Date(today)
      d.setDate(today.getDate() - 29)
      filters.date_from = formatDate(d)
      filters.date_to = formatDate(today)
      break
    }
    case 'year': {
      filters.date_from = `${today.getFullYear()}-01-01`
      filters.date_to = formatDate(today)
      break
    }
  }
  applyFilters()
}

function clearPreset() {
  activePreset.value = ''
  filters.date_from = undefined
  filters.date_to = undefined
  applyFilters()
}

function changePage(page: number) {
  transactionStore.fetchTransactions({ ...filters, page })
}

function resetForm() {
  form.amount = ''
  form.category = undefined
  form.date = new Date().toISOString().slice(0, 10)
  form.description = ''
  form.is_recurring = false
  form.recurring_interval = 'monthly'
}

function openAddModal() {
  editingTransaction.value = null
  resetForm()
  showModal.value = true
}

function openEditModal(tx: Transaction) {
  editingTransaction.value = tx
  form.amount = tx.amount
  form.category = tx.category ?? undefined
  form.date = tx.date
  form.description = tx.description
  form.is_recurring = tx.is_recurring
  form.recurring_interval = tx.recurring_interval || 'monthly'
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingTransaction.value = null
}

async function saveTransaction() {
  try {
    const payload = {
      amount: form.amount,
      category: form.category,
      date: form.date,
      description: form.description,
      is_recurring: form.is_recurring,
      recurring_interval: form.is_recurring ? form.recurring_interval : '',
    }
    if (editingTransaction.value) {
      await transactionStore.updateTransaction(editingTransaction.value.id, payload)
      toast.success('Transaction updated successfully')
    } else {
      await transactionStore.createTransaction(payload)
      toast.success('Transaction created successfully')
    }
    closeModal()
  } catch (err: any) {
    toast.error(err?.response?.data?.detail || 'Failed to save transaction')
  }
}

async function confirmDelete(tx: Transaction) {
  if (!window.confirm(`Delete transaction "${tx.description || tx.amount}"?`)) return
  try {
    await transactionStore.deleteTransaction(tx.id)
    toast.success('Transaction deleted')
  } catch {
    toast.error('Failed to delete transaction')
  }
}

function triggerImportCSV() {
  csvFileInput.value?.click()
}

async function handleImportCSV(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  try {
    const result = await transactionStore.importCSV(file)
    toast.success(result?.message || 'CSV imported successfully')
  } catch {
    toast.error('Failed to import CSV')
  }
  input.value = ''
}
</script>

<style scoped>
.transactions-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 28px 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.page-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.date-presets {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.preset-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.toolbar-buttons {
  display: flex;
  gap: 8px;
  margin-left: auto;
  flex-wrap: wrap;
}

.btn-preset {
  padding: 6px 14px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}

.btn-preset:hover {
  background: var(--color-bg-secondary);
}

.btn-preset.active {
  background: var(--color-accent);
  color: #fff;
  border-color: var(--color-accent);
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  background: var(--color-bg-card);
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: var(--color-shadow);
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 140px;
}

.filter-group label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.filter-group input,
.filter-group select {
  padding: 9px 14px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  background: var(--color-bg-input);
  color: var(--color-text-primary);
}

.filter-group input:focus,
.filter-group select:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-ring);
}

.table-container {
  background: var(--color-bg-card);
  border-radius: 12px;
  box-shadow: var(--color-shadow);
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  text-align: left;
  padding: 12px 16px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  background: var(--color-bg-secondary);
}

td {
  padding: 12px 16px;
  font-size: 0.875rem;
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-border-light);
}

tbody tr:hover {
  background-color: var(--color-bg-secondary);
}

.category-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-dot {
  width: 10px;
  height: 10px;
  border-radius: 6px;
  display: inline-block;
  flex-shrink: 0;
}

.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.badge-income {
  background: var(--color-badge-income-bg);
  color: var(--color-badge-income-text);
}

.badge-expense {
  background: var(--color-badge-expense-bg);
  color: var(--color-badge-expense-text);
}

.badge-recurring {
  background: var(--color-badge-recurring-bg);
  color: var(--color-badge-recurring-text);
  margin-left: 4px;
}

.amount {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.actions {
  display: flex;
  gap: 4px;
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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
}

.page-info {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
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

.form-group input[type='text'],
.form-group input[type='number'],
.form-group input[type='date'],
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

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-group input[type='checkbox'] {
  accent-color: var(--color-accent);
  width: 16px;
  height: 16px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 24px;
}

@media (max-width: 640px) {
  .filter-bar {
    flex-direction: column;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
