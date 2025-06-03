<template>
  <div class="device-control-container">
    <!-- Title at the top of the page -->
    <h2 style="text-align: center; margin-top: 20px; margin-bottom: 20px; font-weight: bold;">
      Device Control
    </h2>

    <!-- Manual mode switching -->
    <el-switch
      v-model="manualMode"
      active-text="Manual Mode"
      inactive-text="Auto Mode"
      @change="toggleManualMode"
    />

    <!-- First row: Lighting and Water Heater -->
    <el-row :gutter="20" class="device-grid">
      <!-- Top Left - Lighting Control -->
      <el-col :span="12">
        <el-card shadow="hover" style="min-height: 320px;">
          <h3>Lighting Control</h3>
          <p><strong>Status:</strong> {{ lightingStatus }}</p>
          <el-button type="success" @click="controlDevice('lighting', 'brighter')" :disabled="!manualMode">Brighter</el-button>
          <el-button type="warning" @click="controlDevice('lighting', 'dimmer')" :disabled="!manualMode">Dimmer</el-button>
          <el-button type="danger" @click="controlDevice('lighting', 'off')" :disabled="!manualMode">Turn Off</el-button>
          <el-button type="primary" @click="viewDeviceData('lighting')" style="margin-left: 10px">View Data</el-button>

          <div v-if="showLightingData" class="device-data-box">
            <h4>Latest Data:</h4>
            <el-table :data="convertToTableFormat(lightingData)" border style="width: 100%; font-size: 13px;">
              <el-table-column prop="key" label="Field" width="180"></el-table-column>
              <el-table-column prop="value" label="Value"></el-table-column>
            </el-table>
            <el-button type="primary" size="mini" @click="refreshDeviceData('lighting')">Refresh</el-button>
            <el-button type="danger" size="mini" @click="closeDeviceData('lighting')" style="margin-left: 5px;">Close</el-button>
          </div>
        </el-card>
      </el-col>

      <!-- Top right - water heater -->
      <el-col :span="12">
        <el-card shadow="hover" style="min-height: 320px;">
          <h3>Water Heater</h3>
          <p><strong>Status:</strong> {{ waterHeaterStatus }}</p>
          <el-button type="primary" @click="toggleHeater" :disabled="!manualMode">{{ heaterButtonText }}</el-button>
          <el-button type="primary" @click="viewDeviceData('water_heater')" style="margin-left: 10px">View Data</el-button>

          <div v-if="showWaterHeaterData" class="device-data-box">
            <h4>Latest Data:</h4>
            <el-table :data="convertToTableFormat(waterHeaterData)" border style="width: 100%; font-size: 13px;">
              <el-table-column prop="key" label="Field" width="180"></el-table-column>
              <el-table-column prop="value" label="Value"></el-table-column>
            </el-table>
            <el-button type="primary" size="mini" @click="refreshDeviceData('water_heater')">Refresh</el-button>
            <el-button type="danger" size="mini" @click="closeDeviceData('water_heater')" style="margin-left: 5px;">Close</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Second row: Camera and Air Conditioner -->
    <el-row :gutter="20" class="device-grid">
      <!-- Bottom left - Camera -->
      <el-col :span="12">
        <el-card shadow="hover" style="min-height: 320px;">
          <h3>Surveillance Camera</h3>
          <p><strong>Status:</strong> {{ manualMode ? cameraStatus : "N/A" }}</p>

          <el-button type="primary" @click="enableCamera" :disabled="!manualMode || cameraStatus === 'on'">Enable Camera</el-button>
          <el-button type="danger" @click="disableCamera" :disabled="!manualMode || cameraStatus === 'off'" style="margin-left: 5px">Stop Camera</el-button>
          <el-button type="primary" @click="viewDeviceData('camera')" style="margin-left: 5px">View Data</el-button>

          <div v-if="cameraStatus === 'on'" class="camera-video-box">
            <video ref="cameraVideo" autoplay muted playsinline style="width: 100%; border-radius: 6px; margin-top: 10px;"></video>
          </div>

          <div v-if="showCameraData" class="device-data-box">
            <h4>Latest Data:</h4>
            <el-table :data="convertToTableFormat(cameraData)" border style="width: 100%; font-size: 13px;">
              <el-table-column prop="key" label="Field" width="180"></el-table-column>
              <el-table-column prop="value" label="Value"></el-table-column>
            </el-table>
            <el-button type="primary" size="mini" @click="refreshDeviceData('camera')">Refresh</el-button>
            <el-button type="danger" size="mini" @click="closeDeviceData('camera')" style="margin-left: 5px;">Close</el-button>
          </div>
        </el-card>
      </el-col>

      <!-- Bottom right - air conditioning -->
      <el-col :span="12">
        <el-card shadow="hover" style="min-height: 320px;">
          <h3>Air Conditioner</h3>
          <p><strong>Cooling:</strong> {{ manualMode ? coolingStatus : "N/A" }}</p>
          <p><strong>Dehumidifying:</strong> {{ manualMode ? dehumidifyingStatus : "N/A" }}</p>

          <div style="margin-bottom: 10px;">
            <el-button type="success" size="mini" @click="setCooling('ON')" :disabled="!manualMode">Cooling (On)</el-button>
            <el-button type="warning" size="mini" @click="setCooling('OFF')" :disabled="!manualMode" style="margin-left: 5px;">Cooling (Off)</el-button>
            <el-button type="success" size="mini" @click="setDehumidifying('ON')" :disabled="!manualMode" style="margin-left: 5px;">Dehumidifying (On)</el-button>
            <el-button type="warning" size="mini" @click="setDehumidifying('OFF')" :disabled="!manualMode" style="margin-left: 5px;">Dehumidifying (Off)</el-button>
          </div>

          <el-button type="primary" @click="viewDeviceData('aircon')">View Data</el-button>

          <div v-if="showAirData" class="device-data-box">
            <h4>Latest Data:</h4>
            <el-table :data="convertToTableFormat(airConditionerData)" border style="width: 100%; font-size: 13px;">
              <el-table-column prop="key" label="Field" width="180"></el-table-column>
              <el-table-column prop="value" label="Value"></el-table-column>
            </el-table>
            <el-button type="primary" size="mini" @click="refreshDeviceData('aircon')">Refresh</el-button>
            <el-button type="danger" size="mini" @click="closeDeviceData('aircon')" style="margin-left: 5px;">Close</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- The back button is fixed in the bottom left corner -->
    <el-button class="back-button" type="info" @click="goBack">
      Back to Home
    </el-button>
  </div>
