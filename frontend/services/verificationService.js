import { MOCK_EXTRACTIONS_AND_MATCHES } from './mock/mockExtractions.js';
import { MOCK_AUDIT_LOGS, MOCK_S_CURVE_DATA, MOCK_DAILY_OUTPUT_TRENDS, MOCK_DISCIPLINE_PROGRESS, MOCK_DELAY_HEATMAP } from './mock/mockAuditLogs.js';

let pendingQueue = [...MOCK_EXTRACTIONS_AND_MATCHES];
let auditLogs = [...MOCK_AUDIT_LOGS];

export const verificationService = {
  /**
   * Get pending verification queue items for planner
   */
  async getPendingQueue(confidenceFilter = 'ALL') {
    if (confidenceFilter === 'ALL') {
      return pendingQueue.filter(item => item.approvalStatus === 'PENDING_VERIFICATION');
    }
    return pendingQueue.filter(
      item => item.approvalStatus === 'PENDING_VERIFICATION' && item.primaryMatch.confidenceRating === confidenceFilter
    );
  },

  /**
   * Approve match as suggested by AI
   */
  async approveMatch(verifId, plannerName = 'Er. V. K. Kulkarni') {
    const itemIndex = pendingQueue.findIndex(i => i.id === verifId);
    if (itemIndex !== -1) {
      pendingQueue[itemIndex].approvalStatus = 'APPROVED';
      pendingQueue[itemIndex].verifiedBy = plannerName;
      pendingQueue[itemIndex].verifiedAt = new Date().toISOString();
      
      // Add audit log
      const targetAct = pendingQueue[itemIndex].primaryMatch;
      const newLog = {
        id: 'AUD-' + Date.now(),
        timestamp: new Date().toISOString(),
        projectCode: 'MMRDA-ML3-P4',
        activityCode: targetAct.l6ActivityCode,
        activityName: targetAct.l6ActivityName,
        action: 'PLANNER_APPROVED',
        actor: plannerName,
        sourceDocument: pendingQueue[itemIndex].extractedEvent.sourceFileName,
        sourceRefLocation: pendingQueue[itemIndex].extractedEvent.sourceRefLocation,
        previousProgress: 40,
        newProgress: 65,
        confidenceScore: targetAct.totalConfidenceScore,
        details: `Planner approved AI match for ${targetAct.l6ActivityName}. Quantity: ${pendingQueue[itemIndex].extractedEvent.quantity} ${pendingQueue[itemIndex].extractedEvent.unit}.`
      };
      auditLogs.unshift(newLog);
    }
    return { success: true };
  },

  /**
   * Re-assign activity or override actual dates/quantity
   */
  async overrideMatch(verifId, overrideData, plannerName = 'Er. V. K. Kulkarni') {
    const itemIndex = pendingQueue.findIndex(i => i.id === verifId);
    if (itemIndex !== -1) {
      pendingQueue[itemIndex].approvalStatus = 'OVERRIDDEN';
      pendingQueue[itemIndex].verifiedBy = plannerName;
      pendingQueue[itemIndex].verifiedAt = new Date().toISOString();
      pendingQueue[itemIndex].plannerNotes = overrideData.notes;
      
      const newLog = {
        id: 'AUD-' + Date.now(),
        timestamp: new Date().toISOString(),
        projectCode: 'MMRDA-ML3-P4',
        activityCode: overrideData.l6ActivityCode || pendingQueue[itemIndex].primaryMatch.l6ActivityCode,
        activityName: overrideData.l6ActivityName || pendingQueue[itemIndex].primaryMatch.l6ActivityName,
        action: 'PLANNER_OVERRIDDEN',
        actor: plannerName,
        sourceDocument: pendingQueue[itemIndex].extractedEvent.sourceFileName,
        sourceRefLocation: pendingQueue[itemIndex].extractedEvent.sourceRefLocation,
        previousProgress: 40,
        newProgress: overrideData.newProgressPercent || 70,
        confidenceScore: pendingQueue[itemIndex].primaryMatch.totalConfidenceScore,
        details: `Planner manual override: ${overrideData.notes || 'Adjusted target activity and progress %'}.`
      };
      auditLogs.unshift(newLog);
    }
    return { success: true };
  },

  /**
   * Reject invalid site update entry
   */
  async rejectMatch(verifId, reason, plannerName = 'Er. V. K. Kulkarni') {
    const itemIndex = pendingQueue.findIndex(i => i.id === verifId);
    if (itemIndex !== -1) {
      pendingQueue[itemIndex].approvalStatus = 'REJECTED';
      pendingQueue[itemIndex].verifiedBy = plannerName;
      pendingQueue[itemIndex].verifiedAt = new Date().toISOString();
      pendingQueue[itemIndex].plannerNotes = reason;
      
      const newLog = {
        id: 'AUD-' + Date.now(),
        timestamp: new Date().toISOString(),
        projectCode: 'MMRDA-ML3-P4',
        activityCode: pendingQueue[itemIndex].primaryMatch.l6ActivityCode,
        activityName: pendingQueue[itemIndex].primaryMatch.l6ActivityName,
        action: 'REJECTED',
        actor: plannerName,
        sourceDocument: pendingQueue[itemIndex].extractedEvent.sourceFileName,
        sourceRefLocation: pendingQueue[itemIndex].extractedEvent.sourceRefLocation,
        previousProgress: 40,
        newProgress: 40,
        confidenceScore: pendingQueue[itemIndex].primaryMatch.totalConfidenceScore,
        details: `Rejected field log entry: ${reason}.`
      };
      auditLogs.unshift(newLog);
    }
    return { success: true };
  },

  /**
   * Fetch audit logs
   */
  async getAuditLogs(filters = {}) {
    let list = [...auditLogs];
    if (filters.action) {
      list = list.filter(l => l.action === filters.action);
    }
    if (filters.query) {
      const q = filters.query.toLowerCase();
      list = list.filter(l => l.activityName.toLowerCase().includes(q) || l.activityCode.toLowerCase().includes(q) || l.actor.toLowerCase().includes(q) || l.sourceDocument.toLowerCase().includes(q));
    }
    return list;
  },

  /**
   * Fetch S-Curve and analytics datasets
   */
  async getAnalyticsData() {
    return {
      sCurve: MOCK_S_CURVE_DATA,
      dailyOutput: MOCK_DAILY_OUTPUT_TRENDS,
      disciplineProgress: MOCK_DISCIPLINE_PROGRESS,
      delayHeatmap: MOCK_DELAY_HEATMAP
    };
  }
};
