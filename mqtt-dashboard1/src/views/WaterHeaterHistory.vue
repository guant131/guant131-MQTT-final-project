<template>
  <div>
    <div class="header-container">
      <h2>Water Heater History Data</h2>
      <el-button size="small" type="primary" @click="fetchHistoryData">Refresh</el-button>
    </div>
    <!-- Newly added temperature information window -->
    <el-card class="temperature-info-card">
      <div slot="header">Temperature Information</div>
      <div class="info-content">
        <p>Max Temperature: {{ maxTemperature }}°C at {{ maxTemperatureTime }} (Status: {{ maxTemperatureStatus }})</p>
        <p>Min Temperature: {{ minTemperature }}°C at {{ minTemperatureTime }} (Status: {{ minTemperatureStatus }})</p>
      </div>
    </el-card>
    <!-- Newly added time search window -->
    <el-card class="search-info-card">
      <div slot="header">Search by Time</div>
      <div class="info-content">
        <el-input v-model="searchTime" placeholder="Enter timestamp" @keyup.enter="searchByTime"></el-input>
        <el-button @click="searchByTime">Search</el-button>
        <p v-if="searchResult">Temperature: {{ searchResult.temperature }}°C, Status: {{ formatIsStarted(searchResult) }}</p>
        <p v-else-if="searchPerformed &&!searchResult">No data found for the given time.</p>
      </div>
    </el-card>
    <el-card>
      <div slot="header">History Data List</div>
      <div class="history-data-scroll">
        <table class="history-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Temperature (°C)</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(data, index) in displayedHistoryData" :key="index">
              <td>{{ formatIsStarted(data) }}</td>
              <td>{{ data.temperature }}</td>
              <td>{{ data.timestamp }}</td>
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
      historyData: [],
      displayedHistoryData: [],
      maxTemperature: null,
      maxTemperatureTime: null,
      maxTemperatureStatus: null,
      minTemperature: null,
      minTemperatureTime: null,
      minTemperatureStatus: null,
      searchTime: '',
      searchResult: null,
      searchPerformed: false
    };
  },
  created() {
    this.fetchHistoryData();
  },
  methods: {
    formatIsStarted(row) {
      return row.status === 'running' ? 'Started' : 'Not Started';
    },
    fetchHistoryData() {
      axios.get('http://localhost:5050/api/history/water_heater')
        .then(res => {
          this.historyData = res.data.history || [];
          this.displayedHistoryData = this.historyData.slice(0, 30);
          this.calculateTemperatureInfo();
        })
        .catch(err => {
          console.error('Failed to fetch history data:', err);
        });
    },
    goBack() {
      this.$router.back();
    },
    calculateTemperatureInfo() {
      if (this.historyData.length === 0) {
        return;
      }
      let maxTemp = this.historyData[0].temperature;
      let maxTempTime = this.historyData[0].timestamp;
      let maxTempStatus = this.historyData[0].status;
      let minTemp = this.historyData[0].temperature;
      let minTempTime = this.historyData[0].timestamp;
      let minTempStatus = this.historyData[0].status;

      for (let data of this.historyData) {
        if (data.temperature > maxTemp) {
          maxTemp = data.temperature;
          maxTempTime = data.timestamp;
          maxTempStatus = data.status;
        }
        if (data.temperature < minTemp) {
          minTemp = data.temperature;
          minTempTime = data.timestamp;
          minTempStatus = data.status;
        }
      }

      this.maxTemperature = maxTemp;
      this.maxTemperatureTime = maxTempTime;
      this.maxTemperatureStatus = maxTempStatus;
      this.minTemperature = minTemp;
      this.minTemperatureTime = minTempTime;
      this.minTemperatureStatus = minTempStatus;
    },
    searchByTime() {
      this.searchPerformed = true;
      this.searchResult = this.historyData.find(data => data.timestamp === this.searchTime);
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

.temperature-info-card,
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