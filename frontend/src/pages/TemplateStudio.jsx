import React, { useState, useEffect } from 'react';
import { Sliders, Plus, CheckCircle2, Layers, Clock, Award } from 'lucide-react';
import api from '../services/api';

export default function TemplateStudio() {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [templateFile, setTemplateFile] = useState(null);
  const [extracting, setExtracting] = useState(false);
  const [editingTemplateId, setEditingTemplateId] = useState(null);
  const [form, setForm] = useState({
    name: '',
    description: '',
    total_marks: 100,
    duration_minutes: 180,
    instructions: 'Figures to the right indicate full marks.',
    sections_config: [{ section_name: 'Section A', marks: 100, instructions: 'Answer all questions as directed.' }],
    bloom_targets: { L1: 10, L2: 20, L3: 30, L4: 25, L5: 10, L6: 5 },
    difficulty_targets: { Easy: 30, Medium: 50, Hard: 20 },
  });

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const res = await api.getTemplates();
      setTemplates(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const extractTemplate = async () => {
    if (!templateFile) return;
    setExtracting(true);
    try {
      const data = new FormData();
      data.append('file', templateFile);
      data.append('doc_type', 'exam_template');
      const res = await api.uploadDocument(data);
      const template = res.data.details?.template || res.data.details?.extracted_data?.[0];
      if (template) setForm({ ...form, ...template });
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    } finally {
      setExtracting(false);
    }
  };

  const createTemplate = async (e) => {
    e.preventDefault();
    try {
      if (editingTemplateId) {
        await api.updateTemplate(editingTemplateId, form);
      } else {
        await api.createTemplate(form);
      }
      setShowCreate(false);
      setEditingTemplateId(null);
      await loadTemplates();
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      
      {/* Header */}
      <div>
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-xl font-extrabold text-slate-900 tracking-tight flex items-center space-x-2">
              <Sliders className="w-5 h-5 text-brand-600" />
              <span>Institutional Templates & Examination Policies</span>
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Predefined academic examination blueprints conforming to university assessment regulations.
            </p>
          </div>
          <button onClick={() => setShowCreate(true)} className="bg-brand-600 text-white text-xs font-bold px-4 py-2 rounded-lg flex items-center gap-1">
            <Plus className="w-4 h-4" /> Create / Extract Template
          </button>
        </div>
      </div>

      {showCreate && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 space-y-4 max-h-[90vh] overflow-auto">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900">Create or Extract Examination Template</h3>
              <button onClick={() => setShowCreate(false)} className="text-slate-400 font-bold">✕</button>
            </div>
            <div className="border-2 border-dashed border-slate-200 rounded-xl p-4 space-y-2">
              <input type="file" accept=".pdf,.docx,.txt,.jpg,.png" onChange={(e) => setTemplateFile(e.target.files?.[0] || null)} />
              <button type="button" onClick={extractTemplate} disabled={!templateFile || extracting} className="bg-purple-600 text-white px-4 py-2 rounded-lg text-xs font-bold">
                {extracting ? 'Running OCR...' : 'Extract Template with OCR'}
              </button>
            </div>
            <form onSubmit={createTemplate} className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <label className="font-semibold">Template Name
                <input value={form.name} onChange={(e) => setForm({...form, name: e.target.value})} className="mt-1 w-full border rounded-lg p-2" required />
              </label>
              <label className="font-semibold">Description
                <input value={form.description} onChange={(e) => setForm({...form, description: e.target.value})} className="mt-1 w-full border rounded-lg p-2" />
              </label>
              <label className="font-semibold">Total Marks
                <input type="number" value={form.total_marks} onChange={(e) => setForm({...form, total_marks: parseInt(e.target.value)})} className="mt-1 w-full border rounded-lg p-2" />
              </label>
              <label className="font-semibold">Duration (Minutes)
                <input type="number" value={form.duration_minutes} onChange={(e) => setForm({...form, duration_minutes: parseInt(e.target.value)})} className="mt-1 w-full border rounded-lg p-2" />
              </label>
              <label className="sm:col-span-2 font-semibold">Instructions
                <textarea value={form.instructions || ''} onChange={(e) => setForm({...form, instructions: e.target.value})} className="mt-1 w-full border rounded-lg p-2" rows={2} />
              </label>
              <div className="sm:col-span-2 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-700">Exam Sections</span>
                  <button type="button" onClick={() => setForm({...form, sections_config: [...form.sections_config, { section_name: `Section ${String.fromCharCode(65 + form.sections_config.length)}`, marks: 0, instructions: '' }]})} className="text-brand-600 font-bold">+ Add Section</button>
                </div>
                {form.sections_config.map((section, index) => (
                  <div key={index} className="grid grid-cols-1 sm:grid-cols-[1fr_100px_1fr_auto] gap-2 p-3 border rounded-lg bg-slate-50 items-end">
                    <label className="font-semibold">Section Name
                      <input value={section.section_name} onChange={(e) => setForm({...form, sections_config: form.sections_config.map((v,i) => i === index ? {...v, section_name:e.target.value} : v)})} className="mt-1 w-full border rounded p-2" />
                    </label>
                    <label className="font-semibold">Marks
                      <input type="number" value={section.marks} onChange={(e) => setForm({...form, sections_config: form.sections_config.map((v,i) => i === index ? {...v, marks:parseInt(e.target.value)||0} : v)})} className="mt-1 w-full border rounded p-2" />
                    </label>
                    <label className="font-semibold">Instructions
                      <input value={section.instructions || ''} onChange={(e) => setForm({...form, sections_config: form.sections_config.map((v,i) => i === index ? {...v, instructions:e.target.value} : v)})} className="mt-1 w-full border rounded p-2" />
                    </label>
                    <button type="button" onClick={() => setForm({...form, sections_config: form.sections_config.filter((_,i) => i !== index)})} className="text-rose-600 px-2 py-2 font-bold">Remove</button>
                    <div className="sm:col-span-4 flex justify-end gap-2">
                      <button type="button" disabled={index === 0} onClick={() => setForm({...form, sections_config: form.sections_config.map((v,i) => i === index-1 ? form.sections_config[index] : i === index ? form.sections_config[index-1] : v)})} className="text-slate-600 disabled:opacity-30">Move Up</button>
                      <button type="button" disabled={index === form.sections_config.length-1} onClick={() => setForm({...form, sections_config: form.sections_config.map((v,i) => i === index+1 ? form.sections_config[index] : i === index ? form.sections_config[index+1] : v)})} className="text-slate-600 disabled:opacity-30">Move Down</button>
                    </div>
                  </div>
                ))}
              </div>
              <div className="sm:col-span-2 grid grid-cols-3 gap-2">
                {Object.entries(form.bloom_targets).map(([level, value]) => (
                  <label key={level} className="font-semibold">{level} %
                    <input type="number" value={value} onChange={(e) => setForm({...form, bloom_targets:{...form.bloom_targets,[level]:parseInt(e.target.value)||0}})} className="mt-1 w-full border rounded p-2" />
                  </label>
                ))}
              </div>
              <div className="sm:col-span-2 grid grid-cols-3 gap-2">
                {Object.entries(form.difficulty_targets).map(([level, value]) => (
                  <label key={level} className="font-semibold">{level} %
                    <input type="number" value={value} onChange={(e) => setForm({...form, difficulty_targets:{...form.difficulty_targets,[level]:parseInt(e.target.value)||0}})} className="mt-1 w-full border rounded p-2" />
                  </label>
                ))}
              </div>
              <div className="sm:col-span-2 flex justify-end gap-2">
                <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 text-slate-600">Cancel</button>
                <button type="submit" className="bg-brand-600 text-white px-5 py-2 rounded-lg font-bold">Save Template</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {templates.map((tpl) => (
          <div key={tpl.id} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-bold text-slate-800 text-base">{tpl.name}</h3>
                <p className="text-xs text-slate-500 mt-0.5">{tpl.description}</p>
              </div>
              <span className="font-mono text-xs font-bold bg-brand-50 text-brand-700 border border-brand-200 px-2.5 py-1 rounded-md">
                {tpl.total_marks} Marks
              </span>
            </div>

            {/* Sections */}
            <div className="space-y-1.5 text-xs">
              <span className="font-bold text-slate-700">Section Structural Layout:</span>
              <div className="space-y-1">
                {(tpl.sections_config || []).map((sec, idx) => (
                  <div key={idx} className="p-2 bg-slate-50 rounded-lg border border-slate-200/80 flex justify-between items-center">
                    <span className="font-medium text-slate-700">{sec.section_name}</span>
                    <span className="font-mono text-slate-500 font-bold">{sec.marks}M</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Bloom's Targets */}
            <div className="text-xs space-y-1">
              <span className="font-bold text-slate-700">Target Cognitive Allocation:</span>
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(tpl.bloom_targets || {}).map(([lvl, pct]) => (
                  <span key={lvl} className="font-mono text-[11px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200">
                    {lvl}: {pct}%
                  </span>
                ))}
              </div>
            </div>

            <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
              <span className="flex items-center space-x-1">
                <Clock className="w-3.5 h-3.5" />
                <span>Duration: {tpl.duration_minutes} Minutes</span>
              </span>
              <span className="text-emerald-600 font-semibold flex items-center space-x-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Active Policy</span>
              </span>
            </div>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => {
                  setEditingTemplateId(tpl.id);
                  setForm({
                    name: tpl.name,
                    description: tpl.description || '',
                    total_marks: tpl.total_marks,
                    duration_minutes: tpl.duration_minutes,
                    instructions: tpl.instructions || '',
                    sections_config: tpl.sections_config || [],
                    bloom_targets: tpl.bloom_targets || {},
                    difficulty_targets: tpl.difficulty_targets || {},
                  });
                  setShowCreate(true);
                }}
                className="text-brand-600 hover:text-brand-800 font-bold"
              >
                Edit Template
              </button>
              <button
                onClick={async () => {
                  if (!confirm(`Delete template "${tpl.name}"?`)) return;
                  await api.deleteTemplate(tpl.id);
                  await loadTemplates();
                }}
                className="text-rose-600 hover:text-rose-800 font-bold"
              >
                Delete
              </button>
            </div>

          </div>
        ))}
      </div>

    </div>
  );
}
