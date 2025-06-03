<template>
  <div class="status-container">
    <h2 class="title">Real-time Device Monitoring</h2>
    <el-row :gutter="20">
      <el-col v-for="device in devices" :key="device.name" :span="12">
        <el-card class="device-card">
          <div class="device-header">{{ device.label }}</div>
          <p><strong>Status:</strong>
            <el-tag :type="device.subscribed ? 'success' : 'danger'">
              {{ device.subscribed ? 'Subscribed' : 'Not Subscribed' }}
            </el-tag>
          </p>
          <p><strong>Latest Data:</strong></p>

          <!-- Aesthetically enhanced data display area -->
          <div class="data-block" v-if="device.latestData">
            <div v-for="(value, key) in device.latestData" :key="key" class="data-row">
              <strong>{{ key }}:</strong> <span>{{ value }}</span>
            </div>
          </div>
          <div class="data-block" v-else>
            <span>N/A</span>
          </div>

          <div class="card-actions">
            <el-button size="mini" type="primary" @click="subscribeDevice(device)" :disabled="device.subscribed">
              Subscribe
            </el-button>
            <div class="right-buttons">
              <el-button size="mini" type="danger" @click="unsubscribeDevice(device)" :disabled="!device.subscribed">
                Unsubscribe
              </el-button>
              <el-button size="mini" type="primary" @click="refreshDevice(device)" :disabled="!device.subscribed">
                Refresh
              </el-button>
              <el-button size="mini" @click="navigateToPage(device)">
                View
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'RealTimeStatusPage',
  data() {
    return {
      devices: [
        {
          name: 'aircon',
          label: 'Air Conditioner',
          subscribed: false,
          latestData: null
        },
        {
          name: 'heater',
          label: 'Water Heater',
          subscribed: false,
          latestData: null
        },
        {
          name: 'camera',
          label: 'Surveillance Camera',
          subscribed: false,
          latestData: null
        },
        {
          name: 'light',
          label: 'Lighting Controller',
          subscribed: false,
          latestData: null
        }
      ]
    }
  },
  methods: {
    async subscribeDevice(device) {
      try {
        device.subscribed = true;
        await this.refreshDevice(device);
      } catch (error) {
        console.error(`Failed to subscribe to ${device.name}:`, error);
        device.subscribed = false;
        device.latestData = null;
      }
    },
    unsubscribeDevice(device) {
      device.subscribed = false;
      device.latestData = null;
    },
    async refreshDevice(device) {
      if (!device.subscribed) return;

      try {
        let url = '';
        switch (device.name) {
          case 'aircon':
            url = '/api/device/aircon/view-data';
            break;
          case 'heater':
            url = '/api/realtime-db/water_heater';
            break;
          case 'camera':
            url = '/api/realtime-db/fps';
            break;
          case 'light':
            url = '/api/realtime-db/light_control';
            break;
        }

        const response = await axios.get(`http://127.0.0.1:5050${url}`);
        device.latestData = response.data;

      } catch (error) {
        console.error(`Failed to refresh ${device.name}:`, error);
      }
    },
    navigateToPage(device) {
      switch (device.name) {
        case 'aircon':
          this.$router.push({ name: 'DevicePage', params: { deviceId: 'aircon' } });
          break;
        case 'heater':
          this.$router.push({ name: 'WaterHeaterPage', params: { deviceId: 'heater' } });
          break;
        case 'camera':
          this.$router.push({ name: 'SurveillanceCameraPage', params: { deviceId: 'camera' } });
          break;
        case 'light':
          this.$router.push({ name: 'LightingControllerPage', params: { deviceId: 'light' } });
          break;
        default:
          console.error('Unknown device');
      }
    }
  }
}
</script>

<style scoped>
.status-container {
  padding: 30px;
}

.title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  text-align: center;
}

.device-card {
  margin-bottom: 30px;
  border-radius: 12px;
  transition: box-shadow 0.3s;
  min-height: 350px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
}

.device-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.device-header {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 10px;
}

.card-actions {
  position: absolute;
  bottom: 15px;
  left: 15px;
  right: 15px;
  display: flex;
  justify-content: space-between;
}

.right-buttons {
  display: flex;
  gap: 8px;
  margin-right: 288px;
}

.data-block {
  background-color: #f8f8f8;
  padding: 10px;
  border-radius: 6px;
  font-family: monospace;
  max-height: 180px;
  overflow: auto;
  margin-bottom: 40px;
  flex-grow: 1;
}

.data-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px solid #eee;
  font-family: monospace;
}
</style>
