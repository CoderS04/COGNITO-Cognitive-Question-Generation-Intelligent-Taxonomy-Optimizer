import React from 'react';
import { Download, FileText, FileCode, CheckCircle2, ShieldCheck, X } from 'lucide-react';
import api from '../services/api';

export default function ExportModal({ paper, onClose }) {
  if (!paper) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-5 animate-in fade-in duration-150">
        
        {/* Header */}
        <div className="flex justify-between items-start border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
              <Download className="w-5 h-5 text-brand-600" />
              <span>Export & Publish Examination Paper</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Standardized formatting ready for institutional archiving and printing.
            </p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Paper Overview */}
        <div className="bg-slate-50 rounded-xl p-3 border border-slate-200 text-xs space-y-1.5">
          <div className="flex justify-between">
            <span className="font-semibold text-slate-600">Paper Title:</span>
            <span className="font-bold text-slate-800 text-right">{paper.title}</span>
          </div>
          <div className="flex justify-between">
            <span className="font-semibold text-slate-600">Total Marks:</span>
            <span className="font-mono font-bold text-slate-800">{paper.total_marks} Marks</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="font-semibold text-slate-600">Validation Status:</span>
            <span className="flex items-center space-x-1 text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-bold">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>CAS Verified ({Math.round(paper.cas_score * 100)}%)</span>
            </span>
          </div>
        </div>

        {/* Export Options */}
        <div className="space-y-2.5">
          {/* PDF */}
          <a
            href={api.getPdfDownloadUrl(paper.id)}
            download
            className="flex items-center justify-between p-3.5 rounded-xl border border-slate-200 hover:border-brand-500 hover:bg-brand-50/50 transition-all group"
          >
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center font-bold text-xs border border-rose-100">
                PDF
              </div>
              <div>
                <p className="text-sm font-bold text-slate-800 group-hover:text-brand-700">
                  Publication Academic PDF
                </p>
                <p className="text-[11px] text-slate-500">
                  University header, instructions, marking scheme, and cognitive tags.
                </p>
              </div>
            </div>
            <Download className="w-4 h-4 text-slate-400 group-hover:text-brand-600" />
          </a>

          {/* Word DOCX */}
          <a
            href={api.getDocxDownloadUrl(paper.id)}
            download
            className="flex items-center justify-between p-3.5 rounded-xl border border-slate-200 hover:border-blue-500 hover:bg-blue-50/50 transition-all group"
          >
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xs border border-blue-100">
                DOCX
              </div>
              <div>
                <p className="text-sm font-bold text-slate-800 group-hover:text-blue-700">
                  Microsoft Word Document
                </p>
                <p className="text-[11px] text-slate-500">
                  Editable format for examiners and departmental moderation committees.
                </p>
              </div>
            </div>
            <Download className="w-4 h-4 text-slate-400 group-hover:text-blue-600" />
          </a>

          {/* JSON */}
          <a
            href={api.getJsonDownloadUrl(paper.id)}
            download
            className="flex items-center justify-between p-3.5 rounded-xl border border-slate-200 hover:border-purple-500 hover:bg-purple-50/50 transition-all group"
          >
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center font-bold text-xs border border-purple-100">
                JSON
              </div>
              <div>
                <p className="text-sm font-bold text-slate-800 group-hover:text-purple-700">
                  Structured Assessment JSON
                </p>
                <p className="text-[11px] text-slate-500">
                  Machine-readable schema with full taxonomy metadata for LMS import.
                </p>
              </div>
            </div>
            <FileCode className="w-4 h-4 text-slate-400 group-hover:text-purple-600" />
          </a>
        </div>

        <div className="pt-2 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
}
