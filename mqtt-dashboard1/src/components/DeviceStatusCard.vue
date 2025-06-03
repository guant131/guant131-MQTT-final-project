<template>
    <el-card class="device-card">
      <div slot="header">{{ title }}</div>
      <p><strong>Status:</strong> {{ status.toUpperCase() }}</p>
      <el-button @click="$emit('toggle')" type="primary">
        {{ status === 'on' ? 'Turn Off' : 'Turn On' }}
      </el-button>
      <div v-if="title === 'Lighting Control'">
        <el-button @click="$emit('increase')" type="success">Brighter</el-button>
        <el-button @click="$emit('decrease')" type="warning">Dimmer</el-button>
        <el-button @click="$emit('turnOff')" type="danger">Turn Off</el-button>
      </div>
    </el-card>
  </template>
  
  <script>
  export default {
    props: {
      title: String,
      status: String
    }
  };
  </script>
  
  <style scoped>
  .device-card {
    padding: 10px;
    background-color: #f9f9f9;
  }
  </style>
  