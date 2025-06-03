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
    name: 'LightingControllerLineChart',
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
              text: 'Light Intensity Over Time'
            },
            legend: {
              display: true,
              position: 'top'
            }
          },
          scales: {
            y: {
              title: {
                display: true,
                text: 'Intensity (Lux)'
              },
              suggestedMin: 0,
              suggestedMax: 1000
            },
            x: {
              display: false
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
  