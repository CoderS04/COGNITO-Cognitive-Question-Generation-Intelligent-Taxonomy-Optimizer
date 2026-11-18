import React, { useEffect, useState } from 'react';
import { 
  Sparkles, 
  HelpCircle, 
  Layers, 
  Check, 
  ArrowUpRight, 
  FileSearch, 
  ChevronDown, 
  ChevronUp,
  Clock
} from 'lucide-react';
import api from '../services/api';

const BLOOM_COLORS = {
  L1: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  L2: 'bg-cyan-50 text-cyan-700 border-cyan-200',
  L3: 'bg-blue-50 text-blue-700 border-blue-200',
  L4: 'bg-purple-50 text-purple-700 border-purple-200',
  L5: 'bg-amber-50 text-amber-700 border-amber-200',
  L6: 'bg-rose-50 text-rose-700 border-rose-200',
};

const DIFFICULTY_COLORS = {
  Easy: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  Medium: 'bg-amber-50 text-amber-700 border-amber-200',
  Hard: 'bg-rose-50 text-rose-700 border-rose-200',
};

export default function QuestionCard({ question, label, onReplaced, paperId, paperQuestionId, bankMode = false }) {
  const [showSolution, setShowSolution] = useState(false);
  const [reframeModalOpen, setReframeModalOpen] = useState(false);
  const [targetLevel, setTargetLevel] = useState('L4');
  const [reframing, setReframing] = useState(false);
  const [reframeResult, setReframeResult] = useState(null);

  const [simChecking, setSimChecking] = useState(false);
  const [simResult, setSimResult] = useState(null);
  const [alternatives, setAlternatives] = useState([]);
  const [loadingAlternatives, setLoadingAlternatives] = useState(false);
  const [customPrompt, setCustomPrompt] = useState('');
  const [pendingReplacement, setPendingReplacement] = useState(null);

  useEffect(() => {
    if (!reframeModalOpen || !paperId || !paperQuestionId) return;
    const loadAlternatives = async () => {
      setLoadingAlternatives(true);
      try {
        const res = await api.getQuestionAlternatives(paperId, paperQuestionId);
        setAlternatives(res.data.alternatives || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingAlternatives(false);
      }
    };
    loadAlternatives();
  }, [reframeModalOpen, paperId, paperQuestionId]);

  const handleReframe = async () => {
    setReframing(true);
    try {
      const res = await api.reframeQuestion({
        question_id: question.id,
        target_level: targetLevel,
        custom_prompt: customPrompt,
      });
      setReframeResult(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setReframing(false);
    }
  };

  const handleSaveReplacement = async (alternative) => {
    if (!paperId || !paperQuestionId) return;
    setPendingReplacement(alternative);
  };

  const confirmReplacement = async () => {
    if (!pendingReplacement || !paperId || !paperQuestionId) return;
    try {
      await api.replaceQuestion(paperId, {
        paper_id: paperId,
        paper_question_id: paperQuestionId,
        replacement_question_id: pendingReplacement?.question_id,
        replacement_text: pendingReplacement?.question_id ? undefined : pendingReplacement?.text,
        target_level: pendingReplacement?.target_level,
        marks: pendingReplacement?.marks,
        primary_verb: pendingReplacement?.primary_verb,
        solution_outline: pendingReplacement?.solution_outline,
      });
      setReframeModalOpen(false);
      setReframeResult(null);
      setPendingReplacement(null);
      if (onReplaced) onReplaced();
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    }
  };

  const handleSimCheck = async () => {
    setSimChecking(true);
    try {
      const res = await api.checkSimilarity({
        text: question.text,
        course_id: question.course_id,
        question_id: question.id,
      });
      setSimResult(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setSimChecking(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 p-4 shadow-sm hover:border-brand-300 transition-all">
      {/* Header Tags */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-2.5">
        <div className="flex items-center space-x-2">
          {label && (
            <span className="font-mono text-xs font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
              {label}
            </span>
          )}
          <span className={`text-[11px] font-bold px-2 py-0.5 rounded border ${BLOOM_COLORS[question.bloom_level] || 'bg-slate-50'}`}>
            {question.bloom_level} ({question.primary_verb || 'Cognitive'})
          </span>
          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded border ${DIFFICULTY_COLORS[question.difficulty] || 'bg-slate-50'}`}>
            {question.difficulty}
          </span>
          {question.is_historical && (
            <span className="text-[10px] bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded flex items-center gap-1 font-mono">
              <Clock className="w-3 h-3" /> Historical ({question.exam_year || 'Past'})
            </span>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <span className="font-bold text-xs font-mono bg-brand-50 text-brand-700 border border-brand-200 px-2 py-0.5 rounded">
            {question.marks} Marks
          </span>
        </div>
      </div>

      {/* Question Text */}
      <p className="text-sm text-slate-800 leading-relaxed font-normal">
        {question.text}
      </p>

      {/* Action Footer */}
      <div className="mt-3 pt-2.5 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex items-center space-x-2">
          {paperId && paperQuestionId && (
            <button
              onClick={() => setReframeModalOpen(true)}
              className="flex items-center space-x-1 text-purple-600 hover:text-purple-700 hover:bg-purple-50 px-2 py-1 rounded font-medium transition"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Edit / Reframe</span>
            </button>
          )}

          <button
            onClick={handleSimCheck}
            disabled={simChecking}
            className="flex items-center space-x-1 text-slate-500 hover:text-brand-600 hover:bg-slate-50 px-2 py-1 rounded transition"
          >
            <FileSearch className="w-3.5 h-3.5" />
            <span>{simChecking ? 'Checking...' : 'Check Repetition'}</span>
          </button>
        </div>

        {question.solution_outline && (
          <button
            onClick={() => setShowSolution(!showSolution)}
            className="text-slate-400 hover:text-slate-600 flex items-center space-x-0.5"
          >
            <span>Grading Outline</span>
            {showSolution ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        )}
      </div>

      {/* Similarity Alert Banner */}
      {simResult && (
        <div className={`mt-2.5 p-2.5 rounded-lg text-xs border ${
          simResult.is_repetition
            ? 'bg-rose-50 border-rose-200 text-rose-800'
            : simResult.is_paraphrase
            ? 'bg-amber-50 border-amber-200 text-amber-800'
            : 'bg-emerald-50 border-emerald-200 text-emerald-800'
        }`}>
          <div className="flex justify-between items-center font-semibold">
            <span>
              {simResult.is_repetition ? '⚠️ Direct Repetition Flagged' : simResult.is_paraphrase ? '⚡ Paraphrased Duplicate' : '✓ Highly Novel Question'}
            </span>
            <span>Max Similarity: {Math.round(simResult.max_similarity * 100)}%</span>
          </div>
          {simResult.matches && simResult.matches.length > 0 && (
            <p className="mt-1 text-[11px] opacity-90 truncate">
              Matches: "{simResult.matches[0].text}" ({simResult.matches[0].exam_year || 'Past'})
            </p>
          )}
        </div>
      )}

      {/* Solution Outline Box */}
      {showSolution && question.solution_outline && (
        <div className="mt-2.5 p-3 bg-slate-50 rounded-lg text-xs text-slate-600 border border-slate-200/70 font-mono leading-relaxed">
          <p className="font-bold text-slate-700 mb-1">Expected Solution / Assessment Rubric:</p>
          {question.solution_outline}
        </div>
      )}

      {/* Reframe Modal */}
      {reframeModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden shadow-2xl border border-slate-200 flex flex-col">
            <div className="flex justify-between items-center border-b border-slate-100 p-6 pb-3">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-purple-600" />
                <h3 className="font-bold text-slate-800">Edit Question</h3>
              </div>
              <button onClick={() => { setReframeModalOpen(false); setReframeResult(null); setPendingReplacement(null); }} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
            </div>
            <div className="overflow-y-auto p-6 space-y-5">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
                <div className="md:col-span-4 p-4 bg-slate-50 border border-slate-200 rounded-xl">
                  <span className="font-bold text-slate-700 block mb-1">Current Question</span>
                  <p className="text-slate-900">{question.text}</p>
                </div>
                <div className="p-3 border rounded-xl"><span className="text-slate-500 block">Topic</span><b>{question.topic_id ? `Topic #${question.topic_id}` : 'Course syllabus'}</b></div>
                <div className="p-3 border rounded-xl"><span className="text-slate-500 block">Marks</span><b>{question.marks}</b></div>
                <div className="p-3 border rounded-xl"><span className="text-slate-500 block">Bloom's Level</span><b>{question.bloom_level}</b></div>
                <div className="p-3 border rounded-xl"><span className="text-slate-500 block">Difficulty</span><b>{question.difficulty}</b></div>
              </div>

              <div>
                <div className="text-xs font-bold text-slate-700 mb-2">Question Bank Alternatives</div>
                {loadingAlternatives ? (
                  <p className="text-xs text-slate-400">Loading alternatives...</p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {alternatives.filter((a) => a.source === 'QUESTION_BANK').map((alternative, index) => (
                      <div key={index} className="border border-slate-200 rounded-xl p-3 text-xs space-y-2">
                        <div className="flex justify-between font-bold"><span>{alternative.target_level}</span><span>{alternative.marks} Marks</span></div>
                        <p>{alternative.text}</p>
                        <button onClick={() => handleSaveReplacement(alternative)} className="text-brand-600 font-bold">Select Alternative</button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="border-t pt-4 space-y-3">
                <div className="text-xs font-bold text-slate-700">Reframe to Bloom's Level</div>
                <div className="grid grid-cols-6 gap-2">
                  {['L1','L2','L3','L4','L5','L6'].map((lvl) => (
                    <button key={lvl} type="button" onClick={() => setTargetLevel(lvl)} className={`py-2 rounded-lg text-xs font-bold border ${targetLevel === lvl ? 'bg-purple-600 text-white border-purple-600' : 'bg-white text-slate-600 border-slate-200'}`}>{lvl}</button>
                  ))}
                </div>
                <label className="block text-xs font-bold text-slate-700">Custom AI Prompt
                  <textarea value={customPrompt} onChange={(e) => setCustomPrompt(e.target.value)} placeholder="Example: Add a real-world constraint, keep it numerical, avoid using CSE examples..." rows={3} className="mt-1 w-full border border-slate-200 rounded-lg p-3 font-normal" />
                </label>
                <button onClick={handleReframe} disabled={reframing} className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2.5 rounded-lg text-xs font-bold flex justify-center gap-2">
                  <Sparkles className="w-4 h-4" /> {reframing ? 'Generating preview...' : `Generate ${targetLevel} Preview`}
                </button>
              </div>

              {reframeResult && (
                <div className="p-4 bg-purple-50 border border-purple-200 rounded-xl space-y-3 text-xs">
                  <div className="flex justify-between font-bold text-purple-900"><span>AI Preview - {reframeResult.target_level}</span><span>{reframeResult.suggested_marks} Marks</span></div>
                  <p className="text-slate-900">{reframeResult.reframed_text}</p>
                  <p className="italic text-purple-700">{reframeResult.explanation}</p>
                  <button onClick={() => handleSaveReplacement({text:reframeResult.reframed_text,target_level:reframeResult.target_level,marks:reframeResult.suggested_marks,primary_verb:reframeResult.primary_verb,solution_outline:reframeResult.rubric_outline})} className="w-full bg-emerald-600 text-white py-2 rounded-lg font-bold">Apply with Human Approval</button>
                </div>
              )}

              {pendingReplacement && (
                <div className="sticky bottom-0 bg-emerald-50 border border-emerald-300 rounded-xl p-4 space-y-3">
                  <b className="text-sm text-emerald-900">Confirm AI / alternative edit</b>
                  <p className="text-xs text-slate-700">{pendingReplacement.text}</p>
                  <div className="flex justify-end gap-2">
                    <button onClick={() => setPendingReplacement(null)} className="px-4 py-2 text-slate-600">Cancel</button>
                    <button onClick={confirmReplacement} className="bg-emerald-600 text-white px-4 py-2 rounded-lg font-bold">Approve & Replace</button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
