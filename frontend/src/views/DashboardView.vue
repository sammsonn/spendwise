<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import { useCategoryStore } from '@/stores/categories'
import ChartPie from '@/components/ChartPie.vue'
import ChartBar from '@/components/ChartBar.vue'
import ChartLine from '@/components/ChartLine.vue'

import { useGoalStore } from '@/stores/goals'

const router = useRouter()
const authStore = useAuthStore()
const categoryStore = useCategoryStore()
const goalStore = useGoalStore()

/* ---- Month selector ---- */
const now = new Date()
const selectedMonth = ref(now.getMonth() + 1)
const selectedYear = ref(now.getFullYear())

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

/* ---- Summary ---- */
const income = ref(0)
const expenses = ref(0)
const balance = ref(0)
const loadingSummary = ref(false)

async function fetchSummary() {
  loadingSummary.value = true
  try {
    const { data } = await api.get('/stats/summary/', {
      params: { month: selectedMonth.value, year: selectedYear.value },
    })
    income.value = Number(data.income)
    expenses.value = Number(data.expenses)
    balance.value = Number(data.balance)
  } catch {
    income.value = 0
    expenses.value = 0
    balance.value = 0
  } finally {
    loadingSummary.value = false
  }
}

/* ---- Category breakdown (pie) ---- */
const categoryLabels = ref<string[]>([])
const categoryData = ref<number[]>([])
const categoryColors = ref<string[]>([])

async function fetchByCategory() {
  try {
    const { data } = await api.get('/stats/by-category/', {
      params: { month: selectedMonth.value, year: selectedYear.value, type: 'expense' },
    })
    categoryLabels.value = data.map((c: any) => c.category)
    categoryData.value = data.map((c: any) => Number(c.total))
    categoryColors.value = data.map((c: any) => c.color || '#6366f1')
  } catch {
    categoryLabels.value = []
    categoryData.value = []
    categoryColors.value = []
  }
}

/* ---- Monthly evolution (bar) -- last 6 months ---- */
const barLabels = ref<string[]>([])
const barIncome = ref<number[]>([])
const barExpenses = ref<number[]>([])

async function fetchMonthlyEvolution() {
  const months: { month: number; year: number; label: string }[] = []
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

  for (let i = 5; i >= 0; i--) {
    let m = selectedMonth.value - i
    let y = selectedYear.value
    while (m <= 0) {
      m += 12
      y -= 1
    }
    months.push({ month: m, year: y, label: `${monthNames[m - 1]} ${y}` })
  }

  try {
    const results = await Promise.all(
      months.map((entry) =>
        api.get('/stats/summary/', { params: { month: entry.month, year: entry.year } }),
      ),
    )
    barLabels.value = months.map((e) => e.label)
    barIncome.value = results.map((r) => Number(r.data.income))
    barExpenses.value = results.map((r) => Number(r.data.expenses))
  } catch {
    barLabels.value = []
    barIncome.value = []
    barExpenses.value = []
  }
}

/* ---- Recent transactions ---- */
const recentTransactions = ref<any[]>([])

async function fetchRecentTransactions() {
  try {
    const lastDay = new Date(selectedYear.value, selectedMonth.value, 0).getDate()
    const dateFrom = `${selectedYear.value}-${String(selectedMonth.value).padStart(2, '0')}-01`
    const dateTo = `${selectedYear.value}-${String(selectedMonth.value).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`
    const { data } = await api.get('/transactions/', {
      params: { date_from: dateFrom, date_to: dateTo, page: 1 },
    })
    recentTransactions.value = (data.results || []).slice(0, 5)
  } catch {
    recentTransactions.value = []
  }
}

/* ---- Fetch everything ---- */
async function fetchAll() {
  await Promise.all([fetchSummary(), fetchByCategoryWithIds(), fetchMonthlyEvolution(), fetchRecentTransactions(), fetchBalanceTrend()])
}

onMounted(() => {
  categoryStore.fetchCategories()
  goalStore.fetchGoals()
  fetchAll()
})

