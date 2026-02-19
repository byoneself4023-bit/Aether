# LLM Service 면접 포인트

> llm-service: Gemini LLM 기반 포트폴리오 자연어 해석 + ChromaDB RAG 금융 지식 서비스
> 82 → 232 테스트 (150개 추가, 13개 이슈 해결)

---

## 1. 프롬프트 인젝션 방어

**한줄**: 정규식 기반 패턴 감지 + XML 태그 격리로 사용자 입력이 시스템 프롬프트를 오염시키지 못하게 방어했습니다.

**깊이 답변**:
LLM 서비스에서 가장 위험한 보안 취약점은 프롬프트 인젝션입니다. "Ignore all previous instructions"처럼 시스템 프롬프트를 무력화하는 공격이죠.

guardrails.py에서 두 계층으로 방어합니다:
- **1차 — 패턴 감지**: INJECTION_PATTERNS (영문 "ignore instructions", "system prompt" 등)과 FINANCIAL_ADVICE_PATTERNS (한글 "100% 수익 보장", "지금 매수" 등)을 정규식으로 검출해 필터링
- **2차 — 입력 격리**: `wrap_user_input()`으로 사용자 입력을 `<user_input>` 태그로 감싸서 시스템 프롬프트 영역과 물리적으로 분리

chat.py와 rag.py의 모든 사용자 입력 경로에 sanitize + wrap을 적용해 우회 경로가 없도록 했습니다.

**후속 질문**:
- Q: 정규식 기반 방어의 한계는?
- A: 우회 표현("Disregard above" 변형)에 취약합니다. 프로덕션에서는 Anthropic의 Constitutional AI나 별도 classifier 모델로 의미 기반 감지를 추가하겠습니다. 현재는 비용 대비 효과가 좋은 1차 방어선으로 정규식을 선택했습니다.

- Q: 금융 조언 패턴 필터링은 왜 필요한가요?
- A: LLM이 "지금 삼성전자 매수하세요" 같은 구체적 투자 조언을 하면 법적 리스크입니다. 투자자문업 미등록 상태에서 투자 권유는 자본시장법 위반이므로, 유도 질문 자체를 차단합니다.

---

## 2. Hallucination 검증

**한줄**: LLM 응답에서 수치를 추출하여 portfolio-service 원본 데이터와 교차 검증하고, 10% 이상 오차 시 경고를 붙여 반환합니다.

**깊이 답변**:
금융 서비스에서 LLM hallucination은 단순 오류가 아니라 잘못된 투자 판단으로 이어집니다. "연 수익률 42.6%인데 LLM이 60%라고 해석"하면 심각한 문제죠.

validators.py에서 세 가지를 검증합니다:
- **수익률 일관성**: LLM 응답에서 정규식으로 퍼센트 수치를 추출, 원본 portfolio-service 결과와 비교. 10% 상대 오차 초과 시 violation
- **티커 존재 여부**: "AAPL, TSLA" 분석 요청인데 응답에 "NVDA" 언급 시 감지. 한국어 혼합 텍스트("삼성전자(005930)")도 lookahead/lookbehind 정규식으로 추출
- **샤프 비율 범위**: -2~5 범위 밖이면 명백한 hallucination

검증 실패 시 응답을 차단하지 않고 `_warnings` 필드로 투명하게 노출합니다. 프론트엔드에서 경고 UI를 표시할 수 있고, 사용자가 최종 판단합니다.

**후속 질문**:
- Q: 10% 오차 허용 기준은 어떻게 정했나요?
- A: LLM이 "약 43%" vs 원본 "42.6%"처럼 반올림하는 건 자연스럽습니다. 절대 오차가 아닌 상대 오차로 계산해 |43-42.6|/42.6 ≈ 0.9%는 통과, |60-42.6|/42.6 ≈ 40.8%는 violation. 10%는 반올림은 허용하되 명백한 오류는 잡는 기준입니다.

- Q: 검증을 통과 못하면 차단하지 않는 이유는?
- A: 금융 분석에서 LLM은 보조 도구입니다. 검증 자체가 false positive를 가질 수 있고, 사용자에게 "이 수치에 불일치가 있습니다"라고 알려주는 게 차단보다 유용합니다. 차단은 서비스 가용성을 떨어뜨립니다.

