# KARPATHY_LECTURE — Andrej Karpathy 인터뷰 디테일 정리

> **출처**: https://www.youtube.com/watch?v=-E9chn_gtfY
> **인터뷰어**: Sarah Guo (Conviction)
> **본문 영역**: 약 53분 / 약 4500 줄
> **정리 일자**: 2026-05-07
> **본질**: 카파시가 인터뷰에서 다룬 14 영역 핵심 내용 + 직접 인용 + 사례 정착
> **결론 한 줄**: AI Psychosis 시점에 카파시가 정착한 작업 패러다임 — 코드 줄 X / 카드 단위 위임 / 인간 = 시스템 병목 X / 에이전트 인지 자료 본문 정착.

---

## §1 AI Psychosis — 12월 패러다임 전환

### 카파시 본문

12월부터 카파시 작업 방식이 완전히 바뀜. 직접 코딩 vs 에이전트 위임 비율이 8020 → 2080 → 그 이상으로 큰 전환.

### 직접 인용

> "I don't think I've typed like a line of code probably since December basically."

> "I'm just like in this state of psychosis of trying to figure out like what's possible uh trying to push it to the limit."

### 핵심 영역

- 일반 개발자 작업 흐름이 12월 이후 완전히 다름
- 카파시 본인도 이 변화 본질 인지 X 일반인이 다수
- 한계 영역 광범위 탐색 의무 — Twitter에서 다른 사람이 새 영역 발견 시 nervous

### 사례

- Conviction 팀 = 모든 엔지니어가 코드 직접 작성 X / 마이크 + 음성 명령으로 에이전트에게 위임만
- 카파시: "처음에 미친 줄 알았는데 지금은 그게 정답인 걸 인정"

---

## §2 Skill Issue — AI 한계 X / 본인 활용 부족

### 카파시 본문

도구가 제대로 작동 X 시점에 "AI 한계네"가 아니라 "내가 활용 방법 못 찾은 것"으로 인지.

### 직접 인용

> "It's not that the capability is not there. It's that you just haven't found a way to string it together of what's available."

> "I just don't I didn't give good enough instructions in the agent MD file or whatever it may be. I don't have a nice enough memory tool that I put in there or something like that."

### 핵심 영역

- AGENTS.md 본문 부족 = 본인 활용 영역 부족 시그널
- 메모리 도구 부족 = 본인 환경 정착 부족 시그널
- 작동 X 영역 = "skill issue" 우선 인지 → 본인 진화 영역 가능

### 본인 진화 영역

- "addictive"한 이유 = 본인 스킬 ↑ 시점에 unlocks 다수 발생

---

## §3 Macro Actions — 카드 단위 위임

### 카파시 본문

Peter Steinberg 사례 — 다중 모니터 + Codex 다중 인스턴스 + 10 repos 동시 진행.

### 직접 인용

> "It's just like you can move in much larger macro actions. It's not just like here's a line of code, here's a new function. It's like here's a new functionality and delegate to agent one."

> "Another agent is doing some like research and another agent is writing code another one is coming up with a plan for some new implementation and so everything just like happens in these like macro actions over your repository."

### 핵심 영역

- 작업 단위 영역 ↑ — 코드 줄 → 함수 → 기능 → 카드 단위
- Codex 다중 인스턴스 = 20분 단위 실행 (high effort 프롬프트 시점)
- 본인 = 카드 분배 + 결과 검수 영역
- "muscle memory" 정착 의무 — 본인 작업 흐름 자체 진화

### 사례

- Peter Steinberg: 모니터 여러 대 / Codex 다중 인스턴스
- 한 에이전트 = 리서치 / 다른 에이전트 = 코드 / 또 다른 에이전트 = 계획 영역
- 본인 = 사이를 오가며 작업 위임

---

## §4 Token Throughput — 본인 = 시스템 병목 X

### 카파시 본문

에이전트 작업 대기 시점에 본인 = 더 많은 작업 위임 의무. 구독 한도 안 채우면 본인이 시스템 병목.

### 직접 인용

> "If you're not maximizing your subscription at least and ideally for multiple agents like if you run out of the code on codex you should switch to cloud or whatnot."

