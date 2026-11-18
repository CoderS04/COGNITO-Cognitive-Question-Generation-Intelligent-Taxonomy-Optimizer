import React from 'react';
import { Brain, Sparkles, ShieldCheck, GraduationCap, FileCheck } from 'lucide-react';

export default function Navbar({ onNavigate }) {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand / Logo */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onNavigate('dashboard')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-700 via-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
            <Brain className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-brand-800 to-indigo-600 bg-clip-text text-transparent">
                COGNITO
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-bold tracking-wide uppercase bg-brand-50 text-brand-700 border border-brand-200 rounded">
                v1.0 AI
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-medium hidden sm:block">
              Cognitive Question Generation & Intelligent Taxonomy Optimizer
            </p>
          </div>
        </div>

        {/* Institution & Actions */}
        <div className="flex items-center space-x-4">
          <div className="hidden md:flex items-center space-x-2 text-xs text-slate-600 bg-slate-100/80 px-3 py-1.5 rounded-full border border-slate-200">
            <GraduationCap className="w-4 h-4 text-brand-600" />
            <span className="font-medium text-slate-700">Vishwakarma Institute of Technology</span>
            <span className="text-slate-300">|</span>
            <span className="text-slate-500">Autonomous Institute</span>
          </div>

          <div className="flex items-center space-x-1.5 bg-emerald-50 text-emerald-700 text-xs px-2.5 py-1 rounded-full font-medium border border-emerald-200">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Taxonomy Engine Active</span>
          </div>

          <button
            onClick={() => onNavigate('generate')}
            className="flex items-center space-x-1.5 bg-brand-600 hover:bg-brand-700 active:scale-95 text-white text-xs sm:text-sm font-semibold px-4 py-2 rounded-lg shadow-sm shadow-brand-600/30 transition-all duration-150"
          >
            <Sparkles className="w-4 h-4" />
            <span>Generate Paper</span>
          </button>
        </div>

      </div>
    </header>
  );
}
