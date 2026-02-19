'use client';

import Link from 'next/link';
import {
  PieChart,
  TrendingUp,
  MessageSquare,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  Info,
} from 'lucide-react';

const quickStats = [
  { label: '포트폴리오 가치', value: '$124,500', change: '+12.5%', isPositive: true },
  { label: '오늘의 수익', value: '+$1,250', change: '+1.02%', isPositive: true },
  { label: 'Sharpe Ratio', value: '1.85', change: '+0.12', isPositive: true },
  { label: '최대 낙폭', value: '-8.5%', change: '-2.1%', isPositive: false },
];

const quickActions = [
  { href: '/dashboard/optimize', icon: PieChart, title: '포트폴리오 최적화', description: '최적의 자산 배분 찾기', color: 'blue' },
  { href: '/dashboard/backtest', icon: TrendingUp, title: '백테스트 실행', description: '전략 성과 검증', color: 'green' },
  { href: '/dashboard/chat', icon: MessageSquare, title: 'AI 분석', description: 'AI 기반 인사이트 받기', color: 'violet' },
];

export default function DashboardPage() {
  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="text-2xl font-bold text-white mb-2">다시 오셨군요!</h1>
        <p className="text-zinc-400">포트폴리오 성과 요약입니다.</p>
      </div>

      {/* Demo Banner */}
      <div className="flex items-center gap-3 p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl">
        <Info className="w-5 h-5 text-amber-400 flex-shrink-0" />
        <p className="text-sm text-amber-300">
          데모 데이터입니다. 실제 포트폴리오 분석은 <Link href="/dashboard/optimize" className="underline font-medium hover:text-amber-200">최적화</Link> 메뉴에서 시작하세요.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {quickStats.map((stat) => (
          <div key={stat.label} className="p-5 bg-zinc-900 border border-zinc-800 rounded-xl hover:border-zinc-700 transition-colors">
            <p className="text-sm text-zinc-500 mb-1">{stat.label}</p>
            <div className="flex items-end justify-between">
              <p className="text-2xl font-bold text-white">{stat.value}</p>
              <div className={`flex items-center gap-1 text-sm ${stat.isPositive ? 'text-green-500' : 'text-red-500'}`}>
                {stat.isPositive ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                {stat.change}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">빠른 실행</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {quickActions.map((action) => (
            <Link key={action.href} href={action.href}
              className="group p-6 bg-zinc-900 border border-zinc-800 rounded-xl hover:border-zinc-700 transition-all hover:scale-[1.02]">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${
                action.color === 'blue' ? 'bg-blue-500/10 text-blue-400'
                  : action.color === 'green' ? 'bg-green-500/10 text-green-400'
                  : 'bg-violet-500/10 text-violet-400'
              }`}>
                <action.icon className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-1 group-hover:text-blue-400 transition-colors">{action.title}</h3>
              <p className="text-sm text-zinc-500">{action.description}</p>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Activity Placeholder */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">최근 활동</h2>
        <div className="p-8 bg-zinc-900 border border-zinc-800 rounded-xl text-center">
          <Activity className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
          <p className="text-zinc-500">아직 활동 내역이 없습니다.</p>
          <p className="text-sm text-zinc-600 mt-1">포트폴리오 최적화 또는 백테스트를 실행해보세요.</p>
        </div>
      </div>
    </div>
  );
}
