# Aether 작업 패턴 가이드 — 발생 문제 + 사전 예방 + 자기 일관성 (Claude Code 필독)

## 본 문서의 본질

> **"같은 실수 반복하지 않는 것 = 시니어의 본질."**
>
> Aether 프로젝트에서 실제 발생한 문제 + 디버깅 비용 + 사전 예방 패턴을 누적 정리.
> Claude Code가 매 카드 plan 시 본 문서 먼저 읽어 같은 실수 반복 차단.

**위치**: `docs/agent-capability-audit/WORK_PATTERNS.md`
**참조 시점**: 매 작업 plan 단계 + 의심 발생 시 즉시
**최종 갱신**: 2026-05-03 (T-2 진입 직전)

---

## 🎯 본 문서 적용 순서 (Claude Code — 매 카드 plan 시작 시)

```
[Step 1] 체크리스트 A-F 적용 (작업 트리 / prompt / 라이브러리 / 5 가드 / 커밋 / 머지)
   ↓
[Step 2] §누적 문제 16건 중 본 카드와 유사 패턴 검색
   ↓
[Step 3] §자기 일관성 패턴 5종 적용 검토
   ↓
[Step 4] §메모리 통합 가이드 (#21/#22/#23 + 본 문서) 적용
   ↓
[Step 5] plan에 "본 문서 적용 결과" 섹션 명시
```

---

## 📋 누적 문제 18건 (2026-04-28 ~ 2026-05-05)

### 카테고리 A — 작업 트리 위생 (3건)

#### 문제 1: `config.py` pre-existing 변경 혼재로 staging 부담 누적