/* ---- Balance trend (line) ---- */
const trendLabels = ref<string[]>([])
const trendData = ref<number[]>([])

async function fetchBalanceTrend() {
  try {
    const { data } = await api.get('/stats/balance-trend/', {
      params: { month: selectedMonth.value, year: selectedYear.value },
    })
    trendLabels.value = data.map((d: any) => d.label)
    trendData.value = data.map((d: any) => d.balance)
  } catch {
    trendLabels.value = []
    trendData.value = []
  }
}

/* ---- Pie click handler ---- */
const categoryIds = ref<number[]>([])

async function fetchByCategoryWithIds() {
  try {
    const { data } = await api.get('/stats/by-category/', {
      params: { month: selectedMonth.value, year: selectedYear.value, type: 'expense' },
    })
    categoryLabels.value = data.map((c: any) => c.category)
    categoryData.value = data.map((c: any) => Number(c.total))
    categoryColors.value = data.map((c: any) => c.color || '#6366f1')
    categoryIds.value = data.map((c: any) => {
      const found = categoryStore.categories.find((cat) => cat.name === c.category)
      return found?.id || 0
    })
  } catch {
    categoryLabels.value = []
    categoryData.value = []
    categoryColors.value = []
    categoryIds.value = []
  }
}

function handlePieClick(index: number) {
  const catId = categoryIds.value[index]
  if (catId) {
    router.push({ path: '/transactions', query: { category: String(catId) } })
  }
}

/* ---- Formatting ---- */
function formatCurrency(value: number): string {
  return value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const topGoals = computed(() => goalStore.goals.slice(0, 3))
</script>

<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1 class="page-title">Dashboard</h1>
      <div class="month-selector">
        <select v-model="selectedMonth" @change="fetchAll">
          <option v-for="m in months" :key="m.value" :value="m.value">{{ m.label }}</option>
        </select>
        <select v-model="selectedYear" @change="fetchAll">
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
    </div>

    <!-- Summary cards -->
    <div class="summary-cards">
      <div class="card card--income">
        <span class="card-label">Income</span>
        <span class="card-amount income-amount">{{ formatCurrency(income) }} {{ authStore.currencySymbol }}</span>
      </div>
      <div class="card card--expenses">
        <span class="card-label">Expenses</span>
        <span class="card-amount expenses-amount">{{ formatCurrency(expenses) }} {{ authStore.currencySymbol }}</span>
      </div>
      <div class="card card--balance">
        <span class="card-label">Balance</span>
        <span class="card-amount balance-amount">{{ formatCurrency(balance) }} {{ authStore.currencySymbol }}</span>
      </div>
    </div>

    <!-- Charts -->
    <div class="charts-row">
      <div class="chart-card">
        <h2 class="chart-title">Expenses by Category</h2>
        <ChartPie :labels="categoryLabels" :data="categoryData" :colors="categoryColors" @slice-click="handlePieClick" />
      </div>
      <div class="chart-card">
        <h2 class="chart-title">Monthly Overview</h2>
        <ChartBar :labels="barLabels" :income-data="barIncome" :expense-data="barExpenses" />
      </div>
    </div>

    <!-- Balance Trend -->
    <div class="chart-card" style="margin-bottom: 20px;">
      <h2 class="chart-title">Balance Trend</h2>
      <ChartLine :labels="trendLabels" :data="trendData" label="Cumulative Balance" />
    </div>

    <!-- Goals Widget -->
    <div v-if="topGoals.length" class="recent-card" style="margin-bottom: 20px;">
      <div class="recent-header">
        <h2 class="chart-title">Savings Goals</h2>
        <RouterLink to="/goals" class="view-all-link">View all</RouterLink>
      </div>
      <div class="goals-widget">
        <div v-for="goal in topGoals" :key="goal.id" class="goal-widget-item">
          <div class="goal-widget-header">
            <span class="goal-widget-name">{{ goal.name }}</span>
            <span class="goal-widget-pct" :class="goal.percentage >= 100 ? 'text-complete' : ''">{{ goal.percentage.toFixed(0) }}%</span>
          </div>
          <div class="goal-widget-bar">
            <div class="goal-widget-fill" :class="goal.percentage >= 100 ? 'fill-complete' : ''" :style="{ width: Math.min(goal.percentage, 100) + '%' }"></div>
          </div>
          <div class="goal-widget-amounts">
            {{ formatCurrency(Number(goal.current_amount)) }} / {{ formatCurrency(Number(goal.target_amount)) }} {{ authStore.currencySymbol }}
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Transactions -->
    <div class="recent-card">
      <div class="recent-header">
        <h2 class="chart-title">Recent Transactions</h2>
        <RouterLink to="/transactions" class="view-all-link">View all</RouterLink>
      </div>
      <table v-if="recentTransactions.length" class="recent-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Category</th>
            <th>Amount</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tx in recentTransactions" :key="tx.id">
            <td>{{ tx.date }}</td>
            <td>{{ tx.description || '---' }}</td>
            <td>
              <span class="category-cell">
                <span class="color-dot" :style="{ backgroundColor: tx.category_color }"></span>
                {{ tx.category_name || '---' }}
              </span>
            </td>
            <td class="amount" :class="tx.category_type === 'income' ? 'amount-income' : 'amount-expense'">
              {{ tx.category_type === 'income' ? '+' : '-' }}{{ tx.amount }} {{ authStore.currencySymbol }}
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty-state">No transactions this month.</p>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}

.page-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.month-selector {
  display: flex;
  gap: 8px;
}

.month-selector select {
  padding: 8px 14px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 0.95rem;
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.month-selector select:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-ring);
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.card {
  background: var(--color-bg-card);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--color-shadow);
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-left: 4px solid transparent;
}

