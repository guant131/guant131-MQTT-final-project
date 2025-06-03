<template>
  <line-chart ref="chart" :data="chartData" :options="chartOptions" />
</template>

<script>
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title, Tooltip, Legend,
  LineElement, PointElement,
  LinearScale, CategoryScale
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, LinearScale, CategoryScale)

export default {
  name: 'WaterHeaterLineChart',
  components: {
    'line-chart': Line
  },
  props: {
    chartData: {
      type: Object,
      default: () => ({
        labels: [],
        datasets: []
      })
    },
    chartOptions: {
      type: Object,
      default: () => ({
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Water Heater Line Chart'
          }
        }
      })
    }
  },
  watch: {
    chartData: {
      deep: true,
      handler() {
        if (this.$refs.chart && this.$refs.chart.chart) {
          this.$refs.chart.chart.update(); // 
        }
      }
    }
  }
}
</script>