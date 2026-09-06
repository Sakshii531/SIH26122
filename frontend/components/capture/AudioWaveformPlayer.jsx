'use client';

import React, { useState } from 'react';
import { Play, Pause, Mic, Volume2, Sparkles, User, Clock } from 'lucide-react';
import { MOCK_VOICE_TRANSCRIPT } from '../../services/mock/mockExtractions.js';
import { Card } from '../common/Card.jsx';

export function AudioWaveformPlayer() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeSegmentIndex, setActiveSegmentIndex] = useState(1);

  return (
    <Card
      title="Voice Record Audio Player & Speech-to-Text (ASR) Live Stream"
      subtitle="File: AUDIO_REC_ErRajesh_20260905_1645.wav (Recorded by Er. Rajesh Sharma, Site Supervisor)"
      action={
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1 text-xs text-blue-700 bg-blue-50 px-2 py-1 rounded-full border border-blue-200 font-bold">
            <Sparkles className="w-3.5 h-3.5" /> ASR Transcribed
          </span>
        </div>
      }
    >
      <div className="space-y-4">
        {/* Waveform Player Bar */}
        <div className="p-4 rounded-xl bg-slate-900 text-white flex items-center gap-4 shadow-md">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="w-11 h-11 rounded-full bg-blue-500 hover:bg-blue-400 text-white flex items-center justify-center transition-all shadow-md shrink-0 cursor-pointer"
          >
            {isPlaying ? <Pause className="w-5 h-5 fill-current" /> : <Play className="w-5 h-5 fill-current ml-0.5" />}
          </button>

          {/* Waveform Bars */}
          <div className="flex-1 flex items-center gap-1 h-10 overflow-hidden">
            {Array.from({ length: 48 }).map((_, i) => {
              const heightPct = Math.max(20, Math.sin(i * 0.4) * 80 + Math.random() * 20);
              const isActive = i >= 12 && i <= 32;
              return (
                <div
                  key={i}
                  className={`flex-1 rounded-full transition-all ${
                    isActive ? 'bg-blue-400' : 'bg-slate-700'
                  }`}
                  style={{ height: `${heightPct}%` }}
                />
              );
            })}
          </div>

          <div className="text-right font-mono text-xs text-slate-300 shrink-0">
            <span className="text-blue-400 font-bold">00:45</span> / 01:05
          </div>
        </div>

        {/* Synchronized Transcript Stream */}
        <div className="space-y-2">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Speech-to-Text (ASR) Live Transcript Stream</p>
          <div className="space-y-2">
            {MOCK_VOICE_TRANSCRIPT.map((seg, idx) => {
              const isCurrent = idx === activeSegmentIndex;
              return (
                <div
                  key={idx}
                  onClick={() => setActiveSegmentIndex(idx)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                    isCurrent
                      ? 'bg-blue-50/80 border-blue-400 shadow-2xs'
                      : 'bg-white border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs mb-1">
                    <div className="flex items-center gap-2">
                      <User className="w-3.5 h-3.5 text-blue-600" />
                      <span className="font-bold text-slate-900">{seg.speaker}</span>
                    </div>
                    <span className="font-mono text-[10px] text-slate-500 font-semibold flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      00:{seg.startTime < 10 ? '0' : ''}{seg.startTime} - 00:{seg.endTime}
                    </span>
                  </div>

                  <p className="text-xs text-slate-700 leading-relaxed font-medium">{seg.text}</p>

                  {/* Highlighted Terms */}
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {seg.keyTerms.map((term, tIdx) => (
                      <span
                        key={tIdx}
                        className="text-[10px] font-mono text-blue-700 bg-blue-100 px-2 py-0.5 rounded border border-blue-200 font-bold"
                      >
                        #{term}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </Card>
  );
}
