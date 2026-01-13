'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, Cpu, Cloud } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface LLMResult {
  answer: string;
  elapsed_time: number;
  model_name: string;
}

interface LLMCompareProps {
  ollama: LLMResult | null;
  gemini: LLMResult | null;
  isLoading?: boolean;
}

export function LLMCompare({ ollama, gemini, isLoading = false }: LLMCompareProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-4">
        {[1, 2].map((i) => (
          <Card key={i} className="shadow-sm">
            <CardHeader className="pb-3">
              <div className="h-6 w-32 bg-slate-200 animate-pulse rounded" />
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="h-4 w-full bg-slate-200 animate-pulse rounded" />
                <div className="h-4 w-5/6 bg-slate-200 animate-pulse rounded" />
                <div className="h-4 w-4/6 bg-slate-200 animate-pulse rounded" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!ollama && !gemini) {
    return null;
  }

  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Ollama (로컬) */}
      <Card className="shadow-sm border-orange-200">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between text-base">
            <div className="flex items-center gap-2">
              <Cpu className="h-4 w-4 text-orange-500" />
              <span>Gemma 2B</span>
              <Badge variant="outline" className="text-xs bg-orange-50 text-orange-700 border-orange-200">
                로컬
              </Badge>
            </div>
            {ollama && (
              <div className="flex items-center gap-1 text-sm text-slate-500">
                <Clock className="h-3 w-3" />
                {ollama.elapsed_time}초
              </div>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {ollama ? (
            <div className="max-h-[300px] overflow-y-auto text-sm leading-relaxed prose prose-sm">
              <ReactMarkdown>{ollama.answer}</ReactMarkdown>
            </div>
          ) : (
            <p className="text-sm text-slate-500">로딩 중...</p>
          )}
        </CardContent>
      </Card>

      {/* Gemini (API) */}
      <Card className="shadow-sm border-blue-200">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between text-base">
            <div className="flex items-center gap-2">
              <Cloud className="h-4 w-4 text-blue-500" />
              <span>Gemini 2.5 Flash Lite</span>
              <Badge variant="outline" className="text-xs bg-blue-50 text-blue-700 border-blue-200">
                API
              </Badge>
            </div>
            {gemini && (
              <div className="flex items-center gap-1 text-sm text-slate-500">
                <Clock className="h-3 w-3" />
                {gemini.elapsed_time}초
              </div>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {gemini ? (
            <div className="max-h-[300px] overflow-y-auto text-sm leading-relaxed prose prose-sm">
              <ReactMarkdown>{gemini.answer}</ReactMarkdown>
            </div>
          ) : (
            <p className="text-sm text-slate-500">로딩 중...</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