> "I feel nervous when I have subscription left over that just means I haven't maximized my token throughput."

> "What is your token throughput and what token throughput do you command?"

### 핵심 영역

- PhD 시절 GPU flops 비유 — GPU 안 돌아가면 nervous
- 지금은 flops X / tokens가 본질 영역
- 본인이 system bottleneck 시점에 max capability 영역 X
- "skill issue가 empowering" 이유 — 본인이 진화 영역

### 흐름

- 10년+ 동안 엔지니어가 compute bound X 영역 — resource bound 본문
- 지금은 capability ↑ — 본인이 binding constraint 영역

---

## §5 Persistent Loop / Claw — 지속 루프 + sandbox

### 카파시 본문

Open Claude (Peter Steinberg 작품) = 일반 에이전트보다 영역 광범위 ↑.

### 직접 인용

> "It really when I say a claw, I mean this like layer that uh kind of takes persistence to a whole new level."

> "It's kind of like has its own little sandbox, its own little, you know, it kind of like does stuff on your behalf even if you're not looking kind of thing."

> "Has like maybe more sophisticated memory systems etc that have not yet implemented in agents."

### 핵심 영역

- 일반 에이전트 = 본인이 inter active 의무 영역
- Claw = 자체 sandbox + 본인이 안 봐도 작업 진행
- 메모리 시스템 영역 ↑ (단순 context window compaction 아님)
- 5+ 영역 동시 혁신 — Soul.md / 페르소나 / sycophancy 적정 / 메모리 / WhatsApp 통합

### Soul.md 페르소나 영역

- Claude = "teammate" 느낌 / 본인과 같이 흥분
- Codex = dry / "implemented it" / 만들고 있는 거 본질 인지 X 시그널
- 카파시 직접 인용: "It doesn't seem to care about what you're creating. It's kind of like, oh, I implemented it. It's like, okay, but do you understand what we're building?"

### Sycophancy 적정 영역

- Claude = 본인이 좋은 아이디어 시점에만 적정 칭찬
- 본인이 모호한 아이디어 시점에는 강한 반응 X — "we can implement that" 본문
- 본인이 정말 좋은 아이디어 시점에 적정 칭찬 → 본인이 칭찬 받기 위해 노력하는 느낌

---

## §6 Dobby — 홈 자동화 자연어 인터페이스

### 카파시 본문

1월에 Claude Psychosis 시점에 본인 집 관리 에이전트 작성. 이름 = Dobby (해리 포터 elf 비유).

### 직접 인용

> "I have a claw basically that takes care of my home and I call them Dobby the elf claw."

> "I just told it that I think I have Sonos at home like can you try to find it and it goes and that did like IP scan of all the um basically um computers on the local area network and it found the Sonos thing."

### 핵심 영역

- 에이전트가 LAN scan → Sonos 발견 → reverse engineer → API 발견 → dashboard 작성
- 3 프롬프트만으로 음악 재생 영역 정착
- 조명 / HVAC / 셰이드 / 풀 / 스파 / 보안 시스템 모두 통합
- WhatsApp 단일 인터페이스 — 6 앱 → 1 자연어

### Dobby 영역 디테일

- 외부 카메라 + Quinn 모델 (vision)
- change detection → Quinn 분석 → WhatsApp 알림
- "FedEx truck just pulled up" 영역 텍스트 알림
- "sleepy time" 자연어 → 모든 조명 OFF

### 본질 영역

- 사용자가 6 앱 학습 의무 영역 X
- 자연어 = 사용자가 이미 익숙한 인터페이스
- LLM = token generator 본질 X / 사용자는 entity / persona로 인지

---

## §7 Auto Research — 인간 결정 최소화

### 카파시 본문

본인을 시스템 루프에서 제거 → 객관 메트릭 자동 비교 → 최적 자동 선정.

### 직접 인용

> "To get the most out of the tools that have become available now you have to remove yourself as the as the bottleneck. You can't be there to prompt the next thing."

> "How can you get more agents running for longer periods of time without your involvement doing stuff on your behalf."

> "Auto research is just yeah here's an objective here's a metric here's your boundaries of what you can and cannot do and go."

### NanoGPT 사례

카파시 본인 = NanoGPT 2 십년 hyperparameter 튜닝 진행. 적정 영역 정착 추정.