</template>




<script>
import axios from "axios";

export default {
  data() {
    return {
      manualMode: false,
      lightingStatus: "N/A",
      waterHeaterStatus: "N/A",
      heaterButtonText: "Turn On",
      statusMapping: {
        brighter: "BRIGHTER",
        dimmer: "DIMMER",
        off: "OFF",
        on: "ON",
      },
        dialogVisible: false,
        deviceData: {},
        currentDevice: "",
        lightingData: {},
        waterHeaterData: {},
        cameraStatus: "N/A",
        cameraData: {},
        showCameraData: false,
        cameraStream: null,
        showLightingData: false,
        showWaterHeaterData: false,
        coolingStatus: "N/A",
        dehumidifyingStatus: "N/A",
        airConditionerData: {},
        showAirData: false,
        fixedStatus: {
           lighting: null,
           water_heater: null
      }
    };
  },
  methods: {
    toggleManualMode() {
  console.log(`[Mode Switch] The current mode: ${this.manualMode ? 'Manual' : 'Auto'}`);

  if (!this.manualMode) {
    // Switch to automatic mode
    console.log("[Switch to Auto Mode] status is reset to N/A");

    // All device status resets
    this.lightingStatus = "N/A";
    this.waterHeaterStatus = "N/A";
    this.coolingStatus = "N/A";
    this.dehumidifyingStatus = "N/A";
    this.heaterButtonText = "Turn On";

    // Clear the local storage
    localStorage.setItem("manualMode", "false");
    localStorage.removeItem("lightingStatus");
    localStorage.removeItem("waterHeaterStatus");
    localStorage.removeItem("coolingStatus");
    localStorage.removeItem("dehumidifyingStatus");

    // Clear the fixed display status
    this.fixedStatus = {
      lighting: null,
      water_heater: null
    };

    // Sync backend: Switch to automatic mode
    axios.post("http://localhost:5050/api/device/toggle-mode", {
      manual_mode: "off"
    })
    .then((response) => {
      console.log("[Backend Sync] switches to automatic mode:", response.data.message);
    })
    .catch((error) => {
      console.error("[Error] Failed to switch to automatic mode:", error);
    });

  } else {
    // Switch to manual mode
    console.log("[Switch to Manual Mode] Restore the state of local storage");

    // Restore the lights and water heater status
    const lightingState = localStorage.getItem("lightingStatus");
    const heaterState = localStorage.getItem("waterHeaterStatus");

    this.lightingStatus = lightingState ? lightingState : "OFF";
    this.waterHeaterStatus = heaterState ? heaterState : "OFF";
    this.heaterButtonText = this.waterHeaterStatus === "ON" ? "Turn Off" : "Turn On";

    // Restore the cooling / dehumidifying state of the air conditioner
    const coolingState = localStorage.getItem("coolingStatus");
    const dehumidifyState = localStorage.getItem("dehumidifyingStatus");

    this.coolingStatus = coolingState ? coolingState : "OFF";
    this.dehumidifyingStatus = dehumidifyState ? dehumidifyState : "OFF";

    // Write to local storage
    localStorage.setItem("manualMode", "true");
    localStorage.setItem("lightingStatus", this.lightingStatus);
    localStorage.setItem("waterHeaterStatus", this.waterHeaterStatus);
    localStorage.setItem("coolingStatus", this.coolingStatus);
    localStorage.setItem("dehumidifyingStatus", this.dehumidifyingStatus);

    // Initialise Fixed Display State (for View Data)
    this.updateFixedStatus("lighting", this.lightingStatus);
    this.updateFixedStatus("water_heater", this.waterHeaterStatus);

    // Sync backend: Switch to manual mode
    axios.post("http://localhost:5050/api/device/toggle-mode", {
      manual_mode: "on"
    })
    .then((response) => {
      console.log("[Backend Sync] Switch to manual mode:", response.data.message);
    })
    .catch((error) => {
      console.error("[Error] Failed to switch to manual mode.:", error);
    });
  }
},
convertToTableFormat(data) {
  if (!data || typeof data !== 'object') return [];
  return Object.entries(data).map(([key, value]) => ({
    key,
    value: typeof value === 'object' ? JSON.stringify(value) : value
  }));
},

setCooling(state) {
  this.coolingStatus = state;
  localStorage.setItem("coolingStatus", state);
  this.syncCurrentState("aircon", `COOLING_${state}`);
},

setDehumidifying(state) {
  this.dehumidifyingStatus = state;
  localStorage.setItem("dehumidifyingStatus", state);
  this.syncCurrentState("aircon", `DEHUMIDIFYING_${state}`);
},
enableCamera() {
  if (!this.manualMode || this.cameraStatus === "on") return;

  navigator.mediaDevices.getUserMedia({ video: true })
    .then((stream) => {
      this.cameraStream = stream;
      this.cameraStatus = "on";

      // It does not enforce the control of showCameraData, only the camera state.
      this.$nextTick(() => {
        const video = this.$refs.cameraVideo;
        if (video) {
          video.srcObject = stream;
          video.play();
        } else {
          console.warn("cameraVideo ref not found — video element not rendered yet.");
        }
      });

      // axios.post("http://localhost:5050/api/device/camera/start");
    })
    .catch((err) => {
      console.error("Failed to enable camera:", err);
    });
},

disableCamera() {
  if (this.cameraStream) {
    this.cameraStream.getTracks().forEach(track => track.stop());
    this.cameraStream = null;
  }

  this.cameraStatus = "off";

  // Clear the video screen
  if (this.$refs.cameraVideo) {
    this.$refs.cameraVideo.srcObject = null;
  }

  // Don't turn off showCameraData, so that the View Data block can be controlled separately.
},


viewDeviceData(device) {
  if (device === "camera") {
    axios.get("http://localhost:5050/api/device/camera/manual-state")
      .then((stateRes) => {
        const manual = stateRes.data.manual_override;

        axios.get("http://localhost:5050/api/realtime-db/fps")
          .then((res) => {
            const data = res.data;
            data.status = manual === "on" ? this.cameraStatus : "N/A";
            this.cameraData = data;
            this.showCameraData = true;
          });
      });
    return;
  }

  // The air conditioner is forced to use a fixed interface path to avoid dynamic splicing errors.
  const url = device === "aircon"
    ? "http://localhost:5050/api/device/aircon/view-data"
    : `http://localhost:5050/api/device/${device}/view-data`;

  axios.get(url)
    .then((response) => {
      const originalData = response.data;

      axios.get(`http://localhost:5050/api/device/${device}/manual-state`)
        .then((stateRes) => {
          const status = stateRes.data.status;
          const manual = stateRes.data.manual_override;

          if (device === "lighting" && manual === "on") {
            this.updateFixedStatus(device, status);
            originalData.status = this.fixedStatus.lighting;
          }

          if (device === "water_heater" && manual === "on") {
            this.updateFixedStatus(device, status);
            originalData.status = this.fixedStatus.water_heater;
          }

          if (device === "aircon" && manual === "on") {
            originalData.cooling_status = this.coolingStatus;
            originalData.dehumidifying_status = this.dehumidifyingStatus;
          }

          if (device === "lighting") {
            this.lightingData = originalData;
            this.showLightingData = true;
          } else if (device === "water_heater") {
            this.waterHeaterData = originalData;
            this.showWaterHeaterData = true;
          } else if (device === "aircon") {
            this.airConditionerData = originalData;
            this.showAirData = true;
          }
        });
    });
},


refreshDeviceData(device) {
  if (device === "camera") {
    this.viewDeviceData("camera");
    return;
  }

  const url = device === "aircon"
    ? "http://localhost:5050/api/device/aircon/view-data"
    : `http://localhost:5050/api/device/${device}/view-data`;

  axios.get(url)
    .then((response) => {
      const refreshed = response.data;

      axios.get(`http://localhost:5050/api/device/${device}/manual-state`)
        .then((res) => {
          const manual = res.data.manual_override;
          const status = res.data.status;

          if (manual === "on") {
            this.updateFixedStatus(device, status);

            if (device === "lighting") {
              refreshed.status = this.fixedStatus.lighting;
            } else if (device === "water_heater") {
              refreshed.status = this.fixedStatus.water_heater;
            } else if (device === "aircon") {
              refreshed.cooling_status = this.coolingStatus;
              refreshed.dehumidifying_status = this.dehumidifyingStatus;
            }
          }

          if (device === "lighting") {
            this.lightingData = refreshed;
          } else if (device === "water_heater") {
            this.waterHeaterData = refreshed;
          } else if (device === "aircon") {
            this.airConditionerData = refreshed;
          }
        });
    });
},
syncLightingStatus() {
  axios.get("http://localhost:5050/api/device/lighting/manual-state")
    .then((res) => {
      const status = res.data.status;
      const manual = res.data.manual_override;
      if (manual === "on") {
        this.updateFixedStatus("lighting", status);
        this.lightingStatus = status;  // Use the original state displayed in the box.
      }
    });
},

syncWaterHeaterStatus() {
  axios.get("http://localhost:5050/api/device/water_heater/manual-state")
    .then((res) => {
      const status = res.data.status;
      const manual = res.data.manual_override;
      if (manual === "on") {
        this.updateFixedStatus("water_heater", status);
        this.waterHeaterStatus = status;  // Use the original state displayed in the box.
        this.heaterButtonText = status === "ON" ? "Turn Off" : "Turn On";
      }
    });
},


  syncAirconStatus() {
    axios.get("http://localhost:5050/api/device/aircon/manual-state")
      .then((res) => {
        const manual = res.data.manual_override;
        if (manual === "on") {
          this.coolingStatus = res.data.cooling_status || "ON";
          this.dehumidifyingStatus = res.data.dehumidifying_status || "ON";
        }
      });
  },

updateFixedStatus(device, status) {
  if (device === "lighting") {
    if (status === "BRIGHTER") {
      this.fixedStatus.lighting = "on (Brighter)";
    } else if (status === "DIMMER") {
      this.fixedStatus.lighting = "on (Dimmer)";
    } else if (status === "OFF") {
      this.fixedStatus.lighting = "off";
    }
  } else if (device === "water_heater") {
    if (status === "ON") {
      this.fixedStatus.water_heater = "running";
    } else if (status === "OFF") {
      this.fixedStatus.water_heater = "stopped";
    }
  }
},


closeDeviceData(device) {
  if (device === "lighting") {
    this.showLightingData = false;
  } else if (device === "water_heater") {
    this.showWaterHeaterData = false;
  } else if (device === "camera") {
    this.showCameraData = false;
  } else if (device === "aircon") {
    this.showAirData = false;
  }
},


    controlDevice(device, action) {
      axios
        .post(`http://localhost:5050/api/device/${device}/${action}`)
        .then(() => {
          if (device === "lighting") {
            this.lightingStatus = this.statusMapping[action] || "OFF";
          } else if (device === "water_heater") {
            this.waterHeaterStatus = this.statusMapping[action] || "OFF";
          }

          if (this.manualMode) {
            this.syncCurrentState(device, action);
          }
        })
        .catch((error) => {
          console.error(`Failed to control ${device}:`, error);
        });
    },
    syncCurrentState(device, action) {
      axios.post(`http://localhost:5050/api/device/${device}/save-state`, {
        status: action,
        mode: this.manualMode ? "on" : "off"
      })
      .then(() => {
        console.log(`State synced for ${device}: ${action}, Mode: ${this.manualMode ? "Manual" : "Auto"}`);
      })
      .catch((error) => {
        console.error("Failed to sync state:", error);
      });
    },
    toggleHeater() {
      const action = this.waterHeaterStatus === "OFF" || this.waterHeaterStatus === "N/A" ? "on" : "off";
      this.controlDevice("water_heater", action);

      // Toggle button text
      this.heaterButtonText = action === "on" ? "Turn Off" : "Turn On";
    },
    goBack() {
      this.$router.push('/home');
    }
  },
  mounted() {
  console.log("[Initialise] Synchronise manual mode and device status.");

  axios.get("http://localhost:5050/api/device/water_heater/current-status")
    .then((response) => {
      const { manual_mode, status } = response.data;

      // Recovery mode
      this.manualMode = manual_mode === "on";

      if (!this.manualMode) {
        // If it's auto mode
        this.lightingStatus = "N/A";
        this.waterHeaterStatus = "N/A";
        this.coolingStatus = "N/A";
        this.dehumidifyingStatus = "N/A";
        this.heaterButtonText = "Turn On";
      } else {
        // Automatically synchronises the current manual state.
        this.syncLightingStatus();
        this.syncWaterHeaterStatus();
        this.syncAirconStatus();
      }

      console.log(`[Mode Sync] The current mode: ${manual_mode}, Water heater status: ${status}`);
    })
    .catch((error) => {
      console.error("[Error] Failed to get device status: ", error);
    });
},


};
</script>

