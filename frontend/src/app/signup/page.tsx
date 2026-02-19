'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { Sparkles, Loader2, Mail, Lock, User } from 'lucide-react';
import { signUp as signUpApi } from '@/lib/api/auth';

export default function SignUpPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsLoading(true);

    try {
      await signUpApi({ email, password, name });
      setSuccess('계정이 생성되었습니다. 로그인 페이지로 이동합니다.');
      setTimeout(() => router.push('/login'), 1500);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.data?.error?.message) {
        setError(err.response.data.error.message);
      } else {
        setError('계정 생성에 실패했습니다. 잠시 후 다시 시도해주세요.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-violet-500 rounded-xl flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold text-white">Aether</span>
          </Link>
        </div>

        <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8">
          <h1 className="text-2xl font-bold text-white mb-2">계정 생성</h1>
          <p className="text-zinc-400 mb-6">포트폴리오 최적화를 시작하세요</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                {error}
              </div>
            )}
            {success && (
              <div className="p-3 bg-green-500/10 border border-green-500/20 rounded-lg text-green-400 text-sm">
                {success}
              </div>
            )}

            <div>
              <label htmlFor="name" className="block text-sm text-zinc-400 mb-2">이름</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                <input id="name" type="text" value={name} onChange={(e) => setName(e.target.value)}
                  placeholder="이름을 입력하세요" required
                  className="w-full pl-10 pr-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition-colors" />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm text-zinc-400 mb-2">이메일</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com" required
                  className="w-full pl-10 pr-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition-colors" />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm text-zinc-400 mb-2">비밀번호</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                  placeholder="8자 이상 입력하세요" required minLength={8}
                  className="w-full pl-10 pr-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition-colors" />
              </div>
            </div>

            <button type="submit" disabled={isLoading}
              className="w-full py-3 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2">
              {isLoading ? (<><Loader2 className="w-5 h-5 animate-spin" />생성 중...</>) : '계정 생성'}
            </button>
          </form>

          <p className="text-center text-sm text-zinc-500 mt-6">
            이미 계정이 있으신가요?{' '}
            <Link href="/login" className="text-blue-400 hover:text-blue-300">로그인</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
