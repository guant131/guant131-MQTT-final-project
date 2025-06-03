<template>
  <bar-chart ref="chart" :data="chartData" :options="chartOptions" />
</template>

<script>
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title, Tooltip, Legend,
  BarElement, CategoryScale, LinearScale
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default {
  name: 'LightingControllerBarChart',
  components: {
    'bar-chart': Bar
  },
  props: {
    chartData: {
      type: Object,
      default: () => ({
        labels: ['ON (Too Bright)', 'ON (Too Dark)', 'OFF'],
        datasets: [
          {
            label: 'Light Control Status',
            data: [0, 0, 0], // 初始值，后续会被替换
            backgroundColor: ['#FFA726', '#66BB6A', '#FF6B6B'] // 橙色、绿色、红色
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
            text: 'Bar Chart of Lighting Controller Switch Status Proportion'
          },
          legend: {
            position: 'bottom'
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Device Count'
            }
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
