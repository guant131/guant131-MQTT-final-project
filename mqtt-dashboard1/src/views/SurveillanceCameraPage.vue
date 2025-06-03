<template>
  <div>
    <h2>Surveillance Camera</h2>

    <!-- Real-time FPS data card -->
    <el-card class="mb-4">
      <div slot="header">Real-time Data</div>
      <div v-if="realTimeData && realTimeData.fps !== null">
        <p><strong>Current FPS:</strong> {{ realTimeData.fps }} FPS</p>
        <p><strong>Time:</strong> {{ realTimeData.timestamp }}</p>
      </div>
      <div v-else-if="loading">
        Loading...
      </div>
      <div v-else>
        No real-time data available.
      </div>
    </el-card>

    <!-- FPS line chart -->
    <el-card class="mt-4">
      <div slot="header">FPS Variation Chart Over Time</div>
      <line-chart :chart-data="fpsChartData" :chart-options="fpsChartOptions" />
    </el-card>

    <!-- Dual-camera view -->
    <div class="camera-container">
      <!-- Original camera video -->
      <el-card class="camera-card">
        <div slot="header" class="flex justify-between items-center">
          <span>Original Camera Feed</span>
          <div>
            <el-button
              type="primary"
              size="mini"
              @click="enterFullscreen('original')"
              :disabled="!streamActive">
              Full Screen
            </el-button>
            <el-button
              type="danger"
              size="mini"
              @click="stopCamera"
              :disabled="!streamActive">
              Stop Camera
            </el-button>
            <el-button
              type="info"
              size="mini"
              @click="flipCamera"
              :disabled="!streamActive">
              Flip Camera
            </el-button>
          </div>
        </div>
        <video
          ref="cameraVideo"
          width="100%"
          controls
          autoplay
          muted
          class="live-camera"
          v-show="streamActive"
        ></video>
        <div v-if="!streamActive" class="camera-prompt">
          <el-button type="primary" @click="startCamera">Enable Camera</el-button>
          <p class="hint">Camera access required for live feed</p>
          <p v-if="cameraError" class="error">{{ cameraError }}</p>
          <p v-if="cameraStopped" class="stopped">Camera has been stopped.</p>
        </div>
      </el-card>

      <!-- Processed YOLOv8 video -->
      <el-card class="camera-card">
        <div slot="header" class="flex justify-between items-center">
          <span>YOLOv8 Detection Results</span>
          <div>
            <el-button
              type="primary"
              size="mini"
              @click="enterFullscreen('processed')"
              :disabled="!streamActive || !yoloActive">
              Full Screen
            </el-button>
            <el-button
              type="success"
              size="mini"
              :class="{ 'is-loading': yoloLoading }"
              @click="toggleYolo"
              :disabled="!streamActive">
              {{ yoloActive ? 'Stop Detection' : 'Start Detection' }}
            </el-button>
          </div>
        </div>
        <img
          ref="yoloVideo"
          src="http://localhost:5001/video_feed"
          width="100%"
          class="live-camera"
          v-show="streamActive && yoloActive"
        />
        <div v-if="!streamActive || !yoloActive" class="camera-prompt">
          <p v-if="!yoloActive && streamActive" class="hint">Click "Start Detection" to enable YOLOv8 processing</p>
          <p v-if="yoloError" class="error">{{ yoloError }}</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import LineChart from '@/components/LineChart.vue'