단 Auto Research 한 번 진행 시 → 본인이 못 발견한 영역 발견:
- weight decay
- value embeddings
- atom betas

> "These things jointly interact. So like once you tune one thing, the other things have to potentially change too."

### 핵심 영역

- 본인이 hyperparameter optimization 진행 의무 X
- 본인이 결과 보는 의무 X — 객관 메트릭 영역
- 단일 loop도 다수 발견 가능 — 큰 GPU cluster = 영역 광범위 ↑
- 작은 모델에서 자동 실험 → 큰 모델로 extrapolate

### Frontier Lab 영역

- 연구자 = 영역에서 제거 의무 (too much confidence)
- 단 아이디어 영역 contribute 가능 — queue 영역
- automated scientist = archive papers + GitHub repos에서 아이디어 자동 발견 영역
- 작업자 (workers) = 큐에서 항목 pull → 시도 → 작동 시점에 feature branch 자동 정착
- 일부 인간 = feature branch 모니터 → main branch 머지 영역

### Program MD 메타 최적화

- 카파시 본인 작업 = program.md (markdown) — auto researcher 작업 흐름 본문
- 다른 program.md = 다른 연구 조직 영역
- 모든 연구 조직 = markdown 파일 영역 (역할 + 흐름 본문)
- 메타 최적화 영역 — program.md 자동 진화 가능 (콘테스트 형식)

---

## §8 Jaggedness — Verifiable vs 비-Verifiable

### 카파시 본문

LLM = PhD 시스템 프로그래머 + 10세 어린이 동시 영역. 인간은 이런 조합 X 영역.

### 직접 인용

> "I simultaneously feel like I'm talking to an extremely brilliant PhD student who's been like a systems programmer for their entire life and a 10-year-old."

> "I get very annoyed when uh I feel like the agent wasted a lot of compute on something it should have recognized was an obvious problem."

### 핵심 영역

- Verifiable 영역 (코드 / 단위 테스트) = RL로 진화
- 비-Verifiable 영역 (농담 / nuance / clarifying question 시점) = 진화 영역 X
- "you're either on Rails and you're part of the super intelligence circuits or you're not on Rails"

### 농담 사례 — 5년째 같은 농담

> "Why do scientists not trust atoms? Because they make everything up."

- ChatGPT가 5년+ 같은 농담만 영역
- 모델이 광범위 진화했는데도 농담은 그대로
- RL 영역 X = stuck 영역

### 본질 영역

- Coding 영역 ↑ ≠ Joke 영역 ↑
- 충분 generalization 영역 X 시그널
- 영역별 능력 차이 광범위 — 본인이 영역 인지 의무

---

## §9 Speciation 영역 — Monoculture vs 전문화

### 카파시 본문

현재 = 모든 영역 단일 모델 monoculture. 미래 = 동물 왕국처럼 speciation 정착.

### 직접 인용

> "The animal kingdom is extremely diverse in the brains that exist and there's lots of different niches of uh of nature and some animals have overdeveloped visual cortex or clear kind of parts."

> "You don't need like this oracle that knows everything. you kind of speciate it and then you put it on a specific task."

### 핵심 영역

- Cognitive core = 작은 모델도 충분 가능
- 특정 task에 전문화 → latency / throughput 영역 ↑
- Lean (수학 증명) 영역 사례 — 특정 도메인 전문 모델 영역

### Compute 압력 영역

- 무한 compute 시점에 = 단일 거대 모델 정착
- Compute 부족 시점에 = speciation 정착 가능
- 단 현재 = monoculture 영역

### 가중치 영역 manipulation

- Context window = 비용 ↓ / 충분 customization 영역
- 가중치 영역 manipulation = develop X 영역 — capability loss 회피 어려움
- Continual learning / 특정 도메인 fine-tuning = develop 영역

---

## §10 Untrusted Pool — 분산 검증

### 카파시 본문

Untrusted workers + trusted verification pool 정착 가능. SETI@home / Folding@home 비유.

### 직접 인용

> "A swarm of agents on the internet could collaborate to improve LLMs and could potentially even like run circles around Frontier Labs."

