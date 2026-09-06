/**
 * Mock AI Extractions, Semantic Matching Results & Planner Verification Queue Items
 */

export const MOCK_EXTRACTIONS_AND_MATCHES = [
  {
    id: 'VERIF-2026-0905-01',
    extractedEvent: {
      id: 'EXT-001',
      sourceType: 'DSR_PDF',
      sourceFileName: 'DSR_2026_09_05_Zone3_Pier14.pdf',
      sourceRefLocation: 'Page 2, Section 3.2 (Shift B Log)',
      rawText: 'Poured 165 cum of M45 grade concrete at Pier 14 Lift 2 using 2 transit mixers and Putzmeister boom pump. Concrete slump verified at 140mm.',
      extractedActivity: 'Pier 14 M45 Concrete Pouring Lift 2',
      quantity: 165,
      unit: 'm³',
      extractedStart: '2026-09-05T07:30:00Z',
      extractedFinish: '2026-09-05T18:00:00Z',
      equipmentUsed: ['Putzmeister Boom Pump BP-02', 'Transit Mixer TM-08', 'TM-12'],
      workforceCount: 18,
      remarks: 'Smooth pour, cubes casted for 7D and 28D testing',
      timestamp: '2026-09-05T18:30:00Z'
    },
    primaryMatch: {
      l6ActivityId: 'ACT-L6-1049',
      l6ActivityCode: '1.2.4.1.B',
      l6ActivityName: 'Pier 14 M45 Concrete Pouring & Curing (Lift 2)',
      wbsPath: 'Metro Package 4 > Substructure > Piers > Pier 12-16',
      semanticSimilarityScore: 0.94,
      contextualScore: 0.96,
      totalConfidenceScore: 95,
      confidenceRating: 'HIGH',
      matchingRationale: 'High semantic match on activity keyword "Pier 14 M45 Concrete" combined with exact matches on WBS Pier 14 node and date window.'
    },
    alternateCandidates: [
      {
        l6ActivityId: 'ACT-L6-1048',
        l6ActivityCode: '1.2.4.1.A',
        l6ActivityName: 'Pier 14 Reinforcement Cage Tying & Shuttering Installation',
        wbsPath: 'Metro Package 4 > Substructure > Piers > Pier 12-16',
        semanticSimilarityScore: 0.52,
        contextualScore: 0.85,
        totalConfidenceScore: 61,
        confidenceRating: 'MEDIUM',
        matchingRationale: 'Shares Pier 14 location but activity discipline differs (Rebar vs Concrete).'
      }
    ],
    approvalStatus: 'PENDING_VERIFICATION'
  },
  {
    id: 'VERIF-2026-0905-02',
    extractedEvent: {
      id: 'EXT-002',
      sourceType: 'VOICE_MEMO',
      sourceFileName: 'AUDIO_REC_ErRajesh_20260905_1645.wav',
      sourceRefLocation: 'Timestamp 01:14 - 01:52',
      rawText: 'We completed epoxy gluing and stitch concreting for 3 precast segments on Span 12 to 13 today. Rain stopped work for 2 hours in afternoon.',
      extractedActivity: 'Precast segment stitch concreting Span 12-13',
      quantity: 3,
      unit: 'Segments',
      extractedStart: '2026-09-05T09:00:00Z',
      extractedFinish: '2026-09-05T16:30:00Z',
      equipmentUsed: ['Gantry Crane GC-01', 'Epoxy Dispensing Rig'],
      workforceCount: 12,
      remarks: 'Delay due to heavy rain shower',
      timestamp: '2026-09-05T16:50:00Z'
    },
    primaryMatch: {
      l6ActivityId: 'ACT-L6-2012',
      l6ActivityCode: '1.3.2.1.A',
      l6ActivityName: 'Span 12-13 Precast Segment Stitch Concrete & Epoxy Jointing',
      wbsPath: 'Metro Package 4 > Superstructure > Gantry Span 10-14',
      semanticSimilarityScore: 0.88,
      contextualScore: 0.90,
      totalConfidenceScore: 89,
      confidenceRating: 'HIGH',
      matchingRationale: 'Exact match on segment stitch concreting and Span 12-13 target activity code.'
    },
    alternateCandidates: [],
    approvalStatus: 'PENDING_VERIFICATION'
  },
  {
    id: 'VERIF-2026-0905-03',
    extractedEvent: {
      id: 'EXT-003',
      sourceType: 'EXCEL',
      sourceFileName: 'Weekly_Site_Log_W36_Sheet1.xlsx',
      sourceRefLocation: 'Sheet1, Row 42 (Cells B42:G42)',
      rawText: 'Excavated 120m3 of rock slurry for D-wall panel D22 at BKC underground station area using hydrofraise cutter.',
      extractedActivity: 'D-wall panel trenching underground station',
      quantity: 120,
      unit: 'm³',
      extractedStart: '2026-09-04T08:00:00Z',
      extractedFinish: '2026-09-05T17:00:00Z',
      equipmentUsed: ['Bauer Trench Cutter BC-40'],
      workforceCount: 8,
      remarks: 'Hard rock encountered at -18m depth',
      timestamp: '2026-09-05T19:10:00Z'
    },
    primaryMatch: {
      l6ActivityId: 'ACT-L6-3045',
      l6ActivityCode: '1.4.1.2.A',
      l6ActivityName: 'BKC Underground Station Diaphragm Wall Panel Trenching (Panel D-22)',
      wbsPath: 'Metro Package 4 > Stations > BKC Station > D-Wall',
      semanticSimilarityScore: 0.74,
      contextualScore: 0.70,
      totalConfidenceScore: 72,
      confidenceRating: 'MEDIUM',
      matchingRationale: 'Moderate confidence. Matches panel D-22 trenching, but Excel text lacked explicit station code prefix.'
    },
    alternateCandidates: [
      {
        l6ActivityId: 'ACT-L6-3048',
        l6ActivityCode: '1.4.1.2.D',
        l6ActivityName: 'BKC Underground Station Guide Wall Construction',
        wbsPath: 'Metro Package 4 > Stations > BKC Station > D-Wall',
        semanticSimilarityScore: 0.58,
        contextualScore: 0.65,
        totalConfidenceScore: 61,
        confidenceRating: 'MEDIUM',
        matchingRationale: 'Located in same D-Wall WBS folder but activity step is Guide Wall instead of Panel Trenching.'
      }
    ],
    approvalStatus: 'PENDING_VERIFICATION'
  },
  {
    id: 'VERIF-2026-0905-04',
    extractedEvent: {
      id: 'EXT-004',
      sourceType: 'VOICE_MEMO',
      sourceFileName: 'AUDIO_REC_SiteEngg_20260905_1920.wav',
      sourceRefLocation: 'Timestamp 00:05 - 00:38',
      rawText: 'Shifted temporary 33kV high tension power cable away from Pier 19 foundation line to clear way for rig movement.',
      extractedActivity: 'HT Cable Utility Shifting near Pier 19',
      quantity: 1,
      unit: 'Job',
      extractedStart: '2026-09-05T10:00:00Z',
      extractedFinish: '2026-09-05T16:00:00Z',
      equipmentUsed: ['Mobile Crane 20T'],
      workforceCount: 6,
      remarks: 'MSEDCL lineman supervised shut down',
      timestamp: '2026-09-05T19:25:00Z'
    },
    primaryMatch: {
      l6ActivityId: 'ACT-L6-1002',
      l6ActivityCode: '1.1.2.1.A',
      l6ActivityName: '33kV Electrical HT Cable Relocation & Jointing (Section 2)',
      wbsPath: 'Metro Package 4 > Pre-Construction > Utility Shifting',
      semanticSimilarityScore: 0.51,
      contextualScore: 0.55,
      totalConfidenceScore: 53,
      confidenceRating: 'LOW',
      matchingRationale: 'Low confidence match. Spoken audio notes utility shift near Pier 19, but schedule lists utility shifting under 1.1.2.1 pre-construction.'
    },
    alternateCandidates: [
      {
        l6ActivityId: 'ACT-L6-1056',
        l6ActivityCode: '1.2.4.2.B',
        l6ActivityName: 'Pier 18 Foundation Rebar Cage Assembly & Sonic Tube Fixing',
        wbsPath: 'Metro Package 4 > Substructure > Piers > Pier 17-20',
        semanticSimilarityScore: 0.32,
        contextualScore: 0.60,
        totalConfidenceScore: 42,
        confidenceRating: 'LOW',
        matchingRationale: 'Spatially close to Pier 18/19 work zone but different work package.'
      }
    ],
    approvalStatus: 'PENDING_VERIFICATION'
  }
];

export const MOCK_VOICE_TRANSCRIPT = [
  {
    startTime: 0,
    endTime: 12,
    speaker: 'Er. Rajesh Sharma (Senior Site Engineer)',
    text: 'Daily site progress update for September 5th, 2026. Shift B viaduct construction team.',
    keyTerms: ['Progress Update', 'Viaduct']
  },
  {
    startTime: 13,
    endTime: 45,
    speaker: 'Er. Rajesh Sharma (Senior Site Engineer)',
    text: 'We completed epoxy gluing and stitch concreting for 3 precast segments on Span 12 to 13 today. The gantry alignment was verified by surveyor.',
    keyTerms: ['Epoxy Gluing', 'Stitch Concreting', '3 Precast Segments', 'Span 12 to 13']
  },
  {
    startTime: 46,
    endTime: 65,
    speaker: 'Er. Rajesh Sharma (Senior Site Engineer)',
    text: 'Heavy rain shower stopped work for 2 hours in the afternoon between 2:00 PM and 4:00 PM. Total workforce on gantry was 12 riggers.',
    keyTerms: ['Delay', 'Heavy Rain', '12 Riggers']
  }
];
