import { apiFetch } from './api';

export interface FeedbackRequest {
  query: string;
  answer: string;
  model_name?: string;
  domain?: string;
  category?: string;
  rating: number; // 1=helpful, 0=not helpful
  comment?: string;
}

export interface FeedbackResponse {
  id: number;
  message: string;
}

export async function submitFeedback(
  data: FeedbackRequest,
): Promise<FeedbackResponse> {
  return apiFetch<FeedbackResponse>('/feedback', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}
