import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, AuthState } from '@/types/auth';

interface AuthStore extends AuthState {
  _hasHydrated: boolean;
  setHasHydrated: (hydrated: boolean) => void;
  setUser: (user: User | null) => void;
  setTokens: (accessToken: string, refreshToken: string) => void;
  logout: () => void;
  setLoading: (isLoading: boolean) => void;
  getRefreshToken: () => string | null;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: true,
      _hasHydrated: false,

      setHasHydrated: (hydrated) => set({ _hasHydrated: hydrated }),

      setUser: (user) =>
        set({
          user,
          isAuthenticated: !!user,
        }),

      // TODO: Production에서는 HttpOnly 쿠키로 이동 권장 (XSS 방어)
      // 현재는 포트폴리오 프로젝트 범위상 localStorage 사용
      setTokens: (accessToken, refreshToken) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem('aether-refresh-token', refreshToken);
        }
        set({ accessToken, isAuthenticated: true });
      },

      logout: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('aether-refresh-token');
        }
        set({
          user: null,
          accessToken: null,
          isAuthenticated: false,
        });
      },

      setLoading: (isLoading) => set({ isLoading }),

      getRefreshToken: () => {
        if (typeof window !== 'undefined') {
          return localStorage.getItem('aether-refresh-token');
        }
        return null;
      },
    }),
    {
      name: 'aether-auth',
      // accessToken을 persist에서 제외 — 메모리에만 보관
      // XSS 시 localStorage에서 accessToken 탈취 불가
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);
