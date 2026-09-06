/**
 * @typedef {'AI_EXTRACTED' | 'SEMANTIC_MATCHED' | 'PLANNER_APPROVED' | 'PLANNER_OVERRIDDEN' | 'REJECTED' | 'DB_COMMITTED'} AuditActionType
 * 
 * @typedef {Object} AuditLogEntry
 * @property {string} id - Unique log ID
 * @property {string} timestamp - ISO Timestamp of event
 * @property {string} projectCode - Project code identifier
 * @property {string} activityCode - Primavera/MS Project Activity Code
 * @property {string} activityName - Primavera Activity Description
 * @property {AuditActionType} action - Type of workflow action performed
 * @property {string} actor - User or AI system identifier (e.g. 'AI Semantic Matching Engine' or 'Planner - Er. V. K. Kulkarni')
 * @property {string} sourceDocument - Source document reference (e.g. 'DSR_2026_09_05_Pier14.pdf')
 * @property {string} sourceRefLocation - Line/Cell/Timestamp reference in source
 * @property {number} previousProgress - Progress % before update
 * @property {number} newProgress - Progress % after update
 * @property {number} confidenceScore - Confidence percentage at time of matching
 * @property {string} details - Detailed human-readable change description
 */

export {};
