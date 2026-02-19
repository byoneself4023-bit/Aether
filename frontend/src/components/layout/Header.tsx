'use client';

import { usePathname, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Bell, LogOut, Menu } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { logout as logoutApi } from '@/lib/api/auth';

const pageTitles: Record<string, string> = {
  '/': '홈',
  '/dashboard': '대시보드',
  '/dashboard/optimize': '포트폴리오 최적화',
  '/dashboard/backtest': '백테스트',
  '/dashboard/chat': 'AI 어시스턴트',
  '/login': '로그인',
  '/signup': '회원가입',
};

interface HeaderProps {
  onMenuClick?: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isAuthenticated, logout, accessToken, _hasHydrated } = useAuthStore();

  const title = pageTitles[pathname] || 'Aether';

  const handleLogout = async () => {
    try {
      if (accessToken) {
        await logoutApi();
      }
    } catch {
      // 서버 로그아웃 실패해도 클라이언트는 정리
    } finally {
      logout();
      router.push('/login');
    }
  };

  return (
    <header className="h-16 border-b border-zinc-800 flex items-center justify-between px-4 sm:px-6 bg-zinc-950/80 backdrop-blur-sm sticky top-0 z-40">
      <div className="flex items-center gap-4">
        {/* Mobile menu button */}
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors"
          aria-label="Toggle menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <h1 className="text-lg font-semibold text-white">{title}</h1>
      </div>

      <div className="flex items-center gap-3">
        {!_hasHydrated ? (
          /* hydration 전에는 빈 공간으로 표시하여 SSR/CSR 불일치 방지 */
          <div className="w-24 h-8" />
        ) : isAuthenticated ? (
          <>
            {/* Notifications */}
            <button
              className="p-2 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors relative"
              aria-label="알림"
            >
              <Bell className="w-5 h-5" />
            </button>

            {/* User menu */}
            <div className="flex items-center gap-3 pl-3 border-l border-zinc-800">
              <div className="hidden sm:block text-right">
                <p className="text-sm font-medium text-white">{user?.name}</p>
                <p className="text-xs text-zinc-500">{user?.email}</p>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-red-400 transition-colors"
                title="로그아웃"
                aria-label="로그아웃"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </>
        ) : (
          <div className="flex items-center gap-2">
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
              회원가입
            </Link>
          </div>
        )}
      </div>
    </header>
  );
}
