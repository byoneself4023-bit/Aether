# Portfolio Service 코드 리뷰

## 요약

| 항목 | 내용 |
|------|------|
| 서비스 | portfolio-service (Python/FastAPI 0.104.1) |
| 총 이슈 | 11개 (Critical 4 + Major 4 + Minor 3) |
| 전부 해결 | ✅ |

## Critical (4건)

| # | 이슈 | 수정 |
|---|------|------|
| C1 | yfinance 데이터 수집 실패 시 전체 서비스 에러 | 부분 실패 허용 (4개 중 2개 실패해도 나머지로 최적화) |
| C2 | 공분산 행렬 특이행렬(singular matrix) 시 최적화 실패 | 자동 정칙화 (Ridge Regularization) + 조건수 검증 |
| C3 | 캐시 키 충돌 가능성 | 티커+기간 기반 해시 키 생성 |
| C4 | 환경변수 미분리 (하드코딩된 설정값) | pydantic-settings 기반 환경변수 외부화 |

## Major (4건)

| # | 이슈 | 수정 |
|---|------|------|
| M1 | 구조화 로깅 미적용 | StructuredLogger 도입 (JSON 형식) |
| M2 | Prometheus 메트릭 미수집 | prometheus-client 기반 메트릭 엔드포인트 |
| M3 | 백테스트 거래비용 미반영 | transaction_cost 파라미터 (기본 0.1%) |
| M4 | 에러 응답 비표준 | HTTPException + detail 구조 통일 |

## Minor (3건)

| # | 이슈 | 수정 |
|---|------|------|
| m1 | Health Check 엔드포인트 없음 | `/health` 엔드포인트 추가 |
| m2 | Request Logging 미적용 | RequestLoggingMiddleware 추가 |
| m3 | Dockerfile 최적화 | non-root 사용자 + HEALTHCHECK |
