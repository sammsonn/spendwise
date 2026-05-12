<template>
  <div class="goals-page">
    <div class="page-header">
      <h1>Savings Goals</h1>
      <button class="btn btn-primary" @click="openAddModal">Add Goal</button>
    </div>

    <div v-if="goalStore.goals.length" class="goals-grid">
      <div v-for="goal in goalStore.goals" :key="goal.id" class="goal-card">
        <div class="goal-header">
          <h3>{{ goal.name }}</h3>
          <span v-if="goal.deadline" class="deadline">{{ goal.deadline }}</span>
        </div>

        <div class="goal-amounts">
          <span class="current">{{ formatNumber(Number(goal.current_amount)) }}</span>
          <span class="separator">/</span>
          <span class="target">{{ formatNumber(Number(goal.target_amount)) }} {{ authStore.currencySymbol }}</span>
        </div>

        <div class="progress-bar-container">
          <div
            class="progress-bar"
            :class="goal.percentage >= 100 ? 'progress-complete' : 'progress-active'"
            :style="{ width: Math.min(goal.percentage, 100) + '%' }"
          ></div>
        </div>
        <span class="percentage-label" :class="goal.percentage >= 100 ? 'text-complete' : 'text-active'">
          {{ goal.percentage.toFixed(0) }}%
        </span>
        <span v-if="goal.percentage >= 100" class="goal-badge badge-complete">Goal reached!</span>

        <div class="card-actions">
          <button class="btn-action" @click="openEditModal(goal)">Edit</button>
          <button class="btn-action btn-action-danger" @click="confirmDelete(goal)">Delete</button>
        </div>
      </div>
    </div>
    <p v-else class="empty-state">No savings goals yet. Create one to start tracking!</p>

    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h2>{{ editingGoal ? 'Edit Goal' : 'Add Goal' }}</h2>
        <form @submit.prevent="saveGoal">
          <div class="form-group">
            <label>Name</label>
            <input v-model="form.name" type="text" required />
          </div>
          <div class="form-group">
            <label>Target Amount</label>
            <input v-model="form.target_amount" type="number" step="0.01" required />
          </div>
          <div class="form-group">
            <label>Current Amount</label>
            <input v-model="form.current_amount" type="number" step="0.01" />
          </div>
          <div class="form-group">
            <label>Deadline (optional)</label>
            <input v-model="form.deadline" type="date" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button type="submit" class="btn btn-primary">{{ editingGoal ? 'Update' : 'Create' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useGoalStore, type SavingsGoal } from '@/stores/goals'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const toast = useToast()
const goalStore = useGoalStore()
const authStore = useAuthStore()

const showModal = ref(false)
const editingGoal = ref<SavingsGoal | null>(null)

const form = reactive({
  name: '',
  target_amount: '',
  current_amount: '0',
  deadline: '',
})

onMounted(() => {
  goalStore.fetchGoals()
})

function formatNumber(val: number): string {
  return val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function resetForm() {
  form.name = ''
  form.target_amount = ''
  form.current_amount = '0'
  form.deadline = ''
}

function openAddModal() {
  editingGoal.value = null
  resetForm()
  showModal.value = true
}

function openEditModal(goal: SavingsGoal) {
  editingGoal.value = goal
  form.name = goal.name
  form.target_amount = goal.target_amount
  form.current_amount = goal.current_amount
  form.deadline = goal.deadline || ''
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingGoal.value = null
}

async function saveGoal() {
  try {
    const payload = {
      name: form.name,
      target_amount: form.target_amount,
      current_amount: form.current_amount || '0',
      deadline: form.deadline || null,
    }
    if (editingGoal.value) {
      await goalStore.updateGoal(editingGoal.value.id, payload)
      toast.success('Goal updated successfully')
    } else {
      await goalStore.createGoal(payload)
      toast.success('Goal created successfully')
    }
    closeModal()
  } catch (err: any) {
    toast.error(err?.response?.data?.detail || 'Failed to save goal')
  }
}

async function confirmDelete(goal: SavingsGoal) {
  if (!window.confirm(`Delete goal "${goal.name}"?`)) return
  try {
    await goalStore.deleteGoal(goal.id)
    toast.success('Goal deleted')
  } catch {
    toast.error('Failed to delete goal')
  }
}
</script>

<style scoped>
.goals-page {
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

.goals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.goal-card {
  background: var(--color-bg-card);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--color-shadow);
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: box-shadow 0.15s;
}

.goal-card:hover {
  box-shadow: var(--color-shadow-hover);
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.goal-header h3 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.deadline {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-weight: 500;
}

.goal-amounts {
  font-size: 1rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.current {
  color: var(--color-accent);
}

.separator {
  margin: 0 4px;
  color: var(--color-text-placeholder);
}

.target {
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

.progress-active {
  background: var(--color-accent);
}

.progress-complete {
  background: var(--color-income);
}

.percentage-label {
  font-size: 0.8125rem;
  font-weight: 600;
}

.text-active {
  color: var(--color-accent);
}

.text-complete {
  color: var(--color-income);
}

.goal-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 9999px;
  display: inline-block;
}

.badge-complete {
  background: var(--color-badge-income-bg);
  color: var(--color-badge-income-text);
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

.form-group input[type='text'],
.form-group input[type='number'],
.form-group input[type='date'] {
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

.form-group input:focus {
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
}
</style>
