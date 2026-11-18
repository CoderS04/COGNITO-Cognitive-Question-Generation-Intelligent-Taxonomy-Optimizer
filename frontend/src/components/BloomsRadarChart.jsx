import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts';

export default function BloomsRadarChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-400 text-sm">
        No Bloom's distribution metrics available.
      </div>
    );
  }

  // Format data for Recharts Radar
  const radarData = data.map((item) => ({
    level: item.level,
    target: item.target_pct,
    actual: item.actual_pct,
    marks: item.marks,
    count: item.question_count
  }));

  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
          <PolarGrid stroke="#e2e8f0" />
          <PolarAngleAxis dataKey="level" stroke="#64748b" tick={{ fontSize: 12, fontWeight: 600 }} />
          <PolarRadiusAxis angle={30} domain={[0, 45]} stroke="#cbd5e1" tick={{ fontSize: 10 }} />
          
          <Radar
            name="Target Distribution (%)"
            dataKey="target"
            stroke="#94a3b8"
            fill="#94a3b8"
            fillOpacity={0.2}
            strokeDasharray="4 4"
          />
          <Radar
            name="Actual Assessment (%)"
            dataKey="actual"
            stroke="#026fc7"
            fill="#026fc7"
            fillOpacity={0.4}
            strokeWidth={2}
          />

          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const d = payload[0].payload;
                return (
                  <div className="bg-white p-3 rounded-xl shadow-lg border border-slate-200 text-xs space-y-1">
                    <p className="font-bold text-slate-800 text-sm">{d.level} Cognitive Domain</p>
                    <p className="text-brand-600 font-semibold">Actual: {d.actual}% ({d.marks} Marks)</p>
                    <p className="text-slate-500">Target: {d.target}%</p>
                    <p className="text-slate-400">Questions: {d.count}</p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
