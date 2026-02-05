'use client';

import { usePathname, useRouter } from 'next/navigation';
import {
  MessageSquare,
  BarChart3,
  ClipboardList,
  Bot,
  Settings,
  Sparkles,
  Menu,
  X,
} from 'lucide-react';
import { useEffect, useState } from 'react';

const navItems = [
  { id: '/', label: '상담', icon: MessageSquare },
  { id: '/dashboard', label: '대시보드', icon: BarChart3 },
  { id: '/history', label: '히스토리', icon: ClipboardList },
  { id: '/models', label: '모델', icon: Bot },
];

const footerItems = [
  { id: '/settings', label: '설정', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);

  // 라우트 변경 시 모바일 사이드바 닫기
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  // ESC 키로 닫기
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMobileOpen(false);
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, []);

  const sidebarContent = (
    <>
      {/* Logo */}
      <div className="p-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 bg-blue-500 rounded-lg flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight text-white">Claro</span>
        </div>
        {/* 모바일 닫기 버튼 */}
        <button
          onClick={() => setMobileOpen(false)}
          className="lg:hidden p-1.5 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.id;
          return (
            <button
              key={item.id}
              onClick={() => router.push(item.id)}
              className={`relative w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 text-sm ${
                isActive
                  ? 'bg-zinc-900 text-blue-500 font-bold'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-900/50'
              }`}
            >
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-blue-500 rounded-r-full" />
              )}
              <item.icon className={`w-5 h-5 transition-transform duration-200 ${isActive ? '' : 'group-hover:scale-110'}`} />
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-zinc-800 space-y-1">
        {footerItems.map((item) => {
          const isActive = pathname === item.id;
          return (
            <button
              key={item.id}
              onClick={() => router.push(item.id)}
              className={`relative w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 text-sm ${
                isActive
                  ? 'bg-zinc-900 text-blue-500 font-bold'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-900/50'
              }`}
            >
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-blue-500 rounded-r-full" />
              )}
              <item.icon className="w-5 h-5" />
              {item.label}
            </button>
          );
        })}
      </div>
    </>
  );

  return (
    <>
      {/* 모바일 햄버거 버튼 */}
      <button
        onClick={() => setMobileOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-zinc-900 border border-zinc-800 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
        aria-label="메뉴 열기"
      >
        <Menu className="w-5 h-5" />
      </button>

      {/* 모바일 오버레이 */}
      {mobileOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-30"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* 모바일 사이드바 (슬라이드) */}
      <aside
        className={`lg:hidden fixed inset-y-0 left-0 z-40 w-64 bg-zinc-950 border-r border-zinc-800 flex flex-col transform transition-transform duration-300 ease-in-out ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {sidebarContent}
      </aside>

      {/* 데스크톱 사이드바 */}
      <aside className="hidden lg:flex w-64 bg-zinc-950 border-r border-zinc-800 flex-col z-20 flex-shrink-0">
        {sidebarContent}
      </aside>
    </>
  );
}
