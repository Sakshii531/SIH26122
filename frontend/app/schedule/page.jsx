'use client';

import React, { useState, useEffect } from 'react';
import { scheduleService } from '../../services/scheduleService.js';
import { WBSTree } from '../../components/schedule/WBSTree.jsx';
import { GanttChart } from '../../components/schedule/GanttChart.jsx';
import { L5L6ActivityDetail } from '../../components/schedule/L5L6ActivityDetail.jsx';
import { Card } from '../../components/common/Card.jsx';
import { Layers, CalendarDays, Search, Download } from 'lucide-react';

export default function SchedulePage() {
  const [wbsData, setWbsData] = useState([]);
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [activeTab, setActiveTab] = useState('gantt'); // 'gantt' | 'tree'

  useEffect(() => {
    scheduleService.getWBSTree('PRJ-METRO-03').then((data) => {
      setWbsData(data);
      if (data[0]?.children[1]?.children[0]?.children[0]?.activities[0]) {
        setSelectedActivity(data[0].children[1].children[0].children[0].activities[0]);
      }
    });
  }, []);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <CalendarDays className="w-6 h-6 text-blue-600" />
            Primavera P6 & MS Project Schedule View
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Level 5 (L5 Work Packages) & Level 6 (L6 Granular Field Activities) Baseline vs Approved Progress
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex bg-slate-200/80 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab('gantt')}
              className={`px-3 py-1 text-xs font-bold rounded-md transition-all cursor-pointer ${
                activeTab === 'gantt' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Gantt Timeline
            </button>
            <button
              onClick={() => setActiveTab('tree')}
              className={`px-3 py-1 text-xs font-bold rounded-md transition-all cursor-pointer ${
                activeTab === 'tree' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              WBS Tree View
            </button>
          </div>

          <button className="px-3 py-1.5 rounded-lg bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold flex items-center gap-1.5 border border-slate-300 shadow-2xs cursor-pointer">
            <Download className="w-4 h-4" />
            <span>Export Schedule XER/XML</span>
          </button>
        </div>
      </div>

      {/* Main Split Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          {activeTab === 'gantt' ? (
            <GanttChart
              selectedActivity={selectedActivity}
              onSelectActivity={setSelectedActivity}
            />
          ) : (
            <Card title="Work Breakdown Structure (WBS)" subtitle="Expand nodes to inspect L5 work packages & L6 field tasks">
              <WBSTree
                wbsData={wbsData}
                selectedActivity={selectedActivity}
                onSelectActivity={setSelectedActivity}
              />
            </Card>
          )}
        </div>

        {/* Right Detail Side Drawer */}
        <div className="space-y-4">
          <L5L6ActivityDetail activity={selectedActivity} />
        </div>
      </div>
    </div>
  );
}
