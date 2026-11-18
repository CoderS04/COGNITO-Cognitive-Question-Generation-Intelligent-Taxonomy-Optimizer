import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Layers, CheckCircle2 } from 'lucide-react';
import api from '../services/api';
import BloomsRadarChart from '../components/BloomsRadarChart';
import DifficultyPieChart from '../components/DifficultyPieChart';
import UnitCoverageChart from '../components/UnitCoverageChart';

export default function AnalyticsView() {
  const [papers, setPapers] = useState([]);
  const [selectedPaperId, setSelectedPaperId] = useState('');
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

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
        fetchAnalytics(res.data[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async (pId) => {
    try {
      const res = await api.getPaperAnalytics(pId);
      setAnalytics(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handlePaperChange = (id) => {
    setSelectedPaperId(id);
    fetchAnalytics(id);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      
      {/* Header */}
      <div className="flex flex-wrap justify-between items-center gap-3">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900 tracking-tight flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-brand-600" />
            <span>Interactive Cognitive & Assessment Analytics</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Visual evaluation of Bloom's Taxonomy adherence, difficulty variance, and unit-wise marks distribution.
          </p>
        </div>

        <select
          value={selectedPaperId}
          onChange={(e) => handlePaperChange(e.target.value)}
          className="bg-white border border-slate-200 text-xs rounded-xl p-2.5 font-bold shadow-sm focus:ring-2 focus:ring-brand-500"
        >
          {papers.map((p) => (
            <option key={p.id} value={p.id}>
              #{p.id}: {p.title}
            </option>
          ))}
        </select>
      </div>

      {analytics && (
        <div className="space-y-6">
          
          {/* Top Metric Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Cognitive Depth Index</span>
              <div className="flex items-baseline space-x-2 mt-1">
                <span className="text-3xl font-extrabold text-brand-700 font-mono">
                  {analytics.cognitive_depth_index}
                </span>
                <span className="text-xs text-slate-400 font-medium">/ 6.0 Scale</span>
              </div>
              <p className="text-[11px] text-emerald-600 font-medium mt-1">
                Balanced between procedural and high-order evaluation
              </p>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Overall CAS Score</span>
              <div className="flex items-baseline space-x-2 mt-1">
                <span className="text-3xl font-extrabold text-slate-900 font-mono">
                  {Math.round(analytics.cas_score * 100)}%
                </span>
                <span className="text-xs text-slate-400 font-medium">Verified</span>
              </div>
              <p className="text-[11px] text-brand-600 font-medium mt-1">
                Status: {analytics.status}
              </p>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Historical Repetition Rate</span>
              <div className="flex items-baseline space-x-2 mt-1">
                <span className="text-3xl font-extrabold text-emerald-600 font-mono">
                  {analytics.high_similarity_flags_count}
                </span>
                <span className="text-xs text-slate-400 font-medium">Flagged Duplicates</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                Avg similarity to past papers: {Math.round(analytics.average_similarity_to_history * 100)}%
              </p>
            </div>
          </div>

          {/* Visual Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <div className="mb-3">
                <h3 className="font-bold text-slate-900 text-sm">Bloom's Taxonomy Radar Mapping</h3>
                <p className="text-xs text-slate-500">Target % versus Actual % across all cognitive tiers</p>
              </div>
              <BloomsRadarChart data={analytics.bloom_distribution} />
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <div className="mb-3">
                <h3 className="font-bold text-slate-900 text-sm">Difficulty Balance Distribution</h3>
                <p className="text-xs text-slate-500">Proportion of Easy, Medium, and Hard question items</p>
              </div>
              <DifficultyPieChart data={analytics.difficulty_distribution} />
            </div>

          </div>

          {/* Unit-wise Coverage Bar Chart */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <div className="mb-3">
              <h3 className="font-bold text-slate-900 text-sm">Syllabus Breadth & Unit-Wise Marks Allocation</h3>
              <p className="text-xs text-slate-500">Ensures uniform curriculum assessment without thematic blind spots</p>
            </div>
            <UnitCoverageChart data={analytics.unit_coverage} />
          </div>

        </div>
      )}

    </div>
  );
}
