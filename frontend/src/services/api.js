/**
 * API Client Service
 * Handles all HTTP requests to the backend API
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = {
  /**
   * Get all projects
   * @returns {Promise<Array>} List of projects
   */
  async getProjects() {
    const response = await axios.get(`${API_BASE_URL}/projects`)
    return response.data.data
  },

  /**
   * Get a single project by ID
   * @param {number} id - Project ID
   * @returns {Promise<Object>} Project details
   */
  async getProject(id) {
    const response = await axios.get(`${API_BASE_URL}/projects/${id}`)
    return response.data.data
  },

  /**
   * Get metrics for a project
   * @param {number} id - Project ID
   * @returns {Promise<Object>} Project metrics
   */
  async getProjectMetrics(id) {
    const response = await axios.get(`${API_BASE_URL}/projects/${id}/metrics`)
    return response.data.data
  },

  /**
   * Get dashboard data
   * @returns {Promise<Object>} Dashboard data with summary and projects
   */
  async getDashboard() {
    const response = await axios.get(`${API_BASE_URL}/dashboard`)
    return response.data.data
  },

  /**
   * Trigger a directory scan
   * @param {string} directory - Directory path to scan
   * @returns {Promise<Object>} Scan results
   */
  async triggerScan(directory) {
    const response = await axios.post(`${API_BASE_URL}/scan`, { directory })
    return response.data.data
  },

  /**
   * Check API health
   * @returns {Promise<Object>} Health status
   */
  async getHealth() {
    const response = await axios.get(`${API_BASE_URL}/health`)
    return response.data
  }
}

export default api
