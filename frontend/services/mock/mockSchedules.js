/**
 * Primavera P6 / MS Project Schedule Data Structure (L5 Work Packages & L6 Activities)
 */

export const MOCK_WBS_TREE = [
  {
    id: 'WBS-1',
    code: '1.0',
    name: 'Metro Viaduct Package 4 Construction',
    level: 1,
    plannedProgressPercent: 68.4,
    actualProgressPercent: 61.2,
    children: [
      {
        id: 'WBS-1.1',
        code: '1.1',
        name: 'Pre-Construction & Utility Shifting',
        level: 2,
        parentId: 'WBS-1',
        plannedProgressPercent: 100,
        actualProgressPercent: 100,
        children: []
      },
      {
        id: 'WBS-1.2',
        code: '1.2',
        name: 'Substructure Works (Piers & Abutments)',
        level: 2,
        parentId: 'WBS-1',
        plannedProgressPercent: 88.5,
        actualProgressPercent: 82.0,
        children: [
          {
            id: 'WBS-1.2.4',
            code: '1.2.4',
            name: 'Piers Construction (Chainage 12+400 to 14+800)',
            level: 3,
            parentId: 'WBS-1.2',
            plannedProgressPercent: 84.0,
            actualProgressPercent: 76.5,
            children: [
              {
                id: 'WBS-1.2.4.1',
                code: '1.2.4.1 (L5)',
                name: 'L5 Work Package: Pier 12 to Pier 16 Substructure',
                level: 5,
                parentId: 'WBS-1.2.4',
                plannedProgressPercent: 78.0,
                actualProgressPercent: 70.0,
                activities: [
                  {
                    id: 'ACT-L6-1048',
                    code: '1.2.4.1.A',
                    name: 'Pier 14 Reinforcement Cage Tying & Shuttering Installation',
                    wbsId: 'WBS-1.2.4.1',
                    wbsPath: 'Metro Package 4 > Substructure > Piers > Pier 12-16',
                    discipline: 'Structural',
                    plannedStart: '2026-08-20',
                    plannedFinish: '2026-08-28',
                    plannedDurationDays: 8,
                    actualStart: '2026-08-21',
                    actualFinish: '2026-08-30',
                    plannedProgressPercent: 100,
                    actualProgressPercent: 100,
                    baselineQuantity: 28,
                    actualQuantity: 28,
                    unitOfMeasure: 'MT',
                    isCriticalPath: true,
                    status: 'Completed'
                  },
                  {
                    id: 'ACT-L6-1049',
                    code: '1.2.4.1.B',
                    name: 'Pier 14 M45 Concrete Pouring & Curing (Lift 2)',
                    wbsId: 'WBS-1.2.4.1',
                    wbsPath: 'Metro Package 4 > Substructure > Piers > Pier 12-16',
                    discipline: 'Civil',
                    plannedStart: '2026-09-01',
                    plannedFinish: '2026-09-07',
                    plannedDurationDays: 6,
                    actualStart: '2026-09-02',
                    actualFinish: undefined,
                    plannedProgressPercent: 80,
                    actualProgressPercent: 65,
                    baselineQuantity: 420,
                    actualQuantity: 275,
                    unitOfMeasure: 'm³',
                    isCriticalPath: true,
                    status: 'In Progress',
                    delayDays: 2
                  },
                  {
                    id: 'ACT-L6-1050',
                    code: '1.2.4.1.C',
                    name: 'Pier Cap 14 Casting Bed Reinforcement & Pre-stressing Duct Fixing',
                    wbsId: 'WBS-1.2.4.1',
                    wbsPath: 'Metro Package 4 > Substructure > Piers > Pier 12-16',
                    discipline: 'Structural',
                    plannedStart: '2026-09-05',
                    plannedFinish: '2026-09-12',
                    plannedDurationDays: 7,
                    actualStart: undefined,
                    actualFinish: undefined,
                    plannedProgressPercent: 20,
                    actualProgressPercent: 0,
                    baselineQuantity: 18,
                    actualQuantity: 0,
                    unitOfMeasure: 'MT',
                    isCriticalPath: false,
                    status: 'Not Started'
                  }
                ]
              },
              {
                id: 'WBS-1.2.4.2',
                code: '1.2.4.2 (L5)',
                name: 'L5 Work Package: Pier 17 to Pier 20 Substructure',
                level: 5,
                parentId: 'WBS-1.2.4',
                plannedProgressPercent: 90.0,
                actualProgressPercent: 88.0,
                activities: [
                  {
                    id: 'ACT-L6-1055',
                    code: '1.2.4.2.A',
                    name: 'Pier 18 Pile Cap Excavation & Lean Concrete Blinding',
                    wbsId: 'WBS-1.2.4.2',
                    wbsPath: 'Metro Package 4 > Substructure > Piers > Pier 17-20',
                    discipline: 'Geotechnical',
                    plannedStart: '2026-08-15',
                    plannedFinish: '2026-08-22',
                    plannedDurationDays: 7,
                    actualStart: '2026-08-15',
                    actualFinish: '2026-08-22',
                    plannedProgressPercent: 100,
                    actualProgressPercent: 100,
                    baselineQuantity: 650,
                    actualQuantity: 650,
                    unitOfMeasure: 'm³',
                    isCriticalPath: false,
                    status: 'Completed'
                  },
                  {
                    id: 'ACT-L6-1056',
                    code: '1.2.4.2.B',
                    name: 'Pier 18 Foundation Rebar Cage Assembly & Sonic Tube Fixing',
                    wbsId: 'WBS-1.2.4.2',
                    wbsPath: 'Metro Package 4 > Substructure > Piers > Pier 17-20',
                    discipline: 'Structural',
                    plannedStart: '2026-08-23',
                    plannedFinish: '2026-09-03',
                    plannedDurationDays: 11,
                    actualStart: '2026-08-24',
                    actualFinish: '2026-09-04',
                    plannedProgressPercent: 100,
                    actualProgressPercent: 100,
                    baselineQuantity: 45,
                    actualQuantity: 45,
                    unitOfMeasure: 'MT',
                    isCriticalPath: false,
                    status: 'Completed'
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        id: 'WBS-1.3',
        code: '1.3',
        name: 'Superstructure Works (Precast Segment Erection)',
        level: 2,
        parentId: 'WBS-1',
        plannedProgressPercent: 54.0,
        actualProgressPercent: 46.5,
        children: [
          {
            id: 'WBS-1.3.2',
            code: '1.3.2 (L5)',
            name: 'L5 Work Package: Launching Gantry Erection Span 10-14',
            level: 5,
            parentId: 'WBS-1.3',
            plannedProgressPercent: 60.0,
            actualProgressPercent: 48.0,
            activities: [
              {
                id: 'ACT-L6-2012',
                code: '1.3.2.1.A',
                name: 'Span 12-13 Precast Segment Stitch Concrete & Epoxy Jointing',
                wbsId: 'WBS-1.3.2',
                wbsPath: 'Metro Package 4 > Superstructure > Gantry Span 10-14',
                discipline: 'Structural',
                plannedStart: '2026-09-02',
                plannedFinish: '2026-09-10',
                plannedDurationDays: 8,
                actualStart: '2026-09-03',
                actualFinish: undefined,
                plannedProgressPercent: 60,
                actualProgressPercent: 40,
                baselineQuantity: 12,
                actualQuantity: 5,
                unitOfMeasure: 'Segments',
                isCriticalPath: true,
                status: 'In Progress',
                delayDays: 3
              },
              {
                id: 'ACT-L6-2013',
                code: '1.3.2.1.B',
                name: 'Span 12-13 High-Strength Strand Post-Tensioning & Grouting',
                wbsId: 'WBS-1.3.2',
                wbsPath: 'Metro Package 4 > Superstructure > Gantry Span 10-14',
                discipline: 'Mechanical',
                plannedStart: '2026-09-09',
                plannedFinish: '2026-09-15',
                plannedDurationDays: 6,
                actualStart: undefined,
                actualFinish: undefined,
                plannedProgressPercent: 0,
                actualProgressPercent: 0,
                baselineQuantity: 24,
                actualQuantity: 0,
                unitOfMeasure: 'Tendons',
                isCriticalPath: true,
                status: 'Not Started'
              }
            ]
          }
        ]
      }
    ]
  }
];

export const MOCK_ALL_L6_ACTIVITIES = [
  {
    id: 'ACT-L6-1048',
    code: '1.2.4.1.A',
    name: 'Pier 14 Reinforcement Cage Tying & Shuttering Installation',
    wbsPath: 'Metro Package 4 > Substructure > Piers > Pier 12-16',
    discipline: 'Structural',
    plannedStart: '2026-08-20',
    plannedFinish: '2026-08-28',
    plannedProgressPercent: 100,
    actualProgressPercent: 100,
    unitOfMeasure: 'MT',
    status: 'Completed'
  },
  {
    id: 'ACT-L6-1049',
    code: '1.2.4.1.B',
    name: 'Pier 14 M45 Concrete Pouring & Curing (Lift 2)',
    wbsPath: 'Metro Package 4 > Substructure > Piers > Pier 12-16',
    discipline: 'Civil',
    plannedStart: '2026-09-01',
    plannedFinish: '2026-09-07',
    plannedProgressPercent: 80,
    actualProgressPercent: 65,
    unitOfMeasure: 'm³',
    status: 'In Progress'
  },
  {
    id: 'ACT-L6-1050',
    code: '1.2.4.1.C',
    name: 'Pier Cap 14 Casting Bed Reinforcement & Pre-stressing Duct Fixing',
    wbsPath: 'Metro Package 4 > Substructure > Piers > Pier 12-16',
    discipline: 'Structural',
    plannedStart: '2026-09-05',
    plannedFinish: '2026-09-12',
    plannedProgressPercent: 20,
    actualProgressPercent: 0,
    unitOfMeasure: 'MT',
    status: 'Not Started'
  },
  {
    id: 'ACT-L6-2012',
    code: '1.3.2.1.A',
    name: 'Span 12-13 Precast Segment Stitch Concrete & Epoxy Jointing',
    wbsPath: 'Metro Package 4 > Superstructure > Gantry Span 10-14',
    discipline: 'Structural',
    plannedStart: '2026-09-02',
    plannedFinish: '2026-09-10',
    plannedProgressPercent: 60,
    actualProgressPercent: 40,
    unitOfMeasure: 'Segments',
    status: 'In Progress'
  },
  {
    id: 'ACT-L6-3045',
    code: '1.4.1.2.A',
    name: 'BKC Underground Station Diaphragm Wall Panel Trenching (Panel D-22)',
    wbsPath: 'Metro Package 4 > Stations > BKC Station > D-Wall',
    discipline: 'Geotechnical',
    plannedStart: '2026-09-03',
    plannedFinish: '2026-09-09',
    plannedProgressPercent: 70,
    actualProgressPercent: 50,
    unitOfMeasure: 'm³',
    status: 'In Progress'
  }
];
