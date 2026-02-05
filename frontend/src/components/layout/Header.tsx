'use client';

import { usePathname } from 'next/navigation';
import { Activity, Wifi, WifiOff, AlertTriangle } from 'lucide-react';
import { useEffect, useState } from 'react';

const pageTitles: Record<string, string> = {
  '/': '민원 상담',
  '/dashboard': '대시보드',
  '/history': '상담 히스토리',
  '/models': '모델 관리',
  '/settings': '설정',
};

type BackendStatus = 'online' | 'offline' | 'checking' | 'mock';

export default function Header() {
  const pathname = usePathname();
  const [backendStatus, setBackendStatus] = useState<BackendStatus>('checking');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('/health', { signal: AbortSignal.timeout(3000) });
        if (res.ok) {
          const data = await res.json();
          setBackendStatus(data.mock_mode ? 'mock' : 'online');
        } else {
          setBackendStatus('offline');
        }
      } catch {
        setBackendStatus('offline');
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const title = pageTitles[pathname] || '민원 상담';

  return (
    <header className="h-16 border-b border-zinc-800 flex items-center justify-between px-4 sm:px-6 bg-zinc-950/50 backdrop-blur-sm sticky top-0 z-10">
      {/* 모바일에서 햄버거 버튼 공간 확보 */}
      <h2 className="text-lg font-bold text-white pl-10 lg:pl-0">{title}</h2>

      <div className="flex items-center gap-3">
        {/* Backend status */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800">
          {backendStatus === 'online' ? (
            <>
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500" />
              </span>
              <span className="text-xs text-green-500">서버 연결</span>
            </>
          ) : backendStatus === 'mock' ? (
            <>
              <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
              <span className="text-xs text-amber-500">데모 모드</span>
            </>
          ) : backendStatus === 'offline' ? (
            <>
              <WifiOff className="w-3.5 h-3.5 text-red-500" />
              <span className="text-xs text-red-500">서버 미연결</span>
            </>
          ) : (
            <>
              <Activity className="w-3.5 h-3.5 text-zinc-500 animate-pulse" />
              <span className="text-xs text-zinc-500">확인 중</span>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
