import { api } from './api'
import type { FitnessMetrics, ACWRResult, MultiSportPMC, WeeklySummary } from '@/types/metrics'

export const metricsService = {
  async getAll(): Promise<FitnessMetrics[]> {
    const response = await api.get('/metrics')
    return response.data
  },

  async getLatest(): Promise<FitnessMetrics[]> {
    const response = await api.get('/metrics/latest')
    return response.data
  },

  async getACWR(): Promise<ACWRResult> {
    const response = await api.get('/advanced/acwr')
    return response.data
  },

  async getPMCBySport(): Promise<MultiSportPMC> {
    const response = await api.get('/advanced/pmc-by-sport')
    return response.data
  },

  async getWeeklySummary(): Promise<WeeklySummary> {
    const response = await api.get('/workouts/summary')
    return response.data
  },
}
