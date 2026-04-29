# CLAUDE.md

> Claude Code/AI 에이전트의 작업 규칙. AGENTS.md가 "코드 사실(What)"을 다룬다면, 본 문서는 "작업 방식(How)"을 다룬다.

---

## §1. 브랜치 전략

- 기능 추가: `feat/T-<id>-<slug>` (예: `feat/T-1-tool-use`).
- 버그 수정: `fix/<slug>` (예: `fix/rag-empty-context`).
- 문서/리팩터: `docs/<slug>`, `refactor/<slug>`.
- 한 카드 = 한 브랜치 = 한 PR (본 문서 §6).
- main 직접 push 금지. 머지는 squash merge로 카드 1건 = 커밋 1건 유지.

---

## §2. PR 게이트 (H-7 도입 예정)

PR은 다음을 모두 통과해야 머지 가능:

- `pytest tests/ -x -q` — 변경 대상 서비스 테스트 통과 (현재 519건, AGENTS.md §7).
- `ruff check .` — 린트 0 violation. (H-7 도입 후 적용.)
- `black --check .` — 포맷 차이 0. (H-7 도입 후.)
- `mypy app/` — 타입 에러 0. (H-7 도입 후.)
- `npm run build` — 프론트 변경 시 빌드 성공 (`Jenkinsfile:82-91`).
- AGENTS.md 갱신 체크박스 — 카드가 §7 지배 숫자나 §1-§6 사실을 변경했다면 본 PR에 갱신 포함.

H-7 도입 전까지는 pytest + npm build만 강제. 신규 코드는 ruff/black/mypy 위반을 만들지 않도록 작성한다.

---

## §3. 코드 스타일

- Python: PEP8, 4-space indent, line length 100. 한글 주석 허용 (도메인 용어가 한글일 때 가독성 우선).
- **타입 힌트 의무**: 신규 함수 시그니처는 인자/반환 모두 타입 힌트 필수. `from __future__ import annotations`를 파일 상단에 두고 forward ref 사용 가능.
- **import는 파일 상단**: 함수 내 import 금지. import 에러는 모듈 로드 시점에 즉시 노출되어야 한다 (early-fail).
- 신규 docstring은 한 줄 요약만. 멀티 paragraph docstring 금지 (CLAUDE.md 시스템 가이드).
- 주석은 WHY가 비자명할 때만. WHAT은 식별자 이름으로 표현 (Header 시스템 가이드 §Tone).

---

## §4. 위험 작업 사용자 확인

다음 작업은 **반드시 사용자 확인 후**에만 실행:

- `git push --force` (특히 main/develop). origin/main에 대한 force push는 절대 금지.
- DB 스키마 drop, `alembic downgrade`, `DROP TABLE`, `DELETE FROM` 무조건자.
- secrets/credentials 파일 git에 commit (`.env`, `*-credentials.json`, `id_rsa` 등).
- `docker compose down -v` (볼륨 삭제 — ChromaDB 인덱스 손실).
- `--no-verify`, `--no-gpg-sign`, hooks 우회 플래그 일체.
- 외부 시스템에 메시지 발송 (Slack, GitHub PR 코멘트, 이메일).

쉽게 되돌릴 수 있는 로컬 파일 편집은 자유. 위 항목만 확인이 필요하다.

---

## §5. 작업 시작 절차

1. 카드 파일 읽기 — `docs/agent-capability-audit/phase3/<id>_*.md`. §4 변경 대상 파일 목록을 정확히 파악.
2. AGENTS.md §8 체크리스트를 순서대로 호출.
3. TaskCreate로 카드 §1-§11을 단계별 task로 분해.
4. 작업 중 발견한 새 사실은 AGENTS.md/ADR에 즉시 반영 (같은 PR).
5. 머지 전 카드 §8 완료 검증 명령을 모두 실행.

---

## §6. 작업 단위 원칙 (FDE 1함수 1책임 확장)

- **한 카드 = 한 책임**: `docs/agent-capability-audit/phase3/<id>_*.md` 1건이 다루는 범위만 수정한다. 카드 §4 변경 대상 외 파일은 건드리지 않는다.
  - **사례 — H-4 (e9acdf8)**: `prompts.py` / `prompt_registry.py` / `rag.py` / `test_prompt_registry.py` 4 파일만 수정. README/frontend/auth-service의 pre-existing 변경은 분리 보존.
- **한 PR = 한 카드**: 카드 1건당 단일 커밋·단일 PR. 롤백은 `git revert <commit>` 한 줄로 끝나야 한다.
- **한 에이전트 = 한 줄 정의**: `BaseAgent` 상속 클래스는 `name`, 도구 목록, `run()` 1줄 책임 기술 (H-2 도입 후, ADR 0002 참조).
- **ADR 동시 갱신 의무**: 카드가 ADR이 다루는 결정을 바꾸면 해당 ADR 수정도 같은 PR 범위. 1책임은 ADR 갱신 책임을 포함한다.
- **임계값**: 한 카드의 작업 시간이 30분 이상 걸리면 카드 분해 검토. 1시간 이상이면 분해 의무.
