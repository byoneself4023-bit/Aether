'use client';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tag, TrendingUp } from 'lucide-react';

interface ClassificationResultProps {
  domain: string | null;
  confidence: number | null;
  isLoading?: boolean;
}

export function ClassificationResult({
  domain,
  confidence,
  isLoading = false,
}: ClassificationResultProps) {
  // 신뢰도에 따른 색상
  const getConfidenceColor = (conf: number) => {
    if (conf >= 0.9) return 'bg-green-100 text-green-800 border-green-200';
    if (conf >= 0.7) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  // 도메인별 색상
  const getDomainColor = (domain: string) => {
    const colors: Record<string, string> = {
      '금융/보험': 'bg-blue-500',
      'K쇼핑': 'bg-purple-500',
      '질병관리본부': 'bg-green-500',
      '다산콜센터': 'bg-orange-500',
    };
    return colors[domain] || 'bg-slate-500';
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <Tag className="h-4 w-4" />
            분류 결과
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-3">
            <div className="h-8 w-24 animate-pulse rounded-md bg-slate-200" />
            <div className="h-6 w-16 animate-pulse rounded-full bg-slate-200" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!domain) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <Tag className="h-4 w-4" />
            분류 결과
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-500">
            민원 내용을 입력하면 자동으로 분류됩니다.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Tag className="h-4 w-4" />
          분류 결과
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* 도메인 뱃지 */}
            <Badge
              className={`${getDomainColor(domain)} text-white px-3 py-1 text-sm font-medium`}
            >
              {domain}
            </Badge>

            {/* 신뢰도 */}
            {confidence !== null && (
              <Badge
                variant="outline"
                className={`${getConfidenceColor(confidence)} px-2 py-1`}
              >
                <TrendingUp className="mr-1 h-3 w-3" />
                {(confidence * 100).toFixed(1)}%
              </Badge>
            )}
          </div>
        </div>

        {/* 신뢰도 바 */}
        {confidence !== null && (
          <div className="mt-4">
            <div className="flex justify-between text-xs text-slate-500 mb-1">
              <span>신뢰도</span>
              <span>{(confidence * 100).toFixed(1)}%</span>
            </div>
            <div className="h-2 w-full rounded-full bg-slate-100">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${
                  confidence >= 0.9
                    ? 'bg-green-500'
                    : confidence >= 0.7
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
                }`}
                style={{ width: `${confidence * 100}%` }}
              />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
