'use client';

import AppLayout from '@/components/layout/AppLayout';
import { api } from '@/services/api';
import { useToastContext } from '@/components/common/ToastProvider';
import { Save, RotateCcw, Server, Wifi, WifiOff, CheckCircle2 } from 'lucide-react';
import { useEffect, useState } from 'react';

interface SettingsData {
  llm_provider: string;
  ollama_model: string;
  top_k: number;
  min_similarity: number;
  max_tokens: number;
  backend_version?: string;
  ollama_base_url?: string;
  google_api_configured?: boolean;
}

export default function SettingsPage() {
  const toast = useToastContext();
  const [settings, setSettings] = useState<SettingsData>({
    llm_provider: 'ollama',
    ollama_model: 'gemma2:2b',
    top_k: 5,
    min_similarity: 0.5,
    max_tokens: 1024,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const data = await api.get<SettingsData>('/settings');
        setSettings(data);
      } catch { /* use defaults */ }
      setLoading(false);
    })();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const result = await api.put<{ success: boolean; settings: SettingsData }>('/settings', {
        llm_provider: settings.llm_provider,
        ollama_model: settings.ollama_model,
        top_k: settings.top_k,
        min_similarity: settings.min_similarity,
        max_tokens: settings.max_tokens,
      });
      if (result.settings) setSettings(prev => ({ ...prev, ...result.settings }));
      setSaved(true);
      toast.success('설정이 저장되었습니다');
      setTimeout(() => setSaved(false), 2000);
    } catch {
      toast.error('설정 저장에 실패했습니다');
    }
    setSaving(false);
  };

  const handleReset = async () => {
    const defaults: Partial<SettingsData> = {
      llm_provider: 'ollama',
      ollama_model: 'gemma2:2b',
      top_k: 5,
      min_similarity: 0.5,
      max_tokens: 1024,
    };
    setSettings(prev => ({ ...prev, ...defaults }));
    toast.info('기본값으로 초기화되었습니다');
  };

  const update = (key: keyof SettingsData, value: unknown) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const inputCls = "w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/30 transition-all";

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto space-y-6 animate-in fade-in duration-500">
        {/* System Info */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 hover:border-zinc-700 transition-all">
          <h3 className="text-sm font-bold text-zinc-400 mb-4 flex items-center gap-2">
            <Server className="w-4 h-4" /> 시스템 정보
          </h3>
          {loading ? (
            <div className="space-y-3">{[1, 2, 3].map(i => <div key={i} className="skeleton h-6 w-full rounded" />)}</div>
          ) : (
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-zinc-800/50 border border-zinc-700/50 rounded-lg p-3">
                <p className="text-xs text-zinc-500">백엔드 버전</p>
                <p className="text-sm font-medium text-white mt-0.5">{settings.backend_version || '-'}</p>
              </div>
              <div className="bg-zinc-800/50 border border-zinc-700/50 rounded-lg p-3">
                <p className="text-xs text-zinc-500">Ollama</p>
                <p className="text-sm font-medium text-white mt-0.5 truncate">{settings.ollama_base_url || '-'}</p>
              </div>
              <div className="bg-zinc-800/50 border border-zinc-700/50 rounded-lg p-3">
                <p className="text-xs text-zinc-500">Gemini API</p>
                <div className="flex items-center gap-1.5 mt-0.5">
                  {settings.google_api_configured ? (
                    <><Wifi className="w-3.5 h-3.5 text-green-500" /><span className="text-sm text-green-500">설정됨</span></>
                  ) : (
                    <><WifiOff className="w-3.5 h-3.5 text-zinc-500" /><span className="text-sm text-zinc-500">미설정</span></>
                  )}
                </div>
              </div>
              <div className="bg-zinc-800/50 border border-zinc-700/50 rounded-lg p-3">
                <p className="text-xs text-zinc-500">현재 LLM</p>
                <p className="text-sm font-medium text-white mt-0.5">{settings.ollama_model}</p>
              </div>
            </div>
          )}
        </div>

        {/* LLM Settings */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 hover:border-zinc-700 transition-all">
          <h3 className="text-sm font-bold text-zinc-400 mb-4">LLM 설정</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-xs text-zinc-500 mb-1.5">LLM 프로바이더</label>
              <select value={settings.llm_provider} onChange={(e) => update('llm_provider', e.target.value)} className={inputCls}>
                <option value="ollama">Ollama (로컬)</option>
                <option value="gemini">Gemini (클라우드)</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-zinc-500 mb-1.5">Ollama 모델</label>
              <select value={settings.ollama_model} onChange={(e) => update('ollama_model', e.target.value)} className={inputCls}>
                <option value="gemma2:2b">Gemma 2 2B</option>
                <option value="qwen2.5:7b-instruct">Qwen 2.5 7B Instruct</option>
                <option value="llama3:8b">Llama 3 8B</option>
                <option value="mistral:7b">Mistral 7B</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-zinc-500 mb-1.5">최대 토큰 수</label>
              <input type="number" value={settings.max_tokens} onChange={(e) => update('max_tokens', Number(e.target.value))} min={128} max={4096} className={inputCls} />
            </div>
          </div>
        </div>

        {/* Search Settings */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 hover:border-zinc-700 transition-all">
          <h3 className="text-sm font-bold text-zinc-400 mb-4">검색 설정</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-xs text-zinc-500 mb-1.5">유사 문서 수 (top-k)</label>
              <input type="number" value={settings.top_k} onChange={(e) => update('top_k', Number(e.target.value))} min={1} max={20} className={inputCls} />
            </div>
            <div>
              <label className="block text-xs text-zinc-500 mb-1.5">최소 유사도 임계값</label>
              <input type="number" value={settings.min_similarity} onChange={(e) => update('min_similarity', Number(e.target.value))} min={0} max={1} step={0.05} className={inputCls} />
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className={`flex items-center gap-2 px-5 py-2.5 text-white text-sm font-bold rounded-lg disabled:opacity-50 transition-all duration-300 ${saved ? 'bg-green-500 hover:bg-green-400' : 'bg-blue-500 hover:bg-blue-400'}`}
          >
            {saved ? <CheckCircle2 className="w-4 h-4" /> : <Save className="w-4 h-4" />}
            {saved ? '저장됨' : saving ? '저장 중...' : '설정 저장'}
          </button>
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-5 py-2.5 bg-zinc-800 text-zinc-300 text-sm rounded-lg hover:bg-zinc-700 transition-all border border-zinc-700"
          >
            <RotateCcw className="w-4 h-4" />
            초기화
          </button>
        </div>
      </div>
    </AppLayout>
  );
}
