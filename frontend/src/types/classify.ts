export interface ClassifyResult {
  domain: string;
  domain_id: number;
  confidence: number;
  category?: string;
  category_id?: number;
  category_confidence?: number;
}
