/** JSON 키 패턴이 노출된 분석 텍스트를 한글 헤더로 치환 (D-3 / ADR 0013) */
export function cleanAnalysisText(text: string): string {
  const keyMap: Record<string, string> = {
    return_analysis: '수익률 분석',
    risk_analysis: '리스크 분석',
    sharpe_analysis: '샤프 비율 분석',
    composition: '포트폴리오 구성',
    summary: '요약',
    metrics_interpretation: '지표 해석',
    top_holdings: '주요 종목',
    sector_concentration: '섹터 집중도',
    diversification_score: '분산 점수',
    investor_profile: '투자자 유형',
  };

  let cleaned = text;
  for (const [key, label] of Object.entries(keyMap)) {
    cleaned = cleaned.replace(
      new RegExp(`\\*{0,2}${key}\\*{0,2}\\s*:\\s*`, 'gi'),
      `**${label}**: `,
    );
  }
  return cleaned;
}
