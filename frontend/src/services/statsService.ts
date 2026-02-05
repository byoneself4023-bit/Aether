import { apiFetch } from './api';

export interface ModelStats {
  model_name: string;
  total_queries: number;
  avg_response_time_ms: number;
  helpful_rate: number | null;
  total_feedback: number;
}

export interface DailyCount {
  date: string;
  count: number;
}

export interface DomainCount {
  domain: string;
  count: number;
}

export interface FeedbackSummary {
  id: number;
  query: string;
  answer: string;
  model_name: string;
  domain: string | null;
  rating: number;
  created_at: string;
}

export async function fetchOverview(): Promise<{ models: ModelStats[] }> {
  return apiFetch('/stats/overview');
}

export async function fetchDaily(days = 30): Promise<{ daily: DailyCount[] }> {
  return apiFetch(`/stats/daily?days=${days}`);
}

export async function fetchDomains(): Promise<{ domains: DomainCount[] }> {
  return apiFetch('/stats/domains');
}

export async function fetchFeedbackList(
  limit = 20,
): Promise<{ feedback: FeedbackSummary[] }> {
  return apiFetch(`/stats/feedback?limit=${limit}`);
}