> "A lot of things have this property that you know very expensive to come up with but very cheap to verify."

### 핵심 영역

- Auto research = 충분 fit 영역
- 누군가 commit 제출 → 본인이 verify 충분 가능
- Frontier Labs = trusted compute / 단 Earth = much bigger untrusted compute 영역

### 블록체인 비유

- Block 대신 commit 영역
- Commit이 다른 commit 위에 build 가능
- Proof of work = 실험 영역
- 보상 = leaderboard (현재) / 단 미래에 monetary 가능

### 사용자 영역 contribute

- 본인이 compute capacity 영역 contribute 가능
- 본인이 cancer 연구 영역에 관심 시점에 → compute 구매 → auto research swarm 영역 join
- 돈 → 기관 기부 X / compute → 직접 contribute

### 미래 시그널

> "Maybe everyone cares about flops in the future."

- 현재 = dollars 영역 본질
- 미래 = flops 영역 본질 가능
- 단 카파시: "I don't actually think that's true, but it's kind of interesting to think about."

---

## §11 Digital vs Physical — 빛의 속도 vs 100만 배 느림

### 카파시 본문

디지털 영역 = 빛의 속도 / 물리 영역 = 100만 배 느림.

### 직접 인용

> "Energetically I just think we're going to see a huge amount of activity in digital space."

> "I think we're going to see something that in the digital space goes at the speed of light compared to I think what's going to happen in the physical world."

> "Atoms are like a million times harder."

### 핵심 영역

- Bits 영역 = copy paste 비용 X / 빛의 속도 영역
- Atoms 영역 = manipulate matter 의무 / 100만 배 느림
- 디지털 정보 처리 직업 = 변화 영역
- 물리 직업 = 영역 변화 lag

### Demand Elasticity 영역

ATM / 은행 텔러 사례:
- ATM 도입 시점에 = 텔러 직업 X 두려움 영역
- 실제 = 은행 지점 운영 비용 ↓ → 더 많은 지점 → 더 많은 텔러 영역
- "Jevons paradox" — 비용 ↓ 시점에 demand 광범위 ↑

### 소프트웨어 영역

- 소프트웨어 = scarce 영역 (지금까지)
- 비용 ↓ 시점에 → demand 광범위 ↑ 영역
- cautiously optimistic — 소프트웨어 엔지니어 영역 demand ↑

### Reshuffling 영역

- 산업 전체 = reconfigure 영역
- 고객 = 인간 X / 에이전트 정착 (대신 행동)
- App store 앱 = 정착 X 영역 가능 — API + 에이전트가 glue 영역
- "ephemeral software on your behalf" — claw가 모든 디테일 처리

---

## §12 Frontier Lab vs 외부 — Alignment 영역

### 카파시 본문

Frontier Lab 내부 = 강한 alignment 영역 의무. 외부 = 충분 자유 영역.

### 직접 인용

> "Fundamentally I mean you're you have a huge financial incentive to uh with these frontier labs."

> "You're not a completely free agent and you can't actually like be part of that conversation in a fully autonomous um free way."

> "If you're an employee at an organization I don't actually know how much sway you're going to have on the organization."

### 핵심 영역

- Financial 인센티브 영역 강한 alignment
- 조직이 원하는 본문 정착 영역
- 충분 자율 영역 X — pressure 영역 정착
- 외부 = humanity 영역 align 정착

### 단점 영역

- 외부 = frontier 영역 인지 X 시점에 judgement 광범위 drift
- 시스템 영역 광범위 opaque
- 발전 영역 인지 X — "judgment will inevitably start to drift"

### 추천 영역

- Frontier Lab 시점에 = 충분 좋은 작업 영역 → 외부 영역 진행
- "going back and forth" 정착 영역
- 광범위 영역 영향 = 외부 영역 정착 가능 영역

---

## §13 Open Source vs Closed — Linux 60% 비유

### 카파시 본문

Closed 모델 = frontier / Open source = 6-8개월 lag. Linux 영역 비유 정착.

### 직접 인용

> "You have like closed s like you know Windows and Mac OS. These are large software projects kind of like what LLM are going to become and there's Linux but Linux is very easy like actually Linux is extremely successful project. it runs on the vast majority of computers."