---

## 3. LLM Provider 추상화 (Protocol 패턴)

**한줄**: Python Protocol로 LLM Provider 인터페이스를 정의하여, config 변경만으로 Gemini → OpenAI → Claude를 교체할 수 있는 구조입니다.

**깊이 답변**:
기존에는 llm.py가 `google.generativeai`를 직접 import해서 Gemini만 사용 가능했습니다. Gemini 장애 시 서비스 전체가 다운되는 구조죠.

llm_provider.py에서 `LLMProvider` Protocol을 정의합니다:
```python
class LLMProvider(Protocol):
    def generate(self, prompt, system_prompt, temperature, max_tokens) -> str: ...
    def generate_json(self, prompt, system_prompt, temperature) -> dict: ...
```

`GeminiProvider`가 이걸 구현하고, `get_llm_provider()` 팩토리가 config의 `llm_provider` 설정값으로 인스턴스를 생성합니다. 기존 `call_llm()`, `call_llm_json()`은 하위 호환 래퍼로 유지하여 chat.py, rag.py 등 호출부는 수정 불필요.

retry, 토큰 추적, 캐시 로직 모두 provider 내부에 통합되어 새 provider 추가 시에도 일관된 동작을 보장합니다.

**후속 질문**:
- Q: ABC(Abstract Base Class) 대신 Protocol을 쓴 이유는?
- A: Protocol은 structural subtyping(덕 타이핑)이라 구현 클래스가 명시적 상속 없이도 인터페이스를 만족하면 됩니다. 서드파티 라이브러리 래핑 시 상속 체인이 복잡해지는 걸 피하고, 런타임 오버헤드 없이 mypy로 타입 체크할 수 있습니다.

- Q: 실제 OpenAI Provider를 추가한다면?
- A: `OpenAIProvider` 클래스에서 `generate()`, `generate_json()`만 구현하고, config.py에 `llm_provider: str = "openai"`로 바꾸면 됩니다. 기존 코드 변경 0줄. 환경변수로 관리하면 배포 시점에 결정할 수 있습니다.

---

## 4. 토큰 비용 추적

**한줄**: 모든 LLM 호출의 input/output 토큰을 스레드 안전하게 집계하고, /api/metrics/tokens로 실시간 비용을 모니터링합니다.

**깊이 답변**:
LLM 서비스 운영에서 가장 큰 리스크는 예상치 못한 비용 폭증입니다. 트래픽 10배 증가 시 비용도 10배인데, 추적 없으면 월말 청구서에서야 알게 됩니다.

token_tracker.py에서:
- `TokenUsage` dataclass로 input/output 토큰, 모델명, 타임스탬프 기록
- `TokenTracker`가 `threading.Lock`으로 동시 호출 안전하게 집계
- `estimate_cost()`로 Gemini 2.5 Flash 가격 기준 실시간 비용 산출
- 시간별/일별 집계로 이상 트래픽 감지 가능

llm_provider.py에서 모든 LLM 응답의 `usage_metadata`를 자동 추출하고, /api/metrics/tokens 엔드포인트로 대시보드에서 모니터링합니다.

**후속 질문**:
- Q: 스레드 안전은 왜 필요한가요?
- A: FastAPI는 async지만 내부적으로 thread pool에서 sync 작업을 실행합니다. 여러 요청이 동시에 `record_usage()`를 호출하면 리스트 append와 합계 계산에서 race condition이 발생할 수 있어 Lock으로 보호합니다.

- Q: 인메모리 집계의 한계는?
- A: 서버 재시작 시 데이터 유실됩니다. 프로덕션에서는 Redis나 Prometheus pushgateway로 영속화하고, Grafana 대시보드와 연동하겠습니다. 현재는 단일 인스턴스 MVP 단계이므로 인메모리로 충분합니다.

---

## 5. RAG Chunking + Context Window 최적화

**한줄**: 2단계 분할(헤더→문단)과 쿼리 관련성 스코어링으로 토큰 예산 내에서 최적의 컨텍스트를 구성합니다.

**깊이 답변**:
RAG 파이프라인의 두 가지 문제를 함께 해결했습니다:

