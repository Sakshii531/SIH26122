/**
 * Mock Infrastructure Projects Data
 */
export const MOCK_PROJECTS = [
  {
    id: 'PRJ-METRO-03',
    name: 'Metro Elevated Viaduct & Stations (Package 4)',
    code: 'MMRDA-ML3-P4',
    client: 'Mumbai Metropolitan Region Development Authority',
    contractor: 'L&T Infrastructure - Shapoorji Pallonji JV',
    location: 'Bandra-Kurla Complex to Seepz (14.2 km Viaduct)',
    startDate: '2025-01-15',
    targetCompletion: '2027-06-30',
    overallPlannedProgress: 68.4,
    overallActualProgress: 61.2,
    spi: 0.89, // Schedule Performance Index
    cpi: 0.94, // Cost Performance Index
    totalActivities: 1240,
    activeDelaysCount: 14,
    pendingVerificationsCount: 6,
    status: 'In Progress - Minor Delay'
  },
  {
    id: 'PRJ-EXPRESSWAY-04',
    name: 'NHAI 8-Lane Access Controlled Expressway (Section 2B)',
    code: 'NHAI-EC-SEC2B',
    client: 'National Highways Authority of India',
    contractor: 'Dilip Buildcon Ltd',
    location: 'Vadodara to Kim Stretch (42.0 km)',
    startDate: '2024-09-01',
    targetCompletion: '2026-12-31',
    overallPlannedProgress: 82.1,
    overallActualProgress: 84.5,
    spi: 1.03,
    cpi: 1.01,
    totalActivities: 890,
    activeDelaysCount: 2,
    pendingVerificationsCount: 3,
    status: 'Ahead of Schedule'
  },
  {
    id: 'PRJ-BRIDGE-01',
    name: 'Kachhi Dargah Bidupur 6-Lane Cable Stayed Bridge',
    code: 'BSRDC-KDB-01',
    client: 'Bihar State Road Development Corporation',
    contractor: 'Daewoo - L&T JV',
    location: 'Ganga River Crossing, Patna',
    startDate: '2023-11-10',
    targetCompletion: '2026-10-15',
    overallPlannedProgress: 76.0,
    overallActualProgress: 72.8,
    spi: 0.96,
    cpi: 0.98,
    totalActivities: 1560,
    activeDelaysCount: 8,
    pendingVerificationsCount: 5,
    status: 'In Progress'
  }
];

export const MOCK_PROJECT_STATS = {
  totalProjects: 3,
  totalL6Activities: 3690,
  averageSPI: 0.96,
  totalPendingVerifications: 14,
  totalAuditLogs: 128,
  highConfidenceMatchRate: 84.2,
  unmatchedQueueCount: 6
};
