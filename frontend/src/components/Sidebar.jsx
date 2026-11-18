import React from 'react';
import { 
  LayoutDashboard, 
  Sparkles, 
  BookOpen, 
  UploadCloud, 
  Sliders, 
  CheckCircle2, 
  BarChart3, 
  FileText
} from 'lucide-react';

export default function Sidebar({ currentTab, onNavigate }) {
  const menuItems = [
    { id: 'dashboard', label: 'Executive Dashboard', icon: LayoutDashboard, badge: null },
    { id: 'generate', label: 'Paper Generator', icon: Sparkles, badge: 'AI' },
    { id: 'questions', label: 'Question Bank & NLP', icon: BookOpen, badge: null },
    { id: 'documents', label: 'Document Ingestion', icon: UploadCloud, badge: null },
    { id: 'templates', label: 'Institutional Templates', icon: Sliders, badge: null },
    { id: 'validation', label: 'Validation Studio', icon: CheckCircle2, badge: 'CAS' },
    { id: 'analytics', label: 'Cognitive Analytics', icon: BarChart3, badge: null },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 shrink-0 hidden lg:flex flex-col justify-between p-4 min-h-[calc(100vh-4rem)]">
      <div>
        <div className="px-3 py-2 text-xs font-bold uppercase tracking-wider text-slate-400">
          Core Workspaces
        </div>
        <nav className="space-y-1 mt-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-brand-50 text-brand-700 font-semibold'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-brand-600' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                    isActive ? 'bg-brand-200 text-brand-800' : 'bg-slate-100 text-slate-500'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bloom's Quick Reference Widget */}
      <div className="bg-slate-50 rounded-xl p-3 border border-slate-200/80 text-xs">
        <div className="font-semibold text-slate-700 mb-2 flex items-center justify-between">
          <span>Bloom's Levels</span>
          <span className="text-[10px] text-brand-600 font-mono">L1 - L6</span>
        </div>
        <div className="space-y-1 font-mono text-[11px]">
          <div className="flex justify-between items-center text-slate-600">
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-emerald-500"></span>L1 Remember</span>
            <span className="text-slate-400">Recall</span>
          </div>
          <div className="flex justify-between items-center text-slate-600">
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-cyan-500"></span>L2 Understand</span>
            <span className="text-slate-400">Explain</span>
          </div>
          <div className="flex justify-between items-center text-slate-600">
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-blue-500"></span>L3 Apply</span>
            <span className="text-slate-400">Solve</span>
          </div>
          <div className="flex justify-between items-center text-slate-600">
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-purple-500"></span>L4 Analyze</span>
            <span className="text-slate-400">Compare</span>
          </div>
          <div className="flex justify-between items-center text-slate-600">
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-amber-500"></span>L5 Evaluate</span>
            <span className="text-slate-400">Critique</span>
          </div>
          <div className="flex justify-between items-center text-slate-600">
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-red-500"></span>L6 Create</span>
            <span className="text-slate-400">Design</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
