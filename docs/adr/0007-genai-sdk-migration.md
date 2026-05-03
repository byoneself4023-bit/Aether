# ADR 0007 — google-generativeai → google-genai SDK 마이그레이션

- **상태**: Accepted
- **일자**: 2026-05-03
- **관련 작업**: H-6 디벨롭 (구조화 출력 SDK 마이그레이션, H-6b 후속 카드 흡수)
- **선행 ADR**: 0005 (LangGraph 채택), 0006 (ReAct 패턴)

---

## 컨텍스트

H-6 (f57d459) 머지 시점의 `llm-service/requirements.txt`에는 두 Gemini 관련 의존성이 공존했다.

```text
google-generativeai==0.8.6     # legacy SDK (deprecated, FutureWarning 노출)
langchain-google-genai>=2.0    # T-1b ReAct 의존
```

운영·테스트에서 `FutureWarning: The 'google.generativeai' module is deprecated...`가 노출되고, legacy SDK는 신규 기능 (Gemini 2.x async 패턴 등) 추적이 끊긴 상태. 동시에 `langchain-google-genai 4.2.2`의 Requires-Dist는 다음과 같다:

```text
google-genai<2.0.0,>=1.65.0
```

즉, **신규 SDK `google-genai`는 langchain-google-genai의 전이의존으로 이미 설치되어 있고**, legacy SDK 호출 2 파일 (`llm_provider.py`, `rag.py`) 만 교체하면 의존성 그래프 단일화 + FutureWarning 제거가 동시에 끝난다.

기존에 Gemini 채택 자체를 다룬 ADR은 없었다 (ADR 0003은 prompt-registry-policy). 본 ADR이 SDK 선택의 첫 공식 기록을 겸한다.

---

## 결정

**legacy `google-generativeai` 의존성을 제거하고, 모든 Gemini 호출을 `google-genai` (Client API) 로 이전한다.**

- `requirements.txt` 라인 4 `google-generativeai==0.8.6` 삭제
- `llm_provider.py`: `genai.configure + GenerativeModel` → `genai.Client + client.models.generate_content`
- `rag.py`: `genai.embed_content` → `client.models.embed_content` + `result.embeddings[0].values` 어댑터
- Pydantic `response_schema` 13종 + `response.text` / `response.usage_metadata` 속성 그대로 유지 → 호출자 (`call_llm_structured` 사용처, frontend) 회귀 0
- `tests/test_llm_provider.py` 5건 — 패치 타겟을 `genai.GenerativeModel` → `_ensure_client` (Client 반환)으로 갱신

---

## 대안 비교

| 옵션 | 장점 | 단점 | 결정 |
|---|---|---|---|
| **google-genai로 마이그레이션 (본 결정)** | FutureWarning 0 / 의존성 그래프 단일화 / 신규 기능 (async, batch) 진입로 / langchain-google-genai와 같은 SDK 공유 | SDK API 학습 / 테스트 mock 갱신 (5건) | **채택** |
| legacy 유지 + suppressed warning | 코드 변경 0 | deprecated 부채 누적 / langchain-google-genai 메이저 갱신 시 충돌 위험 | 미채택 |
| 두 SDK 병행 (점진 이전) | 롤백 면적 최소 | 의존성 중복 / 테스트 매트릭스 2배 / 1책임 위반 (H-6 본질 흐려짐) | 미채택 |

---

## 응답 호환 전략

### Gemini structured output

```python
# Before
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
genai.configure(api_key=...)
model = genai.GenerativeModel(
    model_name=...,
    generation_config=GenerationConfig(
        response_mime_type="application/json",
        response_schema=response_model,
    ),
)
response = model.generate_content(prompt, request_options={"timeout": ...})

# After
from google import genai
from google.genai import types
client = genai.Client(api_key=..., http_options=types.HttpOptions(timeout=ms))
response = client.models.generate_content(
    model=settings.llm_model,
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=response_model,
    ),
)
```

`response.text` / `response.usage_metadata.prompt_token_count` 속성 동일 → `model_validate_json` 로직 그대로.

### Embedding (`rag.py`)

```python
# Before
result = genai.embed_content(model=..., content=text, task_type="...")
return result["embedding"]

# After
result = client.models.embed_content(
    model=settings.embedding_model,
    contents=text,
    config=types.EmbedContentConfig(task_type="..."),
)
return list(result.embeddings[0].values)
```

응답 어댑터 한 줄. `GeminiEmbeddingFunction.__call__` 등 호출자 변경 0.

---

## 가드 1 (측정 기반 결정 시스템) 첫 적용

본 작업은 5 가드 시스템 첫 실전 카드다. 가드 1 트리거 자동 결정:

1. **사전 측정 4건**: import 위치 / response_schema 사용 / 신규 SDK API / langchain-google-genai 의존성
2. **트리거 조건**: 측정 4에서 langchain-google-genai가 legacy SDK를 요구하면 → 보류 (ADR만 박음, 코드 0)
3. **실측**: `Requires-Dist: google-genai<2.0.0,>=1.65.0` — legacy 의존 0
4. **자동 결정**: 진행 가능
5. **시간 cap**: 2시간 내 완료, 회귀 270 통과

가드 1은 단순 시간 cap이 아니라 *측정 결과에 따른 자동 분기*가 본질이다. 본 카드에서 "디벨롭 진행" / "ADR 보류" 두 분기를 plan에 박아두고, 측정 4 결과로 분기 선택을 자동화했다.

---

## 영향

- **FutureWarning 제거**: `pytest tests/ 2>&1 | grep -i "futurewarning\|google.generativeai"` 0 hits
- **의존성 정리**: `pip list | grep google-generativeai` 부재 (전이의존 X)
- **Pydantic 13종 보존**: `app/schemas/llm_output.py` 변경 0
- **T-1a/T-1b 인프라 무관**: `app/agents/`, `app/routers/chat.py` 변경 0 (langchain-google-genai 경유라 SDK 마이그레이션 영향 X)
- **회귀 0**: 270 passed, coverage 87% (≥81%)
- **H-6b 후속 카드 흡수**: FutureWarning 정리가 본 카드의 부산물

---

## YAGNI — 본 카드에서 미도입

- async 호출 (`client.aio.models.generate_content`) — 동기 호출 그대로 유지, T-3 Multi-Agent 진입 시 검토
- batch embedding (`contents=[...]` list) — `GeminiEmbeddingFunction.__call__`이 단일 호출 루프, 회귀 0 우선
- Gemini 2.x thinking_config, image_config — 본 케이스 무관
- HttpOptions retry_options — tenacity 데코레이터로 충분

신규 도구·기능 추가 시 위 항목들이 자연스럽게 들어올 자리가 마련되어 있다 (`GenerateContentConfig` / `EmbedContentConfig` 모두 확장 가능).
