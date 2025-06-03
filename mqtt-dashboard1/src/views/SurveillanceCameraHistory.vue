<template>
  <div>
    <div class="header-container">
      <h2>Surveillance Camera History Data</h2>
      <el-button size="small" type="primary" @click="fetchHistoryData">Refresh</el-button>
    </div>
    <!-- Newly added FPS information window -->
    <el-card class="fps-info-card">
      <div slot="header">FPS Information</div>
      <div class="info-content">
        <p>Max FPS: {{ maxFps }} at {{ maxFpsTime }}</p>
        <p>Min FPS: {{ minFps }} at {{ minFpsTime }}</p>
      </div>
    </el-card>
    <!-- Newly added time search window -->
    <el-card class="search-info-card">
      <div slot="header">Search by Time</div>
      <div class="info-content">
        <el-input v-model="searchTime" placeholder="Enter timestamp" @keyup.enter="searchByTime"></el-input>
        <el-button @click="searchByTime">Search</el-button>
        <p v-if="searchResult">FPS: {{ searchResult.fps }}</p>
        <p v-else-if="searchPerformed &&!searchResult">No data found for the given time.</p>
      </div>
    </el-card>
    <el-card>
      <div slot="header">History Data List</div>
      <div class="history-data-scroll">
        <table class="history-table">
          <thead>
            <tr>
              <th>FPS</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(data, index) in displayedHistoryData" :key="index">
              <td>{{ data.fps }}</td>
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
      maxFps: null,
      maxFpsTime: null,
      minFps: null,
      minFpsTime: null,
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
      axios.get('http://localhost:5050/api/history/fps')
        .then(res => {
          this.historyData = res.data.history || [];
          this.displayedHistoryData = this.historyData.slice(0, 30);
          this.calculateFpsInfo();
        })
        .catch(err => {
          console.error('Failed to fetch history data:', err);
        });
    },
    goBack() {
      this.$router.back();
    },
    calculateFpsInfo() {
      if (this.historyData.length === 0) {
        return;
      }
      let maxFps = this.historyData[0].fps;
      let maxFpsTime = this.historyData[0].timestamp;
      let minFps = this.historyData[0].fps;
      let minFpsTime = this.historyData[0].timestamp;

      for (let data of this.historyData) {
        if (data.fps > maxFps) {
          maxFps = data.fps;
          maxFpsTime = data.timestamp;
        }
        if (data.fps < minFps) {
          minFps = data.fps;
          minFpsTime = data.timestamp;
        }
      }

      this.maxFps = maxFps;
      this.maxFpsTime = maxFpsTime;
      this.minFps = minFps;
      this.minFpsTime = minFpsTime;
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

.fps-info-card,
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