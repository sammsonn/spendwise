<script setup lang="ts">
import { computed } from 'vue'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { Pie } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps<{
  labels: string[]
  data: number[]
  colors: string[]
}>()

const hasData = computed(() => props.data.length > 0 && props.data.some((v) => v > 0))

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      data: props.data,
      backgroundColor: props.colors,
      borderWidth: 0,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const,
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
          const total = ctx.dataset.data.reduce((a: number, b: number) => a + b, 0)
          const pct = total ? ((ctx.parsed / total) * 100).toFixed(1) : '0'
          return ` ${ctx.label}: ${ctx.parsed.toFixed(2)} (${pct}%)`
        },
      },
    },
  },
}
</script>

<template>
  <div class="chart-pie-wrapper">
    <Pie v-if="hasData" :data="chartData" :options="chartOptions" />
    <div v-else class="no-data">No data available</div>
  </div>
</template>

<style scoped>
.chart-pie-wrapper {
  position: relative;
  width: 100%;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-data {
  color: #94a3b8;
  font-size: 0.95rem;
  font-weight: 500;
}
</style>