**Chunking 개선 (#7)**:
기존에는 `##` 헤더로만 분할해서, "효율적 프론티어" 섹션이 3000자면 통째로 하나의 청크였습니다. 검색 정확도가 떨어지고 토큰이 낭비됩니다.

2단계 분할로 개선:
- 1단계: ## 헤더 기준 섹션 분할 (기존 유지)
- 2단계: chunk_size(1000자) 초과 섹션은 문단(빈 줄) 기준 추가 분할, chunk_overlap(200자)으로 문맥 연결

**Context Window 최적화 (#13)**:
검색된 문서 5개를 그대로 LLM에 넘기면 15000자 → 토큰 낭비. `build_optimized_context()`에서:
- 문서당 예산을 균등 분배 (max_context_chars / 문서 수)
- 예산 초과 문서는 `extract_relevant_paragraphs()`로 쿼리 단어 overlap이 높은 문단만 추출
- 결과적으로 3000자 이내로 관련성 높은 컨텍스트만 구성

**후속 질문**:
- Q: overlap이 왜 필요한가요?
- A: "효율적 프론티어는 마코위츠가 제안한 이론으로" / "이 이론에서 리스크는..." 이렇게 두 청크로 나뉘면, 두 번째 청크만 검색됐을 때 "이 이론"이 뭔지 모릅니다. overlap으로 앞 청크의 마지막 200자를 포함시켜 문맥을 유지합니다.

- Q: 단어 overlap 기반 관련성의 한계는?
- A: 동의어("수익률" vs "리턴")를 잡지 못합니다. 프로덕션에서는 임베딩 유사도를 쓰겠지만, paragraph 레벨 임베딩은 비용이 추가됩니다. 현재 단계에서는 키워드 매칭이 비용 대비 충분한 성능을 보여줍니다.

---

## 6. 프롬프트 버전 관리

**한줄**: PromptRegistry에 프롬프트를 버전별로 등록하여 변경 이력을 추적하고, A/B 테스트와 롤백이 가능한 구조입니다.

**깊이 답변**:
LLM 서비스에서 프롬프트는 모델의 행동을 결정하는 핵심 파라미터입니다. 그런데 prompts.py에 하드코딩하면:
- "지난주 프롬프트가 더 좋았는데" → 롤백 불가
- "어떤 프롬프트가 더 정확한지" → A/B 테스트 불가

prompt_registry.py에서:
- `PromptTemplate` dataclass로 name, version, template, created_at 관리
- `PromptRegistry`가 버전별 프롬프트를 저장, 최신 버전 자동 반환
- `get_system_prompt(version="1.0")`으로 특정 버전 호출 가능
- 레지스트리 실패 시 기존 SYSTEM_PROMPT fallback 보장

**후속 질문**:
- Q: 인메모리 레지스트리의 한계는?
- A: 서버 재시작 시 코드에 등록된 v1.0만 남습니다. 프로덕션에서는 DB 저장 + 관리 UI로 확장하겠습니다. 현재 구조는 인터페이스가 동일하므로 저장소만 교체하면 됩니다.

---

## 7. 구조화된 로깅 + Rate Limiting + Health Check

**한줄**: JSON 로그에 request_id 부여, IP 기반 요청 제한, 의존성별 상태 체크로 프로덕션 운영 가시성을 확보했습니다.

**깊이 답변**:

**구조화된 로깅 (#5)**: 모든 요청에 UUID v4 request_id를 부여하고 JSON 포맷으로 로그를 남깁니다. "request_id abc123"으로 ELK 스택에서 하나의 요청 흐름을 추적할 수 있습니다.

**Rate Limiting (#10)**: IP당 분당 60회 sliding window 제한. 초과 시 429 + Retry-After 헤더. /health와 /는 제외하여 모니터링에 영향 없음. X-Forwarded-For 지원으로 로드밸런서 뒤에서도 실제 IP 식별.

**Health Check (#12)**: 기존 항상 "healthy" → API 키/벡터스토어/portfolio-service 개별 체크. 하나라도 실패 시 "degraded". 쿠버네티스 readiness probe에서 degraded를 감지해 트래픽을 다른 파드로 돌릴 수 있습니다.

**후속 질문**:
- Q: Rate Limiting이 인메모리인데 서버가 여러 대면?
- A: 각 서버가 독립적으로 카운트하므로 전체 제한이 서버 수 × 60이 됩니다. 프로덕션에서는 Redis 기반 분산 rate limiter(예: Nginx rate_limit 모듈 또는 Redis sliding window)로 교체합니다.

---

## 8. LLM 응답 캐시

**한줄**: SHA-256 해시 키 기반 LRU 캐시로 동일 질문의 LLM 재호출을 방지하고, TTL로 오래된 캐시를 자동 만료합니다.

**깊이 답변**:
"샤프 비율이 뭐야?"를 10명이 물어보면 10번 LLM을 호출할 필요가 없습니다. 

cache.py에서:
- `_make_key()`: prompt + system_prompt + temperature 등을 SHA-256 해시로 캐시 키 생성. 동일 파라미터 → 동일 키 보장
- `LLMCache`: OrderedDict 기반 LRU. max_size(기본 1000) 초과 시 가장 오래된 항목 제거
- TTL(기본 3600초) 만료 시 자동 삭제
- `threading.Lock`으로 동시 접근 안전
- `use_cache=False`로 캐시 우회 가능 (실시간 데이터 분석 시)

generate_json()에서는 JSON 캐시를 별도로 관리하고, 내부 generate() 호출 시 `use_cache=False`로 중복 캐싱을 방지합니다.

**후속 질문**:
- Q: 포트폴리오 분석은 캐싱하면 안 되지 않나요?
- A: 맞습니다. 사용자별 포트폴리오 데이터가 다르므로 캐시 키에 포트폴리오 데이터도 포함됩니다. 동일 포트폴리오 + 동일 질문이면 캐시 히트, 다른 포트폴리오면 미스. 실시간성이 중요한 호출은 `use_cache=False`로 우회합니다.

---

## 9. RAG 평가 체계

**한줄**: Precision@K와 키워드 커버리지로 RAG 검색 품질을 정량 측정하는 평가 프레임워크를 구축했습니다.

**깊이 답변**:
RAG 파이프라인에서 "검색 결과가 좋은지"를 감(感)이 아닌 숫자로 알아야 합니다.

rag_evaluator.py에서:
- `EvalQuery`: 질문 + 기대 소스 + 기대 키워드로 평가 데이터셋 정의
- `evaluate_single_query()`: Precision@K (상위 K개 중 관련 문서 비율) + 키워드 커버리지 (기대 키워드 중 검색 결과에 포함된 비율)
- `evaluate_retrieval()`: 전체 데이터셋 평가 → `EvalSummary` (source_accuracy, avg_keyword_coverage)
- 기본 6개 평가 쿼리: 샤프 비율, 효율적 프론티어, VaR, 포트폴리오 최적화 등

**후속 질문**:
- Q: Precision@K만으로 충분한가요?
- A: Recall@K, MRR, NDCG도 중요합니다. 현재는 MVP 평가로 Precision@K + 키워드 커버리지를 선택했고, 프레임워크 구조상 새 메트릭 추가는 `evaluate_single_query()`에 필드를 추가하면 됩니다.

---

## 통합 아키텍처 답변

**"llm-service 전체 구조를 설명해주세요"**:

```
[사용자 질문]
    ↓
[Rate Limiting] → 429 차단
    ↓
[Request Logging] → UUID + JSON 로그
    ↓
[Guardrails] → 인젝션/금융조언 필터링
    ↓
[RAG Pipeline]
    ├─ ChromaDB 검색 (개선된 Chunking)
    ├─ Context Window 최적화 (관련 문단만)
    └─ Prompt Registry (버전 관리)
    ↓
[LLM Provider] → Gemini (추상화, 교체 가능)
    ├─ Token Tracker (비용 추적)
    └─ LLM Cache (중복 호출 방지)
    ↓
[Validators] → Hallucination 검증
    ↓
[응답 + _warnings]
```

"입구에서 rate limit과 로깅으로 트래픽을 관리하고, guardrails로 악의적 입력을 차단합니다. RAG 파이프라인에서 최적화된 컨텍스트를 구성하고, Provider 추상화를 통해 LLM을 호출합니다. 응답은 hallucination 검증을 거쳐 경고와 함께 반환됩니다. 모든 호출은 토큰 추적과 캐시를 거치며, health check로 서비스 상태를 실시간 모니터링합니다."
