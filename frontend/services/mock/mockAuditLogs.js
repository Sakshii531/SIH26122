/**
 * Mock Audit Logs, Traceability Records & S-Curve Datasets
 */

export const MOCK_AUDIT_LOGS = [
  {
    id: 'AUD-90501',
    timestamp: '2026-09-05T18:35:12Z',
    projectCode: 'MMRDA-ML3-P4',
    activityCode: '1.2.4.1.B',
    activityName: 'Pier 14 M45 Concrete Pouring & Curing (Lift 2)',
    action: 'PLANNER_APPROVED',
    actor: 'Er. V. K. Kulkarni (Chief Planning Manager)',
    sourceDocument: 'DSR_2026_09_05_Zone3_Pier14.pdf',
    sourceRefLocation: 'Page 2, Section 3.2',
    previousProgress: 40,
    newProgress: 65,
    confidenceScore: 95,
    details: 'Approved 165 m³ M45 concrete pour for Pier 14 Lift 2 based on verified batching plant delivery tickets.'
  },
  {
    id: 'AUD-90502',
    timestamp: '2026-09-05T17:02:44Z',
    projectCode: 'MMRDA-ML3-P4',
    activityCode: '1.3.2.1.A',
    activityName: 'Span 12-13 Precast Segment Stitch Concrete & Epoxy Jointing',
    action: 'SEMANTIC_MATCHED',
    actor: 'AI Semantic Matching Engine v2.4',
    sourceDocument: 'AUDIO_REC_ErRajesh_20260905_1645.wav',
    sourceRefLocation: 'Timestamp 00:13 - 00:45',
    previousProgress: 25,
    newProgress: 40,
    confidenceScore: 89,
    details: 'Matched spoken audio note "3 precast segments on Span 12 to 13" to L6 Activity 1.3.2.1.A with 89% confidence.'
  },
  {
    id: 'AUD-90408',
    timestamp: '2026-09-04T15:20:00Z',
    projectCode: 'MMRDA-ML3-P4',
    activityCode: '1.2.4.1.A',
    activityName: 'Pier 14 Reinforcement Cage Tying & Shuttering Installation',
    action: 'PLANNER_OVERRIDDEN',
    actor: 'Er. V. K. Kulkarni (Chief Planning Manager)',
    sourceDocument: 'DSR_2026_09_04_Pier14_Rebar.pdf',
    sourceRefLocation: 'Page 1, Paragraph 4',
    previousProgress: 85,
    newProgress: 100,
    confidenceScore: 78,
    details: 'Planner manual override: Marked activity 100% complete after site photo verification of final shutter inspection.'
  },
  {
    id: 'AUD-90312',
    timestamp: '2026-09-03T11:14:00Z',
    projectCode: 'MMRDA-ML3-P4',
    activityCode: '1.2.4.2.B',
    activityName: 'Pier 18 Foundation Rebar Cage Assembly & Sonic Tube Fixing',
    action: 'DB_COMMITTED',
    actor: 'Automated Progress Linking Engine',
    sourceDocument: 'Weekly_Site_Log_W35.xlsx',
    sourceRefLocation: 'Sheet3, Row 18',
    previousProgress: 60,
    newProgress: 100,
    confidenceScore: 92,
    details: 'Batch update committed to Primavera P6 Progress Database following quality sign-off.'
  }
];

export const MOCK_S_CURVE_DATA = [
  { month: 'Jan 25', planned: 5, actual: 5, baseline: 5 },
  { month: 'Feb 25', planned: 12, actual: 11, baseline: 12 },
  { month: 'Mar 25', planned: 20, actual: 19, baseline: 20 },
  { month: 'Apr 25', planned: 28, actual: 27, baseline: 28 },
  { month: 'May 25', planned: 36, actual: 33, baseline: 36 },
  { month: 'Jun 25', planned: 45, actual: 40, baseline: 45 },
  { month: 'Jul 25', planned: 53, actual: 48, baseline: 53 },
  { month: 'Aug 25', planned: 61, actual: 55, baseline: 61 },
  { month: 'Sep 25', planned: 68, actual: 61.2, baseline: 68 },
  { month: 'Oct 25', planned: 76, actual: null, baseline: 76 },
  { month: 'Nov 25', planned: 84, actual: null, baseline: 84 },
  { month: 'Dec 25', planned: 92, actual: null, baseline: 92 },
  { month: 'Jan 26', planned: 100, actual: null, baseline: 100 }
];

export const MOCK_DAILY_OUTPUT_TRENDS = [
  { date: 'Aug 30', concrete: 210, rebar: 18, excavation: 450 },
  { date: 'Aug 31', concrete: 190, rebar: 22, excavation: 520 },
  { date: 'Sep 01', concrete: 310, rebar: 28, excavation: 380 },
  { date: 'Sep 02', concrete: 280, rebar: 24, excavation: 410 },
  { date: 'Sep 03', concrete: 150, rebar: 16, excavation: 290 },
  { date: 'Sep 04', concrete: 340, rebar: 32, excavation: 610 },
  { date: 'Sep 05', concrete: 275, rebar: 25, excavation: 480 }
];

export const MOCK_DISCIPLINE_PROGRESS = [
  { discipline: 'Civil', planned: 72, actual: 64 },
  { discipline: 'Structural', planned: 81, actual: 76 },
  { discipline: 'Geotechnical', planned: 90, actual: 88 },
  { discipline: 'Mechanical', planned: 54, actual: 46 },
  { discipline: 'Electrical', planned: 45, actual: 38 }
];

export const MOCK_DELAY_HEATMAP = [
  { zone: 'Pier 12-16 Viaduct', level: 'HIGH', delayDays: 4, reason: 'Batching plant concrete delivery delay' },
  { zone: 'Span 12-13 Gantry', level: 'MEDIUM', delayDays: 3, reason: 'Rain interruption & epoxy curing window' },
  { zone: 'BKC Station D-Wall', level: 'MEDIUM', delayDays: 2, reason: 'Hard basalt rock trenching slowing cutter' },
  { zone: 'Utility Shifting Sec 2', level: 'LOW', delayDays: 1, reason: 'MSEDCL shutdown coordination delay' }
];
