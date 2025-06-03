<template>
  <div class="container">
    <!-- MQTT Connection Configuration -->
    <el-card class="card-section">
      <div slot="header">
        <el-icon><i class="el-icon-link"></i></el-icon> MQTT Connection Configuration
      </div>
      <el-form :model="mqttOptions" inline label-width="90px">
        <el-form-item label="Broker">
          <el-input v-model="mqttOptions.brokerUrl" placeholder="127.0.0.1"></el-input>
        </el-form-item>
        <el-form-item label="Port">
          <el-input v-model.number="mqttOptions.port" placeholder="9001"></el-input>
        </el-form-item>
        <el-form-item label="Client ID">
          <el-input v-model="mqttOptions.clientId"></el-input>
        </el-form-item>
        <el-form-item class="button-container">
          <el-button type="primary" @click="connectToMqtt" class="connect-button">Connect</el-button>
          <el-tag :type="isConnected? 'success' : 'danger'" effect="dark" class="status-tag">
            {{ isConnected? 'Connected' : 'Not Connected' }}
          </el-tag>
        </el-form-item>
      </el-form>
    </el-card>
    <!-- Subscription Topic -->
    <el-card class="card-section">
      <div slot="header">
        <el-icon><i class="el-icon-s-promotion"></i></el-icon> Subscription Theme
      </div>
      <el-form inline>
        <el-form-item label="Topic">
          <el-select v-model="selectedTopic" placeholder="Select Topic">
            <el-option v-for="topic in availableTopics" :key="topic" :label="topic" :value="topic">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="success" @click="subscribeAndNavigate" :disabled="!isConnected">Subscribe</el-button>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchMessages" :disabled="!isConnected">Get Message</el-button>
        </el-form-item>
      </el-form>
      <div class="topic-tags">
        <el-tag v-for="topic in subscribedTopics" :key="topic" closable @close="removeTopic(topic)"
          @click="goToDevice(topic)" type="info" class="topic-tag">
          {{ topic }}
        </el-tag>
      </div>
    </el-card>
    <!-- Received Messages Table -->
    <el-card v-if="receivedMessages.length > 0" class="card-section">
      <div slot="header">
        <el-icon><i class="el-icon-message"></i></el-icon> Received Messages
      </div>
      <el-table :data="receivedMessages" border style="width: 100%">
        <el-table-column prop="topic" label="Topic" width="200" />
        <el-table-column prop="message" label="Message Content" />
      </el-table>
    </el-card>
    <!-- Subscribed Device Data (Clickable) -->
    <el-card v-for="(data, topic) in topicData" :key="topic" class="card-section shadow-card">
      <div slot="header">{{ topic }}</div>
      <el-table :data="Object.entries(data)" border stripe style="width: 100%">
        <el-table-column label="Field" prop="0" />
        <el-table-column label="Value" prop="1" />
        <el-table-column label="Action">
          <template>
            <el-button type="primary" size="mini" @click="goToDevice(topic)">View</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <!-- Child Route Page -->
    <router-view />
    <!-- Back Button -->
    <div class="back-container">
      <el-button type="primary" @click="goBack" round>Back</el-button>
    </div>
  </div>
</template>
<script>
import axios from 'axios'

export default {
  name: 'MqttDashboard',
  data() {
    return {
      mqttOptions: {
        brokerUrl: '127.0.0.1',
        port: 1884,
        clientId: 'vue-client-' + Math.random().toString(16).substr(2, 8)
      },
      isConnected: false,
      selectedTopic: '',
      availableTopics: ['device/temperature', 'device/water_heater','device/light_control', 'device/surveillance_camera'],  //李浩勋 王睿涵
      newTopic: '',
      topicData: {},
      subscribedTopics: [],
      receivedMessages: []
    }
  },
  methods: {
    connectToMqtt() {
      axios.post('http://127.0.0.1:5050/connect-mqtt', this.mqttOptions)
      .then(res => {
          this.isConnected = true
          console.log('Connection Successful:', res.data)
        })
      .catch(err => {
          console.error('Connection Failed:', err.response? err.response.data : err.message)
        })
    },
    subscribeAndNavigate() {
      if (!this.selectedTopic) return
      axios.post('http://127.0.0.1:5050/subscribe', { topic: this.selectedTopic })
      .then(res => {
          this.subscribedTopics.push(this.selectedTopic)
          console.log('Subscription Successful:', res.data)
          const deviceName = this.selectedTopic.split('/').pop()
          if (this.selectedTopic === 'device/temperature') {
            this.$router.push({ name: 'DevicePage', params: { deviceId: deviceName } })
          } else if (this.selectedTopic === 'device/water_heater') {
            this.$router.push({ name: 'WaterHeaterPage', params: { deviceId: deviceName } })
          }
           else if (this.selectedTopic === 'device/light_control') {          //李浩勋
            this.$router.push({ name: 'LightingControllerPage', params: { deviceId: deviceName } })
          }
          else if (this.selectedTopic === 'device/surveillance_camera') { 
            this.$router.push({ name: 'SurveillanceCameraPage', params: { deviceId: deviceName } })
          }
        })
      .catch(err => {
          console.error('Subscription Failed:', err)
        })
    },
    fetchMessages() {
      const topic = this.selectedTopic || this.subscribedTopics.slice(-1)[0]
      if (!topic) return
      const deviceId = topic.split('/').pop()
      axios.get(`http://127.0.0.1:5050/messages/${deviceId}`)
      .then(res => {
          this.receivedMessages = res.data.messages.map(msg => ({
            topic,
            message: typeof msg === 'string'? msg : JSON.stringify(msg)
          }))
        })
      .catch(err => {
          console.error('Failed to Fetch Messages:', err)
        })
    },
    removeTopic(topic) {
      this.subscribedTopics = this.subscribedTopics.filter(t => t!== topic)
      this.$delete(this.topicData, topic)
    },
    goToDevice(topic) {
      const deviceName = topic.split('/').pop()
      if (topic === 'device/temperature') {
        this.$router.push({ name: 'DevicePage', params: { deviceId: deviceName } })
      } else if (topic === 'device/water_heater') {
        this.$router.push({ name: 'WaterHeaterPage', params: { deviceId: deviceName } })
      }else if (topic === 'device/light_control') {       
        this.$router.push({ name: 'LightingControllerPage', params: { deviceId: deviceName } })
      }
      else if (topic === 'device/surveillance_camera') {
        this.$router.push({ name: 'SurveillanceCameraPage', params: { deviceId: deviceName } })
      }
    },
    goBack() {
      this.$router.push('/home')
    }
  }
}
</script>
<style scoped>
.container {
  padding: 20px;
}
.card-section {
  margin-bottom: 24px;
}
.topic-tag {
  margin: 6px 4px;
  cursor: pointer;
}
.shadow-card {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.topic-tags {
  margin-top: 10px;
}
.back-container {
  margin-top: 40px;
  text-align: center;
}
/* Center-align the Connect button and status tag */
.button-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}
.connect-button {
  margin-right: 10px;
}
.status-tag {
  height: 40px;
  line-height: 38px;
}
</style>