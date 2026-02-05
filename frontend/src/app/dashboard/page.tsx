'use client';

import AppLayout from '@/components/layout/AppLayout';
import { useEffect, useState } from 'react';
import { fetchOverview, fetchDaily, fetchDomains, fetchFeedbackList } from '@/services/statsService';
import { BarChart3, Clock, ThumbsUp, TrendingUp } from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts';

interface ModelStats {
  model_name: string;
  total_queries: number;
  avg_response_time_ms: number;
  helpful_rate: number | null;
  total_feedback: number;
}

const PIE_COLORS = ['#3B82F6', '#8B5CF6', '#EC4899', '#F59E0B', '#10B981', '#6366F1', '#EF4444', '#14B8A6'];

export default function DashboardPage() {
  const [models, setModels] = useState<ModelStats[]>([]);
  const [daily, setDaily] = useState<Array<{ date: string; count: number }>>([]);
  const [domains, setDomains] = useState<Array<{ domain: string; count: number }>>([]);
  const [feedback, setFeedback] = useState<Array<{ id: number; query: string; rating: number; domain: string | null; created_at: string }>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [ov, dl, dom, fb] = await Promise.all([
          fetchOverview().catch(() => null),
          fetchDaily(30).catch(() => null),
          fetchDomains().catch(() => null),
          fetchFeedbackList(20).catch(() => null),
        ]);
        if (ov?.models) setModels(ov.models);
        if (dl?.daily) setDaily(dl.daily);
        if (dom?.domains) setDomains(dom.domains);
        if (fb?.feedback) setFeedback(fb.feedback);
      } catch { /* silent */ }
      setLoading(false);
    })();
  }, []);

  const totalQueries = models.reduce((sum, m) => sum + m.total_queries, 0);
  const avgResponseTime = models.length > 0
    ? models.reduce((sum, m) => sum + m.avg_response_time_ms, 0) / models.length / 1000
    : 0;
  const avgSatisfaction = models.filter(m => m.helpful_rate !== null).length > 0
    ? models.filter(m => m.helpful_rate !== null).reduce((sum, m) => sum + (m.helpful_rate || 0), 0) / models.filter(m => m.helpful_rate !== null).length
    : 0;

  const kpis = [
    { label: '총 쿼리', value: totalQueries > 0 ? totalQueries.toLocaleString() : '-', icon: BarChart3, color: 'text-blue-500' },
    { label: '평균 응답시간', value: avgResponseTime > 0 ? `${avgResponseTime.toFixed(1)}s` : '-', icon: Clock, color: 'text-amber-500' },
    { label: '만족도', value: avgSatisfaction > 0 ? `${(avgSatisfaction * 100).toFixed(0)}%` : '-', icon: ThumbsUp, color: 'text-green-500' },
  ];

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-500">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {kpis.map((k, i) => (
            <div key={k.label} className={`card-hover bg-zinc-900 border border-zinc-800 rounded-xl p-5 hover:border-zinc-700 animate-fade-in-up stagger-${i + 1}`}>
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm text-zinc-400">{k.label}</span>
                <k.icon className={`w-5 h-5 ${k.color}`} />
              </div>
              {loading ? <div className="skeleton h-8 w-24 rounded" /> : <p className="text-2xl font-bold animate-count-up">{k.value}</p>}
            </div>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Daily Trend */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 hover:border-zinc-700 transition-all">
            <h3 className="text-sm font-bold text-zinc-400 mb-4 flex items-center gap-2">
              <TrendingUp className="w-4 h-4" /> 일별 쿼리 추이
            </h3>
            {loading ? (
              <div className="skeleton h-48 w-full rounded-lg" />
            ) : daily.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={daily}>
                  <XAxis
                    dataKey="date"
                    tick={{ fill: '#71717A', fontSize: 11 }}
                    tickFormatter={(v) => v.slice(5)}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: '#71717A', fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                    width={30}
                  />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#27272A', border: '1px solid #3F3F46', borderRadius: '8px', fontSize: '12px' }}
                    labelStyle={{ color: '#A1A1AA' }}
                    itemStyle={{ color: '#3B82F6' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke="#3B82F6"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4, fill: '#3B82F6' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="py-12 text-center text-zinc-600">
                <TrendingUp className="w-8 h-8 mx-auto mb-2 opacity-30" />
                <p className="text-sm">데이터가 없습니다</p>
              </div>
            )}
          </div>

          {/* Domain Distribution Pie */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 hover:border-zinc-700 transition-all">
            <h3 className="text-sm font-bold text-zinc-400 mb-4 flex items-center gap-2">
              <BarChart3 className="w-4 h-4" /> 도메인 분포
            </h3>
            {loading ? (
              <div className="skeleton h-48 w-full rounded-lg" />
            ) : domains.length > 0 ? (
              <div className="flex items-center gap-4">
                <ResponsiveContainer width="50%" height={200}>
                  <PieChart>
                    <Pie
                      data={domains.slice(0, 8)}
                      dataKey="count"
                      nameKey="domain"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      innerRadius={40}
                      strokeWidth={0}
                    >
                      {domains.slice(0, 8).map((_, i) => (
                        <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ backgroundColor: '#27272A', border: '1px solid #3F3F46', borderRadius: '8px', fontSize: '12px' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex-1 space-y-1.5">
                  {domains.slice(0, 8).map((d, i) => (
                    <div key={d.domain} className="flex items-center gap-2 text-xs">
                      <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: PIE_COLORS[i % PIE_COLORS.length] }} />
                      <span className="text-zinc-400 truncate flex-1">{d.domain}</span>
                      <span className="text-zinc-500">{d.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-zinc-600">
                <BarChart3 className="w-8 h-8 mx-auto mb-2 opacity-30" />
                <p className="text-sm">데이터가 없습니다</p>
              </div>
            )}
          </div>
        </div>

        {/* Recent Feedback */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 hover:border-zinc-700 transition-all">
          <h3 className="text-sm font-bold text-zinc-400 mb-4 flex items-center gap-2">
            <ThumbsUp className="w-4 h-4" /> 최근 피드백
            {feedback.length > 0 && <span className="text-xs text-zinc-600 ml-auto">{feedback.length}건</span>}
          </h3>
          {loading ? (
            <div className="space-y-3">{[1, 2, 3, 4, 5].map(i => <div key={i} className="skeleton h-10 w-full rounded-lg" />)}</div>
          ) : feedback.length > 0 ? (
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {feedback.map(fb => (
                <div key={fb.id} className="flex items-center gap-3 bg-zinc-800/50 border border-zinc-700/50 rounded-lg p-3 hover:bg-zinc-800 hover:border-zinc-600 transition-all cursor-pointer group">
                  <span className="text-sm">{fb.rating === 1 ? '👍' : '👎'}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white truncate">{fb.query}</p>
                    <div className="flex items-center gap-2 mt-1">
                      {fb.domain && (
                        <span className="px-1.5 py-0.5 text-xs bg-blue-500/10 text-blue-400 rounded border border-blue-500/20">
                          {fb.domain}
                        </span>
                      )}
                      <span className="text-xs text-zinc-500">{fb.created_at}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center text-zinc-600">
              <ThumbsUp className="w-8 h-8 mx-auto mb-2 opacity-30" />
              <p className="text-sm">피드백이 없습니다</p>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
