<template>
  <div class="categories-page">
    <!-- Header -->
    <div class="page-header">
      <h1>Categories</h1>
      <button class="btn btn-primary" @click="openAddModal">Add Category</button>
    </div>

    <!-- Grid -->
    <div v-if="categoryStore.categories.length" class="category-grid">
      <div v-for="cat in categoryStore.categories" :key="cat.id" class="category-card">
        <div class="card-top">
          <div class="card-info">
            <span class="color-dot" :style="{ backgroundColor: cat.color }"></span>
            <h3 class="category-name">{{ cat.name }}</h3>
          </div>
          <span class="badge" :class="cat.type === 'income' ? 'badge-income' : 'badge-expense'">
            {{ cat.type }}
          </span>
        </div>
        <div class="card-actions">
          <button class="btn-action" @click="openEditModal(cat)">Edit</button>
          <button class="btn-action btn-action-danger" @click="confirmDelete(cat)">Delete</button>
        </div>
      </div>
    </div>
    <p v-else class="empty-state">No categories yet. Create one to get started.</p>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h2>{{ editingCategory ? 'Edit Category' : 'Add Category' }}</h2>
        <form @submit.prevent="saveCategory">
          <div class="form-group">
            <label>Name</label>
            <input v-model="form.name" type="text" required />
          </div>
          <div class="form-group">
            <label>Type</label>
            <select v-model="form.type" required>
              <option value="income">Income</option>
              <option value="expense">Expense</option>
            </select>
          </div>
          <div class="form-group">
            <label>Color</label>
            <div class="color-swatches">
              <button
                v-for="c in colorOptions"
                :key="c"
                type="button"
                class="color-swatch"
                :class="{ selected: form.color === c }"
                :style="{ backgroundColor: c }"
                @click="form.color = c"
              ></button>
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button type="submit" class="btn btn-primary">{{ editingCategory ? 'Update' : 'Create' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useCategoryStore, type Category } from '@/stores/categories'
import { useToast } from 'vue-toastification'

const toast = useToast()
const categoryStore = useCategoryStore()

const showModal = ref(false)
const editingCategory = ref<Category | null>(null)

const colorOptions = [
  '#0d9488', '#059669', '#2563eb', '#7c3aed', '#db2777',
  '#e11d48', '#d97706', '#ea580c', '#64748b', '#0f172a',
]

const form = reactive({
  name: '',
  type: 'expense' as 'income' | 'expense',
  color: '#0d9488',
})

onMounted(() => {
  categoryStore.fetchCategories()
})

function resetForm() {
  form.name = ''
  form.type = 'expense'
  form.color = '#0d9488'
}

function openAddModal() {
  editingCategory.value = null
  resetForm()
  showModal.value = true
}

function openEditModal(cat: Category) {
  editingCategory.value = cat
  form.name = cat.name
  form.type = cat.type
  form.color = cat.color
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingCategory.value = null
}

async function saveCategory() {
  try {
    const payload = { name: form.name, type: form.type, color: form.color }
    if (editingCategory.value) {
      await categoryStore.updateCategory(editingCategory.value.id, payload)
      toast.success('Category updated successfully')
    } else {
      await categoryStore.createCategory(payload)
      toast.success('Category created successfully')
    }
    closeModal()
  } catch (err: any) {
    toast.error(err?.response?.data?.detail || 'Failed to save category')
  }
}

async function confirmDelete(cat: Category) {
  if (!window.confirm(`Delete category "${cat.name}"?`)) return
  try {
    await categoryStore.deleteCategory(cat.id)
    toast.success('Category deleted')
  } catch {
    toast.error('Failed to delete category')
  }
}
</script>

<style scoped>
.categories-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 28px 20px;
}

/* Page header */
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
  color: #0f172a;
  margin: 0;
}

/* Grid */
.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.category-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: box-shadow 0.15s;
}

.category-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.color-dot {
  width: 10px;
  height: 10px;
  border-radius: 6px;
  flex-shrink: 0;
}

.category-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
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
  background: #ecfdf5;
  color: #059669;
}

.badge-expense {
  background: #fff1f2;
  color: #e11d48;
}

.card-actions {
  display: flex;
  gap: 6px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
  margin-top: auto;
}

.btn-action {
  background: none;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 500;
  color: #475569;
  transition: background 0.15s, border-color 0.15s;
}

.btn-action:hover {
  background: #f1f5f9;
}

.btn-action-danger:hover {
  background: #fff1f2;
  border-color: #fca5a5;
  color: #e11d48;
}

.empty-state {
  text-align: center;
  padding: 48px 16px;
  color: #94a3b8;
  font-size: 0.875rem;
}

/* Buttons */
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

.btn-secondary {
  background: #f1f5f9;
  color: #334155;
}

.btn-secondary:hover:not(:disabled) {
  background: #e2e8f0;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 16px;
}

.modal {
  background: #fff;
  border-radius: 16px;
  padding: 28px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
}

.modal h2 {
  margin: 0 0 24px;
  font-size: 1.25rem;
  font-weight: 700;
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

.form-group input[type='text'],
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

.color-swatches {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.color-swatch {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: border-color 0.15s, transform 0.15s;
  padding: 0;
}

.color-swatch:hover {
  transform: scale(1.1);
}

.color-swatch.selected {
  border-color: #0f172a;
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px #0f172a;
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