<style scoped>
.device-control-container {
  padding: 20px;
  min-height: 140vh; /* Make two rows of cards large enough to expand. */
  box-sizing: border-box;
}

.device-grid {
  margin-top: 20px;
}

.back-button {
  position: fixed;
  bottom: 20px;
  left: 20px;
}

/* Data display area for all devices */
.device-data-box {
  background-color: #ffffff;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 10px;
  margin-top: 10px;
  font-size: 13px;
  max-height: 260px;
  overflow-y: auto;
}

/* Beautify the table display fields. */
.device-data-box .el-table {
  font-size: 13px;
}

.device-data-box .el-table td,
.device-data-box .el-table th {
  padding: 4px 8px;
  font-family: monospace;
  white-space: nowrap;
}

/* Uniform height for all common device cards (including after expanding View Data) */
.el-card {
  min-height: 580px; /* Consistent with the camera to prevent post-click propping up or misalignment. */
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* Camera card class name (can be styled separately) */
.camera-card {
  min-height: 580px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

/* Camera video display area (heightened) */
.camera-video-box {
  margin-top: 10px;
  overflow: hidden;
  border: 1px solid #ccc;
  border-radius: 6px;
  height: 360px;
}

/* The video fills the container but does not stretch */
.camera-video-box video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Responsive order (cameras below) */
@media (min-width: 768px) {
  .camera-col {
    order: 2;
  }
  .heater-col {
    order: 1;
  }
}
</style>








  
  
  
  
  
  
  