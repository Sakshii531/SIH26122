/**
 * @typedef {'HIGH' | 'MEDIUM' | 'LOW'} ConfidenceLevel
 * @typedef {'PENDING_VERIFICATION' | 'APPROVED' | 'OVERRIDDEN' | 'REJECTED'} VerificationStatus
 * 
 * @typedef {Object} MatchCandidate
 * @property {string} l6ActivityId - Target Primavera L6 activity ID
 * @property {string} l6ActivityCode - Activity Code (e.g. '1.2.4.1.A')
 * @property {string} l6ActivityName - Target Primavera Activity Name
 * @property {string} wbsPath - Full WBS path context
 * @property {number} semanticSimilarityScore - Text vector similarity score (0.0 to 1.0)
 * @property {number} contextualScore - WBS & Date proximity score (0.0 to 1.0)
 * @property {number} totalConfidenceScore - Combined confidence percentage (0 to 100%)
 * @property {ConfidenceLevel} confidenceRating - High (>=85%), Medium (60-84%), Low (<60%)
 * @property {string} matchingRationale - Explainable AI sentence explaining why this match was suggested
 */

/**
 * @typedef {Object} VerificationItem
 * @property {string} id - Unique match record ID
 * @property {import('./capture').ExtractedEntity} extractedEvent - Extracted site report event
 * @property {MatchCandidate} primaryMatch - Best AI candidate match
 * @property {MatchCandidate[]} alternateCandidates - Top-N alternative candidate matches
 * @property {VerificationStatus} approvalStatus - Current verification status
 * @property {string} [verifiedBy] - Planner name who approved/edited
 * @property {string} [verifiedAt] - Timestamp of verification
 * @property {string} [plannerNotes] - Planner's rationale or audit notes
 * @property {number} [appliedProgressPercent] - Final approved progress %
 * @property {string} [appliedActualStart] - Approved actual start date
 * @property {string} [appliedActualFinish] - Approved actual finish date
 */

export {};
