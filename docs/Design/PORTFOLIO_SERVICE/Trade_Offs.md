# 기술 선택 트레이드오프

## 핵심 선택

| 선택        | 대안                  | 왜 이걸 선택했나                                        |
| ----------- | --------------------- | ------------------------------------------------------- |
| scipy       | cvxpy, PyPortfolioOpt | 직접 구현으로 수학 이해도 증명, 외부 의존성 최소화      |
| Chroma      | FAISS, Pinecone       | 로컬 실행 가능, 무료, 임베딩 저장/검색 통합             |
| LangChain   | 직접 구현             | RAG 패턴 빠르게 적용, 프롬프트 체이닝 편의성            |
| FastAPI     | Flask, Django         | 비동기 기본 지원, 타입 힌트 자동 문서화                 |
| JWT + Redis | 세션 기반             | stateless 마이크로서비스, 토큰 블랙리스트로 즉시 무효화 |

------

## 아키텍처 선택

### 마이크로서비스 vs 모놀리식

- **선택:** 마이크로서비스 (auth / portfolio / llm / frontend)
- **이유:** 실무 아키텍처 경험 + 서비스별 독립 배포/스케일링
- **트레이드오프:** 복잡성 증가, 서비스 간 통신 오버헤드
- **인식:** 1인 프로젝트에서는 모놀리식이 효율적이지만, 학습 목적으로 분리

### REST 동기 vs 메시지 큐

- **선택:** REST 동기
- **이유:** 단순함, 디버깅 용이
- **트레이드오프:** 서비스 장애 전파, 동시 처리 제한
- **향후:** gRPC 또는 메시지 큐 도입 가능

------

## 데이터/모델 선택

### Markowitz + Shrinkage vs Black-Litterman

- **선택:** Markowitz + Ledoit-Wolf Shrinkage
- **이유:** 기본 이론부터 직접 구현, Shrinkage로 실무 보완
- **트레이드오프:** 투자자 전망(view) 미반영
- **향후:** Black-Litterman, Risk Parity 추가 가능

### Sample 공분산 vs Shrinkage 공분산

- **선택:** Shrinkage 기본 적용
- **근거:** 조건수 81,229 → 7,322 (91% 개선), T/N=3.2로 Sample 불안정
- **트레이드오프:** 극단적 상관관계 정보 일부 손실
- **검증:** Phase 0-3에서 Sample vs Shrinkage 효율적 프론티어 비교 완료

### yfinance vs 유료 데이터

- **선택:** yfinance (무료)
- **이유:** 포트폴리오 프로젝트 목적, 비용 최소화
- **트레이드오프:** Rate limiting, Survivorship bias, 데이터 신뢰성
- **인식:** 실서비스는 Bloomberg/Refinitiv 필요