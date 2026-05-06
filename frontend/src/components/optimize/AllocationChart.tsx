'use client';

import { PieChart as RechartsPie, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { CHART_COLORS } from '@/lib/utils/constants';

interface AllocationChartProps {
  weights: Record<string, number>;
}

const formatPercent = (value: number) => (value * 100).toFixed(2) + '%';

export default function AllocationChart({ weights }: AllocationChartProps) {
  const chartData = Object.entries(weights)
    .filter(([, w]) => w > 0.001)
    .sort(([, a], [, b]) => b - a)
    .map(([ticker, weight]) => ({ name: ticker, value: weight }));
  const allEntries = Object.entries(weights).sort(([, a], [, b]) => b - a);

  return (
    <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
      <h2 className="text-lg font-semibold text-white mb-4">최적 비중</h2>
      <div className="flex flex-col md:flex-row items-center gap-6">
        <div className="w-full md:w-1/2 h-64 relative">
          <ResponsiveContainer width="100%" height="100%">
            <RechartsPie>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius="60%"
                outerRadius="80%"
                dataKey="value"
                stroke="none"
              >
                {chartData.map((_, idx) => (
                  <Cell key={idx} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: number | undefined) => (value != null ? formatPercent(value) : '')}
                contentStyle={{ backgroundColor: '#18181b', border: '1px solid #3f3f46', borderRadius: '8px' }}
                itemStyle={{ color: '#e4e4e7' }}
              />
            </RechartsPie>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="text-center">
              <p className="text-2xl font-bold text-white">{chartData.length}</p>
              <p className="text-xs text-zinc-500">종목</p>
            </div>
          </div>
        </div>
        <div className="w-full md:w-1/2 space-y-2">
          {allEntries.map(([ticker, weight]) => {
            const chartIdx = chartData.findIndex((d) => d.name === ticker);
            const isZero = weight <= 0.001;
            return (
              <div key={ticker} className="flex items-center gap-3">
                <span
                  className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: isZero ? '#3f3f46' : CHART_COLORS[chartIdx % CHART_COLORS.length] }}
                />
                <span className={`text-sm font-medium w-14 ${isZero ? 'text-zinc-600' : 'text-zinc-300'}`}>{ticker}</span>
                <div className="flex-1 bg-zinc-800 rounded-full h-1.5">
                  {!isZero && (
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${Math.max(weight * 100, 2)}%`,
                        backgroundColor: CHART_COLORS[chartIdx % CHART_COLORS.length],
                      }}
                    />
                  )}
                </div>
                <span className={`text-sm w-16 text-right ${isZero ? 'text-zinc-600' : 'text-zinc-400'}`}>
                  {formatPercent(weight)}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
