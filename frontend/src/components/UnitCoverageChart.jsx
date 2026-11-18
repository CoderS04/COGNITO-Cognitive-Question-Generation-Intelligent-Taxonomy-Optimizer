import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';

export default function UnitCoverageChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-400 text-sm">
        No unit coverage metrics available.
      </div>
    );
  }

  const chartData = data.map((d) => ({
    name: `Unit ${d.unit_number}`,
    fullTitle: d.title,
    marks: d.marks,
    actual_pct: d.actual_pct,
    target_pct: d.target_pct,
    questions: d.questions_count
  }));

  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 11, fontWeight: 500 }} />
          <YAxis stroke="#64748b" tick={{ fontSize: 10 }} unit="M" />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const item = payload[0].payload;
                return (
                  <div className="bg-white p-3 rounded-xl shadow-lg border border-slate-200 text-xs space-y-1">
                    <p className="font-bold text-slate-800 text-sm">{item.name}: {item.fullTitle}</p>
                    <p className="text-brand-600 font-semibold">{item.marks} Marks ({item.actual_pct}%)</p>
                    <p className="text-slate-500">Target Weight: {item.target_pct}%</p>
                    <p className="text-slate-400">Total Questions: {item.questions}</p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Bar dataKey="marks" fill="#026fc7" radius={[4, 4, 0, 0]} name="Allocated Marks" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
