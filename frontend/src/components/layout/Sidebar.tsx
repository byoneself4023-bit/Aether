'use client';

import { usePathname, useRouter } from 'next/navigation';
import {
  LayoutDashboard,
  PieChart,
  TrendingUp,
  MessageSquare,
  Settings,
  X,
  Sparkles,
  Home,
} from 'lucide-react';

const navItems = [
  { id: '/', label: '홈', icon: Home },
  { id: '/dashboard', label: '대시보드', icon: LayoutDashboard },
  { id: '/dashboard/optimize', label: '최적화', icon: PieChart },
  { id: '/dashboard/backtest', label: '백테스트', icon: TrendingUp },
  { id: '/dashboard/chat', label: 'AI 채팅', icon: MessageSquare },
];

const footerItems = [
  { id: '/settings', label: '설정', icon: Settings },
];

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();

  const handleNavigation = (path: string) => {
    router.push(path);
    onClose();
  };

  const sidebarContent = (
    <>
      {/* Logo */}
      <div className="p-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-violet-500 rounded-xl flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="text-xl font-bold tracking-tight text-white">Aether</span>
            <p className="text-xs text-zinc-500">Portfolio Intelligence</p>
          </div>
        </div>
        {/* Mobile close button */}
        <button
          onClick={onClose}
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
              onClick={() => handleNavigation(item.id)}
              className={`relative w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 text-sm ${
                isActive
                  ? 'bg-blue-500/10 text-blue-400 font-medium'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-800/50'
              }`}
            >
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-blue-500 rounded-r-full" />
              )}
              <item.icon className={`w-5 h-5 ${isActive ? 'text-blue-400' : ''}`} />
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
              onClick={() => handleNavigation(item.id)}
              className={`relative w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 text-sm ${
                isActive
                  ? 'bg-blue-500/10 text-blue-400 font-medium'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-800/50'
              }`}
            >
              <item.icon className="w-5 h-5" />
              {item.label}
            </button>
          );
        })}

        {/* Version */}
        <div className="px-4 py-2 text-xs text-zinc-600">
          v0.1.0
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
          onClick={onClose}
        />
      )}

      {/* Mobile sidebar */}
      <aside
        className={`lg:hidden fixed inset-y-0 left-0 z-50 w-64 bg-zinc-950 border-r border-zinc-800 flex flex-col transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {sidebarContent}
      </aside>

      {/* Desktop sidebar */}
      <aside className="hidden lg:flex w-64 bg-zinc-950 border-r border-zinc-800 flex-col flex-shrink-0">
        {sidebarContent}
      </aside>
    </>
  );
}