.card--income {
  border-left-color: var(--color-income);
}

.card--expenses {
  border-left-color: var(--color-expense);
}

.card--balance {
  border-left-color: var(--color-accent);
}

.card-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-muted);
}

.card-amount {
  font-size: 1.5rem;
  font-weight: 700;
}

.income-amount {
  color: var(--color-income);
}

.expenses-amount {
  color: var(--color-expense);
}

.balance-amount {
  color: var(--color-accent);
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card {
  background: var(--color-bg-card);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--color-shadow);
}

.chart-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 16px;
}

.recent-card {
  background: var(--color-bg-card);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--color-shadow);
}

.recent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.recent-header .chart-title {
  margin-bottom: 0;
}

.view-all-link {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-accent);
  text-decoration: none;
}

.view-all-link:hover {
  text-decoration: underline;
}

.recent-table {
  width: 100%;
  border-collapse: collapse;
}

.recent-table th {
  text-align: left;
  padding: 8px 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  border-bottom: 1px solid var(--color-border-light);
}

.recent-table td {
  padding: 10px 12px;
  font-size: 0.875rem;
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-border-light);
}

.category-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.color-dot {
  width: 8px;
  height: 8px;
  border-radius: 4px;
  flex-shrink: 0;
}

.amount {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.amount-income {
  color: var(--color-income);
}

.amount-expense {
  color: var(--color-expense);
}

.empty-state {
  text-align: center;
  padding: 24px 16px;
  color: var(--color-text-placeholder);
  font-size: 0.875rem;
}

.goals-widget {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.goal-widget-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.goal-widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.goal-widget-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.goal-widget-pct {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-accent);
}

.goal-widget-pct.text-complete {
  color: var(--color-income);
}

.goal-widget-bar {
  width: 100%;
  height: 6px;
  background: var(--color-border-light);
  border-radius: 9999px;
  overflow: hidden;
}

.goal-widget-fill {
  height: 100%;
  border-radius: 9999px;
  background: var(--color-accent);
  transition: width 0.3s ease;
}

.goal-widget-fill.fill-complete {
  background: var(--color-income);
}

.goal-widget-amounts {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-variant-numeric: tabular-nums;
}

@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}
</style>
