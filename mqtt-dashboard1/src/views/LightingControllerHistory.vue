<template>
  <div>
    <div class="header-container">
      <h2>Lighting Controller History Data</h2>
      <el-button size="small" type="primary" @click="fetchHistoricalData">Refresh</el-button>
    </div>
    <!-- The newly added light intensity information window -->
    <el-card class="intensity-info-card">
      <div slot="header">Light Intensity Information</div>
      <div class="info-content">
        <p>Max Light Intensity: {{ maxIntensity }} Lux at {{ maxIntensityTime }} (Status: {{ maxIntensityStatus }})</p>
        <p>Min Light Intensity: {{ minIntensity }} Lux at {{ minIntensityTime }} (Status: {{ minIntensityStatus }})</p>
      </div>
    </el-card>
    <!-- The newly added time search window -->
    <el-card class="search-info-card">
      <div slot="header">Search by Time</div>
      <div class="info-content">
        <el-input v-model="searchTime" placeholder="Enter timestamp" @keyup.enter="searchByTime"></el-input>
        <el-button @click="searchByTime">Search</el-button>
        <p v-if="searchResult">Light Intensity: {{ searchResult.intensity }} Lux, Status: {{ formatStatus(searchResult) }}</p>
        <p v-else-if="searchPerformed &&!searchResult">No data found for the given time.</p>
      </div>
    </el-card>
    <el-card>
      <div slot="header">History Data List</div>
      <div class="history-data-scroll">
        <table class="history-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Light Control Status</th>
              <th>Light Intensity (Lux)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(data, index) in displayedHistoricalData" :key="index">
              <td>{{ data.timestamp }}</td>
              <td>{{ formatStatus(data) }}</td>
              <td>{{ data.intensity }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </el-card>
    <div class="back-container">
      <el-button type="primary" round @click="goBack">Back</el-button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      historicalData: [],
      displayedHistoricalData: [],
      maxIntensity: null,
      maxIntensityTime: null,
      maxIntensityStatus: null,
      minIntensity: null,
      minIntensityTime: null,
      minIntensityStatus: null,
      searchTime: '',
      searchResult: null,
      searchPerformed: false
    };
  },
  created() {
    this.fetchHistoricalData();
  },
  methods: {
    formatStatus(row) {
      return row.status === 'on' ? 'On' : 'Off';
    },
    fetchHistoricalData() {
      axios.get('http://localhost:5050/api/history/light_control')
        .then(res => {
          this.historicalData = res.data.history || [];
          this.displayedHistoricalData = this.historicalData.slice(0, 30);
          this.calculateIntensityInfo();
        })
        .catch(err => {
          console.error('Failed to fetch historical data:', err);
        });
    },
    goBack() {
      this.$router.back();
    },
    calculateIntensityInfo() {
      if (this.historicalData.length === 0) {
        return;
      }
      let maxInt = this.historicalData[0].intensity;
      let maxIntTime = this.historicalData[0].timestamp;
      let maxIntStatus = this.historicalData[0].status;
      let minInt = this.historicalData[0].intensity;
      let minIntTime = this.historicalData[0].timestamp;
      let minIntStatus = this.historicalData[0].status;

      for (let data of this.historicalData) {
        if (data.intensity > maxInt) {
          maxInt = data.intensity;
          maxIntTime = data.timestamp;
          maxIntStatus = data.status;
        }
        if (data.intensity < minInt) {
          minInt = data.intensity;
          minIntTime = data.timestamp;
          minIntStatus = data.status;
        }
      }

      this.maxIntensity = maxInt;
      this.maxIntensityTime = maxIntTime;
      this.maxIntensityStatus = maxIntStatus;
      this.minIntensity = minInt;
      this.minIntensityTime = minIntTime;
      this.minIntensityStatus = minIntStatus;
    },
    searchByTime() {
      this.searchPerformed = true;
      this.searchResult = this.historicalData.find(data => data.timestamp === this.searchTime);
    }
  }
};
</script>

<style scoped>
.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.intensity-info-card,
.search-info-card {
  margin-bottom: 20px;
}

.info-content {
  padding: 10px;
}

.history-data-scroll {
  max-height: 400px;
  overflow-y: auto;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th,
.history-table td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: center;
}

.back-container {
  margin-top: 40px;
  text-align: center;
}
</style>