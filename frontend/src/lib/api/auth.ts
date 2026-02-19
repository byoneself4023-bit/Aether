import axios from 'axios';
import { API_URLS } from '@/lib/utils/constants';
import { createApiClient } from './client';
import type { LoginRequest, SignUpRequest, TokenResponse, User } from '@/types/auth';

// 인증 불필요 요청 (login, signup, refresh)은 plain axios
const publicApi = axios.create({
  baseURL: API_URLS.AUTH,
  headers: { 'Content-Type': 'application/json' },
});

// 인증 필요 요청 (logout, getMe)은 공통 클라이언트
const authApi = createApiClient(API_URLS.AUTH);

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: {
    code: string;
    message: string;
  };
}

export async function login(request: LoginRequest): Promise<TokenResponse> {
  const response = await publicApi.post<ApiResponse<TokenResponse>>('/api/auth/login', request);
  return response.data.data;
}

export async function signUp(request: SignUpRequest): Promise<User> {
  const response = await publicApi.post<ApiResponse<User>>('/api/auth/signup', request);
  return response.data.data;
}

export async function refreshToken(token: string): Promise<TokenResponse> {
  const response = await publicApi.post<ApiResponse<TokenResponse>>('/api/auth/refresh', {
    refreshToken: token,
  });
  return response.data.data;
}

export async function logout(): Promise<void> {
  await authApi.post('/api/auth/logout');
}

export async function getMe(): Promise<User> {
  const response = await authApi.get<ApiResponse<User>>('/api/auth/me');
  return response.data.data;
}
