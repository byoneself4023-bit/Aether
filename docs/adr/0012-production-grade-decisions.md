# ADR 0012 — 운영급 결정 정착 (D-2)

- **상태**: Accepted
- **일자**: 2026-05-06
- **관련 카드**: D-2 (`docs/agent-capability-audit/META_REVIEW.md` §1.4 백엔드 학습 정착)
- **결정 근거**: META_REVIEW §1.4 + PRINCIPLES 패턴 6 (보류 결정 명시) + ADR 0011 형식 적용

---

## 컨텍스트

시나리오 A는 기술 데모 / 면접용 (사용자 0명). 그러나 운영급 결정을 시나리오 A 단계에서 정착하면 시니어 시그널이 강화된다 — 데모 본질을 깨지 않으면서 실서비스 운영 본능을 입증.

D-1 ADR 0011은 본질 X 기능을 보류했지만, 본 ADR 0012는 **본질 O 운영 결정** 3 영역을 정착한다:

1. cache eviction 정책 (FIFO → LRU)
2. CORS 정책 (와일드카드 → 명시 리스트)
3. API 키 검증 시점 (lifespan + config validator 이중 안전장치)

**미적용 영역**도 동시에 명시하여 PRINCIPLES 패턴 6 ("미적용 결정 = 명시한 결정만큼 강한 시그널") 정착.

---

## 결정

### 1. cache LRU 전환 + CACHE_MAXSIZE 환경변수

| 영역 | Before | After |
|---|---|---|
| 자료구조 | `dict` + `min(key=created_at)` (O(n) eviction) | `OrderedDict` + `popitem(last=False)` (O(1) eviction) |
| eviction 정책 | FIFO (생성 시점 기준) | **LRU** (최근 접근 시점 기준) |
| 크기 한계 | `max_size=1000` 하드코딩 | `CACHE_MAXSIZE` 환경변수 (default 1000) |
| `get()` hit 동작 | 변경 X | `move_to_end()`로 끝으로 이동 |

위치: `portfolio-service/app/services/cache.py`. 환경변수 sync: `docker-compose.yml` + `.env.example` + `app/config.py`.

### 2. CORS allow_methods / allow_headers 명시

| 영역 | Before | After |
|---|---|---|
| `allow_methods` | `["*"]` | `["GET", "POST", "OPTIONS"]` |
| `allow_headers` | `["*"]` | `["Authorization", "Content-Type", "X-Request-ID"]` |

위치: `portfolio-service/app/main.py` + `llm-service/app/main.py`.

frontend 사용 메서드 검증 (D-2 Phase 1 실측): GET 2건 + POST 6건 = 8건. PUT/DELETE 0건. X-Request-ID는 ADR 0004 forward 의무 (헤더 리스트 보존).

### 3. llm config Pydantic field validator (이중 안전장치)

`llm-service/app/main.py:27-32` lifespan은 startup 시점 RuntimeError로 fail-fast 정착됨 (기존 적용 확인). 본 카드는 추가로 `app/config.py`에 `google_api_key` Pydantic field validator 적용 — Settings(BaseSettings) 인스턴스화 시점에서도 빈 문자열 거부.

```python
@field_validator("google_api_key")
@classmethod
def google_api_key_must_be_present(cls, v: str) -> str:
    if not v or not v.strip():
        raise ValueError(...)
    return v
```

**이중 검증 의도**: lifespan은 uvicorn startup 시점, validator는 Settings 인스턴스화 시점. settings를 lifespan 외에서 import하는 케이스 (예: 단위 테스트 / CLI / 스크립트) 보호.

---

## 영향

### 시그널 강화 (+)

- 운영급 결정 (LRU O(1) / 명시 CORS / 이중 fail-fast) 정착으로 시니어 본능 입증
- ADR 0011 + 0012 = 보류 결정 + 정착 결정 양면 정책 패턴 도입

### Reversibility (Type 2)

- `CACHE_MAXSIZE=0` 또는 환경변수 토글로 즉시 롤백 (WORK_PATTERNS 패턴 4)
- CORS 변경: `allow_methods=["*"]` 1줄 복원
- validator: `@field_validator` 데코레이터 1 함수 제거

### 응답 시간 변동 X

- LRU eviction = O(1) (기존 FIFO + min() = O(n)에서 향상)
- CORS 명시 정책: preflight 응답 동일 (브라우저 캐싱 동작 X)

---

## 미적용 영역 (시나리오 B 진입 시 트리거)

본 카드는 시나리오 A 본질에 부합하는 결정만 정착. 다음 영역은 시나리오 B (실 사용자 발생) 또는 특정 트리거 발생 시 후속 카드로 진입:

| 영역 | 트리거 조건 | 본질 |
|---|---|---|
| Rate Limit 분산화 | 다중 인스턴스 배포 시점 | Redis-backed 토큰 버킷 (현재 in-memory 한정) |
| `.env.prod` 분리 | 실 배포 환경 발생 시점 | dev/staging/prod 환경별 설정 분리 |
| 시크릿 관리 (Vault / AWS Secrets Manager) | 시크릿 회전 정책 필요 시점 | 환경변수 평문 → Vault 동적 주입 |
| 서비스 메쉬 / OpenTelemetry | 분산 trace 시스템 도입 시점 | X-Request-ID → W3C traceparent 표준 (ADR 0004 §L-7b 후속) |
| RS256 + JWKS | 비밀키 회전 또는 보안 강도 격상 시점 | HS512 → 비대칭 RS256 (ADR 0004 §H-10b 후속) |
| 다중 인스턴스 cache 공유 | Redis 도입 + scale-out 시점 | InMemoryCache → RedisCache 전환 (이미 backend 어댑터 도입됨) |

---

## 후속 카드

| 카드 | 트리거 | 본질 |
|---|---|---|
| **F-N (운영 강화)** | 시나리오 B 진입 | Rate Limit 분산화 / .env.prod / Vault |
| **L-7b** | 분산 trace 시스템 도입 | OpenTelemetry / W3C traceparent |
| **H-10b** | 비대칭 키 보안 격상 | RS256 + JWKS |

---

## 갱신 이력

| 일자 | 버전 | 변경 |
|---|---|---|
| 2026-05-06 | v1 | 초기 Accepted (D-2 산출). 결정 3건 + 미적용 영역 6건 + 트리거 명시. ADR 0011 형식 적용. |
