import React, { useState, useEffect } from 'react';
import { 
  CheckCircle2, 
  ShieldCheck, 
  AlertTriangle, 
  RefreshCw, 
  Sparkles, 
  Layers, 
  BookOpen
} from 'lucide-react';
import api from '../services/api';
import ComplianceGauge from '../components/ComplianceGauge';

export default function ValidationStudio({ onSelectPaper }) {
  const [papers, setPapers] = useState([]);
  const [selectedPaperId, setSelectedPaperId] = useState('');
  const [audit, setAudit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refining, setRefining] = useState(false);
  const [refineResult, setRefineResult] = useState(null);

  useEffect(() => {
    loadPapers();
  }, []);

  const loadPapers = async () => {
    try {
      setLoading(true);
      const res = await api.getPapers();
      setPapers(res.data);
      if (res.data.length > 0) {
        setSelectedPaperId(res.data[0].id);
        runAudit(res.data[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const runAudit = async (pId) => {
    try {
      const res = await api.validatePaper(pId);
      setAudit(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handlePaperChange = (id) => {
    setSelectedPaperId(id);
    setRefineResult(null);
    runAudit(id);
  };

  const handleAutoRefine = async () => {
    if (!selectedPaperId) return;
    setRefining(true);
    try {
      const res = await api.autoRefinePaper(selectedPaperId);
      setRefineResult(res.data);
      await runAudit(selectedPaperId);
    } catch (err) {
      console.error(err);
    } finally {
      setRefining(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      
      {/* Header */}
      <div className="flex flex-wrap justify-between items-center gap-3">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900 tracking-tight flex items-center space-x-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            <span>Independent Validation & Quality Assurance Studio</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Evaluates syllabus breadth, Bloom's compliance, difficulty ratios, marks parity, and novelty.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <select
            value={selectedPaperId}
            onChange={(e) => handlePaperChange(e.target.value)}
            className="bg-white border border-slate-200 text-xs rounded-xl p-2.5 font-bold shadow-sm focus:ring-2 focus:ring-brand-500"
          >
            {papers.map((p) => (
              <option key={p.id} value={p.id}>
                #{p.id}: {p.title} ({p.total_marks}M)
              </option>
            ))}
          </select>

          <button
            onClick={handleAutoRefine}
            disabled={refining || !selectedPaperId}
            className="bg-purple-600 hover:bg-purple-700 active:scale-95 text-white text-xs font-bold px-4 py-2.5 rounded-xl transition flex items-center space-x-1.5 shadow-sm"
          >
            <Sparkles className="w-4 h-4" />
            <span>{refining ? 'Refining Paper...' : 'Execute Closed-Loop Refinement'}</span>
          </button>
        </div>
      </div>

      {audit && (
        <div className="space-y-6">
          
          {/* Top KPI row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-1">
              <ComplianceGauge casScore={audit.cas_score} status={audit.status} />
            </div>

            <div className="md:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-3">
              <h3 className="font-bold text-slate-900 text-sm">CAS Formula Component Verification</h3>
              <p className="text-xs text-slate-500 font-mono">
                CAS = 0.25*S + 0.25*B + 0.20*D + 0.15*M + 0.10*N + 0.05*T
              </p>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs pt-2">
                {[
                  { name: 'Syllabus (S)', score: audit.metrics.syllabus_coverage },
                  { name: "Bloom's (B)", score: audit.metrics.bloom_compliance },
                  { name: 'Difficulty (D)', score: audit.metrics.difficulty_compliance },
                  { name: 'Marks (M)', score: audit.metrics.marks_compliance },
                  { name: 'Novelty (N)', score: audit.metrics.repetition_score },
                  { name: 'Template (T)', score: audit.metrics.template_compliance },
                ].map((item) => (
                  <div key={item.name} className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <span className="text-[11px] text-slate-500 font-medium block">{item.name}</span>
                    <span className="text-base font-bold font-mono text-slate-800 mt-0.5 block">
                      {Math.round(item.score * 100)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Auto-Refine Feedback Log */}
          {refineResult && (
            <div className="p-4 bg-purple-50 border border-purple-200 rounded-2xl text-xs text-purple-900 space-y-2 animate-in fade-in">
              <div className="flex justify-between items-center font-bold">
                <span>Closed-Loop Refinement Execution Summary:</span>
                <span className="font-mono">
                  Initial CAS: {Math.round(refineResult.initial_cas * 100)}% → Final CAS: {Math.round(refineResult.final_cas * 100)}%
                </span>
              </div>
              <ul className="list-disc pl-5 space-y-1 text-purple-800">
                {refineResult.actions_taken.map((act, i) => (
                  <li key={i}>{act}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Violations & Warnings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <h4 className="font-bold text-slate-900 text-sm flex items-center space-x-1.5 text-rose-700">
                <AlertTriangle className="w-4 h-4 text-rose-500" />
                <span>Detected Imbalances & Violations</span>
              </h4>
              {audit.violations && audit.violations.length > 0 ? (
                <ul className="text-xs text-rose-800 space-y-1.5 list-disc pl-5">
                  {audit.violations.map((v, i) => (
                    <li key={i}>{v}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-emerald-600 font-medium flex items-center space-x-1">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  <span>No hard constraint violations detected. Ready for publication!</span>
                </p>
              )}
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <h4 className="font-bold text-slate-900 text-sm flex items-center space-x-1.5 text-amber-700">
                <Sparkles className="w-4 h-4 text-amber-500" />
                <span>Actionable Recommendations</span>
              </h4>
              {audit.recommendations && audit.recommendations.length > 0 ? (
                <ul className="text-xs text-amber-800 space-y-1.5 list-disc pl-5">
                  {audit.recommendations.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-slate-400">All target parameters optimized.</p>
              )}
            </div>

          </div>

        </div>
      )}

    </div>
  );
}
