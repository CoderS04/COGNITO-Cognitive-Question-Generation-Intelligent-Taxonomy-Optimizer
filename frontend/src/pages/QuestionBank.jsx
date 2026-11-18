import React, { useState, useEffect } from 'react';
import { 
  BookOpen, 
  Search, 
  Filter, 
  Plus, 
  Sparkles, 
  SlidersHorizontal,
  Layers,
  ArrowRight
} from 'lucide-react';
import api from '../services/api';
import QuestionCard from '../components/QuestionCard';

export default function QuestionBank() {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedBloom, setSelectedBloom] = useState('');
  const [selectedDiff, setSelectedDiff] = useState('');
  const [onlyHistorical, setOnlyHistorical] = useState(false);
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [units, setUnits] = useState([]);
  const [selectedUnit, setSelectedUnit] = useState('');
  const [selectedIds, setSelectedIds] = useState([]);
  const [showUnitModal, setShowUnitModal] = useState(false);
  const [unitForm, setUnitForm] = useState({ unit_number: 1, title: '', description: '', target_weightage_pct: 16.67 });
  const [editQuestion, setEditQuestion] = useState(null);
  const [showCourseModal, setShowCourseModal] = useState(false);
  const [courseForm, setCourseForm] = useState({
    code: '',
    title: '',
    department: 'Computer Science & Engineering',
    institution: 'Vishwakarma Institute of Technology',
    semester: 'Semester VI',
    academic_year: '2025-2026',
  });

  // Live AI Analyzer state
  const [analyzerText, setAnalyzerText] = useState('Compare and analyze the asymptotic time complexity of A* search versus Dijkstra algorithm on dense graphs.');
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  // New Question Form state
  const [showAddModal, setShowAddModal] = useState(false);
  const [newText, setNewText] = useState('');
  const [newMarks, setNewMarks] = useState(5);
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    loadCourses();
    loadQuestions();
  }, [selectedBloom, selectedDiff, onlyHistorical]);

  useEffect(() => {
    const course = courses.find((c) => String(c.id) === String(selectedCourse));
    setUnits(course?.units || []);
    setSelectedUnit('');
    loadQuestions();
  }, [selectedCourse]);

  useEffect(() => {
    loadQuestions();
  }, [selectedUnit]);

  const loadCourses = async () => {
    try {
      const res = await api.getCourses();
      setCourses(res.data);
      if (!selectedCourse && res.data.length > 0) {
        const first = res.data[0];
        setSelectedCourse(String(first.id));
        setUnits(first.units || []);
      } else {
        const course = res.data.find((c) => String(c.id) === String(selectedCourse));
        setUnits(course?.units || []);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const loadQuestions = async () => {
    try {
      setLoading(true);
      const params = {};
      if (selectedBloom) params.bloom_level = selectedBloom;
      if (selectedDiff) params.difficulty = selectedDiff;
      if (onlyHistorical) params.is_historical = true;
      if (search) params.search = search;
      if (selectedCourse) params.course_id = selectedCourse;
      if (selectedUnit) params.unit_id = selectedUnit;

      const res = await api.getQuestions(params);
      setQuestions(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadQuestions();
  };

  const handleRunAnalyzer = async () => {
    if (!analyzerText.trim()) return;
    setAnalyzing(true);
    try {
      const res = await api.analyzeQuestion({
        text: analyzerText,
        marks: 6,
        course_id: selectedCourse ? parseInt(selectedCourse) : null,
      });
      setAnalysisResult(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleAddQuestion = async (e) => {
    e.preventDefault();
    if (!newText.trim()) return;
    setAdding(true);
    try {
      await api.addQuestion({
        course_id: parseInt(selectedCourse),
        unit_id: selectedUnit ? parseInt(selectedUnit) : null,
        text: newText,
        marks: parseInt(newMarks),
        is_historical: false
      });
      setShowAddModal(false);
      setNewText('');
      await loadQuestions();
    } catch (err) {
      console.error(err);
    } finally {
      setAdding(false);
    }
  };

  const handleCreateCourse = async (e) => {
    e.preventDefault();
    try {
      const res = await api.createCourse({ ...courseForm, units: [] });
      await loadCourses();
      setSelectedCourse(String(res.data.id));
      setShowCourseModal(false);
      setCourseForm({
        code: '',
        title: '',
        department: 'Computer Science & Engineering',
        institution: 'Vishwakarma Institute of Technology',
        semester: 'Semester VI',
        academic_year: '2025-2026',
      });
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    }
  };

  const handleCreateUnit = async (e) => {
    e.preventDefault();
    try {
      await api.addUnit(parseInt(selectedCourse), {
        ...unitForm,
        topics: [],
      });
      await loadCourses();
      setShowUnitModal(false);
      setUnitForm({ unit_number: 1, title: '', description: '', target_weightage_pct: 16.67 });
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) return;
    if (!confirm(`Delete ${selectedIds.length} selected question(s)?`)) return;
    const res = await api.bulkDeleteQuestions(selectedIds);
    setSelectedIds([]);
    await loadQuestions();
    alert(`Deleted ${res.data.deleted}; ${res.data.blocked} used by papers were blocked.`);
  };

  return (
    <div className="space-y-6">
      
      {/* Page Header */}
      <div className="flex flex-wrap justify-between items-center gap-3">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900 tracking-tight flex items-center space-x-2">
            <BookOpen className="w-5 h-5 text-brand-600" />
            <span>Question Bank & Cognitive Taxonomy Repository</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Browse, classify, reframe, and evaluate examination items across L1 to L6.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowCourseModal(true)}
            className="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold px-4 py-2 rounded-xl transition"
          >
            Add Course
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold px-4 py-2 rounded-xl transition flex items-center space-x-1.5 shadow-sm"
          >
            <Plus className="w-4 h-4" />
            <span>Add Question</span>
          </button>
        </div>
      </div>

      {/* Live AI Taxonomy Analyzer Playground */}
      <div className="bg-gradient-to-r from-purple-900 via-indigo-900 to-slate-900 rounded-2xl p-5 text-white shadow-md space-y-3">
        <div className="flex items-center space-x-2 text-xs font-bold text-purple-300">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <span>LIVE AI TAXONOMY CLASSIFIER & DIFFICULTY ESTIMATOR</span>
        </div>

        <div className="flex flex-col sm:flex-row gap-2">
          <input
            type="text"
            value={analyzerText}
            onChange={(e) => setAnalyzerText(e.target.value)}
            placeholder="Type any question prompt to evaluate its Bloom's level and difficulty..."
            className="flex-1 bg-white/10 border border-white/20 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-400"
          />
          <button
            onClick={handleRunAnalyzer}
            disabled={analyzing}
            className="bg-purple-500 hover:bg-purple-600 text-white text-xs font-bold px-5 py-2.5 rounded-xl transition shrink-0 active:scale-95"
          >
            {analyzing ? 'Evaluating...' : 'Analyze Prompt'}
          </button>
        </div>

        {analysisResult && (
          <div className="mt-3 bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/10 text-xs space-y-2 animate-in fade-in">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center space-x-2">
                <span className="bg-purple-500/30 text-purple-200 border border-purple-400/40 px-2.5 py-0.5 rounded-full font-bold">
                  Level: {analysisResult.bloom_level} ({analysisResult.cognitive_target})
                </span>
                <span className="bg-blue-500/30 text-blue-200 border border-blue-400/40 px-2.5 py-0.5 rounded-full font-semibold">
                  Verb: {analysisResult.primary_verb}
                </span>
                <span className="bg-amber-500/30 text-amber-200 border border-amber-400/40 px-2.5 py-0.5 rounded-full font-semibold">
                  Difficulty: {analysisResult.difficulty} ({analysisResult.difficulty_score})
                </span>
              </div>
              <span className="font-mono text-slate-300 font-bold">
                Confidence: {Math.round(analysisResult.confidence * 100)}%
              </span>
            </div>
            <p className="text-slate-200 text-[11px] leading-relaxed italic">
              {analysisResult.explanation}
            </p>
          </div>
        )}
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-3 text-xs">
        
        {/* Search */}
        <form onSubmit={handleSearchSubmit} className="flex-1 min-w-[240px] relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search questions by topic, algorithm, concept..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-brand-500"
          />
        </form>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={selectedCourse}
            onChange={(e) => setSelectedCourse(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-lg p-2 font-medium"
          >
            {courses.map((course) => (
              <option key={course.id} value={course.id}>
                {course.code} - {course.title}
              </option>
            ))}
          </select>
          <select
            value={selectedUnit}
            onChange={(e) => setSelectedUnit(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-lg p-2 font-medium"
          >
            <option value="">All Units</option>
            {units.map((unit) => (
              <option key={unit.id} value={unit.id}>Unit {unit.unit_number}: {unit.title}</option>
            ))}
          </select>
          <button type="button" onClick={() => setShowUnitModal(true)} disabled={!selectedCourse} className="border border-slate-200 rounded-lg p-2 font-bold text-brand-600">
            + Unit
          </button>
          <select
            value={selectedBloom}
            onChange={(e) => setSelectedBloom(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-lg p-2 font-medium"
          >
            <option value="">All Bloom's Levels</option>
            <option value="L1">L1: Remember</option>
            <option value="L2">L2: Understand</option>
            <option value="L3">L3: Apply</option>
            <option value="L4">L4: Analyze</option>
            <option value="L5">L5: Evaluate</option>
            <option value="L6">L6: Create</option>
          </select>

          <select
            value={selectedDiff}
            onChange={(e) => setSelectedDiff(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-lg p-2 font-medium"
          >
            <option value="">All Difficulties</option>
            <option value="Easy">Easy</option>
            <option value="Medium">Medium</option>
            <option value="Hard">Hard</option>
          </select>

          <label className="flex items-center space-x-1.5 cursor-pointer text-slate-700 font-medium px-2 py-1.5 rounded hover:bg-slate-50 border border-slate-200">
            <input
              type="checkbox"
              checked={onlyHistorical}
              onChange={(e) => setOnlyHistorical(e.target.checked)}
              className="rounded accent-brand-600"
            />
            <span>Historical Only</span>
          </label>
        </div>

      </div>

      {/* Question List Grid */}
      {loading ? (
        <div className="h-64 flex items-center justify-center text-slate-400 text-sm">
          Loading question repository...
        </div>
      ) : questions.length === 0 ? (
        <div className="h-64 flex flex-col items-center justify-center text-slate-400 text-sm bg-white rounded-2xl border border-dashed border-slate-300">
          <BookOpen className="w-8 h-8 mb-2 opacity-50 text-slate-400" />
          <p>No questions matched the selected criteria.</p>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between bg-white border border-slate-200 rounded-xl px-4 py-2 text-xs">
            <label className="flex items-center gap-2 font-semibold text-slate-600">
              <input type="checkbox" checked={questions.length > 0 && selectedIds.length === questions.length} onChange={(e) => setSelectedIds(e.target.checked ? questions.map((q) => q.id) : [])} />
              Select all visible
            </label>
            {selectedIds.length > 0 && (
              <button onClick={handleBulkDelete} className="text-rose-600 font-bold">Delete selected ({selectedIds.length})</button>
            )}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {questions.map((q) => (
              <div key={q.id} className="relative">
                <div className="absolute left-2 top-2 z-10">
                  <input type="checkbox" checked={selectedIds.includes(q.id)} onChange={(e) => setSelectedIds(e.target.checked ? [...selectedIds,q.id] : selectedIds.filter((id) => id !== q.id))} />
                </div>
                <QuestionCard question={q} bankMode={true} />
                <div className="mt-2 flex justify-end gap-3 text-xs">
                  <button onClick={() => setEditQuestion(q)} className="text-brand-600 font-bold">Edit</button>
                  <button onClick={async () => { if(confirm('Delete this question?')) { await api.deleteQuestion(q.id); await loadQuestions(); } }} className="text-rose-600 font-bold">Delete</button>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Add Question Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-base">Add Question to Repository</h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
            </div>

            <form onSubmit={handleAddQuestion} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Question Prompt</label>
                <textarea
                  rows={4}
                  value={newText}
                  onChange={(e) => setNewText(e.target.value)}
                  placeholder="e.g. Design a fault-tolerant distributed consensus protocol..."
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs focus:ring-2 focus:ring-brand-500 font-sans"
                  required
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Marks Allocation</label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={newMarks}
                  onChange={(e) => setNewMarks(e.target.value)}
                  className="w-28 bg-slate-50 border border-slate-200 rounded-lg p-2 font-mono font-bold"
                />
                <p className="text-[11px] text-slate-400 mt-1">
                  Bloom's Taxonomy and difficulty level will be automatically inferred via hybrid classification.
                </p>
              </div>

              <div className="pt-2 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={adding}
                  className="bg-brand-600 hover:bg-brand-700 text-white font-bold px-5 py-2 rounded-lg transition"
                >
                  {adding ? 'Indexing Question...' : 'Save & Auto-Tag'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showCourseModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-base">Create Academic Course</h3>
              <button onClick={() => setShowCourseModal(false)} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
            </div>
            <form onSubmit={handleCreateCourse} className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              {[
                ['code', 'Course Code'],
                ['title', 'Course Title'],
                ['department', 'Department'],
                ['institution', 'Institution'],
                ['semester', 'Semester'],
                ['academic_year', 'Academic Year'],
              ].map(([field, label]) => (
                <label key={field} className="font-semibold text-slate-700">
                  {label}
                  <input
                    value={courseForm[field]}
                    onChange={(e) => setCourseForm({ ...courseForm, [field]: e.target.value })}
                    className="mt-1 w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5"
                    required
                  />
                </label>
              ))}
              <div className="sm:col-span-2 flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowCourseModal(false)} className="px-4 py-2 text-slate-600">Cancel</button>
                <button type="submit" className="bg-brand-600 text-white px-5 py-2 rounded-lg font-bold">Create Course</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showUnitModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4">
            <h3 className="font-bold text-slate-900">Create Course Unit</h3>
            <form onSubmit={handleCreateUnit} className="grid grid-cols-1 gap-3 text-xs">
              <label>Unit Number
                <input type="number" value={unitForm.unit_number} onChange={(e) => setUnitForm({...unitForm,unit_number:parseInt(e.target.value)||1})} className="mt-1 w-full border rounded p-2" />
              </label>
              <label>Unit Title
                <input value={unitForm.title} onChange={(e) => setUnitForm({...unitForm,title:e.target.value})} className="mt-1 w-full border rounded p-2" required />
              </label>
              <label>Description
                <textarea value={unitForm.description} onChange={(e) => setUnitForm({...unitForm,description:e.target.value})} className="mt-1 w-full border rounded p-2" />
              </label>
              <div className="flex justify-end gap-2">
                <button type="button" onClick={() => setShowUnitModal(false)} className="px-4 py-2">Cancel</button>
                <button type="submit" className="bg-brand-600 text-white px-4 py-2 rounded-lg font-bold">Create Unit</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {editQuestion && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 space-y-4">
            <h3 className="font-bold text-slate-900">Edit Question</h3>
            <textarea value={editQuestion.text} onChange={(e) => setEditQuestion({...editQuestion,text:e.target.value})} rows={5} className="w-full border rounded-lg p-3 text-sm" />
            <div className="grid grid-cols-3 gap-3 text-xs">
              <label>Marks
                <input type="number" value={editQuestion.marks} onChange={(e) => setEditQuestion({...editQuestion,marks:parseInt(e.target.value)||1})} className="mt-1 w-full border rounded p-2" />
              </label>
              <label>Bloom
                <select value={editQuestion.bloom_level} onChange={(e) => setEditQuestion({...editQuestion,bloom_level:e.target.value})} className="mt-1 w-full border rounded p-2">
                  {['L1','L2','L3','L4','L5','L6'].map((l)=><option key={l}>{l}</option>)}
                </select>
              </label>
              <label>Difficulty
                <select value={editQuestion.difficulty} onChange={(e) => setEditQuestion({...editQuestion,difficulty:e.target.value})} className="mt-1 w-full border rounded p-2">
                  {['Easy','Medium','Hard'].map((d)=><option key={d}>{d}</option>)}
                </select>
              </label>
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={() => setEditQuestion(null)} className="px-4 py-2">Cancel</button>
              <button onClick={async () => { await api.updateQuestion(editQuestion.id,{text:editQuestion.text,marks:editQuestion.marks,bloom_level:editQuestion.bloom_level,difficulty:editQuestion.difficulty,unit_id:selectedUnit?parseInt(selectedUnit):editQuestion.unit_id,topic_id:editQuestion.topic_id,solution_outline:editQuestion.solution_outline}); setEditQuestion(null); await loadQuestions(); }} className="bg-brand-600 text-white px-4 py-2 rounded-lg font-bold">Save Changes</button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
