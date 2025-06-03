<template>
  <div>
    <div class="header-container">
      <h2>Temperature History Data</h2>
      <el-button
        size="small"
        type="primary"
        @click="fetchHistoryData"
        class="refresh-button"
      >
        Refresh
      </el-button>
    </div>
    <!-- The newly added temperature information window -->
    <el-card class="temperature-info-card">
      <div slot="header">Temperature Information</div>
      <div class="info-content">
        <p>Max Temperature: {{ maxTemperature }}°C at {{ maxTemperatureTime }}</p>
        <p>Min Temperature: {{ minTemperature }}°C at {{ minTemperatureTime }}</p>
      </div>
    </el-card>
    <!-- The newly added time search window -->
    <el-card class="search-info-card">
      <div slot="header">Search by Time</div>
      <div class="info-content">
        <el-input v-model="searchTime" placeholder="Enter timestamp" @keyup.enter="searchByTime"></el-input>
        <el-button @click="searchByTime">Search</el-button>
        <p v-if="searchResult">Temperature: {{ searchResult.temperature }}°C</p>
        <p v-else-if="searchPerformed &&!searchResult">No data found for the given time.</p>
      </div>
    </el-card>
    <el-card>
      <div slot="header">History Data List</div>
      <div class="history-data-scroll">
        <table class="history-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Temperature (°C)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(data, index) in historyData" :key="index">
              <td>{{ data.timestamp }}</td>
              <td>{{ data.temperature }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DeviceData',
  data() {
    return {
      historyData: [],
      loading: true,
      error: null,
      maxTemperature: null,
      maxTemperatureTime: null,
      minTemperature: null,
      minTemperatureTime: null,
      searchTime: '',
      searchResult: null,
      searchPerformed: false
    };
  },
  created() {
    this.fetchHistoryData();
  },
  methods: {
    fetchHistoryData() {
      this.loading = true;
      this.error = null;
      axios.get(`http://localhost:5050/api/history/temperature`)
        .then(res => {
          const allData = res.data.history || [];
          // Sort the data by timestamp
          const sortedData = allData.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
          this.historyData = sortedData;
          this.calculateTemperatureInfo();
        })
        .catch(err => {
          this.error = 'Failed to fetch historical data. Please try again later.';
          console.error('Failed to fetch historical data:', err);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    calculateTemperatureInfo() {
      if (this.historyData.length === 0) {
        return;
      }
      let maxTemp = this.historyData[0].temperature;
      let maxTempTime = this.historyData[0].timestamp;
      let minTemp = this.historyData[0].temperature;
      let minTempTime = this.historyData[0].timestamp;

      for (let data of this.historyData) {
        if (data.temperature > maxTemp) {
          maxTemp = data.temperature;
          maxTempTime = data.timestamp;
        }
        if (data.temperature < minTemp) {
          minTemp = data.temperature;
          minTempTime = data.timestamp;
        }
      }

      this.maxTemperature = maxTemp;
      this.maxTemperatureTime = maxTempTime;
      this.minTemperature = minTemp;
      this.minTemperatureTime = minTempTime;
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
  margin-bottom: 10px;
}

.refresh-button {
  background-color: #409EFF;
  color: white;
  border-radius: 5px;
  font-size: 14px;
}

.refresh-button:hover {
  background-color: #66b1ff;
  color: white;
}

.temperature-info-card,
.search-info-card {
  margin-bottom: 20px;
}

.info-content {
  padding: 10px;
}

.history-data-scroll {
  max-height: 500px;
  overflow-y: auto;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th {
  background-color: white;
  font-family: "Arial", "Helvetica", sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: #000000;
  text-align: center;
  border: 1px solid #d9d9d9;
  padding: 12px;
}

.history-table td {
  font-family: "Arial", "Helvetica", sans-serif;
  font-size: 16px;
  color: black;
  text-align: center;
  border: 1px solid #d9d9d9;
  padding: 12px;
}

.history-table tr:nth-child(even) {
  background-color: white;
}
</style>