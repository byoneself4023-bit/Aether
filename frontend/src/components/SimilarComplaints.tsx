'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileSearch } from 'lucide-react';

interface SimilarComplaint {
  question: string;
  answer: string;
  domain: string;
  category: string;
  score: number;
}

interface SimilarComplaintsProps {
  complaints: SimilarComplaint[];
  isLoading?: boolean;
  onSelect?: (complaint: SimilarComplaint) => void;
}

export function SimilarComplaints({
  complaints,
  isLoading = false,
  onSelect,
}: SimilarComplaintsProps) {
  const getScoreColor = (score: number) => {
    if (score >= 0.95) return 'text-green-600';
    if (score >= 0.85) return 'text-blue-600';
    if (score >= 0.75) return 'text-yellow-600';
    return 'text-slate-500';
  };

  if (isLoading) {
    return (
      <Card className="shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <FileSearch className="h-4 w-4 text-blue-500" />
            유사 민원
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="p-4 rounded-xl border bg-slate-50 animate-pulse">
                <div className="h-4 w-20 bg-slate-200 rounded mb-2" />
                <div className="h-4 w-full bg-slate-200 rounded mb-2" />
                <div className="h-3 w-32 bg-slate-200 rounded" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (complaints.length === 0) {
    return (
      <Card className="shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <FileSearch className="h-4 w-4 text-blue-500" />
            유사 민원
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-500">
            민원을 입력하면 과거 유사 사례를 찾아드립니다.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-base">
          <div className="flex items-center gap-2">
            <FileSearch className="h-4 w-4 text-blue-500" />
            유사 민원
          </div>
          <Badge variant="secondary" className="bg-blue-100 text-blue-700">
            {complaints.length}건 발견
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 pt-0">
        <div className="max-h-[350px] overflow-y-auto space-y-3 pr-1">
          {complaints.map((complaint, index) => (
            <button
              key={index}
              onClick={() => onSelect?.(complaint)}
              className="w-full text-left p-4 rounded-xl border border-slate-200 hover:border-blue-400 hover:shadow-md transition-all bg-white"
            >
              {/* 순위 + 유사도 */}
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-semibold text-slate-500">{index + 1}위</span>
                <span className="text-xs text-slate-300">·</span>
                <span className={`text-xs font-bold ${getScoreColor(complaint.score)}`}>
                  {(complaint.score * 100).toFixed(0)}%
                </span>
              </div>
              
              {/* 질문 */}
              <p className="text-sm font-medium text-slate-800 mb-2 line-clamp-2">
                {complaint.question}
              </p>
              
              {/* 도메인 · 카테고리 */}
              <p className="text-xs text-slate-400">
                {complaint.domain} · {complaint.category}
              </p>
            </button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
