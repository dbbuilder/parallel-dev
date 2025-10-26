<template>
  <div class="dashboard container">
    <div class="dashboard-summary card">
      <h2>Summary</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">Total Projects</div>
          <div class="stat-value">{{ summary.total_projects || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Total Tasks</div>
          <div class="stat-value">{{ summary.total_tasks || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Total Requirements</div>
          <div class="stat-value">{{ summary.total_requirements || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Overall Completion</div>
          <div class="stat-value">{{ formatPercentage(summary.overall_completion) }}</div>
        </div>
      </div>
    </div>

    <div class="projects-section">
      <h2>Projects</h2>
      <div v-if="loading" class="loading">Loading projects...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="projects.length === 0" class="empty">No projects found</div>
      <div v-else class="projects-grid">
        <div v-for="project in projects" :key="project.id" class="project-card card">
          <h3>{{ project.name }}</h3>
          <p class="project-path">{{ project.path }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api.js'

const summary = ref({})
const projects = ref([])
const loading = ref(true)
const error = ref(null)

const formatPercentage = (value) => {
  return value ? `${value.toFixed(1)}%` : '0.0%'
}

const loadDashboard = async () => {
  try {
    loading.value = true
    error.value = null
    const data = await api.getDashboard()
    summary.value = data.summary
    projects.value = data.projects
  } catch (err) {
    error.value = 'Failed to load dashboard data'
    console.error('Dashboard load error:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.dashboard {
  padding: 30px 20px;
}

.dashboard-summary {
  margin-bottom: 30px;
}

.dashboard-summary h2 {
  margin-bottom: 20px;
  font-size: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #667eea;
}

.projects-section h2 {
  margin-bottom: 20px;
  font-size: 24px;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.project-card h3 {
  margin-bottom: 8px;
  font-size: 18px;
  color: #333;
}

.project-path {
  font-size: 12px;
  color: #666;
  font-family: monospace;
}

.loading,
.error,
.empty {
  padding: 40px;
  text-align: center;
  color: #666;
}

.error {
  color: #dc3545;
}
</style>
