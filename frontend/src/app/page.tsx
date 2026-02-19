import Link from 'next/link';
import {
  Sparkles,
  PieChart,
  TrendingUp,
  MessageSquare,
  Shield,
  Zap,
  ArrowRight,
  Github,
} from 'lucide-react';

const features = [
  {
    icon: PieChart,
    title: '포트폴리오 최적화',
    description: '현대 포트폴리오 이론으로 샤프 비율을 극대화하세요. 리스크 허용 범위에 맞는 최적의 자산 배분을 찾아드립니다.',
  },
  {
    icon: TrendingUp,
    title: '백테스트',
    description: '과거 데이터로 전략을 검증하세요. 낙폭, 수익률, 리밸런싱 성과를 분석합니다.',
  },
  {
    icon: MessageSquare,
    title: 'AI 분석',
    description: 'RAG 기반 AI가 인사이트를 제공합니다. 자연어로 포트폴리오에 대해 질문하세요.',
  },
  {
    icon: Shield,
    title: '리스크 관리',
    description: 'VaR, CVaR, 최대 낙폭을 모니터링하세요. 상관관계와 분산투자 효과를 파악합니다.',
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-zinc-950">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-zinc-950/80 backdrop-blur-md border-b border-zinc-800">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-violet-500 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">Aether</span>
          </div>

          <div className="flex items-center gap-4">
            <Link
              href="/login"
              className="px-4 py-2 text-sm text-zinc-400 hover:text-white transition-colors"
            >
              로그인
            </Link>
            <Link
              href="/signup"
              className="px-4 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              시작하기
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/20 rounded-full text-blue-400 text-sm mb-8">
            <Zap className="w-4 h-4" />
            AI & 현대 포트폴리오 이론 기반
          </div>

          <h1 className="text-5xl sm:text-6xl font-bold text-white mb-6 leading-tight">
            지능형 포트폴리오
            <br />
            <span className="bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
              최적화 & 분석
            </span>
          </h1>

          <p className="text-xl text-zinc-400 mb-10 max-w-2xl mx-auto">
            퀀트 전략으로 포트폴리오를 최적화하세요. 성과 백테스트, 리스크 분석,
            AI 인사이트를 하나의 플랫폼에서 제공합니다.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className="flex items-center gap-2 px-8 py-4 bg-blue-500 text-white font-semibold rounded-xl hover:bg-blue-600 transition-colors"
            >
              최적화 시작
              <ArrowRight className="w-5 h-5" />
            </Link>
            <a
              href="#"
              className="flex items-center gap-2 px-8 py-4 bg-zinc-800 text-zinc-400 font-semibold rounded-xl border border-zinc-700 cursor-default"
            >
              <Github className="w-5 h-5" />
              GitHub (Coming Soon)
            </a>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 bg-zinc-900/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">
              포트폴리오 관리에 필요한 모든 것
            </h2>
            <p className="text-zinc-400 max-w-2xl mx-auto">
              최적화부터 분석까지, Aether는 퀀트 포트폴리오 관리를 위한
              종합 도구를 제공합니다.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="p-6 bg-zinc-900 border border-zinc-800 rounded-2xl hover:border-zinc-700 transition-colors group"
              >
                <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center mb-4 group-hover:bg-blue-500/20 transition-colors">
                  <feature.icon className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-zinc-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { value: '10+', label: '최적화 전략' },
              { value: '5+', label: '리스크 지표' },
              { value: 'RAG', label: 'AI 기반 분석' },
              { value: 'Real-time', label: '시장 데이터' },
            ].map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-4xl font-bold text-white mb-2">{stat.value}</div>
                <div className="text-sm text-zinc-500">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6 bg-gradient-to-b from-zinc-900/50 to-zinc-950">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            포트폴리오를 최적화할 준비가 되셨나요?
          </h2>
          <p className="text-zinc-400 mb-8">
            Aether와 함께 데이터 기반의 투자 결정을 시작하세요.
          </p>
          <Link
            href="/signup"
            className="inline-flex items-center gap-2 px-8 py-4 bg-blue-500 text-white font-semibold rounded-xl hover:bg-blue-600 transition-colors"
          >
            무료 계정 생성
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-zinc-800">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-400" />
            <span className="font-semibold text-white">Aether</span>
          </div>
          <p className="text-sm text-zinc-500">
            &copy; {new Date().getFullYear()} Aether. Built with Next.js, FastAPI & Spring Boot.
          </p>
        </div>
      </footer>
    </div>
  );
}
