<template>
  <div id="app">
    <header class="app-header">
      <h1>ParallelDev</h1>
      <p>Development Project Manager</p>
    </header>

    <Dashboard />
  </div>
</template>

<script setup>
import Dashboard from './components/Dashboard.vue'
</script>

<style scoped>
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  font-size: 32px;
  margin-bottom: 8px;
}

.app-header p {
  font-size: 14px;
  opacity: 0.9;
}
</style>
