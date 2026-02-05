'use client';

import { CheckCircle2, XCircle, AlertTriangle, Info, X } from 'lucide-react';
import type { Toast as ToastData } from '@/hooks/useToast';

const config: Record<string, { icon: typeof CheckCircle2; color: string; bg: string }> = {
  success: { icon: CheckCircle2, color: 'text-green-400', bg: 'border-green-500/30 bg-green-500/10' },
  error:   { icon: XCircle,     color: 'text-red-400',   bg: 'border-red-500/30 bg-red-500/10' },
  warning: { icon: AlertTriangle, color: 'text-amber-400', bg: 'border-amber-500/30 bg-amber-500/10' },
  info:    { icon: Info,         color: 'text-blue-400',  bg: 'border-blue-500/30 bg-blue-500/10' },
};

export default function ToastContainer({
  toasts,
  onRemove,
}: {
  toasts: ToastData[];
  onRemove: (id: number) => void;
}) {
  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map((t) => {
        const c = config[t.type] || config.info;
        const Icon = c.icon;
        return (
          <div
            key={t.id}
            className={`pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl border backdrop-blur-md shadow-lg toast-enter ${c.bg}`}
          >
            <Icon className={`w-4 h-4 shrink-0 ${c.color}`} />
            <span className="text-sm text-white flex-1">{t.message}</span>
            <button
              onClick={() => onRemove(t.id)}
              className="text-zinc-500 hover:text-white transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        );
      })}
    </div>
  );
}
