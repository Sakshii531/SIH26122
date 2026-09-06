'use client';

import React, { useState, useEffect } from 'react';
import { verificationService } from '../../services/verificationService.js';
import { VerificationQueueTable } from '../../components/planner/VerificationQueueTable.jsx';
import { ApprovalDrawer } from '../../components/planner/ApprovalDrawer.jsx';
import { CheckSquare, Filter, ShieldCheck, AlertTriangle, ShieldAlert } from 'lucide-react';

export default function VerificationPage() {
  const [items, setItems] = useState([]);
  const [confidenceFilter, setConfidenceFilter] = useState('ALL'); // 'ALL' | 'HIGH' | 'MEDIUM' | 'LOW'
  const [selectedReviewItem, setSelectedReviewItem] = useState(null);

  const fetchQueue = async () => {
    const list = await verificationService.getPendingQueue(confidenceFilter);
    setItems(list);
  };

  useEffect(() => {
    fetchQueue();
  }, [confidenceFilter]);

  const handleQuickApprove = async (id) => {
    await verificationService.approveMatch(id);
    fetchQueue();
  };

  const handleApprove = async (id) => {
    await verificationService.approveMatch(id);
    setSelectedReviewItem(null);
    fetchQueue();
  };

  const handleOverride = async (id, overrideData) => {
    await verificationService.overrideMatch(id, overrideData);
    setSelectedReviewItem(null);
    fetchQueue();
  };

  const handleReject = async (id, reason) => {
    await verificationService.rejectMatch(id, reason);
    setSelectedReviewItem(null);
    fetchQueue();
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <CheckSquare className="w-6 h-6 text-cyan-400" />
            Planner Verification & Approval Queue
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Human-in-the-loop verification workspace for AI extracted daily site updates
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="flex bg-slate-900 border border-slate-800 p-1 rounded-lg">
          <button
            onClick={() => setConfidenceFilter('ALL')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
              confidenceFilter === 'ALL' ? 'bg-cyan-600 text-slate-950 shadow-md' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            All Items ({items.length})
          </button>
          <button
            onClick={() => setConfidenceFilter('HIGH')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
              confidenceFilter === 'HIGH' ? 'bg-emerald-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            High Conf (&ge;85%)
          </button>
          <button
            onClick={() => setConfidenceFilter('MEDIUM')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
              confidenceFilter === 'MEDIUM' ? 'bg-amber-600 text-slate-950 shadow-md' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Med Conf (60-84%)
          </button>
          <button
            onClick={() => setConfidenceFilter('LOW')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
              confidenceFilter === 'LOW' ? 'bg-rose-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Low Conf (&lt;60%)
          </button>
        </div>
      </div>

      {/* Main Queue Table */}
      {items.length > 0 ? (
        <VerificationQueueTable
          items={items}
          onSelectReview={setSelectedReviewItem}
          onQuickApprove={handleQuickApprove}
          onQuickReject={(id) => handleReject(id, 'Quick rejected')}
        />
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center space-y-3">
          <ShieldCheck className="w-12 h-12 text-emerald-400 mx-auto" />
          <h3 className="text-base font-bold text-slate-100">Verification Queue Clear!</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            All extracted daily site updates for this filter have been verified and committed to the project progress database.
          </p>
        </div>
      )}

      {/* Review Drawer */}
      {selectedReviewItem && (
        <ApprovalDrawer
          item={selectedReviewItem}
          onClose={() => setSelectedReviewItem(null)}
          onApprove={handleApprove}
          onOverride={handleOverride}
          onReject={handleReject}
        />
      )}
    </div>
  );
}
