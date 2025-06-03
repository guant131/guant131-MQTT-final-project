<template>
  <div>
    <h2>Water Heater</h2>
    <el-card class="mb-4">
      <div slot="header">Real-time Data</div>
      <div v-if="realTimeData && realTimeData.status!== null">
        <p><strong>Is Started:</strong> {{ realTimeData.status === 'running'? 'Started' : 'Not Started' }}</p>
        <p><strong>Current Water Temperature:</strong> {{ realTimeData.temperature }} °C</p>
        <p><strong>Time:</strong> {{ realTimeData.timestamp }}</p>
      </div>
      <div v-else-if="realTimeData === null">
        Loading...
      </div>
      <div v-else>
        No real-time data available.
      </div>
    </el-card>
    <el-card class="mt-4">
      <div slot="header">Water Temperature Variation Chart Over Time</div>
      <line-chart :chart-data="temperatureChartData" :chart-options="temperatureChartOptions" />
    </el-card>
    <el-card class="mt-4">
      <div slot="header">Pie Chart of Water Heater Switch Status Proportion</div>
      <div style="width: 30%; margin: 0 auto;">
        <pie-chart :chart-data="switchStatusChartData" :chart-options="switchStatusChartOptions" />
      </div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';
import LineChart from '../components/WaterHeaterLineChart.vue';
import PieChart from '../components/WaterHeaterPieChart.vue';

export default {
  name: 'WaterHeaterPage',
  components: {
    LineChart,
    PieChart
  },
  data() {
    return {
      deviceId: this.$route.params.deviceId || 'waterHeater1',
      realTimeData: null,
      temperatureChartData: {
        labels: [],
        datasets: [
          {
            label: 'Water Temperature (°C)',
            data: [],
            borderColor: '#42A5F5',
            fill: false,
            tension: 0.3
          }
        ]
      },
      temperatureChartOptions: {
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
              text: 'Water Temperature (°C)'
            },
            suggestedMin: 0,
            suggestedMax: 100
          }
        },
        plugins: {
          legend: {
            display: false
          }
        }
      },
      switchStatusChartData: {
        labels: ['Started', 'Not Started'],
        datasets: [
          {
            data: [0, 0],
            backgroundColor: ['#42A5F5', '#FF6B6B']
          }
        ]
      },
      switchStatusChartOptions: {
        responsive: true,
        animation: {
          duration: 500
        },
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    };
  },
  created() {
    this.fetchAllData();
    this.interval = setInterval(this.fetchAllData, 5000);
  },
  beforeDestroy() {
    clearInterval(this.interval);
  },
  methods: {
    formatIsStarted(row) {
      return row.status === 'running'? 'Started' : 'Not Started';
    },
    fetchAllData() {
      axios.get('http://localhost:5050/api/history/water_heater')
        .then(res => {
          const allData = res.data.history || [];
          const now = new Date();
          const fiveSecondsAgo = new Date(now.getTime() - 5000);
          const twoMinutesAgo = new Date(now.getTime() - 2 * 60 * 1000);

          const realTime = allData.find(item => {
            const ts = new Date(item.timestamp);
            return ts >= fiveSecondsAgo;
          });

          const temperatureChartDataPoints = allData.filter(item => {
            const ts = new Date(item.timestamp);
            return ts >= twoMinutesAgo;
          });

          this.realTimeData = realTime || null;

          this.temperatureChartData = {
            labels: temperatureChartDataPoints.map(() => ''),
            datasets: [
              {
                label: 'Water Temperature (°C)',
                data: temperatureChartDataPoints.map(item => item.temperature),
                borderColor: '#42A5F5',
                fill: false,
                tension: 0.3
              }
            ]
          };

          const allDataInOneMinute = allData.filter(item => {
            const ts = new Date(item.timestamp);
            return ts >= new Date(now.getTime() - 60 * 1000);
          });
          const startedCount = allDataInOneMinute.filter(item => item.status === 'running').length;
          const notStartedCount = allDataInOneMinute.length - startedCount;

          this.switchStatusChartData = {
            labels: ['Started', 'Not Started'],
            datasets: [
              {
                data: [startedCount, notStartedCount],
                backgroundColor: ['#42A5F5', '#FF6B6B']
              }
            ]
          };
        })
        .catch(err => {
          console.error('Failed to fetch data:', err);
        });
    }
  }
};
</script>

<style scoped>
.mb-4 {
  margin-bottom: 20px;
}

.mt-4 {
  margin-top: 20px;
}
</style>