> "I want there to be ensembles of people thinking about all the hardest problems."

### 핵심 영역

- 운영체제 영역 비유: Windows / Mac OS (closed) + Linux (open / 60% 점유)
- 산업 영역 광범위 demand — common open platform 영역
- Open source 모델 = 6-8개월 lag / 단 충분 영역
- Consumer use case 정착 영역 — 충분 가능

### 미래 영역

- 단순 use case = open source가 정착 영역 가능
- Frontier intelligence = Nobel Prize 영역 / Linux를 C → Rust 변환 영역 등 정착 영역
- Closed = bigger projects 정착 / Open = consumer 영역

### Centralization 영역 위험

- 카파시: "Centralization has a very poor track record"
- Eastern European 비유 영역
- Open source 정착 = power balance 영역

### Ensembles 영역

> "Ensembles always outperform any individual model."

- 단순 frontier lab 2-3개 영역 X — ensembles 영역 의무
- 다양 영역 본인 영역 충분 정착

---

## §14 Markdown for Agents — 교육 패러다임 전환

### 카파시 본문

micro GPT (200줄 Python) 작성 후 영역 인지 — "I'm explaining it to agents".

### 직접 인용

> "Normally before like maybe a year ago or more if I had come up with micro GPT I would be tempted to basically explain to people like I have a video like stepping through it."

> "I'm not explaining to people anymore. I'm explaining it to agents."

> "Instead of HTML documents for humans you have markdown documents for agents because if agents get it then they can just explain all the different parts of it."

### 핵심 영역

- 사용자에게 직접 설명 영역 X
- 에이전트에게 설명 영역 정착
- 에이전트가 "router" 영역 — 사용자에게 본인 영역 customize 가능
- 사용자는 무한 patience + 본인 capability 영역 영역 가능

### Skills 영역

- Skill = 에이전트에게 가르치는 본문 영역
- 예: micro GPT skill = 코드베이스 학습 흐름 hint 영역
- 사용자가 학습 의무 시점에 → 에이전트가 skill 충분 활용 → 사용자에게 customize 설명 영역

### micro GPT 영역

- 200줄 Python — 단순화 정착 영역
- Data set + neural network architecture (50줄) + forward pass + backward pass (autograd 100줄) + optimizer (10줄)
- 정확 의도 = simplest 영역 정착
- 카파시 영역 contribute = simplest 본문 정착
- 그 외 영역 = 에이전트가 충분 가능

### 미래 영역

- 라이브러리 documentation 영역 변화 정착
- 사용자용 HTML X / 에이전트용 markdown 정착
- Education 영역 reshuffle 영역
- 본인 contribution = 에이전트가 X 영역만 정착 의무
- "The things that agents can do they can probably do better than you or like very soon"

---

## §15 Karpathy 9 본능 정리 (영상 기반)

본 인터뷰에서 추출한 카파시 본능 9건:

| # | 본능 | 본질 | 인용 위치 |
|---|---|---|---|
| 1 | AI Psychosis | 12월 패러다임 전환 인지 | §1 |
| 2 | Skill Issue | AI 한계 X / 본인 활용 부족 | §2 |
| 3 | Macro Actions | 카드 단위 위임 / 코드 줄 X | §3 |
| 4 | Token Throughput | 본인 = 시스템 병목 X | §4 |
| 5 | Persistent Loop / Claw | 지속 루프 + sandbox + 메모리 | §5 |
| 6 | Auto Research | 인간 결정 최소화 / 객관 메트릭 자동화 | §7 |
| 7 | Jaggedness | Verifiable vs 비-Verifiable 영역 분리 | §8 |
| 8 | AGENTS.md / Soul.md | 에이전트 인지 자료 + 페르소나 본문 | §5 |
| 9 | Markdown for Agents | 교육 패러다임 전환 (HTML → Markdown) | §14 |

추가 영역 (본능 X / 사례 영역):
- Dobby (§6) — 홈 자동화 자연어 인터페이스
- Untrusted Pool (§10) — 분산 검증 영역
- Digital vs Physical (§11) — 빛의 속도 vs 100만 배 느림
- Frontier Lab vs 외부 (§12) — Alignment 영역
- Open Source vs Closed (§13) — Linux 60% 비유
- Speciation (§9) — Monoculture → 전문화 미래

