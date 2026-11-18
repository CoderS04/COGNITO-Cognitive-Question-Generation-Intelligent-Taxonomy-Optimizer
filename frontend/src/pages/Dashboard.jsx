import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Sparkles, 
  BookOpen, 
  FileCheck2, 
  ArrowRight, 
  Award, 
  TrendingUp, 
  CheckCircle, 
  AlertCircle,
  FileText,
  UploadCloud
} from 'lucide-react';
import api from '../services/api';
import BloomsRadarChart from '../components/BloomsRadarChart';
import DifficultyPieChart from '../components/DifficultyPieChart';
import ComplianceGauge from '../components/ComplianceGauge';

export default function Dashboard({ onNavigate, onSelectPaper }) {
  const [stats, setStats] = useState(null);
  const [recentPaperAnalytics, setRecentPaperAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const res = await api.getSystemStats();
      setStats(res.data);

      if (res.data.recent_papers && res.data.recent_papers.length > 0) {
        const topPaperId = res.data.recent_papers[0].id;
        const aRes = await api.getPaperAnalytics(topPaperId);
        setRecentPaperAnalytics(aRes.data);
      }
    } catch (err) {
      console.error('Failed to load dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Hero Welcome Banner */}
      <div className="bg-gradient-to-r from-brand-900 via-brand-800 to-indigo-900 rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center space-x-2 bg-white/10 backdrop-blur-md px-3 py-1 rounded-full text-xs font-semibold text-brand-200 mb-3 border border-white/10">
            <Sparkles className="w-3.5 h-3.5 text-brand-300" />
            <span>AI Assessment Engineering & Bloom's Optimization</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight leading-tight">
            Design Standardized, Bloom's-Compliant Question Papers in Seconds
          </h1>
          <p className="mt-2 text-sm text-brand-100/90 leading-relaxed">
            COGNITO analyzes historical exam papers, syllabus structures, and institutional marking rules to generate mathematically optimized examinations with balanced cognitive depth.
          </p>

          <div className="mt-5 flex flex-wrap gap-3">
            <button
              onClick={() => onNavigate('generate')}
              className="bg-brand-500 hover:bg-brand-400 active:scale-95 text-white text-xs sm:text-sm font-bold px-5 py-2.5 rounded-xl shadow-lg shadow-brand-500/30 transition flex items-center space-x-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>Launch Paper Generator</span>
            </button>
            <button
              onClick={() => onNavigate('documents')}
              className="bg-white/10 hover:bg-white/20 active:scale-95 text-white text-xs sm:text-sm font-semibold px-4 py-2.5 rounded-xl border border-white/20 transition flex items-center space-x-2"
            >
              <UploadCloud className="w-4 h-4" />
              <span>Ingest Syllabus / Papers</span>
            </button>
          </div>
        </div>

        {/* Ambient background decoration */}
        <div className="absolute right-0 bottom-0 translate-x-12 translate-y-12 w-80 h-80 rounded-full bg-brand-500/20 blur-3xl pointer-events-none" />
        <div className="absolute right-12 top-1/2 -translate-y-1/2 hidden xl:block opacity-20 text-white">
          <Brain className="w-64 h-64" />
        </div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Indexed Courses</p>
            <h3 className="text-2xl font-bold text-slate-800 mt-1 font-mono">{stats?.total_courses || 1}</h3>
            <p className="text-[11px] text-slate-500 mt-0.5">Vishwakarma Inst. of Tech</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <BookOpen className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Question Repository</p>
            <h3 className="text-2xl font-bold text-slate-800 mt-1 font-mono">{stats?.total_questions || 28}</h3>
            <p className="text-[11px] text-emerald-600 font-medium mt-0.5">L1 to L6 Indexed</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
            <Brain className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Historical Benchmarks</p>
            <h3 className="text-2xl font-bold text-slate-800 mt-1 font-mono">{stats?.historical_questions_count || 12}</h3>
            <p className="text-[11px] text-slate-500 mt-0.5">Repetition Threshold: 85%</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
            <TrendingUp className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Average CAS Score</p>
            <h3 className="text-2xl font-bold text-slate-800 mt-1 font-mono">
              {Math.round((stats?.average_cas_score || 0.92) * 100)}%
            </h3>
            <p className="text-[11px] text-emerald-600 font-medium mt-0.5">Compliance Approved</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <Award className="w-6 h-6" />
          </div>
        </div>

      </div>

      {/* Analytics Preview & Radar */}
      {recentPaperAnalytics && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm lg:col-span-2">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h3 className="font-bold text-slate-900 text-base">Bloom's Taxonomy Cognitive Distribution</h3>
                <p className="text-xs text-slate-500">Target % versus Actual % for recent examination paper</p>
              </div>
              <span className="text-xs font-mono font-bold bg-slate-100 text-slate-700 px-2.5 py-1 rounded-md">
                Cognitive Depth: {recentPaperAnalytics.cognitive_depth_index} / 6.0
              </span>
            </div>
            <BloomsRadarChart data={recentPaperAnalytics.bloom_distribution} />
          </div>

          <div className="space-y-6">
            <ComplianceGauge
              casScore={recentPaperAnalytics.cas_score}
              status={recentPaperAnalytics.status}
            />

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
              <h4 className="font-bold text-slate-900 text-sm mb-3">Difficulty Balance</h4>
              <DifficultyPieChart data={recentPaperAnalytics.difficulty_distribution} />
            </div>
          </div>

        </div>
      )}

      {/* Recent Generated Papers Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="font-bold text-slate-900 text-base">Recently Generated Question Papers</h3>
            <p className="text-xs text-slate-500">Validated against institutional criteria and Bloom's balance</p>
          </div>
          <button
            onClick={() => onNavigate('generate')}
            className="text-brand-600 hover:text-brand-700 text-xs font-bold flex items-center space-x-1"
          >
            <span>Create New</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-semibold border-y border-slate-200">
              <tr>
                <th className="py-3 px-4">Examination Title</th>
                <th className="py-3 px-4">Marks</th>
                <th className="py-3 px-4">CAS Score</th>
                <th className="py-3 px-4">Audit Status</th>
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(stats?.recent_papers || []).map((p) => (
                <tr key={p.id} className="hover:bg-slate-50/80 transition">
                  <td className="py-3.5 px-4 font-bold text-slate-800">
                    <span 
                      onClick={() => onSelectPaper(p.id)}
                      className="cursor-pointer hover:text-brand-600 transition"
                    >
                      {p.title}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-mono text-slate-600">{p.total_marks} Marks</td>
                  <td className="py-3.5 px-4">
                    <span className="font-mono font-bold text-slate-700">
                      {Math.round(p.cas_score * 100)}%
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2 py-0.5 rounded-full font-bold text-[11px] ${
                      p.status === 'APPROVED' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'
                    }`}>
                      {p.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-slate-400 font-mono">{p.created_at}</td>
                  <td className="py-3.5 px-4 text-right space-x-2">
                    <button
                      onClick={() => onSelectPaper(p.id)}
                      className="text-brand-600 hover:text-brand-800 font-semibold text-xs"
                    >
                      View & Edit
                    </button>
                    <a
                      href={api.getPdfDownloadUrl(p.id)}
                      download
                      className="text-slate-500 hover:text-slate-800 text-xs"
                    >
                      PDF
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
