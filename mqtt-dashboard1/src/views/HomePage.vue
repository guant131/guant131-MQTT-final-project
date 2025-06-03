<template>
  <div class="home-container">
    <el-card class="welcome-card">
      <h1>Welcome to the Smart Home System</h1>
      <p class="description">Monitor and manage your IoT devices easily and securely.</p>
      <div class="quick-links">
        <el-button type="primary" @click="$router.push('/mqtt')">Go to Dashboard</el-button>
        <el-button type="info" @click="$router.push('/personal-data')">View Personal Data</el-button>
        <el-button type="danger" @click="logout">Logout</el-button>
      </div>
    </el-card>

    <el-row :gutter="20" class="feature-grid">
      <el-col :span="8">
        <div class="clickable-wrapper" @click="goToRealTimeStatus">
          <el-card class="clickable-card" shadow="hover">
            <h3>Real-time Monitoring</h3>
            <p>Stay updated with live sensor data from your smart home environment.</p>
          </el-card>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="clickable-wrapper" @click="goToDeviceControl">
          <el-card class="clickable-card" shadow="hover">
            <h3>Device Control</h3>
            <p>Send commands and interact with your connected devices instantly.</p>
          </el-card>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="clickable-wrapper" @click="goToDataHistory">
          <el-card class="clickable-card" shadow="hover">
            <h3>Data History</h3>
            <p>Visualize and analyze historical data to identify trends and insights.</p>
          </el-card>
        </div>
      </el-col>
    </el-row>

    <!-- Intelligent AI mini - buoy -->
    <div class="ai-float-icon" @click="toggleChatWindow">
      <img src="@/assets/生成机器人浮标图标.png" alt="AI Icon" style="width: 100%; height: 100%; border-radius: 50%;">
    </div>

    <!-- Intelligent AI floating window -->
    <div class="ai-chat-window" v-if="isChatWindowVisible">
      <div class="chat-header">
        <h2>Smart Home Assistant</h2>
      </div>
      <div class="chat-messages" ref="chatMessages">
        <!-- Show the communication message -->
        <div
          v-for="(message, index) in chatMessages"
          :key="index"
          :class="message.sender === 'user' ? 'user-message' : 'ai-message'"
        >
          <div class="message-bubble">{{ message.content }}</div>
        </div>
      </div>
      <div class="chat-input">
        <el-input
          v-model="userInput"
          placeholder="Ask me about your smart home devices..."
          @keyup.enter="sendMessage"
        ></el-input>
        <el-button @click="sendMessage">Send</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'HomePage',
  data() {
    return {
      userInput: '',
      chatMessages: [],
      isChatWindowVisible: false,
      apiKey: 'a104e834-a3c5-4760-a819-2e4dd8de484d',
      modelId: 'doubao-1-5-thinking-pro-250415',
      apiUrl: 'https://ark.cn-beijing.volces.com/api/v3/chat/completions'
    };
  },
  async mounted() {
    try {
      const requestData = {
        model: this.modelId,
        messages: [
          {
            role: 'system',
            content: 'You are a smart home assistant. Say hello to the user and introduce. Answer in English.'
          }
        ]
      };
      console.log('Sending initial request data:', requestData);

      const response = await axios.post(this.apiUrl, requestData, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        }
      });

      console.log('Received initial response:', response.data);

      const aiReply = response.data.choices[0].message.content;
      this.chatMessages.push({ sender: 'ai', content: aiReply });
    } catch (error) {
      console.error('Initial API call failed:', error);
      if (error.response) {
        console.error('Response data:', error.response.data);
        console.error('Response status:', error.response.status);
        console.error('Response headers:', error.response.headers);
      } else if (error.request) {
        console.error('No response received:', error.request);
      } else {
        console.error('Error setting up the request:', error.message);
      }
      this.chatMessages.push({
        sender: 'ai',
        content: 'Sorry, the service is temporarily unavailable. Please try again later.'
      });
    } finally {
      this.$nextTick(() => {
        this.$refs.chatMessages.scrollTop = this.$refs.chatMessages.scrollHeight;
      });
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('loggedIn');
      this.$router.push('/login');
    },
    goToRealTimeStatus() {
      console.log('Navigating to real-time status...');
      if (this.$route.path !== '/real-time-status') {
        this.$router.push('/real-time-status');
      }
    },
    goToDataHistory() {
      if (this.$route.path !== '/data-history') {
        this.$router.push('/data-history');
      }
    },
    goToDeviceControl() {
      if (this.$route.path !== '/device-control') {
        this.$router.push('/device-control');
      }
    },
    toggleChatWindow() {
      this.isChatWindowVisible = !this.isChatWindowVisible;
    },
    async sendMessage() {
      if (!this.userInput.trim()) return;

      this.chatMessages.push({ sender: 'user', content: this.userInput });

      try {
        const requestData = {
          model: this.modelId,
          messages: [
            { role: 'system', content: 'You are a smart home assistant. Answer all questions in English regarding device control and data query.' },
            { role: 'user', content: this.userInput }
          ]
        };
        console.log('Sending request data:', requestData);

        const response = await axios.post(this.apiUrl, requestData, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.apiKey}`
          }
        });

        console.log('Received response:', response.data);

        const aiReply = response.data.choices[0].message.content;
        this.chatMessages.push({ sender: 'ai', content: aiReply });
      } catch (error) {
        console.error('Doubao API call failed:', error);
        if (error.response) {
          console.error('Response data:', error.response.data);
          console.error('Response status:', error.response.status);
          console.error('Response headers:', error.response.headers);
        } else if (error.request) {
          console.error('No response received:', error.request);
        } else {
          console.error('Error setting up the request:', error.message);
        }
        this.chatMessages.push({
          sender: 'ai',
          content: 'Sorry, the service is temporarily unavailable. Please try again later.'
        });
      } finally {
        this.userInput = '';
        this.$nextTick(() => {
          this.$refs.chatMessages.scrollTop = this.$refs.chatMessages.scrollHeight;
        });
      }
    }
  }
};
</script>

<style scoped>
.home-container {
  padding: 40px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.welcome-card {
  text-align: center;
  padding: 30px;
  margin-bottom: 40px;
}
.description {
  font-size: 18px;
  color: #666;
  margin-bottom: 20px;
}
.quick-links {
  display: flex;
  justify-content: center;
  gap: 20px;
}
.feature-grid {
  margin-top: 30px;
}
.el-card h3 {
  margin-bottom: 10px;
}
.clickable-wrapper {
  cursor: pointer;
}
.clickable-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
}

/* AI 浮标和窗口样式 */
.ai-float-icon {
  position: fixed;
  right: 20px;
  bottom: 20px;
  width: 56px;
  height: 56px;
  background: #409eff;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 24px;
  color: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s;
}

.ai-float-icon:hover {
  transform: scale(1.05);
}

.ai-chat-window {
  position: fixed;
  right: 20px;
  bottom: 80px;
  width: 350px;
  height: 420px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  background: white;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
}

.chat-header h2 {
  margin: 0;
  font-size: 18px;
  color: #409eff; /* 蓝色字体 */
  text-align: center; /* 居中 */
}

.chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.user-message {
  text-align: right;
  margin: 8px 0;
}

.ai-message {
  text-align: left;
  margin: 8px 0;
}

.message-bubble {
  display: inline-block;
  padding: 8px 12px;
  border-radius: 8px;
  max-width: 70%;
}

.user-message .message-bubble {
  background-color: #e1f5fe;
  color: #333;
}

.ai-message .message-bubble {
  background-color: #f1f3f4;
  color: #303133;
}

.chat-input {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  gap: 8px;
}

.chat-input el-input {
  flex: 1;
  border-radius: 4px;
  box-shadow: none;
}
</style>