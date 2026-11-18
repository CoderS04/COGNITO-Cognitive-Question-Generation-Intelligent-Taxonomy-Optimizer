import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, 
  Download, 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle, 
  RefreshCw, 
  FileText, 
  ShieldCheck, 
  Trash2,
  Share2,
  Replace
} from 'lucide-react';
import api from '../services/api';
import QuestionCard from '../components/QuestionCard';
import ExportModal from '../components/ExportModal';

export default function PaperDetail({ paperId, onBack }) {
  const [paper, setPaper] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('paper'); // 'paper' | 'validation'
  const [validationResult, setValidationResult] = useState(null);
  const [refining, setRefining] = useState(false);
  const [refineResult, setRefineResult] = useState(null);
  const [exportModalOpen, setExportModalOpen] = useState(false);

  useEffect(() => {
    loadPaper();
  }, [paperId]);

  const loadPaper = async () => {
    try {
      setLoading(true);
      const res = await api.getPaperDetail(paperId);
      setPaper(res.data);
      // Run validation audit query
      const vRes = await api.validatePaper(paperId);
      setValidationResult(vRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAutoRefine = async () => {
    setRefining(true);
    try {
      const res = await api.autoRefinePaper(paperId);
      setRefineResult(res.data);
      await loadPaper();
    } catch (err) {
      console.error(err);
    } finally {
      setRefining(false);
    }
  };

  const handleReplaceQuestion = async (paperQuestionId) => {
    try {
      await api.replaceQuestion(paperId, {
        paper_id: paperId,
        paper_question_id: paperQuestionId
      });
      await loadPaper();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading || !paper) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-400 text-sm">
        Loading examination blueprint and validation metrics...
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      
      {/* Navigation & Actions Top Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <button
          onClick={onBack}
          className="flex items-center space-x-1 text-slate-600 hover:text-slate-900 text-xs font-semibold px-2 py-1.5 rounded-lg hover:bg-slate-100 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </button>

        <div className="flex items-center space-x-2">
          <button
            onClick={async () => {
              try {
                const res = await api.savePaperQuestions(paperId, {});
                alert(`Saved ${res.data.saved} new questions; ${res.data.already_exists} matched existing bank questions.`);
              } catch (err) {
                alert(err.response?.data?.detail || err.message);
              }
            }}
            className="flex items-center space-x-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 text-xs font-bold px-3 py-2 rounded-lg"
          >
            <span>Save Questions to Bank</span>
          </button>
          <button
            onClick={handleAutoRefine}
            disabled={refining}
            className="flex items-center space-x-1.5 bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200 text-xs font-bold px-3 py-2 rounded-lg transition"
          >
            <Sparkles className="w-3.5 h-3.5 text-purple-600" />
            <span>{refining ? 'Refining...' : 'Closed-Loop Auto-Refine'}</span>
          </button>

          <button
            onClick={() => setExportModalOpen(true)}
            className="flex items-center space-x-1.5 bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold px-4 py-2 rounded-lg shadow-sm transition"
          >
            <Download className="w-4 h-4" />
            <span>Export & Publish</span>
          </button>
        </div>
      </div>

      {/* Paper Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-3">
        <div className="flex flex-wrap justify-between items-start gap-2">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold font-mono text-brand-700 bg-brand-50 px-2 py-0.5 rounded border border-brand-200">
                {paper.academic_year} | {paper.semester}
              </span>
              <span className="text-xs text-slate-400 font-mono">Paper ID: #{paper.id}</span>
            </div>
            <h1 className="text-xl font-extrabold text-slate-900 mt-1">{paper.title}</h1>
          </div>

          <div className="text-right">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Compliance Score</span>
            <div className="flex items-center space-x-1 text-emerald-700 font-extrabold text-xl font-mono">
              <ShieldCheck className="w-5 h-5 text-emerald-500" />
              <span>{Math.round(paper.cas_score * 100)}% CAS</span>
            </div>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex space-x-2 border-b border-slate-100 pt-2">
          <button
            onClick={() => setActiveTab('paper')}
            className={`pb-2 text-xs font-bold border-b-2 transition ${
              activeTab === 'paper' ? 'border-brand-600 text-brand-600' : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            Examination Paper Blueprint
          </button>
          <button
            onClick={() => setActiveTab('validation')}
            className={`pb-2 text-xs font-bold border-b-2 transition ${
              activeTab === 'validation' ? 'border-brand-600 text-brand-600' : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            Independent Validation Report
          </button>
        </div>
      </div>

      {/* Auto-Refine Status Notice */}
      {refineResult && (
        <div className="bg-purple-50 border border-purple-200 text-purple-900 p-4 rounded-xl text-xs space-y-1">
          <div className="flex justify-between font-bold">
            <span>Closed-Loop Refinement Completed:</span>
            <span>CAS: {Math.round(refineResult.initial_cas * 100)}% → {Math.round(refineResult.final_cas * 100)}%</span>
          </div>
          <ul className="list-disc pl-4 space-y-0.5 text-purple-800">
            {refineResult.actions_taken.map((act, i) => (
              <li key={i}>{act}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Tab 1: Examination Paper Blueprint */}
      {activeTab === 'paper' && (
        <div className="space-y-6">
          {paper.sections.map((section) => (
            <div key={section.id} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
              <div className="flex justify-between items-center border-b border-slate-100 pb-3">
                <div>
                  <h3 className="font-bold text-slate-800 text-sm">{section.section_name}</h3>
                  {section.instructions && (
                    <p className="text-xs text-slate-500 italic mt-0.5">{section.instructions}</p>
                  )}
                </div>
                <span className="font-mono text-xs font-bold bg-slate-100 text-slate-700 px-2.5 py-1 rounded">
                  {section.total_marks} Marks
                </span>
              </div>

              <div className="space-y-3">
                {section.questions.map((pq) => (
                  <div key={pq.id} className="relative group">
                    <QuestionCard
                      question={pq.question}
                      label={pq.sub_question_label}
                      paperId={paperId}
                      paperQuestionId={pq.id}
                      onReplaced={loadPaper}
                    />
                    <div className="mt-1 flex justify-end">
                      <button
                        onClick={() => handleReplaceQuestion(pq.id)}
                        className="text-[11px] text-slate-400 hover:text-brand-600 flex items-center space-x-1"
                      >
                        <Replace className="w-3 h-3" />
                        <span>Swap Alternative Question</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 2: Validation Audit Details */}
      {activeTab === 'validation' && validationResult && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
          <div>
            <h3 className="text-base font-bold text-slate-900">Independent Academic Quality Audit</h3>
            <p className="text-xs text-slate-500">Comprehensive Assessment Score (CAS) formula evaluation</p>
          </div>

          {/* Metric Breakdown Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
            {[
              { label: 'Syllabus Coverage (S)', val: validationResult.metrics.syllabus_coverage, weight: '25%' },
              { label: "Bloom's Compliance (B)", val: validationResult.metrics.bloom_compliance, weight: '25%' },
              { label: 'Difficulty Compliance (D)', val: validationResult.metrics.difficulty_compliance, weight: '20%' },
              { label: 'Marks Verification (M)', val: validationResult.metrics.marks_compliance, weight: '15%' },
              { label: 'Novelty & Non-Repetition (N)', val: validationResult.metrics.repetition_score, weight: '10%' },
              { label: 'Template Compliance (T)', val: validationResult.metrics.template_compliance, weight: '5%' },
            ].map((m) => (
              <div key={m.label} className="p-3 bg-slate-50 rounded-xl border border-slate-200/80">
                <span className="text-[11px] text-slate-500 block font-medium">{m.label}</span>
                <span className="text-lg font-bold font-mono text-slate-800 mt-1 block">
                  {Math.round(m.val * 100)}%
                </span>
                <span className="text-[10px] text-slate-400">Weight: {m.weight}</span>
              </div>
            ))}
          </div>

          {/* Violations / Warnings */}
          {validationResult.violations && validationResult.violations.length > 0 && (
            <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs space-y-1">
              <span className="font-bold text-rose-800 flex items-center space-x-1">
                <AlertTriangle className="w-4 h-4 text-rose-600" />
                <span>Detected Violations:</span>
              </span>
              <ul className="list-disc pl-5 text-rose-700 space-y-0.5">
                {validationResult.violations.map((v, i) => (
                  <li key={i}>{v}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {validationResult.recommendations && validationResult.recommendations.length > 0 && (
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-xs space-y-1">
              <span className="font-bold text-amber-800 flex items-center space-x-1">
                <CheckCircle2 className="w-4 h-4 text-amber-600" />
                <span>Actionable Recommendations:</span>
              </span>
              <ul className="list-disc pl-5 text-amber-700 space-y-0.5">
                {validationResult.recommendations.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Export Modal */}
      {exportModalOpen && (
        <ExportModal paper={paper} onClose={() => setExportModalOpen(false)} />
      )}

    </div>
  );
}