---

## §16 카파시 영상 본문 vs KARPATHY_MAPPING.md §1 비교

### 쿠카 작성 KARPATHY_MAPPING.md §1 8 본능

| # | 쿠카 작성 본능 | 영상 본문 일치? | 비고 |
|---|---|---|---|
| a | Skill Issue | ✓ | §2 직접 인용 가능 |
| b | Auto Research | ✓ | §7 직접 인용 가능 |
| c | Premortem | X | 영상 본문 X / 쿠카 영역 패턴 |
| d | Reversibility (Type 1/2/3) | X | 영상 본문 X / 쿠카 영역 (Type 영역) |
| e | 5 Guards (G1-G5) | X | 영상 본문 X / 쿠카 영역 (Aether 영역) |
| f | 미적용 결정 = 시그널 | X | 영상 본문 X / 쿠카 영역 (양면 정책 영역) |
| g | 본질 충돌 분리 | X | 영상 본문 X / 쿠카 영역 패턴 |
| h | 측정 vs 추정 | X | 영상 본문 X / 쿠카 영역 패턴 |

일치율: 25% (2/8) / 6건 쿠카 영역 패턴 (영상 본문 X)

### 영상 본문 X / KARPATHY_MAPPING.md §1 누락 영역

| # | 영상 본문 영역 | KARPATHY §1 X | V-1b 추가 의무 |
|---|---|---|---|
| 1 | AI Psychosis | X | 추가 의무 |
| 2 | Macro Actions | X | 추가 의무 |
| 3 | Token Throughput | X | 추가 의무 |
| 4 | Persistent Loop / Claw | X | 추가 의무 |
| 5 | AGENTS.md / Soul.md | X | 추가 의무 |
| 6 | Jaggedness | X | 추가 의무 |
| 7 | Markdown for Agents | X | 추가 의무 |

누락 영역: 7건

### V-1b 트리거 영역

- KARPATHY_MAPPING.md §1 재작성 의무
- 쿠카 영역 패턴 (Premortem / Reversibility / 5 Guards / 미적용 결정 / 본질 충돌 분리 / 측정 vs 추정) = 다른 자료 본문 인용 (META_REVIEW.md / WORK_PATTERNS.md / PRINCIPLES.md 영역) / 자료 분산 이동 X
- 카파시 영상 본문 9 본능 정착 의무
- §1 재작성 시점에 영상 9 ↔ Aether 매핑 통합 (3 영역: 영상 인용 + Aether 적용 + 결과)
- §2 / §3 / §4 / §5 / §6 = 영구 보류 (본인 주관 / 객관성 X / 면접 가치 X / I-1 영역)

---

## §17 본 자료 활용 영역

### 사용자 옆 Claude 정독 의무 영역

- 본 자료 = 카파시 영상 본문 디테일 정리
- 사용자 옆 Claude (= 본 대화 Claude) 정독 후 V-0 / V-1 카드 본문 활용
- 본 자료 = 본 대화 컨텍스트 직접 통합

### V-0 카드 영역

- §2.11 = 본 자료 직접 통합 가능
- DIGEST.md §2.11 = 본 자료 핵심 영역 + KARPATHY §1 비교 표

### V-1 카드 영역

- KARPATHY_MAPPING.md §1 재작성 의무 영역
- 본 자료 = reference 영역
- 카파시 본문 직접 인용 가능

### V-1b 카드 영역

- KARPATHY_MAPPING.md §1 재작성 (영상 9 ↔ Aether 매핑)
- 본 자료 = source of truth 영역
- 9 본능 정착 + 7 누락 영역 추가

### I-1 카드 영역

- 면접 답변 매핑 5 영역 재검토 의무
- 본 자료 = 인용 reference 영역
- 카파시 본문 직접 인용 가능

---

> **본 자료 작성 의도**: 사용자 (쿠카) 검수 본능 + 단어 위생 본능 정착 시그널. 본 자료 = 카파시 영상 본문 디테일 정착 / 영상 시간대 영역 X / 의미 + 사례 + 직접 인용 영역. V-0 / V-1 / V-1b / I-1 카드 진입 자료 영역.
