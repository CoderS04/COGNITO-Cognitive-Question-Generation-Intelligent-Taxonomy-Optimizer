import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const COLORS = {
  Easy: '#10B981',   // Green
  Medium: '#F59E0B', // Amber
  Hard: '#EF4444'    // Red
};

export default function DifficultyPieChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-400 text-sm">
        No difficulty data available.
      </div>
    );
  }

  const chartData = data.map((d) => ({
    name: d.category,
    value: d.marks,
    pct: d.actual_pct,
    target: d.target_pct,
    count: d.question_count,
    color: COLORS[d.category] || '#64748b'
  }));

  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="45%"
            innerRadius={60}
            outerRadius={85}
            paddingAngle={4}
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} stroke="#ffffff" strokeWidth={2} />
            ))}
          </Pie>
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const item = payload[0].payload;
                return (
                  <div className="bg-white p-2.5 rounded-lg shadow-md border border-slate-200 text-xs">
                    <p className="font-bold text-slate-800">{item.name} Difficulty</p>
                    <p className="font-semibold" style={{ color: item.color }}>{item.value} Marks ({item.pct}%)</p>
                    <p className="text-slate-500">Target: {item.target}% | {item.count} Qs</p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(val, entry) => (
              <span className="text-xs text-slate-600 font-medium">
                {val} ({entry.payload.pct}%)
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
