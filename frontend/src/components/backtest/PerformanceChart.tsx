'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface PerformanceChartProps {
  data: Array<{ date: string; value: number }>;
}

export default function PerformanceChart({ data }: PerformanceChartProps) {
  if (data.length === 0) return null;

  return (
    <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
      <h2 className="text-lg font-semibold text-white mb-4">포트폴리오 가치</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
          <XAxis
            dataKey="date"
            stroke="#71717a"
            tick={{ fontSize: 11 }}
            tickFormatter={(d: string) => d.slice(0, 7)}
            interval="preserveStartEnd"
          />
          <YAxis stroke="#71717a" tick={{ fontSize: 11 }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#18181b', border: '1px solid #3f3f46', borderRadius: '8px' }}
            labelStyle={{ color: '#a1a1aa' }}
            itemStyle={{ color: '#3b82f6' }}
          />
          <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
