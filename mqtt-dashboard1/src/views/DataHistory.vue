<template>
  <div class="data-history-container">
    <h1 class="page-title">Data History</h1>
    <div class="device-modules">
      <el-card
        class="device-card"
        v-for="(device, index) in devices"
        :key="index"
        body-style="padding: 32px; display: flex; flex-direction: column; align-items: center;"
      >
        <div class="device-header">{{ device.title }}</div>
        <div class="card-actions">
          <el-button
            size="medium"
            type="primary"
            @click="viewDetails(device.title, device.id)"
            style="width: 100%; max-width: 200px;"
          >
            View Details <el-icon><arrow-right /></el-icon>
          </el-button>
        </div>
      </el-card>
    </div>
    <div class="back-container">
      <el-button
        type="primary"
        round
        size="medium"
        @click="goBack"
        style="padding: 12px 24px; font-size: 16px;"
      >
        <el-icon><arrow-left /></el-icon> Back to Dashboard
      </el-button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      devices: [
        { title: 'Air Conditioner Sensor', id: 'sensor1' },
        { title: 'Water Heater Sensor', id: 'heater1' },
        { title: 'Surveillance Camera', id: 'camera1' },
        { title: 'Lighting Controller', id: 'controller1' }
      ]
    };
  },
  methods: {
    viewDetails(deviceTitle, deviceId) {
      if (deviceTitle === 'Water Heater') {
        this.$router.push({ name: 'WaterHeaterHistory' });
      } else if (deviceTitle === 'Surveillance Camera') {
        this.$router.push({ name: 'SurveillanceCameraHistory' });
      } else if (deviceTitle === 'Lighting Controller') {
        this.$router.push({ name: 'LightingControllerHistory', params: { deviceId } });
      } else {
        this.$router.push({ name: 'DeviceData', params: { deviceId, deviceTitle } });
      }
    },
    goBack() {
      this.$router.back();
    }
  }
};
</script>

<style scoped>
.data-history-container {
  padding: 40px 20px;
  background-color: #f0f2f5;
}

.page-title {
  font-size: 32px;
  color: #1a73e8;
  margin-bottom: 32px;
  text-align: center;
  font-weight: 500;
  letter-spacing: 0.8px;
}

.device-modules {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 32px;
  max-width: 1440px;
  margin: 0 auto;
}

.device-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
  min-height: 280px;
  padding: 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.device-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

.device-header {
  font-size: 24px;
  color: #333;
  font-weight: 600;
  text-align: center;
  margin-bottom: 24px;
}

.card-actions {
  width: 100%;
  display: flex;
  justify-content: center;
  gap: 12px;
}

.el-button--primary {
  background-color: #409eff;
  border-color: #409eff;
  box-shadow: none;
  transition: all 0.3s;
  padding: 12px 24px; /* Unify the button padding */
}

.el-button--primary:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
}

.back-container {
  margin-top: 64px;
  text-align: center;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .device-modules {
    grid-template-columns: 1fr;
  }
  .page-title {
    font-size: 24px;
  }
  .device-card {
    padding: 24px;
    min-height: 240px;
  }
  .device-header {
    font-size: 20px;
    margin-bottom: 16px;
  }
  .el-button {
    font-size: 14px;
    padding: 10px 20px; /* Adjust the padding for small screens */
  }
}
</style>