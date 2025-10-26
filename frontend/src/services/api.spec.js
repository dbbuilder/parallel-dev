/**
 * Tests for API client service
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import axios from 'axios'
import api from './api.js'

// Mock axios
vi.mock('axios')

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getProjects', () => {
    it('should fetch all projects', async () => {
      const mockProjects = [
        { id: 1, name: 'Project 1', path: '/test/path1' },
        { id: 2, name: 'Project 2', path: '/test/path2' }
      ]

      axios.get.mockResolvedValue({
        data: {
          status: 'success',
          data: mockProjects
        }
      })

      const result = await api.getProjects()

      expect(axios.get).toHaveBeenCalledWith('/api/projects')
      expect(result).toEqual(mockProjects)
    })

    it('should handle errors when fetching projects', async () => {
      axios.get.mockRejectedValue(new Error('Network error'))

      await expect(api.getProjects()).rejects.toThrow('Network error')
    })
  })

  describe('getProject', () => {
    it('should fetch a single project by ID', async () => {
      const mockProject = {
        id: 1,
        name: 'Test Project',
        path: '/test/path',
        tasks: [],
        requirements: []
      }

      axios.get.mockResolvedValue({
        data: {
          status: 'success',
          data: mockProject
        }
      })

      const result = await api.getProject(1)

      expect(axios.get).toHaveBeenCalledWith('/api/projects/1')
      expect(result).toEqual(mockProject)
    })
  })

  describe('getProjectMetrics', () => {
    it('should fetch metrics for a project', async () => {
      const mockMetrics = {
        project_id: 1,
        metrics: {
          total_tasks: 10,
          completed_tasks: 5,
          completion_percentage: 50.0
        }
      }

      axios.get.mockResolvedValue({
        data: {
          status: 'success',
          data: mockMetrics
        }
      })

      const result = await api.getProjectMetrics(1)

      expect(axios.get).toHaveBeenCalledWith('/api/projects/1/metrics')
      expect(result).toEqual(mockMetrics)
    })
  })

  describe('getDashboard', () => {
    it('should fetch dashboard data', async () => {
      const mockDashboard = {
        summary: {
          total_projects: 5,
          total_tasks: 50,
          overall_completion: 60.0
        },
        projects: []
      }

      axios.get.mockResolvedValue({
        data: {
          status: 'success',
          data: mockDashboard
        }
      })

      const result = await api.getDashboard()

      expect(axios.get).toHaveBeenCalledWith('/api/dashboard')
      expect(result).toEqual(mockDashboard)
    })
  })

  describe('triggerScan', () => {
    it('should trigger a directory scan', async () => {
      const mockResponse = {
        projects_found: 3,
        projects_added: 3
      }

      axios.post.mockResolvedValue({
        data: {
          status: 'success',
          data: mockResponse
        }
      })

      const result = await api.triggerScan('/test/directory')

      expect(axios.post).toHaveBeenCalledWith('/api/scan', {
        directory: '/test/directory'
      })
      expect(result).toEqual(mockResponse)
    })

    it('should handle scan errors', async () => {
      axios.post.mockRejectedValue(new Error('Invalid directory'))

      await expect(api.triggerScan('/invalid')).rejects.toThrow('Invalid directory')
    })
  })

  describe('getHealth', () => {
    it('should check API health', async () => {
      const mockHealth = {
        status: 'healthy',
        timestamp: '2025-10-25T12:00:00'
      }

      axios.get.mockResolvedValue({
        data: mockHealth
      })

      const result = await api.getHealth()

      expect(axios.get).toHaveBeenCalledWith('/api/health')
      expect(result).toEqual(mockHealth)
    })
  })
})
