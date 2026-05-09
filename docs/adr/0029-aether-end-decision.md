# ADR 0029 — Aether 종료 결정 (시나리오 A 종료 / Houseman 진입)

- **상태**: Accepted
- **일자**: 2026-05-10
- **관련 카드**: AETHER-END (Aether 종료 결정 / 카드 누적 32 마감)
- **결정 근거**: SCENARIO.md §1.1 (시나리오 A/B/C 정의) + META_REVIEW.md §9 (Top 10 9.5/10) + AUDIT_REPORT.md §3.1 (Critical 3 정착 / Major 11 + Minor 8 보류) + PRINCIPLES.md 패턴 6 (미적용 결정 = 시그널)

---

## 컨텍스트

Phase 1 종료 (DBG-1 / DBG-2 / DEV-FE-1 / PR #49 / #50 / #51) + TG-MANUAL 정착 (PR #52) 후 시나리오 A 본질 정착 완료. 시나리오 B 진입 트리거 3 질문 (SCENARIO.md §1.1 인용):

1. **도메인 질문**: 한국 개인 투자자 진짜 문제 Top 5 — 답 X (도메인 검증 미진행)
2. **사용자 질문**: 5+ 인터뷰 — 미진행 (사용자 0명 일관성)
3. **PMF 질문**: 10불 내고 쓸 가치 — 미검증 (시연 + 면접 자료 본질)

→ **답 X** → 시나리오 A 종료 + 별도 프로젝트 분리 (Houseman 진입 / 별도 repo).

본 카드 (AETHER-END) = 시나리오 A 본질 정착 완료 영역 영역 영역 종료 결정 추적 + Houseman 진입 본질 명시.

---

## 결정 (양면 정책 / 5 분기 추적)

### 분기 1: 옵션 A (시나리오 A 종료 + Houseman 진입) vs 옵션 B (시나리오 B 진입) vs 옵션 C (시나리오 C 진입) — **A 채택**

**옵션 A (선택)** = 시나리오 A 종료 + Houseman 진입:

- 시나리오 A 본질 정착 완료 (기술 데모 + 시니어 패턴)
- 카드 누적 32 마감 (AETHER-END 머지 후)
- Houseman 진입 = 별도 repo + Phase 7-12 + Subagents + Soul.md
- Aether 본 repo 보존 (시연 + 면접 자료 정착)

**옵션 B (보류)** = 시나리오 B 진입 (소수 사용자 / PMF 영역):

- 도메인 검증 (한국 개인 투자자 진짜 문제) — 답 X / 미진행
- 5+ 인터뷰 — 미진행
- PMF 10불 — 미검증
- → 시나리오 B 진입 본질 X / 보류

**옵션 C (보류)** = 시나리오 C 진입 (SaaS 본격 운영):

- PMF 검증 + 운영 인프라 + 마케팅
- 시나리오 B 미정착 → 시나리오 C 진입 X
- → 보류

근거: 시나리오 분리 (PRINCIPLES 패턴 7 / 본질 충돌 분리) — Aether 영역 = 시나리오 A 일관성 정착. 시나리오 B+ 진입 = 별도 repo 의무 (Houseman).

### 분기 2: Phase 2 Major 11 + Phase 3 Minor 8 보류 vs 정착 — **보류 채택**

근거:

- AUDIT_REPORT.md §1 영역 22 발견 = Critical 3 (정착 완료) + Major 11 + Minor 8
- Major 11 (DEV-AUTH-1 / DEV-DRY-1 / DEV-IMPORT-1 / DEV-ERR-1 / DEV-ERR-2 / DEV-COMPLEX-1 / DEV-OBS-1 / DEV-SEC-1 / DEV-API-1 / DEV-LOG-1 / DEV-TEST-1) = 시나리오 B 진입 시점 트리거 본질 (시연 영향 X)
- Minor 8 (DEV-SEC-2 / DEV-SEC-3 / DEV-CONC-1 / DEV-PERF-1 / DEV-PERF-2 / DEV-API-2 / DEV-OBS-2 / DEV-OBS-3) = Houseman 시점 (코드 품질)
- 보류 결정 = 시그널 (PRINCIPLES 패턴 6 / 미적용 결정 = 명시 결정만큼 강한 시그널)

### 분기 3: HOUSEMAN_APPLICATION.md 작성 위치 — **Aether repo 영역 작성**

근거:

- I-1-REVIEW §6.6 약속 (PR #47) — "Aether 종료 시점 작성 예정" 표기 영역 정착 의무
- Aether repo 영역 = 진입 본질 명시 + 학습 인용 (META_REVIEW §6 / KARPATHY_MAPPING / PRINCIPLES / WORK_PATTERNS / AGENTS.md §7 / AUDIT_REPORT)
- 실제 Houseman 정착 = 별도 repo + 사용자 직접 정착 의무 (시나리오 정의 / Soul.md 본문 / Phase 7-12 카드)
- 본 자료 영역 = 진입 본질만 / 실제 정착 X (PRINCIPLES 패턴 4 / 본질 vs 비본질 일관성)

### 분기 4: Aether 본 repo 보존 vs 영역 — **보존 채택**

근거:

- 시연 + 면접 자료 정착 (TG-MANUAL §2 면접 시점 / INTERVIEW_SIMULATION.md / DIFFERENTIATION.md)
- 영역 영역 = 학습 자산 손실 위험 / 시그널 X
- Houseman = 별도 repo (시나리오 분리 / 영역 영역 영역 영역 영역 영역 영역 영역 X)

### 분기 5: README.md 갱신 (Aether 종료 명시) — **선택 (사용자 결정)**

근거:

- README.md 영역 = 영역 영역 영역 영역 영역 영역 — 사용자 결정 의무
- 본 카드 영역 영역 = 의무 X / 선택 영역
- 사용자 결정 영역 = 본 카드 영역 영역 X / 별도 영역 정착 영역

---

## 영향

### 신규

- `docs/HOUSEMAN_APPLICATION.md` — Aether → Houseman 진입 본질 (~150 LOC / 6 §)
- `docs/adr/0029-aether-end-decision.md` — 본 ADR (양면 정책 5 분기 추적)

### 갱신

- `docs/agent-capability-audit/META_REVIEW.md` — §12 Aether 종료 회고 추가 (~30 LOC / 학습 10건 정리 + Houseman 적용)
- `docs/agent-capability-audit/SCENARIO.md` — §1.1.1 Aether 종료 시점 추가 (~10 LOC / 본 ADR 인용)
- `AGENTS.md` §7 AETHER-END baseline 행 추가

### 회귀

- 코드 변경 0 (자료 카드 / 회귀 검증 X)
- 테스트 영향 X
- 4 서비스 + 인프라 영향 X

---

## 결과

### 긍정적

- **카드 누적 32 마감** (본질 정착 완료 / 0-1 + Top 10 + DIFF-1 + TG-1/2/2b/2c/2d + I-1 + I-1-REVIEW + AUDIT-1 + DBG-1 + DBG-2 + DEV-FE-1 + TG-MANUAL + AETHER-END)
- **Aether 학습 → Houseman 적용** (META_REVIEW §6 / 10건 인용)
- **본 repo 보존** = 시연 + 면접 자료 정착
- **Houseman 진입 = 별도 repo / 영향 분리**
- **양면 정책 19 ADR** (0011-0029) 마감

### 부정적

- Phase 2 Major 11 + Phase 3 Minor 8 = 보류 (시나리오 B 트리거)
- 단 보류 결정 = 시그널 (PRINCIPLES 패턴 6 / 미적용 결정 = 명시 결정만큼 강한 시그널)

---

## 시그널 (면접 답변)

### "왜 종료?"

> "시나리오 A 본질 (기술 데모 + 시니어 패턴) 정착 완료 — 카드 32 마감 / 양면 정책 19 ADR / Top 10 9.5/10. 시나리오 B 트리거 3 질문 (도메인 / 사용자 / PMF) 답 X → 시나리오 A 종료 + 별도 프로젝트 분리 (Houseman 진입). PRINCIPLES 패턴 4 (본질 vs 비본질) + 패턴 7 (본질 충돌 분리) 일관성."

### "Major 11 안 고치고 종료?"

> "양면 정책 — Major 11 (DEV-AUTH-1 ~ DEV-TEST-1) = 시나리오 B 진입 시점 트리거 본질 (시연 영향 X / 사용자 0명 영역 우선순위 X). 보류 결정 = 시그널 (PRINCIPLES 패턴 6 / 미적용 결정 = 명시 결정만큼 강한 시그널). AUDIT_REPORT.md §3.2 + §3.3 영역 명시 / 본 ADR 0029 영역 추적."

### "Houseman은 뭐가 다른가?"

> "Aether = AGENTS.md 정착 / Soul.md X (시나리오 A 일관성). Houseman = Soul.md 정착 (시나리오 B+ 진입 본질) — 카파시 영상 8번 본질 트리거. Aether 학습 10건 (META_REVIEW §6) 직접 적용 + 시나리오 분리 (별도 repo)."

---

## 인용 자료

- SCENARIO.md §1.1 (시나리오 A/B/C 정의 / 진입 트리거 3 질문)
- META_REVIEW.md §6 + §9 + §12 (학습 10건 + Top 10 + Aether 종료 회고)
- AUDIT_REPORT.md §3.1-§3.3 (Critical 3 정착 / Major 11 + Minor 8 보류)
- PRINCIPLES.md 패턴 4 (본질 vs 비본질) + 패턴 6 (미적용 결정 시그널) + 패턴 7 (본질 충돌 분리)
- HOUSEMAN_APPLICATION.md (Houseman 진입 본질)
- I-1-REVIEW §6.6 약속 (HOUSEMAN_APPLICATION.md 작성 정착)
- 양면 정책 일관성 — ADR 0010 / 0011 / 0014 / 0025 / 0026 / 0027 / 0028

---

## 카드 누적 영역

- ADR 0011-0029 = **양면 정책 19 ADR** (정착 11 / 보류 4 / 메타 4 / 정리 1).
- Aether 카드 누적 32 마감 (AETHER-END 머지 후) — 시나리오 A 본질 정착 완료.
- 다음 진입: **Houseman** (별도 repo / Phase 7-12 / Subagents + Soul.md / 사용자 직접 정착 의무).
