# Jenkins CI/CD 파이프라인

---

## 한 줄 요약

**"코드를 GitHub에 올리면 자동으로 테스트 → 빌드 → 배포해주는 로봇"**

---

## 수동 vs 자동 비교

```
현재 (수동):
1. 코드 수정
2. pytest 실행 (portfolio-service)
3. pytest 실행 (llm-service)
4. gradlew test (auth-service)
5. npm run build (frontend)
6. docker compose build
7. docker compose up -d
→ 이걸 매번 손으로 함

Jenkins (자동):
1. 코드를 git push하면
2~7. Jenkins가 알아서 전부 실행
→ 실패하면 알림, 성공하면 자동 배포
```

---

## Jenkinsfile 각 단계 (식당 비유)

```
Stage 1. Checkout (재료 가져오기)
  → GitHub에서 최신 코드를 가져옴

Stage 2. Test Backend (재료 검수 — 병렬)
  → 3개 서비스 테스트를 동시에 실행 (순서대로 하면 느리니까)
  → portfolio: 209개, llm: 232개, auth: 62개

Stage 3. Test Frontend (매장 점검)
  → npm run build로 타입 에러, import 누락 검사

Stage 4. Docker Build (포장)
  → 4개 서비스를 Docker 이미지로 만듦

Stage 5. Docker Push (물류 센터로 보내기)
  → main 브랜치일 때만 이미지를 Registry에 업로드

Stage 6. Deploy (매장에 진열)
  → main 브랜치일 때만 실제 서버에 배포
  → 배포 후 헬스체크로 "잘 떠있나?" 확인
```

---

## 핵심 개념

### when { branch 'main' }

```
feature 브랜치 push  → 테스트만 실행 (Stage 1~3)
main 브랜치 push     → 전체 실행 (Stage 1~6, 배포 포함)

→ 실수로 미완성 코드가 배포되는 걸 방지
```

### 병렬 테스트 (parallel)

```
순차 실행: portfolio(3분) → llm(3분) → auth(1분) = 7분
병렬 실행: portfolio(3분) + llm(3분) + auth(1분) = 3분 (동시에)

→ 테스트 시간 절반 이상 단축
```

### 이미지 태그 전략

```
IMAGE_TAG = {빌드번호}-{커밋해시 앞 7자리}
예: 42-fe99f40

→ 어떤 커밋에서 빌드된 이미지인지 추적 가능
→ 문제 발생 시 이전 버전으로 롤백 가능
```

### 헬스체크

```
배포 후 30초 대기 → 각 서비스에 curl 요청:
  curl http://localhost:8001/health        (portfolio)
  curl http://localhost:8002/health        (llm)
  curl http://localhost:8003/actuator/health (auth)
  curl http://localhost:3000               (frontend)

→ 하나라도 응답 없으면 배포 실패 처리
→ "배포했는데 실제로 안 돌아가는" 상황 방지
```

### Credentials (비밀 정보 관리)

```
코드에 비밀번호를 직접 쓰면 안 됨 (GitHub에 노출)
→ Jenkins Credentials에 등록하고, 파이프라인에서 참조

credentials('gemini-api-key')    → Gemini API 키
credentials('postgres-password') → DB 비밀번호
credentials('jwt-secret')        → JWT 서명 키

→ 코드에는 변수명만 있고, 실제 값은 Jenkins가 주입
```

---

## 면접 답변

### 기본 질문: "CI/CD 경험이 있나요?"

> "Jenkins 파이프라인으로 push하면 테스트 → 빌드 → 배포가 자동화됩니다. 백엔드 3개 서비스는 병렬 테스트로 시간을 단축했고, main 브랜치만 프로덕션에 배포됩니다."

### 깊이 질문: "파이프라인 설계 시 고려한 점은?"

> "세 가지입니다. 첫째, 백엔드 테스트를 parallel로 실행해서 파이프라인 시간을 절반으로 줄였습니다. 둘째, when { branch 'main' } 조건으로 feature 브랜치에서는 테스트만 돌리고 배포는 main에서만 실행합니다. 셋째, 배포 후 헬스체크로 4개 서비스가 정상인지 확인하고, 실패하면 파이프라인을 중단합니다."

### 후속 질문: "롤백은 어떻게 하나요?"

> "이미지 태그에 빌드번호와 커밋해시를 포함시켜서, 문제 발생 시 이전 태그로 docker compose pull하면 즉시 롤백됩니다. 예를 들어 42-fe99f40에서 문제가 생기면 41-3281ab0으로 되돌립니다."

---

## Aether CI/CD 현재 상태

```
✅ Jenkinsfile 작성 완료 (6개 스테이지)
✅ docs/Design/CI_CD_PIPELINE.md 문서화 완료
✅ GitHub push 완료

⬜ Jenkins 서버 세팅 (배포 서버 확보 시)
⬜ GitHub Webhook 연결
⬜ Slack 알림 연동
```

현재는 파이프라인 설계 완료 상태이며, 배포 인프라 확보 시 즉시 적용 가능.