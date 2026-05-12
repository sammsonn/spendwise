<template>
  <div class="reports-page">
    <div class="page-header">
      <h1>Monthly Report</h1>
      <div class="month-selector">
        <select v-model="selectedMonth" @change="fetchReport">
          <option v-for="m in months" :key="m.value" :value="m.value">{{ m.label }}</option>
        </select>
        <select v-model="selectedYear" @change="fetchReport">
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
    </div>

    <!-- Comparison Cards -->
    <div class="comparison-cards">
      <div class="comparison-card">
        <span class="comp-label">Income</span>
        <span class="comp-amount income-amount">{{ formatNumber(report.current.income) }} {{ authStore.currencySymbol }}</span>
        <span class="comp-change" :class="report.changes.income >= 0 ? 'change-up' : 'change-down'">
          {{ report.changes.income >= 0 ? '+' : '' }}{{ report.changes.income }}%
        </span>
        <span class="comp-prev">vs {{ formatNumber(report.previous.income) }} prev</span>
      </div>
      <div class="comparison-card">
        <span class="comp-label">Expenses</span>
        <span class="comp-amount expense-amount">{{ formatNumber(report.current.expenses) }} {{ authStore.currencySymbol }}</span>
        <span class="comp-change" :class="report.changes.expenses <= 0 ? 'change-up' : 'change-down'">
          {{ report.changes.expenses >= 0 ? '+' : '' }}{{ report.changes.expenses }}%
        </span>
        <span class="comp-prev">vs {{ formatNumber(report.previous.expenses) }} prev</span>
      </div>
      <div class="comparison-card">
        <span class="comp-label">Balance</span>
        <span class="comp-amount balance-amount">{{ formatNumber(report.current.balance) }} {{ authStore.currencySymbol }}</span>
        <span class="comp-change" :class="report.changes.balance >= 0 ? 'change-up' : 'change-down'">
          {{ report.changes.balance >= 0 ? '+' : '' }}{{ report.changes.balance }}%
        </span>
        <span class="comp-prev">vs {{ formatNumber(report.previous.balance) }} prev</span>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <h2 class="section-title">Top Expense Categories</h2>
        <ChartPie
          :labels="topCatLabels"
          :data="topCatData"
          :colors="topCatColors"
        />
      </div>
      <div class="chart-card">
        <h2 class="section-title">Current vs Previous Month</h2>
        <ChartBar
          :labels="['Income', 'Expenses']"
          :income-data="[report.current.income, report.previous.income]"
          :expense-data="[report.current.expenses, report.previous.expenses]"
        />
      </div>
    </div>

    <!-- Budget Adherence -->
    <div v-if="report.budget_adherence.length" class="budget-table-card">
      <h2 class="section-title">Budget Adherence</h2>
      <table class="budget-table">
        <thead>
          <tr>
            <th>Category</th>
            <th>Budgeted</th>
            <th>Spent</th>
            <th>Usage</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in report.budget_adherence" :key="b.category">
            <td>
              <span class="category-cell">
                <span class="color-dot" :style="{ backgroundColor: b.category_color }"></span>
                {{ b.category }}
              </span>
            </td>
            <td>{{ formatNumber(b.budgeted) }} {{ authStore.currencySymbol }}</td>
            <td>{{ formatNumber(b.spent) }} {{ authStore.currencySymbol }}</td>
            <td>
              <div class="usage-bar-container">
                <div
                  class="usage-bar"
                  :class="b.percentage >= 100 ? 'bar-over' : b.percentage >= 80 ? 'bar-warning' : 'bar-ok'"
                  :style="{ width: Math.min(b.percentage, 100) + '%' }"
                ></div>
              </div>
              <span class="usage-pct" :class="b.percentage >= 100 ? 'pct-over' : b.percentage >= 80 ? 'pct-warning' : 'pct-ok'">
                {{ b.percentage.toFixed(0) }}%
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import ChartPie from '@/components/ChartPie.vue'
import ChartBar from '@/components/ChartBar.vue'

const authStore = useAuthStore()

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

const report = reactive({
  current: { income: 0, expenses: 0, balance: 0 },
  previous: { income: 0, expenses: 0, balance: 0 },
  changes: { income: 0, expenses: 0, balance: 0 },
  top_categories: [] as { id: number; name: string; color: string; total: number }[],
  budget_adherence: [] as { category: string; category_color: string; budgeted: number; spent: number; percentage: number }[],
})

const topCatLabels = computed(() => report.top_categories.map(c => c.name))
const topCatData = computed(() => report.top_categories.map(c => c.total))
const topCatColors = computed(() => report.top_categories.map(c => c.color))

function formatNumber(val: number): string {
  return val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function fetchReport() {
  try {
    const { data } = await api.get('/stats/monthly-report/', {
      params: { month: selectedMonth.value, year: selectedYear.value },
    })
    report.current = data.current
    report.previous = data.previous
    report.changes = data.changes
    report.top_categories = data.top_categories
    report.budget_adherence = data.budget_adherence
  } catch {
    report.current = { income: 0, expenses: 0, balance: 0 }
    report.previous = { income: 0, expenses: 0, balance: 0 }
    report.changes = { income: 0, expenses: 0, balance: 0 }
    report.top_categories = []
    report.budget_adherence = []
  }
}

onMounted(fetchReport)
</script>

<style scoped>
.reports-page {
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

/* Comparison Cards */
.comparison-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.comparison-card {
  background: var(--color-bg-card);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--color-shadow);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.comp-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-muted);
}

.comp-amount {
  font-size: 1.5rem;
  font-weight: 700;
}

.income-amount {
  color: var(--color-income);
}

.expense-amount {
  color: var(--color-expense);
}

.balance-amount {
  color: var(--color-accent);
}

.comp-change {
  font-size: 0.875rem;
  font-weight: 600;
}

.change-up {
  color: var(--color-income);
}

.change-down {
  color: var(--color-expense);
}

.comp-prev {
  font-size: 0.75rem;
  color: var(--color-text-placeholder);
}

/* Charts */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: var(--color-bg-card);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--color-shadow);
}

.section-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 16px;
}

/* Budget Table */
.budget-table-card {
  background: var(--color-bg-card);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--color-shadow);
}

.budget-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
}

.budget-table th {
  text-align: left;
  padding: 8px 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  border-bottom: 1px solid var(--color-border-light);
}

.budget-table td {
  padding: 10px 12px;
  font-size: 0.875rem;
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-border-light);
  font-variant-numeric: tabular-nums;
}

.category-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-dot {
  width: 8px;
  height: 8px;
  border-radius: 4px;
  flex-shrink: 0;
}

.usage-bar-container {
  width: 80px;
  height: 6px;
  background: var(--color-border-light);
  border-radius: 9999px;
  overflow: hidden;
  display: inline-block;
  vertical-align: middle;
  margin-right: 8px;
}

.usage-bar {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.3s ease;
}

.bar-ok { background: var(--color-income); }
.bar-warning { background: var(--color-warning); }
.bar-over { background: var(--color-expense); }

.usage-pct {
  font-size: 0.8125rem;
  font-weight: 600;
}

.pct-ok { color: var(--color-income); }
.pct-warning { color: var(--color-warning); }
.pct-over { color: var(--color-expense); }

@media (max-width: 768px) {
  .comparison-cards {
    grid-template-columns: 1fr;
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
