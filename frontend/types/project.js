/**
 * @typedef {'Civil' | 'Structural' | 'Electrical' | 'Mechanical' | 'Marine' | 'Geotechnical'} Discipline
 * @typedef {'Not Started' | 'In Progress' | 'Completed' | 'Delayed' | 'Critical'} ActivityStatus
 * 
 * @typedef {Object} L6Activity
 * @property {string} id - Unique identifier (e.g., 'ACT-L6-1001')
 * @property {string} code - Primavera/MS Project Activity ID (e.g., '1.2.4.1.A')
 * @property {string} name - Activity Description (e.g., 'Pier 14 Concrete Pouring & Curing')
 * @property {string} wbsId - WBS Node ID
 * @property {string} wbsPath - Full WBS Path (e.g., 'Metro Line 3 > Civil Works > Substructure > Piers')
 * @property {Discipline} discipline - Project engineering discipline
 * @property {string} plannedStart - ISO Date string
 * @property {string} plannedFinish - ISO Date string
 * @property {number} plannedDurationDays - Planned duration in days
 * @property {string} [actualStart] - ISO Date string when work actually started
 * @property {string} [actualFinish] - ISO Date string when work finished
 * @property {number} plannedProgressPercent - Planned cumulative progress percentage (0-100)
 * @property {number} actualProgressPercent - Actual approved physical progress percentage (0-100)
 * @property {number} baselineQuantity - Target volume of work (e.g., 450)
 * @property {number} [actualQuantity] - Completed volume of work (e.g., 380)
 * @property {string} unitOfMeasure - Unit (e.g., 'm³', 'MT', 'm', 'units')
 * @property {boolean} isCriticalPath - Whether activity is on critical path
 * @property {ActivityStatus} status - Current activity status
 * @property {number} [delayDays] - Calculated schedule variance in days
 */

/**
 * @typedef {Object} WBSNode
 * @property {string} id - Unique WBS ID
 * @property {string} code - WBS Code (e.g., '1.2.4')
 * @property {string} name - WBS Element Name (e.g., 'Substructure Works')
 * @property {number} level - WBS Hierarchy Level (1 to 6)
 * @property {string} [parentId] - Parent WBS Node ID
 * @property {WBSNode[]} [children] - Child WBS Nodes
 * @property {L6Activity[]} [activities] - L6 Activities under this node
 * @property {number} plannedProgressPercent - Aggregated planned progress %
 * @property {number} actualProgressPercent - Aggregated actual progress %
 */

/**
 * @typedef {Object} InfrastructureProject
 * @property {string} id - Project ID (e.g., 'PRJ-MUM-METRO-03')
 * @property {string} name - Project Title
 * @property {string} code - Project Code (e.g., 'MMRDA-ML3')
 * @property {string} client - Owner/Client agency (e.g., 'MMRC / NHAI')
 * @property {string} contractor - Lead Contractor (e.g., 'L&T - Shapoorji Pallonji JV')
 * @property {string} location - Site Location (e.g., 'Mumbai Package 4, Pier 12-45')
 * @property {string} startDate - Baseline Project Start
 * @property {string} targetCompletion - Baseline Project Target Completion
 * @property {number} overallPlannedProgress - Current overall planned %
 * @property {number} overallActualProgress - Current overall approved actual %
 * @property {number} spi - Schedule Performance Index (Actual / Planned)
 * @property {number} cpi - Cost Performance Index
 * @property {number} totalActivities - Total L6 activities count
 * @property {number} activeDelaysCount - Number of currently delayed activities
 * @property {number} pendingVerificationsCount - Number of field updates awaiting planner approval
 */

export {};
