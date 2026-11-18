import React from 'react';
import { ShieldCheck, AlertTriangle, XCircle, CheckCircle } from 'lucide-react';

export default function ComplianceGauge({ casScore, status }) {
  const scorePct = Math.round((casScore || 0) * 100);

  let color = 'text-emerald-600 bg-emerald-50 border-emerald-200';
  let badgeText = 'Fully Approved';
  let Icon = CheckCircle;

  if (scorePct < 70 || status === 'FAILED') {
    color = 'text-rose-600 bg-rose-50 border-rose-200';
    badgeText = 'Validation Failed';
    Icon = XCircle;
  } else if (scorePct < 82 || status === 'WARNING') {
    color = 'text-amber-600 bg-amber-50 border-amber-200';
    badgeText = 'Needs Review';
    Icon = AlertTriangle;
  }

  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Comprehensive Assessment Score
        </span>
        <div className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${color}`}>
          <Icon className="w-3.5 h-3.5" />
          <span>{badgeText}</span>
        </div>
      </div>

      <div className="my-4 flex items-baseline space-x-2">
        <span className="text-4xl font-extrabold tracking-tight text-slate-900 font-mono">
          {scorePct}%
        </span>
        <span className="text-xs text-slate-500 font-medium">
          / 100% CAS Target (Threshold: 82%)
        </span>
      </div>

      {/* Progress Bar */}
      <div>
        <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 rounded-full ${
              scorePct >= 82 ? 'bg-emerald-500' : scorePct >= 70 ? 'bg-amber-500' : 'bg-rose-500'
            }`}
            style={{ width: `${Math.min(scorePct, 100)}%` }}
          />
        </div>
        <div className="flex justify-between items-center text-[10px] text-slate-400 mt-1 font-mono">
          <span>0%</span>
          <span className="text-slate-500 font-semibold">Min 82%</span>
          <span>100%</span>
        </div>
      </div>
    </div>
  );
}
