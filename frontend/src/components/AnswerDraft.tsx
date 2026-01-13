'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Bot, Copy, Check, RefreshCw, Send, Pencil } from 'lucide-react';

interface AnswerDraftProps {
  answer: string | null;
  isLoading?: boolean;
  onRegenerate?: () => void;
  onSend?: (answer: string) => void;
}

export function AnswerDraft({
  answer,
  isLoading = false,
  onRegenerate,
  onSend,
}: AnswerDraftProps) {
  const [editedAnswer, setEditedAnswer] = useState(answer || '');
  const [copied, setCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  if (answer && answer !== editedAnswer && !isLoading) {
    setEditedAnswer(answer);
  }

  const handleCopy = async () => {
    await navigator.clipboard.writeText(editedAnswer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (isLoading) {
    return (
      <Card className="shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <Bot className="h-4 w-4 text-blue-500" />
            AI 답변 초안
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="h-4 w-full animate-pulse rounded bg-slate-200" />
            <div className="h-4 w-5/6 animate-pulse rounded bg-slate-200" />
            <div className="h-4 w-4/6 animate-pulse rounded bg-slate-200" />
          </div>
          <p className="text-xs text-slate-500 mt-4 flex items-center gap-2">
            <RefreshCw className="h-3 w-3 animate-spin" />
            AI가 답변을 생성하고 있습니다...
          </p>
        </CardContent>
      </Card>
    );
  }

  if (!answer) {
    return (
      <Card className="shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <Bot className="h-4 w-4 text-blue-500" />
            AI 답변 초안
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-500">
            민원 내용을 입력하면 AI가 답변 초안을 생성합니다.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <Bot className="h-4 w-4 text-blue-500" />
            AI 답변 초안
          </CardTitle>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsEditing(!isEditing)}
              className="h-8 w-8 p-0"
              title={isEditing ? "미리보기" : "편집"}
            >
              <Pencil className={`h-4 w-4 ${isEditing ? 'text-blue-500' : 'text-slate-400'}`} />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={onRegenerate}
              className="h-8 w-8 p-0"
              title="다시 생성"
            >
              <RefreshCw className="h-4 w-4 text-slate-400" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
              className="h-8 w-8 p-0"
              title="복사"
            >
              {copied ? (
                <Check className="h-4 w-4 text-green-500" />
              ) : (
                <Copy className="h-4 w-4 text-slate-400" />
              )}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {isEditing ? (
          <Textarea
            value={editedAnswer}
            onChange={(e) => setEditedAnswer(e.target.value)}
            className="min-h-[280px] resize-none text-sm"
            placeholder="AI 생성 답변..."
          />
        ) : (
          <div className="max-h-[280px] overflow-y-auto p-4 border rounded-xl bg-slate-50 text-sm leading-relaxed">
            <ReactMarkdown
              components={{
                p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
                strong: ({ children }) => <strong className="font-semibold text-slate-800">{children}</strong>,
                ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>,
                li: ({ children }) => <li className="text-slate-700">{children}</li>,
              }}
            >
              {editedAnswer}
            </ReactMarkdown>
          </div>
        )}

        <p className="text-xs text-slate-500">
          💡 AI가 생성한 초안입니다. 필요시 수정 후 전송하세요.
        </p>

        <Button
          onClick={() => onSend?.(editedAnswer)}
          className="w-full bg-blue-600 hover:bg-blue-700"
        >
          <Send className="h-4 w-4 mr-2" />
          답변 전송
        </Button>
      </CardContent>
    </Card>
  );
}
