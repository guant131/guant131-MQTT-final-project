<template>
  <el-card class="device-card">
    <div slot="header">{{ title }}</div>
    <p><strong>Status:</strong> {{ status.toUpperCase() }}</p>

    <!-- Control button -->
    <el-button @click="$emit('toggle')" type="primary">
      {{ status === 'on' ? 'Turn Off' : 'Turn On' }}
    </el-button>

    <div v-if="title === 'Lighting Control'">
      <el-button @click="$emit('increase')" type="success">Brighter</el-button>
      <el-button @click="$emit('decrease')" type="warning">Dimmer</el-button>
      <el-button @click="$emit('turnOff')" type="danger">Turn Off</el-button>
    </div>

    <!-- Show the new data -->
    <h4>Latest Data:</h4>
    <pre>{{ JSON.stringify(deviceData, null, 2) }}</pre>
  </el-card>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      required: true
    },
    status: {
      type: String,
      required: true
    },
    deviceData: {
      type: Object,
      default: () => ({})
    }
  }
};
</script>

<style scoped>
.device-card {
  padding: 10px;
  background-color: #f9f9f9;
  margin-bottom: 10px;
  border-radius: 8px;
  border: 1px solid #ddd;
}
</style>