**발생 카드**: H-10 (PR #2 최초), T-1b (PR #4), H-6 디벨롭 (PR #6) — 3회 반복

**증상**:
- 카드 작업 중 `config.py` 변경 시 pre-existing `llm_max_tokens` (2048→4096) hunk와 혼재
- `git add config.py` 시 둘 다 staged
- 커밋에 의도하지 않은 변경 포함 위험

**디버깅 비용**: 매 PR 5-10분 추가 (patch 분리 작업)

**사전 예방**:
1. **사전 측정 의무**: 카드 시작 시 `git status -s | grep config.py` 확인
2. **혼재 발견 시 patch 분리**:
   ```bash
   # 본 카드 변경만 patch로 분리 staging
   cat > /tmp/this_card_only.patch << 'EOF'
   --- a/llm-service/app/config.py
   +++ b/llm-service/app/config.py
   @@ -X,Y +X,Y @@ class Settings(BaseSettings):
   ... (이번 카드 변경만)
   EOF
   git apply --cached --check /tmp/this_card_only.patch
   git apply --cached /tmp/this_card_only.patch
   ```
3. **머지 전 검증**: `git diff --cached llm-service/app/config.py`로 의도된 변경만 staged 확인
4. **Top 10 종료 후 영구 해결 후보**: H-1d (`llm_max_tokens` commit 또는 revert)

#### 문제 2: 작업 트리 변경이 머지 cleanup 방해

**발생 카드**: T-1b (PR #4) — `gh pr merge --delete-branch` 후 `git checkout main` 실패

**증상**:
```
error: Your local changes to the following files would be overwritten by checkout:
   llm-service/app/config.py
Please commit your changes or stash them before you switch branches.
```

**원인**: pre-existing 변경이 main의 새 커밋과 같은 영역 → checkout 충돌

**사전 예방**:
1. 머지 직전 `git status` 확인
2. 충돌 가능 변경 있으면 stash 먼저:
   ```bash
   git stash push -m "pre-existing files for PR cleanup" -- llm-service/app/config.py
   gh pr merge N --squash --delete-branch
   git checkout main && git pull
   git stash pop
   ```
3. **WORK_PATTERNS 패턴 정착**: 모든 PR 머지 시 본 절차 자동 적용

#### 문제 14: `gh pr create` "Warning: N uncommitted changes" 경고 (전반)

**발생 카드**: PR #2 ~ PR #6 모두 (의도된 동작)

**증상**:
```
Warning: 10 uncommitted changes
https://github.com/.../pull/N
```

**원인**: pre-existing 7 modified + 3 untracked 보존이 의도. PR 미포함은 정상.

**사전 예방**:
1. PR 본문에 "**경고는 의도된 보존**" 한 줄 명시
2. 패닉 X — 매 PR마다 발생하는 정상 동작
3. PR 본문 템플릿에 다음 섹션 박음:
   ```markdown
   ## Pre-existing 변경 보존
   본 PR은 작업 트리의 N개 pre-existing 변경을 의도적으로 미포함. 
   gh pr create 'Warning: N uncommitted changes'는 정상 동작.
   ```

---

### 카테고리 B — PR 머지 cleanup (2건)

#### 문제 3: `Co-Authored-By: Claude` 커밋 트레일러 차단

**발생 카드**: H-1c (PR #5)

**증상**:
- Claude Code가 커밋 메시지 끝에 `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` 자동 박음
- 시스템 정책으로 차단 → 첫 commit 실패
- 재시도 시 해당 라인 제거 후 정상 커밋

**원인**: Authorship 위조 방지 정책 — 도구가 공동 작성자처럼 표시되는 것 차단

**사전 예방**:
1. **모든 카드**: 커밋 메시지에 `Co-Authored-By` 트레일러 박지 않음
2. 기본 템플릿에 박혀있으면 commit 명령에서 명시적으로 제거
3. 정책 회피 시도 X — 즉시 재시도

#### 문제 15 (신규): `gh pr merge --delete-branch` 동작 불일치

**발생 카드**: PR #2 (자동 정리), PR #4 (부분 실패), PR #6 (자동 정리 + 추가 prune 필요)

**증상**: `gh pr merge` 동작이 작업 트리 상태에 따라 다름
- 작업 트리 깨끗 → 로컬 + 원격 모두 자동 삭제
- 충돌 가능 변경 있음 → local cleanup 실패 → remote 삭제도 실패

**사전 예방**:
1. 머지 직전 `git status` 확인 (문제 2와 같은 패턴)
2. 머지 후 항상 다음 추가 실행:
   ```bash
   git fetch --prune origin
   git branch -d feat/<branch> 2>/dev/null  # 무해
   ```
3. 원격 ref stale 방지 — `git fetch --prune` 의무

---

### 카테고리 C — 사용자 prompt 검증 / 사전 측정 (4건)

#### 문제 4: 사용자 prompt 응답 키 명칭 부정확

**발생 카드**: T-1b (PR #4)

**증상**:
- 사용자 prompt: `backtest_summary`, `recommendations` (복수)
- 실제 `schemas/chat.py:106-113`: `backtest_analysis`, `recommendation` (단수)
- 측정 안 했으면 응답 형식 깨짐

**사전 예방** (실측 의무):
```bash
# 응답 schema 다루는 카드는 의무
grep -A20 "class .*Response" llm-service/app/schemas/

# Pydantic 필드명 정확 확인
python -c "from app.schemas.chat import AnalysisResponse; print(AnalysisResponse.model_fields.keys())"
```

#### 문제 5: 사용자 prompt ADR 번호 부정확

**발생 카드**: H-6 디벨롭 (PR #6)

**증상**:
- 사용자 prompt: `ADR 0003-gemini-adoption.md` 갱신 명시
- 실제: ADR 0003은 `prompt-registry-policy`. Gemini 채택 ADR 자체가 부재
- 신규 ADR 0007로 박는 게 정답

**사전 예방** (실측 의무):
```bash
# ADR 목록 실측
ls docs/adr/

# 최대 번호 확인 → 신규는 max + 1
ls docs/adr/ | grep -oE '^[0-9]{4}' | sort -rn | head -1
```

#### 문제 6: 사용자 prompt 변경 대상 누락

**발생 카드**: H-6 디벨롭 (PR #6)

**증상**:
- 사용자 prompt: `llm_provider.py`만 변경 대상
- 실제: `rag.py`도 google-generativeai 사용 (embed_content 2 호출)
- 누락 안 잡으면 RAG 시스템 부분 깨짐

**사전 예방** (실측 의무):
```bash
# 호출 위치 grep — 모든 사용처 의무 확인
grep -rn "import {target_lib}\|from {target_lib}" llm-service/app/ --include="*.py"

# 변경 대상 추가 발견 시 plan에 명시
```

#### 문제 7: ToolMessage.content 직렬화 형식 가정 오류

**발생 카드**: T-1b (PR #4)

**증상**:
- 사용자 prompt: `ToolMessage.content`를 string만 가정
- 실제: LangGraph가 content를 JSON string OR dict 둘 다 가능
- 가정대로 했으면 dict 케이스에서 깨짐

**사전 예방** (외부 라이브러리 응답은 try/except + 분기):
```python
if isinstance(content, str):
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data = {"summary": content}
else:
    data = content
```

---

### 카테고리 D — 외부 SDK 마이그레이션 (4건)

#### 문제 11 (신규): FutureWarning 무시 패턴

**발생 카드**: H-6 (PR #1) → H-6b 후속 카드 발생 → H-6 디벨롭 (PR #6)에서 흡수

**증상**:
- google.generativeai FutureWarning이 H-6 머지 후 노출
- "동작 영향 0"으로 무시 → 후속 카드 H-6b 발생
- 결국 H-6 디벨롭에서 google-genai 마이그레이션으로 처리

**사전 예방**:
1. PR 머지 직전 의무 검증:
   ```bash
   pytest tests/ 2>&1 | grep -i "futurewarning\|deprecation" | head -5
   ```
2. 발견 시 결정:
   - 동일 PR에 처리 (작은 변경) → 권장
   - 후속 카드 명시 (큰 마이그레이션) → ADR에 트리거 박음
3. **'경고 무시 = 후속 카드 누적' 패턴 인지**

#### 문제 12 (신규): 외부 SDK 단위 변환 가정 오류

**발생 카드**: H-6 디벨롭 (timeout sec → ms)

**증상**:
- legacy: `request_options={"timeout": 30}` (초)
- 신규: `http_options(timeout=30000)` (ms)
- 단위 변경 가정 검증 안 했으면 timeout 1000배 늘어남

**사전 예방**:
1. 외부 SDK 마이그레이션 시 **인자 단위 변경** 체크리스트 의무:
   - timeout / duration / size / interval / latency
2. 신규 SDK 시그니처 직접 inspect:
   ```bash
   python -c "from {pkg} import {Class}; help({Class}.__init__)"
   ```
3. 단위 변환 명시 코드:
   ```python
   timeout=int(self._settings.llm_timeout * 1000)  # sec → ms
   ```

#### 문제 13 (신규): 응답 구조 변경 어댑터 미적용

**발생 카드**: H-6 디벨롭 (embed_content 응답)

**증상**:
- legacy: `result['embedding']` (dict)
- 신규: `result.embeddings[0].values` (object)
- 어댑터 한 줄로 흡수 가능하지만 가정 검증 안 했으면 RAG 깨짐

**사전 예방**:
1. **마이그레이션 직전 직접 호출 실측 의무**:
   ```python
   # PoC 단계에서 실제 응답 구조 확인
   python -c "
   from {new_sdk} import client
   c = client.Client(api_key='...')
   r = c.models.embed_content(...)
   print(type(r), dir(r))
   "
   ```
2. **응답 어댑터 한 줄 패턴**:
   ```python
   # legacy 호출자 0 변경 보장
   return list(result.embeddings[0].values)  # 신규 → list[float] (호출자 시그니처 보존)
   ```

#### 문제 18 (신규): 신규 패키지 설치 시 의존성 베이스라인 강제 업그레이드 미예측

**발생 카드**: T-2 본격 PR (Blocked, ADR 0008)

**증상**:
- `pip install 'mcp>=1.0,<2.0'` 시도 → mcp 1.27.0이 anyio `>=4.5` / starlette `>=0.49.1` (sse-starlette 경유) 강제 → portfolio-service의 fastapi 0.104.1과 충돌
- 설치 후 `from app.main import app` → `TypeError: Router.__init__() got an unexpected keyword argument 'on_startup'` (starlette 1.0.0 비호환)
- plan 단계에서 "Pydantic 2.5.3 호환 OK = 충돌 위험 LOW" 판정 → **anyio/starlette 차원을 측정 누락**
- 결과: 본격 PR 보류, 선행 카드 (fastapi 업그레이드) 분리 의무

**사전 예방**:
1. 신규 패키지 추가 전 **`pip install --dry-run` 의무**:
   ```bash
   .venv/bin/pip install --dry-run '<new-pkg>' 2>&1 | grep -E "Would install|Would upgrade"
   ```
2. 강제 업그레이드 후보 패키지 vs 베이스라인 핵심 의존성 매트릭스 작성:
   - **검사 대상**: anyio, starlette, httpx, pyjwt, pydantic, uvicorn, sqlalchemy, fastapi (서비스별 핵심 4-6개)
   - 한 줄이라도 충돌 → 차단
3. 충돌 발견 시 분기:
   - 베이스라인 업그레이드 가능 (별도 카드) → **선행 카드** 분리, ADR Blocked
   - 신규 패키지 버전 다운그레이드 가능 → 호환 버전 핀
   - 둘 다 불가 → 본격 PR 폐기, 다른 패키지 검토
4. **plan의 "충돌 위험 LOW" 판정은 다차원 매트릭스 후에만**:
   ```
   plan 작성 시:
   - pydantic ✓
   - anyio ?  ← 이 줄 누락 시 차단
   - starlette ? ← 이 줄 누락 시 차단
   - httpx ?
   ```
5. 가드 G2 (Reversibility) 보호: 베이스라인 업그레이드는 반드시 별도 카드. 신규 도구 PR 안에 베이스라인 업그레이드 끼워넣지 말 것.

---

### 카테고리 E — 문서 / ADR 관리 (3건)

#### 문제 8: 측정 추정값 vs 실측 차이

**발생 카드**: T-1a + H-2 (PR #3)

**증상**:
- plan: "11 단위 테스트" 추정
- 실측: 10 (autouse fixture는 카운트 X)
- 영향 0이지만 자기 점검에서 카운트 차이

**사전 예방**:
1. **테스트 카운트 추정 X** — 작성 후 실제 측정:
   ```bash
   pytest tests/ --co -q | wc -l
   ```
2. 자기 점검 항목은 정성 표현 ("신규 테스트 통과")
3. 정확 카운트는 PR 본문에 실측값만

#### 문제 10 (신규): AGENTS.md §7 지배 숫자 표 중복 행

**발생 카드**: H-1c (PR #5) — 정리 카드 자체

**증상**:
- T-1a/T-1b 갱신 시 옛 행 (등록 프롬프트 수 7) + 새 행 (등록 프롬프트 수 8) 동시 존재
- "추가만" 패턴 → 누적 중복

**사전 예방**:
1. 지배 숫자 표 갱신 시 **"옛 행 삭제 + 새 행 추가" 의무**
2. grep으로 사전 확인:
   ```bash
   grep "등록 프롬프트 수\|테스트 합산" AGENTS.md
   ```
3. 갱신 후 검증: 같은 항목의 행이 1개만 존재

#### 문제 16 (신규): ADR 번호 관리 패턴

**발생 카드**: H-1 (0001-0003 일괄), H-10 (0004), T-1a (0005), T-1b (0006), H-6 디벨롭 (0007)

**증상**:
- ADR 번호 부여 기준 불명확
- 사용자 prompt에 잘못된 번호 (문제 5와 연결)

**사전 예방**:
```bash
# 신규 ADR 작성 전 의무
NEXT=$(($(ls docs/adr/ | grep -oE '^[0-9]{4}' | sort -rn | head -1) + 1))
printf "다음 ADR 번호: %04d\n" $NEXT

# 신규 ADR 파일명: docs/adr/{번호}-{slug}.md
```

---

### 카테고리 F — 의사결정 / 메타 (1건)

#### 문제 9: 의사결정 무한 루프

**발생 카드**: T-2 진입 직전 (메타 결정)

**증상**:
- "디벨롭 vs 직진" 결정에 7 라운드 분석
- 매 라운드마다 결정 변경 (B+D → A → C++ → 3+ADR → T-2 직진)
- 6 패턴 적용했지만 도구가 결정 자체를 대체 = 결정 마비

**디버깅 비용**: 7 라운드 = 약 3-4시간 분석 시간

**사전 예방** (메모리 #22 박힘):
1. **5 가드 강제 적용** — Decision Budget / Reversibility / Done Definition / Round Cap / First Principle
2. **Type 2 결정 (가역)** — 70% 정보로 결정 + 빠른 회고
3. **메타 사고 max 3 라운드** — 메타-메타-메타 이상 금지
4. **충분 기준 사전 명시** — "80/100점이면 결정 종결"
5. **"분석 X, 액션" 모드 강제 트리거** — 라운드 cap 초과 시 자동 전환

---

### 카테고리 G — 후속 카드 누적 (1건, 메타 패턴)

#### 문제 17 (신규): 후속 카드 누적 패턴

**발생 카드**: H-1c, H-6b, H-7b/c/d, H-10b — 후속 카드 5건 발생

**증상**:
- 본 카드에서 모든 디테일 처리 안 함 → 잔여 작업 누적
- 5건이 main에 잔재 (H-1c·H-6b는 흡수, H-7b/c/d·H-10b는 잔재)

**사전 예방**:
1. 본 카드 plan에 **"후속 카드 후보" 섹션** 명시
2. 발견 시 결정 트리:
   ```
   본 카드와 같은 영역 + 5분 이내 처리 가능
       → 즉시 흡수 (예: H-1c)
   본 카드와 다른 영역 + 별도 분석 필요
       → 후속 카드 (예: H-7b/c/d)
   '동작 영향 0' 경고만
       → 보너스 카드 (Top 10 종료 후, 예: H-10b)
   ```
3. 후속 카드 발생 시 ADR에 "트리거 명시":
   ```markdown
   ## 후속 카드 트리거
   - {조건} 발생 시 H-Xb 카드 진입
   - 트리거 안 되면 영구 보류 OK
   ```

---

## 🛡️ 종합 사전 예방 체크리스트 (매 카드 plan 시 필수)

### A. 작업 트리 위생 (문제 1·2·14 차단)

- [ ] `git status -s` — pre-existing 변경 인지
- [ ] `config.py` 등 충돌 가능 파일 grep
- [ ] 본 카드 변경 영역 vs pre-existing 영역 분리 확인
- [ ] PR 본문에 "pre-existing 보존 의도" 명시

### B. 사용자 prompt 검증 — **실측 의무** (문제 4·5·6 차단)

```bash
# 응답 schema 키 정확 확인
grep -A20 "class .*Response" llm-service/app/schemas/

# ADR 번호 실측
ls docs/adr/

# 변경 대상 호출 위치 grep
grep -rn "import {target}\|from {target}" llm-service/app/ --include="*.py"
```

- [ ] 사용자 prompt와 실측 결과 차이 = plan에 "보정 사항" 섹션
- [ ] 가정 X — 모든 사실은 grep / pytest / inspect로 검증

### C. 외부 라이브러리 호환 (문제 7·11·12·13 차단)

```bash
# SDK 버전 + 의존성
pip show {pkg}

# API 시그니처 inspect
python -c "from {pkg} import {Class}; help({Class}.__init__)"

# 응답 구조 직접 호출로 실측
python -c "from {pkg} import client; r = client.call(...); print(type(r), dir(r))"
```

- [ ] SDK 버전 + 의존성 그래프 확인
- [ ] 단위 변환 (timeout / duration / size) 명시
- [ ] 응답 구조 가정 X — 실제 객체 inspect
- [ ] FutureWarning / DeprecationWarning grep:
  ```bash
  pytest tests/ 2>&1 | grep -i "futurewarning\|deprecation" | head -5
  ```
- [ ] **신규 패키지 추가 전 베이스라인 강제 업그레이드 매트릭스** (문제 18 차단):
  ```bash
  .venv/bin/pip install --dry-run '<new-pkg>' 2>&1 | grep -E "Would install|Would upgrade"
  ```
  핵심 의존성(anyio / starlette / httpx / pyjwt / pydantic / uvicorn / fastapi) 충돌 0건 확인. 1줄이라도 충돌 → 선행 카드 분리 의무.

### D. 5 가드 강제 (메모리 #22 — 문제 9 차단)

- [ ] **Decision Budget**: 라운드 max + 시간 cap 사전 명시
- [ ] **Reversibility Test**: Type 1(비가역) vs Type 2(가역) 분류
- [ ] **Done Definition**: "80/100점이면 결정 종결" 1줄
- [ ] **Round Cap**: 메타 사고 max 3
- [ ] **First Principle**: 본질 1줄, 30분마다 자가 점검

### E. 커밋 위생 (문제 3·14 차단)

- [ ] `Co-Authored-By: Claude` 트레일러 제거
- [ ] 단일 squash commit 원칙
- [ ] 커밋 메시지 형식: `feat(scope): 카드명 한 줄`
- [ ] PR 본문 템플릿:
  ```markdown
  ## Summary
  ## PR 게이트 결과
  ## 안전장치
  ## Pre-existing 변경 보존 (의도)
  ## 다음 카드 / 후속 카드
  ```

### F. PR 머지 후 정리 (문제 2·15 차단)

```bash
# 머지 후 의무 실행
git checkout main && git pull
git fetch --prune origin
git branch -d feat/<branch> 2>/dev/null  # 무해

# pre-existing 보존 확인
git status -s
```

- [ ] 로컬 main fast-forward 확인
- [ ] 원격 브랜치 prune
- [ ] pre-existing 7+3 그대로 보존

#### F-패턴: "검증 + 분기 + 머지 자동화" (메모리 #19 진화형)

**본질**: 머지 직전 검증(pre-existing / 회귀 / 호환성)과 머지 명령을 **사용자 한 줄 프롬프트**에 묶어 분기 자동화. Claude가 검증 결과에 따라 머지 진행 또는 사용자 보고를 분기 결정.

**메모리 #19 (머지 패턴) 진화 과정**:

| 세대 | 패턴 | 사용자 손 작업 | Claude 자율도 |
|---|---|---|---|
| #19 v1 | `PR #N squash merge로 머지해줘. ...` | 1회 (명령) | 머지 실행만 |
| **F-패턴 v2 (본 항목)** | `PR #N 머지 전 git diff <X> 결과 보고. pre-existing이면 머지, T-N 작업 박힌 거면 별도 처리.` | 1회 (검증 + 분기 + 머지) | 검증 + 판정 + 분기 + 머지 자동 |

**예시 프롬프트 (실제 사례 — T-2 PR #12 머지 직전, 2026-05-05)**:

```
PR #12 머지 전 git diff llm-service/app/config.py 결과 보고.
pre-existing인지 검증. pre-existing이면 머지 진행, T-2 작업 중 박힌 거면
별도 처리.
```

Claude 자동 분기 흐름:
1. `git diff llm-service/app/config.py` 실행 → diff 1줄 (`llm_max_tokens: 2048 → 4096`)
2. `git log -1 -- llm-service/app/config.py` → 마지막 커밋 `0040f48 (T-1b, 3일 전)`
3. **판정: pre-existing 100%** (T-2 작업 무관, 세션 초입부터 작업트리 보존)
4. **분기 A 채택 (자동)**: 머지 진행 안내. `git diff` 결과 + 판정 근거 + WORK_PATTERNS 문제 1 매칭 보고
5. 사용자 다음 한 줄(`PR #12 squash merge로 머지해줘`)로 머지 실행

**적용 시점**:

- 카드 머지 직전, 검수/검증이 필요한 모든 분기점
- `git status`에 modified 파일이 있을 때 — pre-existing 검증 의무
- 베이스라인 업그레이드 후 — 회귀 검증 분기 (215 통과 / N건 회귀)
- 외부 SDK 추가 후 — 호환성 검증 분기 (충돌 0 / N건)
- 일반화: **"이 변경 X인지 Y인지 검증하고 결과에 따라 다음 단계 자동 분기"**

**효과 / 트레이드오프**:

- **효과**: 사용자 손 작업 1회로 검증 + 판정 + 분기 + 머지 4단계 처리. 머지 직전 휴먼 게이트가 인지 부담 없이 자동화. WORK_PATTERNS 문제 1 (`config.py` pre-existing 혼재) / 문제 14 (Warning N uncommitted) 등 검증 의무를 자연스럽게 흡수.
- **트레이드오프**: Claude 자동 판정 신뢰 의존. 보수적으로는 분기 A(머지 진행) 제안 시점에 사용자가 확인 한 번 거치는 게 안전 — 분기 B(별도 처리) 시점에 머지 즉시 X.

**자기 일관성 자동화 카드 분기 보장**:

본 패턴 적용 시 사용자가 모든 머지 시점에 동일 검증 흐름을 한 줄로 요청 가능 → 검증 누락 0건 + Claude 검증 패턴 일관성 유지. 메모리 #19 베이스라인 + 본 진화형으로 완성.

### G. 문서 갱신 (문제 8·10·16·17 차단)

- [ ] 테스트 카운트 추정 X — 실측만
- [ ] AGENTS.md §7 지배 숫자 표 갱신 시 옛 행 삭제 의무
- [ ] 신규 ADR 번호: `ls docs/adr/` max + 1
- [ ] **후속 카드 발생 시 결정 트리 적용** (즉시 흡수 / 후속 카드 / 보너스)

---

## 📊 자기 일관성 패턴 — 검증된 시니어 패턴 (카드별 사례 보강)

### 패턴 1: Lazy Init Singleton (registry 패턴)

**적용 카드**:
- H-4: `prompt_registry` (7 prompts → T-1b 후 8개)
- T-1a: `tool_registry` (4 @tool)
- H-6 디벨롭: `_genai_client` (rag.py module-level)

**코드 패턴**:
```python
_instance: Type | None = None

def get_instance() -> Type:
    global _instance
    if _instance is None:
        _instance = Type()
        _register_defaults(_instance)
    return _instance
```

### 패턴 2: Autouse Test Fixture + Marker Opt-in

**적용 카드**:
- H-10: `_bypass_jwt` (JWT 검증 우회)
- T-1b: `_disable_react_agent` (절차적 호출 fallback)

**코드 패턴**:
```python
@pytest.fixture(autouse=True)
def _disable_X(request, monkeypatch):
    if request.node.get_closest_marker("X"):
        # opt-in 활성
        ...
    else:
        # 기본 비활성 (기존 테스트 호환)
        ...
```

### 패턴 3: 응답 호환 어댑터 (호출자 0 변경)

**적용 카드**:
- H-6: Pydantic 13종 (Gemini structured output)
- T-1b: ReAct 결과 → 4키 dict (frontend 회귀 0)
- H-6 디벨롭: SDK 마이그레이션 (response.text / usage_metadata 동일 속성)
- H-6 디벨롭: embed_content (`['embedding']` → `.embeddings[0].values`)

**코드 패턴**:
```python
def _adapter(new_sdk_response) -> existing_format:
    # 신규 응답 → 기존 형식 매핑
    # 호출자 시그니처 보존
    return list(new_sdk_response.embeddings[0].values)
```

### 패턴 4: 환경변수 즉시 롤백 (운영 안전망)

**적용 카드**:
- T-1b: `USE_REACT_AGENT` (절차적 호출로 즉시 복원)
- H-6 디벨롭: `GOOGLE_API_KEY` (Client 초기화 fail-fast)

**코드 패턴**:
```python
# 운영 사고 시 환경변수 토글로 즉시 복원
if settings.use_react_agent:
    # 신규 경로
else:
    # fallback 보존
```

### 패턴 5: 옵션 B 2단 분해 (회귀 위험 분리)

**적용 카드**:
- T-1: T-1a (인프라) + T-1b (동작 변경)

**원칙**:
- T-1a 안전하게 main 박힌 후 T-1b 시도
- T-1b 실패 시 T-1a 보호됨
- 회귀 위험 영역 분리

---

## 🧠 메모리 통합 가이드 (#21 + #22 + #23 + 본 문서)

본 프로젝트의 의사결정 + 작업 시스템은 4 레이어 통합 작동:

```
[Layer 1] 메모리 #21 — 6 패턴 자동 적용
   • Big Bet 결정 시 (Multi-Persona / Pre-mortem / Steelmanning / 가중치 / 시나리오 / 메타 검수)
   • 단순 결정엔 미적용

[Layer 2] 메모리 #22 — 5 가드 무한 루프 방지
   • Decision Budget / Reversibility / Done Definition / Round Cap / First Principle
   • 매 결정 시작 전 적용

[Layer 3] 메모리 #23 — 의사결정 진행 패턴
   • 옵션 N개 → 디테일 분석 + 추천 → 그대로 진행
   • Type 2 가역 결정만 (Big Bet 제외)

[Layer 4] 본 문서 — 작업 패턴 + 사전 예방
   • 누적 문제 16건 + 체크리스트 A-G
   • 자기 일관성 패턴 5종
   • 매 카드 plan 시 적용
```

### 통합 적용 시나리오

**시나리오 A — 단순 카드 진입**:
```
1. 본 문서 §체크리스트 A-G 적용
2. 메모리 #22 5 가드 사전 명시 (Done Definition 1줄)
3. plan + auto mode → PR
```

**시나리오 B — Big Bet 결정 (예: T-3 분해)**:
```
1. 메모리 #21 6 패턴 적용 (Multi-Persona ~ 메타 검수)
2. 메모리 #22 5 가드 (Round Cap 의무)
3. 본 문서 §체크리스트 적용
4. 사용자 명시 결정 후 진행
```

**시나리오 C — 옵션 비교 결정**:
```
1. 메모리 #23 — 디테일 분석 + 최적 추천 → 그대로 진행
2. 본 문서 §체크리스트 적용
3. 별도 사용자 결정 단계 X
```

---

## 🎯 본 문서 사용법 (Claude Code)

### 매 카드 plan 단계

1. **본 문서 §적용 순서 (Step 1-5) 의무 수행**
2. **plan 본문에 다음 섹션 박음**:
   ```markdown
   ## WORK_PATTERNS 적용 결과
   - 체크리스트 A-G: [통과 / 보정 발견]
   - 유사 누락 사례: [문제 N 매칭 / 없음]
   - 자기 일관성 패턴: [패턴 N 적용]
   - 메모리 #21/#22/#23 적용: [시나리오 A/B/C]
   ```

### 신규 문제 발견 시 (작업 중 또는 후)

1. **본 문서에 §누락 N으로 추가**
2. 증상 + 원인 + 디버깅 비용 + 사전 예방 명시
3. 같은 PR 또는 별도 PR (H-1c 같은 정리 카드)로 본 문서 갱신
4. PR 본문에 "WORK_PATTERNS 갱신" 한 줄

### 카드 머지 후 회고

1. 발생한 미세 점검 사항 본 문서에 반영
2. 자기 일관성 패턴 정착되면 §패턴 N으로 추가
3. 후속 카드 발생 시 §문제 17 결정 트리 적용

---

## 📈 본 문서의 채용 어필 가치

> **"체계적 문제 추적 + 예방 시스템 구축 = 시니어 시그널"**

면접에서 어필 한 줄:

> *"Aether 프로젝트에서 발생한 18건의 작업 문제를 카테고리별로 정리하고, 종합 체크리스트(A-G) + 자기 일관성 패턴 5종 + 메모리 통합 가이드(4 레이어)로 사전 예방 시스템을 구축했습니다. 새 개발자가 이 문서만 보고도 같은 실수 반복을 차단할 수 있고, Claude Code가 매 카드 plan 시 자동 참조해 학습 누적합니다."*

---

## 🔄 본 문서 갱신 이력

| 일자 | 갱신 내용 | 갱신 사유 |
|---|---|---|
| 2026-05-03 (v1) | 누적 문제 9건 + 체크리스트 A-F + 자기 일관성 5종 | 최초 작성 |
| 2026-05-03 (v2) | **누락 7건 추가 (10·11·12·13·14·15·16·17) + 카테고리 7개 분류 + 메모리 통합 가이드 + 적용 순서 명시** | 검수 결과 누락 발견 |
| 2026-05-05 (v3) | **문제 18 추가 — mcp 패키지 설치 시 anyio/starlette 강제 업그레이드가 fastapi 0.104.1 깨뜨림. 체크리스트 C에 `pip install --dry-run` 의존성 매트릭스 항목 추가** | T-2 본격 PR Blocked → 선행 카드 분리, ADR 0008 Blocked 전환 |
| 2026-05-05 (v4 / 본 문서) | **카테고리 F에 "검증 + 분기 + 머지 자동화" 패턴 추가** (메모리 #19 진화형) — 사용자 한 줄 프롬프트로 pre-existing 검증 + 자동 분기 + 머지 명령까지 묶는 흐름 박음. 실제 사례: T-2 PR #12 머지 직전 `git diff llm-service/app/config.py` 검증 분기. | T-2 머지 흐름에서 발견된 자기 일관성 패턴 정착 |

**다음 갱신 예정**: T-6 (Qdrant) / T-3 (Multi-Agent) 진행 후 신규 문제 발견 시
