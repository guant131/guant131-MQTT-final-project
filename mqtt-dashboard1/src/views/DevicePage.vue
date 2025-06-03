<template>
  <div>
    <h2>Air Conditioner</h2>

    <el-card class="mb-4">
      <div slot="header">Real-time Data</div>
      <div v-if="realTimeData && realTimeData.temperature !== null">
        <p><strong>Current Temperature:</strong> {{ realTimeData.temperature }} °C</p>
        <p><strong>Timestamp:</strong> {{ realTimeData.timestamp }}</p>
      </div>
      <div v-else-if="realTimeData === null">
        Loading...
      </div>
      <div v-else>
        No real-time data available
      </div>
    </el-card>

    <el-card>
      <div slot="header">Historical Data</div>
      <div style="max-height: 300px; overflow-y: auto">
        <el-table :data="historyData" border style="width: 100%">
          <el-table-column prop="timestamp" label="Timestamp" />
          <el-table-column prop="temperature" label="Temperature (°C)" />
        </el-table>
      </div>
    </el-card>

    <el-card class="mt-4">
      <div slot="header">Temperature Variation Over the Last 2 Minutes</div>
      <line-chart :chart-data="chartData" :chart-options="chartOptions" />
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'
import LineChart from '../components/LineChart.vue'

export default {
  name: 'DevicePage',
  components: {
    LineChart
  },
  data() {
    return {
      deviceId: this.$route.params.deviceId || 'sensor1',
      realTimeData: null,
      historyData: [],
      chartData: {
        labels: [],
        datasets: [
          {
            label: 'Temperature (°C)',
            data: [],
            borderColor: '#42A5F5',
            fill: false,
            tension: 0.3
          }
        ]
      },
      chartOptions: {
        responsive: true,
        animation: {
          duration: 500
        },
        scales: {
          x: {
            display: false
          },
          y: {
            title: {
              display: true,
              text: 'Temperature (°C)'
            },
            suggestedMin: 15,
            suggestedMax: 40
          }
        },
        plugins: {
          legend: {
            display: false
          }
        }
      }
    }
  },
  created() {
    this.fetchAllData()
    this.interval = setInterval(this.fetchAllData, 5000)
  },
  beforeDestroy() {
    clearInterval(this.interval)
  },
  methods: {
    fetchAllData() {
      axios.get(`http://localhost:5050/api/history/${this.deviceId}`)
        .then(res => {
          const allData = res.data.history || []

          const now = new Date()
          const fiveSecondsAgo = new Date(now.getTime() - 5000)
          const twoMinutesAgo = new Date(now.getTime() - 2 * 60 * 1000)

          const realTime = allData.find(item => {
            const ts = new Date(item.timestamp)
            return ts >= fiveSecondsAgo
          })

          const history = allData.filter(item => {
            const ts = new Date(item.timestamp)
            return ts < fiveSecondsAgo
          })

          const chartDataPoints = allData.filter(item => {
            const ts = new Date(item.timestamp)
            return ts >= twoMinutesAgo
          })

          this.realTimeData = realTime || null
          this.historyData = history.reverse()

          this.chartData = {
            labels: chartDataPoints.map(() => ''),
            datasets: [
              {
                label: 'Temperature (°C)',
                data: chartDataPoints.map(item => item.temperature),
                borderColor: '#42A5F5',
                fill: false,
                tension: 0.3
              }
            ]
          }
        })
        .catch(err => {
          console.error('Failed to fetch data:', err)
        })
    }
  }
}
</script>

<style scoped>
.mb-4 {
  margin-bottom: 20px;
}

.mt-4 {
  margin-top: 20px;
}
</style>
