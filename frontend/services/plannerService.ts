import { MOCK_DASHBOARD_DATA, DashboardMetrics } from '@/mock/dashboard'

export const plannerService = {
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    // Simulated network latency
    await new Promise((resolve) => setTimeout(resolve, 150))
    return { ...MOCK_DASHBOARD_DATA }
  },
}