export default {
  name: 'SurveillanceCameraPage',
  components: {
    LineChart
  },
  data() {
    return {
      realTimeData: null,
      loading: true,
      fpsChartData: {
        labels: [],
        datasets: [
          {
            label: 'FPS',
            data: [],
            borderColor: '#42A5F5',
            fill: false,
            tension: 0.3
          }
        ]
      },
      fpsChartOptions: {
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
              text: 'FPS'
            },
            suggestedMin: 0,
            suggestedMax: 60
          }
        },
        plugins: {
          legend: {
            display: false
          }
        }
      },
      stream: null,
      streamActive: false,
      cameraError: null,
      cameraStopped: false,
      facingMode: 'environment',
      yoloActive: false,
      yoloError: null,
      yoloLoading: false,
      dataFetchInterval: null
    }
  },
  created() {
    this.fetchAllData()
    this.dataFetchInterval = setInterval(this.fetchAllData, 5000)
  },
  beforeDestroy() {
    clearInterval(this.dataFetchInterval)
    this.stopCamera()
    this.stopYolo()
  },
  methods: {
    fetchAllData() {
      axios.get('http://localhost:5050/api/history/fps')
        .then(res => {
          const allData = res.data.history || []
          const now = new Date()
          const fiveSecondsAgo = new Date(now.getTime() - 5000)
          const twoMinutesAgo = new Date(now.getTime() - 2 * 60 * 1000)

          const realTime = allData.find(item => {
            const ts = new Date(item.timestamp)
            return ts >= fiveSecondsAgo
          })

          const fpsChartDataPoints = allData.filter(item => {
            const ts = new Date(item.timestamp)
            return ts >= twoMinutesAgo
          })

          this.realTimeData = realTime || null
          this.loading = false

          this.fpsChartData = {
            labels: fpsChartDataPoints.map(() => ''),
            datasets: [
              {
                label: 'FPS',
                data: fpsChartDataPoints.map(item => item.fps),
                borderColor: '#42A5F5',
                fill: false,
                tension: 0.3
              }
            ]
          }
        })
        .catch(err => {
          console.error('Failed to fetch data:', err)
          this.loading = false
          this.$message.error('Failed to fetch real-time data. Please check your network connection.')
        })
    },
    startCamera() {
      navigator.mediaDevices.getUserMedia({ video: { facingMode: this.facingMode }, audio: false })
        .then(stream => {
          this.stream = stream
          const videoElement = this.$refs.cameraVideo
          if ('srcObject' in videoElement) {
            videoElement.srcObject = stream
          } else {
            videoElement.src = window.URL.createObjectURL(stream)
          }
          this.streamActive = true
          this.cameraError = null
          this.cameraStopped = false
        })
        .catch(err => {
          console.error('Camera access error:', err)
          this.cameraError = 'Failed to access camera: ' + err.message
        })
    },
    stopCamera() {
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop())
        this.stream = null
      }
      this.streamActive = false
      this.cameraStopped = true
    },
    enterFullscreen(type) {
      const element = type === 'original' ? this.$refs.cameraVideo : this.$refs.yoloVideo
      if (element.requestFullscreen) {
        element.requestFullscreen()
      } else if (element.webkitRequestFullscreen) {
        element.webkitRequestFullscreen()
      } else if (element.mozRequestFullScreen) {
        element.mozRequestFullScreen()
      } else if (element.msRequestFullscreen) {
        element.msRequestFullscreen()
      } else {
        this.$message.warning('Your browser does not support fullscreen mode')
      }
    },
    flipCamera() {
      this.stopCamera()
      this.facingMode = this.facingMode === 'environment' ? 'user' : 'environment'
      this.startCamera()
    },
    startYolo() {
      if (!this.streamActive) {
        this.yoloError = 'Camera is not active'
        this.$message.error(this.yoloError)
        return
      }

      this.yoloActive = true
      this.yoloError = null
    },
    stopYolo() {
      this.yoloActive = false
    },
    toggleYolo() {
      if (this.yoloActive) {
        this.stopYolo()
      } else {
        this.startYolo()
      }
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
.camera-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 20px;
}
.camera-card {
  flex: 1 1 calc(50% - 20px);
  min-width: 300px;
}
.camera-prompt {
  padding: 10px;
  text-align: center;
}
.hint {
  color: #888;
  margin-top: 5px;
}
.error {
  color: red;
  margin-top: 5px;
}
.stopped {
  color: #666;
  margin-top: 5px;
  font-style: italic;
}
.live-camera {
  display: block;
  width: 100%;
  height: auto;
  background-color: #000;
}
.is-loading .el-button__content::after {
  content: '';
  display: inline-block;
  width: 1em;
  height: 1em;
  margin-left: 0.5em;
  border: 2px solid currentColor;
  border-radius: 50%;
  border-right-color: transparent;
  animation: spin 1s linear infinite;
  vertical-align: middle;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>