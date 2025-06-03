<template> 
  <div> 
    <h2>Lighting Controller</h2>

    <!-- Card showing real-time light control data -->
    <el-card class="mb-4">
      <div slot="header">Real-time Data</div>
      <div v-if="realTimeData && realTimeData.status !== null">
        <p><strong>Light Control Status:</strong> {{ realTimeData.status === 'on' ? 'On' : 'Off' }}</p>
        <p><strong>Current Light Intensity:</strong> {{ realTimeData.intensity }} Lux</p>
        <p><strong>Time:</strong> {{ realTimeData.timestamp }}</p>
      </div>
      <div v-else-if="realTimeData === null">
        Loading...
      </div>
      <div v-else>
        No real-time data available.
      </div>
    </el-card>
    
    <!-- Line chart showing light intensity trend -->
    <el-card class="mt-4">
      <div slot="header">Light Intensity Variation Over Time</div>
      <line-chart :chart-data="intensityChartData" :chart-options="intensityChartOptions" />
    </el-card>
    
    <!-- Bar chart showing proportion of switch statuses -->
    <el-card class="mt-4">
      <div slot="header">Light Control Status Distribution (Bar Chart)</div>
      <div style="width: 30%; margin: 0 auto;">
        <bar-chart :chart-data="switchStatusChartData" :chart-options="switchStatusChartOptions" />
      </div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';
import LineChart from '../components/LightingControllerLineChart.vue';
import BarChart from '../components/LightingControllerBarChart.vue';

export default {
  name: 'LightingControllerPage',
  components: {
    LineChart,
    BarChart
  },
  data() {
    return {
      deviceId: this.$route.params.deviceId || 'lightingController1',
      realTimeData: null,
      intensityChartData: {
        labels: [],
        datasets: [
          {
            label: 'Light Intensity (Lux)',
            data: [],
            borderColor: '#FFD700',
            fill: false,
            tension: 0.3
          }
        ]
      },
      intensityChartOptions: {
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
              text: 'Light Intensity (Lux)'
            },
            suggestedMin: 0,
            suggestedMax: 1000
          }
        },
        plugins: {
          legend: {
            display: false
          }
        }
      },
      switchStatusChartData: {
        labels: ['On', 'Off'],
        datasets: [
          {
            data: [0, 0],
            backgroundColor: ['#FFD700', '#FF6B6B']
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
    // Set interval to fetch data every 5 seconds
    this.interval = setInterval(this.fetchAllData, 5000);
  },
  beforeDestroy() {
    clearInterval(this.interval);
  },
  methods: {
    // Format status field (optional method, not used in template)
    formatIsStarted(row) {
      return row.status === 'on' ? 'On' : 'Off';
    },

    // Fetch real-time and historical data
    fetchAllData() { 
      axios.get('http://localhost:5050/api/history/light_control')
        .then(res => {
          const allData = res.data.history || [];
          const now = new Date();
          const fiveSecondsAgo = new Date(now.getTime() - 5000);
          const twoMinutesAgo = new Date(now.getTime() - 2 * 60 * 1000);

          // ✅ Get real-time data from the last 5 seconds
          const realTime = allData.find(item => {
            const ts = new Date(item.timestamp);
            return ts >= fiveSecondsAgo;
          });

          // ✅ Get intensity data from the last 2 minutes for the line chart
          const intensityChartDataPoints = allData.filter(item => {
            const ts = new Date(item.timestamp);
            return ts >= twoMinutesAgo;
          });

          // ⚠️ Update real-time display
          this.realTimeData = realTime || null;

          // ⚠️ Update line chart
          this.intensityChartData = {
            labels: intensityChartDataPoints.map(() => ''),
            datasets: [
              {
                label: 'Light Intensity (Lux)',
                data: intensityChartDataPoints.map(item => item.intensity),
                borderColor: '#42A5F5', // Set to blue
                fill: false,
                tension: 0.3
              }
            ]
          };

          // ✅ Filter the past 1-minute data for bar chart statistics
          const allDataInOneMinute = allData.filter(item => {
            const ts = new Date(item.timestamp);
            return ts >= new Date(now.getTime() - 60 * 1000);
          });

          // ⚠️ Count different statuses based on intensity
          const tooBrightCount = allDataInOneMinute.filter(item => item.intensity >= 600).length;
          const tooDarkCount = allDataInOneMinute.filter(item => item.intensity <= 200).length;
          const offCount = allDataInOneMinute.length - tooBrightCount - tooDarkCount;

          // ⚠️ Update bar chart
          this.switchStatusChartData = {
            labels: ['ON (Too Bright)', 'ON (Too Dark)', 'OFF'],
            datasets: [
              {
                label: 'Light Control Status',
                data: [tooBrightCount, tooDarkCount, offCount],
                backgroundColor: ['#FFA726', '#66BB6A', '#FF6B6B']
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
