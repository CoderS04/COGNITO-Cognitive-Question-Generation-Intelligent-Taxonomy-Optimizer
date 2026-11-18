import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  CheckCircle2, 
  Sliders, 
  BookOpen, 
  Layers, 
  Cpu, 
  ArrowRight, 
  Check, 
  FileText,
  Download
} from 'lucide-react';
import api from '../services/api';

export default function PaperGenerator({ onSelectPaper }) {
  const [courses, setCourses] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [title, setTitle] = useState('End-Semester Examination - Artificial Intelligence');
  const [totalMarks, setTotalMarks] = useState(50);
  const [noveltyThreshold, setNoveltyThreshold] = useState(0.85);

  // Target Bloom's Percentages
  const [bloomTargets, setBloomTargets] = useState({
    L1: 10,
    L2: 20,
    L3: 30,
    L4: 25,
    L5: 10,
    L6: 5
  });

  // Target Difficulty Percentages
  const [diffTargets, setDiffTargets] = useState({
    Easy: 30,
    Medium: 50,
    Hard: 20
  });

  const [generating, setGenerating] = useState(false);
  const [generatedPaper, setGeneratedPaper] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    loadPrerequisites();
  }, []);

  const loadPrerequisites = async () => {
    try {
      const [cRes, tRes] = await Promise.all([
        api.getCourses(),
        api.getTemplates()
      ]);
      setCourses(cRes.data);
      if (cRes.data.length > 0) {
        setSelectedCourse(cRes.data[0].id);
      }
      setTemplates(tRes.data);
      if (tRes.data.length > 0) {
        setSelectedTemplate(tRes.data[0].id);
        if (tRes.data[0].total_marks) {
          setTotalMarks(tRes.data[0].total_marks);
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleTemplateChange = (tplId) => {
    setSelectedTemplate(tplId);
    const tpl = templates.find((t) => t.id === parseInt(tplId));
    if (tpl) {
      setTotalMarks(tpl.total_marks);
      if (tpl.bloom_targets) setBloomTargets(tpl.bloom_targets);
      if (tpl.difficulty_targets) setDiffTargets(tpl.difficulty_targets);
      setTitle(`${tpl.name} - Artificial Intelligence`);
    }
  };

  const handleBloomChange = (level, val) => {
    setBloomTargets((prev) => ({
      ...prev,
      [level]: Math.max(0, parseInt(val) || 0)
    }));
  };

  const handleDiffChange = (cat, val) => {
    setDiffTargets((prev) => ({
      ...prev,
      [cat]: Math.max(0, parseInt(val) || 0)
    }));
  };

  const totalBloom = Object.values(bloomTargets).reduce((a, b) => a + b, 0);
  const totalDiff = Object.values(diffTargets).reduce((a, b) => a + b, 0);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setGenerating(true);
    setErrorMsg('');
    try {
      const payload = {
        course_id: parseInt(selectedCourse),
        template_id: selectedTemplate ? parseInt(selectedTemplate) : null,
        title: title,
        total_marks: parseInt(totalMarks),
        bloom_targets: bloomTargets,
        difficulty_targets: diffTargets,
        novelty_threshold: parseFloat(noveltyThreshold),
        enable_optimization: true
      };

      const res = await api.generatePaper(payload);
      setGeneratedPaper(res.data);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Generation failed. Ensure course syllabus is populated.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      
      {/* Header */}
      <div>
        <h2 className="text-xl font-extrabold text-slate-900 tracking-tight flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-brand-600" />
          <span>Intelligent Question Paper Generator & Optimizer</span>
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          Configure institutional exam constraints, Bloom's cognitive weightage, and difficulty parameters.
        </p>
      </div>

      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl text-xs font-medium">
          {errorMsg}
        </div>
      )}

      {/* Generation Form */}
      <form onSubmit={handleGenerate} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
        
        {/* Step 1: Academic Blueprint */}
        <div>
          <h3 className="text-sm font-bold text-slate-800 flex items-center space-x-2 mb-3">
            <span className="w-5 h-5 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center text-xs font-mono">1</span>
            <span>Academic Blueprint & Course Scope</span>
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Target Course</label>
              <select
                value={selectedCourse}
                onChange={(e) => setSelectedCourse(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg p-2.5 focus:ring-2 focus:ring-brand-500 font-medium"
              >
                {courses.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.code} - {c.title}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Institutional Template</label>
              <select
                value={selectedTemplate}
                onChange={(e) => handleTemplateChange(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg p-2.5 focus:ring-2 focus:ring-brand-500 font-medium"
              >
                {templates.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name} ({t.total_marks}M)
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Total Marks</label>
              <input
                type="number"
                value={totalMarks}
                onChange={(e) => setTotalMarks(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg p-2.5 focus:ring-2 focus:ring-brand-500 font-mono font-bold"
              />
            </div>
          </div>

          <div className="mt-3">
            <label className="block text-xs font-semibold text-slate-700 mb-1">Examination Paper Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg p-2.5 focus:ring-2 focus:ring-brand-500 font-medium"
              required
            />
          </div>
        </div>

        <hr className="border-slate-100" />

        {/* Step 2: Bloom's Taxonomy Targets */}
        <div>
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-sm font-bold text-slate-800 flex items-center space-x-2">
              <span className="w-5 h-5 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center text-xs font-mono">2</span>
              <span>Bloom's Taxonomy Target Distribution (%)</span>
            </h3>
            <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
              totalBloom === 100 ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
            }`}>
              Total: {totalBloom}% {totalBloom === 100 ? '✓' : '(Must sum to 100%)'}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {[
              { lvl: 'L1', name: 'Remember', color: 'border-emerald-300' },
              { lvl: 'L2', name: 'Understand', color: 'border-cyan-300' },
              { lvl: 'L3', name: 'Apply', color: 'border-blue-300' },
              { lvl: 'L4', name: 'Analyze', color: 'border-purple-300' },
              { lvl: 'L5', name: 'Evaluate', color: 'border-amber-300' },
              { lvl: 'L6', name: 'Create', color: 'border-rose-300' },
            ].map((item) => (
              <div key={item.lvl} className={`p-3 rounded-xl border bg-slate-50/60 ${item.color}`}>
                <div className="flex justify-between items-center text-xs font-bold text-slate-700">
                  <span>{item.lvl}</span>
                  <span className="text-[10px] text-slate-400 font-normal">{item.name}</span>
                </div>
                <div className="mt-1.5 flex items-center space-x-1">
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={bloomTargets[item.lvl]}
                    onChange={(e) => handleBloomChange(item.lvl, e.target.value)}
                    className="w-full text-xs font-mono font-bold bg-white border border-slate-200 rounded p-1.5 text-center"
                  />
                  <span className="text-xs text-slate-400 font-bold">%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <hr className="border-slate-100" />

        {/* Step 3: Difficulty & Novelty Targets */}
        <div>
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-sm font-bold text-slate-800 flex items-center space-x-2">
              <span className="w-5 h-5 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center text-xs font-mono">3</span>
              <span>Difficulty Ratio & Novelty Safeguards</span>
            </h3>
            <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
              totalDiff === 100 ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
            }`}>
              Total: {totalDiff}% {totalDiff === 100 ? '✓' : '(Must sum to 100%)'}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              { cat: 'Easy', color: 'text-emerald-700' },
              { cat: 'Medium', color: 'text-amber-700' },
              { cat: 'Hard', color: 'text-rose-700' },
            ].map((item) => (
              <div key={item.cat} className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <span className={`text-xs font-bold ${item.color}`}>{item.cat} Questions</span>
                <div className="mt-1.5 flex items-center space-x-1">
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={diffTargets[item.cat]}
                    onChange={(e) => handleDiffChange(item.cat, e.target.value)}
                    className="w-full text-xs font-mono font-bold bg-white border border-slate-200 rounded p-1.5 text-center"
                  />
                  <span className="text-xs text-slate-400 font-bold">%</span>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-slate-800">Historical Repetition Threshold</span>
              <p className="text-[11px] text-slate-500">Flags questions with cosine similarity greater than or equal to this limit.</p>
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="range"
                min="0.70"
                max="0.95"
                step="0.05"
                value={noveltyThreshold}
                onChange={(e) => setNoveltyThreshold(e.target.value)}
                className="w-28 cursor-pointer accent-brand-600"
              />
              <span className="font-mono text-xs font-bold text-brand-700 bg-brand-50 px-2 py-0.5 rounded border border-brand-200">
                {Math.round(noveltyThreshold * 100)}%
              </span>
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={generating}
            className="w-full bg-gradient-to-r from-brand-600 via-brand-700 to-indigo-600 hover:opacity-95 text-white font-bold py-3 rounded-xl shadow-lg shadow-brand-600/20 text-sm flex items-center justify-center space-x-2 transition active:scale-[0.99]"
          >
            <Cpu className="w-4 h-4 animate-spin-slow" />
            <span>{generating ? 'Executing AI Constraint Optimization...' : 'Synthesize & Optimize Question Paper'}</span>
          </button>
        </div>

      </form>

      {/* Generated Paper Result Preview */}
      {generatedPaper && (
        <div className="bg-emerald-50/70 border border-emerald-200 rounded-2xl p-6 space-y-4 animate-in fade-in">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-6 h-6 text-emerald-600" />
              <div>
                <h3 className="font-bold text-emerald-950 text-base">Paper Generated & Validated Successfully!</h3>
                <p className="text-xs text-emerald-700">Initial CAS Score: {Math.round(generatedPaper.cas_score * 100)}%</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={() => onSelectPaper(generatedPaper.id)}
                className="bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold px-4 py-2 rounded-lg transition"
              >
                Inspect Paper Details
              </button>
              <button
                onClick={async () => {
                  try {
                    const res = await api.savePaperQuestions(generatedPaper.id, {});
                    alert(`Saved ${res.data.saved} new questions; ${res.data.already_exists} matched existing bank questions.`);
                  } catch (err) {
                    alert(err.response?.data?.detail || err.message);
                  }
                }}
                className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold px-4 py-2 rounded-lg"
              >
                Save New Questions to Bank
              </button>
              <a
                href={api.getPdfDownloadUrl(generatedPaper.id)}
                download
                className="bg-white border border-slate-200 text-slate-700 text-xs font-semibold px-3 py-2 rounded-lg hover:bg-slate-50 transition flex items-center space-x-1"
              >
                <Download className="w-3.5 h-3.5" />
                <span>PDF</span>
              </a>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
