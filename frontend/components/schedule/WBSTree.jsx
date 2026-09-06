'use client';

import React, { useState } from 'react';
import { ChevronRight, ChevronDown, Folder, Layers, CheckCircle2, Clock, AlertCircle } from 'lucide-react';
import { Badge } from '../common/Badge.jsx';

export function WBSTree({ wbsData, selectedActivity, onSelectActivity }) {
  const [expandedNodes, setExpandedNodes] = useState({ 'WBS-1': true, 'WBS-1.2': true, 'WBS-1.2.4': true, 'WBS-1.2.4.1': true });

  const toggleExpand = (nodeId) => {
    setExpandedNodes(prev => ({ ...prev, [nodeId]: !prev[nodeId] }));
  };

  const renderWBSNode = (node) => {
    const isExpanded = expandedNodes[node.id];
    const hasChildren = node.children && node.children.length > 0;
    const hasActivities = node.activities && node.activities.length > 0;

    return (
      <div key={node.id} className="select-none">
        {/* Node Row */}
        <div
          onClick={() => toggleExpand(node.id)}
          className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-100 cursor-pointer border border-transparent transition-all"
        >
          <div className="flex items-center gap-2">
            {(hasChildren || hasActivities) ? (
              isExpanded ? (
                <ChevronDown className="w-4 h-4 text-blue-600" />
              ) : (
                <ChevronRight className="w-4 h-4 text-slate-400" />
              )
            ) : (
              <span className="w-4" />
            )}
            <Folder className={`w-4 h-4 ${node.level === 5 ? 'text-amber-500' : 'text-blue-600'}`} />
            <span className="text-xs font-mono font-bold text-slate-700">{node.code}</span>
            <span className="text-xs font-bold text-slate-800">{node.name}</span>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-24 bg-slate-200 rounded-full h-2 overflow-hidden">
              <div
                className="bg-blue-600 h-full rounded-full transition-all"
                style={{ width: `${node.actualProgressPercent}%` }}
              />
            </div>
            <span className="text-[11px] font-mono font-bold text-slate-600 w-10 text-right">
              {node.actualProgressPercent}%
            </span>
          </div>
        </div>

        {/* Children WBS */}
        {isExpanded && hasChildren && (
          <div className="pl-5 border-l border-slate-200 ml-3 my-1 space-y-1">
            {node.children.map(child => renderWBSNode(child))}
          </div>
        )}

        {/* L6 Activities */}
        {isExpanded && hasActivities && (
          <div className="pl-5 border-l border-blue-200 ml-3 my-1 space-y-1">
            {node.activities.map((act) => {
              const isSelected = selectedActivity?.id === act.id;
              return (
                <div
                  key={act.id}
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectActivity(act);
                  }}
                  className={`p-2.5 rounded-lg border cursor-pointer transition-all flex items-center justify-between ${
                    isSelected
                      ? 'bg-blue-50 border-blue-500 text-blue-900 shadow-2xs font-semibold'
                      : 'bg-white border-slate-200 hover:bg-slate-50 text-slate-700'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Layers className={`w-3.5 h-3.5 ${act.isCriticalPath ? 'text-rose-600' : 'text-blue-600'}`} />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-[11px] font-mono font-bold text-amber-700">{act.code}</span>
                        {act.isCriticalPath && (
                          <span className="text-[9px] font-bold text-rose-700 bg-rose-50 px-1.5 py-0.5 rounded border border-rose-200">
                            CRITICAL
                          </span>
                        )}
                      </div>
                      <p className="text-xs font-semibold text-slate-800 line-clamp-1">{act.name}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <Badge variant={act.discipline === 'Civil' ? 'cyan' : act.discipline === 'Structural' ? 'purple' : 'blue'}>
                      {act.discipline}
                    </Badge>
                    <div className="text-right font-mono text-[11px]">
                      <p className="text-slate-900 font-bold">{act.actualProgressPercent}%</p>
                      <p className="text-[9px] text-slate-400">Plan: {act.plannedProgressPercent}%</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-2">
      {wbsData.map(node => renderWBSNode(node))}
    </div>
  );
}
