<script setup lang="ts">
import { computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar } from 'vue-chartjs'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const props = defineProps<{
  labels: string[]
  incomeData: number[]
  expenseData: number[]
}>()

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      label: 'Income',
      data: props.incomeData,
      backgroundColor: '#059669',
      borderRadius: 4,
    },
    {
      label: 'Expenses',
      data: props.expenseData,
      backgroundColor: '#e11d48',
      borderRadius: 4,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  barPercentage: 0.7,
  categoryPercentage: 0.8,
  plugins: {
    legend: {
      position: 'top' as const,
      labels: {
        padding: 16,
        usePointStyle: true,
        pointStyle: 'rectRounded',
        font: { size: 12 },
      },
    },
    tooltip: {
      callbacks: {
        label(ctx: any) {
          return ` ${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2)}`
        },
      },
    },
  },
  scales: {
    x: {
      grid: { display: false },
    },
    y: {
      beginAtZero: true,
      grid: {
        color: '#f1f5f9',
      },
      ticks: {
        callback(value: any) {
          return value.toLocaleString()
        },
      },
    },
  },
}
</script>

<template>
  <div class="chart-bar-wrapper">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.chart-bar-wrapper {
  position: relative;
  width: 100%;
  min-height: 300px;
}
</style>
