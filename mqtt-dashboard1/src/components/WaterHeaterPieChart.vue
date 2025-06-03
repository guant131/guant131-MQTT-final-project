<template>
  <pie-chart ref="chart" :data="chartData" :options="chartOptions" />
</template>

<script>
import { Pie } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title, Tooltip, Legend,
  ArcElement
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, ArcElement)

export default {
  name: 'WaterHeaterPieChart',
  components: {
    'pie-chart': Pie
  },
  props: {
    chartData: {
      type: Object,
      default: () => ({
        labels: [],
        datasets: [
          {
            data: [],
            backgroundColor: []
          }
        ]
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
            text: 'Water Heater Pie Chart'
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
          this.$refs.chart.chart.update(); 
        }
      }
    }
  }
}
</script>