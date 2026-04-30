# ADR 0003 — Prompt Registry: Single Entry Point and Versioning

- **상태**: Accepted
- **일자**: 2026-04-28
- **관련 작업**: H-4 (`e9acdf8` — RAG 프롬프트 registry 일원화)

---

## 컨텍스트

H-4 이전, llm-service는 LLM 프롬프트를 **두 채널로 관리**하고 있었다:

1. 도메인 프롬프트 5종(`system_prompt`, 4개 JSON 스키마)은 `prompt_registry.py:130-189`에 등록되어 `get_registry().get(name, version)`으로 조회.
2. RAG 프롬프트(시스템 + 유저)는 `rag.py:573-590`에 코드 상수로 하드코딩되어 registry를 우회 (`docs/agent-capability-audit/02_agent_implementation.md:§4`, `docs/agent-capability-audit/03_rag_pipeline.md:§5`).

이 2중 채널은 다음을 막았다:

- 프롬프트 변경에 코드 변경(파일 수정 + redeploy)이 필요 — A/B 비교 불가.
- 어떤 프롬프트 버전이 운영 중인지 단일 view 불가.
- 새 프롬프트 추가가 "코드 상수냐 registry냐" 양자택일 — 컨벤션 미정착.

---

## 결정

**모든 LLM 프롬프트는 `prompt_registry.PromptRegistry` 단일 진입점으로 관리한다.**

- 부팅 시 `_register_default_prompts(registry)`가 모든 프롬프트 v1.0을 등록 (`prompt_registry.py:130-189`).
- 호출부는 `get_registry().get(name, version)` 또는 `get(name).template.format(...)`을 사용. 코드 상수 직접 참조 금지.
- 새 버전 등록은 동일 `name` + 새 `version` 문자열로 추가. 환경변수 `PROMPT_VERSION_<NAME>`로 런타임 선택 (현재는 v1.0만 존재).
- 폴백 금지: registry 초기화 실패 시 LLM 호출은 즉시 실패해야 한다 (early-fail). 폴백 프롬프트로 silent degrade하지 않는다.

---

## 본질 — 프롬프트를 코드 상수가 아닌 자산으로

H-4는 단순 코드 정리(`rag.py` 18줄 → 4줄)가 아니다. **프롬프트를 코드와 분리된 운영 자산(asset)으로 다룬다는 선언**이다. 자산이라는 것은:

- **버전이 있고** — v1.0 → v1.1 이력 추적 (`prompt_registry.py` `PromptTemplate.version` 필드).
- **등록·조회의 단일 진입점이 있고** — `registry.get(name, version)` 한 함수.
- **코드 변경 없이 교체 가능하며** — 환경변수·DB 백엔드로 확장 가능 (현재 작업 범위 외).
- **A/B·롤백 정책의 단위가 됨** — Phase 4 L-4 카드의 단위.

이 정책은 RAG 프롬프트뿐 아니라 **향후 모든 LLM 자산**에 동일하게 적용한다. 도메인 프롬프트, 시스템 프롬프트, JSON 스키마, few-shot 예시, eval 데이터셋(`docs/agent-capability-audit/05_evaluation_testing.md:§2` 라인 62 — 6쿼리 in-code → 외부 `.jsonl` 이전이 향후 과제) 모두 포함. **새 LLM 자산을 코드 상수로 추가하면 본 ADR 위반.**

H-6 도입 후 JSON 스키마는 `app/schemas/llm_output.py`의 Pydantic 모델로 코드 표현하되, registry에는 `model_json_schema()` 결과를 등록해 자산 단일 view를 유지한다 — 모델 정의와 registry template의 동기화는 `tests/test_prompt_registry.py::TestSchemaTemplateSync`가 자동 검증한다.

---

## { } escape 정책

Jinja2 템플릿(`{{ var }}`)과 JSON 스키마(`{"key": ...}`)가 한 프롬프트에 혼재할 때 충돌이 발생한다. Jinja2가 JSON의 단일 중괄호를 변수 시작으로 해석하기 때문이다.

규칙:

- **Jinja2 변수**: `{{ var }}` 그대로.
- **JSON 리터럴 중괄호**: `{{ "{" }}`, `{{ "}" }}`로 escape (literal 중괄호 문자열을 Jinja2 표현식으로 출력).
- **혼재 회피**: 가능하면 JSON 스키마는 별도 상수에 두고 Jinja2로 `{{ schema_json }}` 변수 주입. 한 템플릿 안에 두 문법을 직접 섞지 않는다.

근거: `prompts.py`의 4개 JSON 스키마(`PORTFOLIO_ANALYSIS_SCHEMA` 등)는 별도 상수로 정의되어 템플릿에 주입되는 구조 (02:§4).

---

## 현재 등록 7종 (prompt_registry.py:130-189)

| name | version | 용도 |
|---|---|---|
| `system_prompt` | 1.0 | Aether 포트폴리오 분석 AI 시스템 프롬프트 |
| `portfolio_analysis_schema` | 1.0 | 포트폴리오 분석 응답 JSON 스키마 |
| `risk_explanation_schema` | 1.0 | 리스크 설명 응답 JSON 스키마 |
| `backtest_summary_schema` | 1.0 | 백테스트 요약 응답 JSON 스키마 |
| `recommendation_schema` | 1.0 | 투자 추천 응답 JSON 스키마 |
| `rag_system` | 1.0 | RAG 시스템 프롬프트 (금융 지식 답변) |
| `rag_user` | 1.0 | RAG 유저 프롬프트 (context/question 치환) |

H-4 머지 전: 5종 (위 표 상위 5건). H-4 머지로 `rag_system` + `rag_user` 2종 추가, 합 7종.

---

## 영향

- 신규 LLM 호출 코드는 반드시 `get_registry().get(...)` 경유.
- 새 프롬프트 추가 절차: (1) `prompts.py`에 상수 정의, (2) `_register_default_prompts`에 `register(name, version, template, metadata)` 추가, (3) 호출부에서 registry 조회.
- RAG 답변 품질 회귀 검증: `rag_evaluator.py` 6쿼리의 `precision_at_k`, `keyword_coverage`, `source_accuracy` 메트릭이 As-Is 대비 ±0 또는 상승 (H-4 카드 §7).
- 신규 LLM 자산을 코드 상수로 추가하면 본 ADR 위반 — PR 리뷰에서 차단.
- L-4 (Phase 4) A/B·롤백 운영은 본 ADR이 정의한 단일 진입점을 단위로 한다.
