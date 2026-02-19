# Aether CI/CD Pipeline

## 개요

Jenkins 기반 CI/CD 파이프라인. GitHub webhook으로 `main` 브랜치 push 시 자동 실행.
현재는 로컬 Docker Compose로 운영하며, 프로덕션 배포 시 이 파이프라인을 사용한다.

## 파이프라인 흐름

```
┌──────────┐     ┌──────────────────────────────────────┐     ┌──────────────┐
│ Checkout │────>│           Test Backend (병렬)          │────>│Test Frontend │
└──────────┘     │                                        │     └──────┬───────┘
                 │  ┌─────────────────┐                   │            │
                 │  │portfolio-service│  pytest (209)      │            │
                 │  └─────────────────┘                   │            v
                 │  ┌─────────────────┐                   │     ┌──────────────┐
                 │  │  llm-service    │  pytest (232)      │     │ Docker Build │
                 │  └─────────────────┘                   │     └──────┬───────┘
                 │  ┌─────────────────┐                   │            │
                 │  │  auth-service   │  gradlew test      │            v
                 │  └─────────────────┘                   │     ┌──────────────┐
                 └──────────────────────────────────────┘     │ Docker Push  │
                                                               │ (main only)  │
                                                               └──────┬───────┘
                                                                      │
                                                                      v
                                                               ┌──────────────┐
                                                               │   Deploy     │
                                                               │ (main only)  │
                                                               └──────────────┘
```

## 스테이지 상세

### 1. Checkout

Git SCM에서 소스 체크아웃. 브랜치명과 커밋 해시를 로그에 기록한다.

### 2. Test Backend (병렬 실행)

3개 백엔드 서비스를 **병렬**로 테스트하여 실행 시간을 단축한다.

| 서비스 | 런타임 | 테스트 명령 | 테스트 수 |
|--------|--------|------------|----------|
| portfolio-service | Python 3.13 | `pytest tests/ -x -q` | 209 |
| llm-service | Python 3.13 | `pytest tests/ -x -q` | 232 |
| auth-service | Java 21 (Spring Boot) | `./gradlew test` | 8+ |

각 Python 서비스는 격리된 venv를 생성하여 의존성 충돌을 방지한다.
테스트 결과는 JUnit XML로 출력되어 Jenkins UI에서 확인 가능하다.

### 3. Test Frontend

```bash
npm ci --prefer-offline   # 의존성 설치 (lockfile 기반)
npm run build             # Next.js 프로덕션 빌드 + TypeScript 타입 체크
```

빌드 실패 시 타입 에러나 import 누락을 즉시 감지한다.

### 4. Docker Build

`docker compose build`로 4개 서비스 이미지를 빌드한다.

| 이미지 | 베이스 | 포트 |
|--------|--------|------|
| aether-portfolio | python:3.13-slim | 8001 |
| aether-llm | python:3.13-slim | 8002 |
| aether-auth | eclipse-temurin:21-jre | 8003 |
| aether-frontend | node:22-alpine | 3000 |

태그 전략: `{BUILD_NUMBER}-{COMMIT_SHORT}` + `latest`

### 5. Docker Push (main 브랜치만)

빌드된 이미지를 컨테이너 레지스트리에 푸시한다.
`main` 브랜치 빌드에서만 실행된다.

### 6. Deploy (main 브랜치만)

SSH로 배포 서버에 접속하여:
1. `docker compose pull` — 최신 이미지 풀
2. `docker compose up -d` — 롤링 업데이트
3. 헬스체크 — 4개 서비스 엔드포인트 확인

## 트리거

| 트리거 | 조건 | 실행 범위 |
|--------|------|----------|
| GitHub Webhook | `main` push | 전체 파이프라인 |
| GitHub Webhook | PR 생성/업데이트 | Checkout → Test (Push/Deploy 제외) |
| 수동 실행 | Jenkins UI | 전체 파이프라인 |

GitHub Repository → Settings → Webhooks에 Jenkins URL 등록:
```
https://<jenkins-host>/github-webhook/
```

## 환경변수

Jenkins Credentials에 등록이 필요한 항목:

| Credential ID | 타입 | 용도 |
|--------------|------|------|
| `docker-registry-url` | Secret text | 컨테이너 레지스트리 주소 (e.g. `ghcr.io/your-org`) |
| `docker-registry-creds` | Username/Password | 레지스트리 인증 |
| `deploy-ssh-host` | Secret text | 배포 서버 주소 (e.g. `ubuntu@10.0.0.1`) |
| `deploy-ssh-key` | SSH Key | 배포 서버 SSH 키 |
| `gemini-api-key` | Secret text | Google Gemini API 키 |
| `postgres-password` | Secret text | PostgreSQL 비밀번호 |
| `jwt-secret` | Secret text | JWT 서명 키 |

## 현재 운영 방식

```
개발 환경 (현재)
  로컬 머신에서 docker compose up -d
  → 6개 컨테이너 (postgres, redis, portfolio, llm, auth, frontend)

프로덕션 환경 (계획)
  GitHub push → Jenkins 파이프라인 → Docker Registry → 배포 서버
  → 동일한 docker-compose.yml 기반 배포
```

Jenkins 파이프라인은 구현 완료 상태이며, 배포 인프라(서버, 레지스트리) 확보 시 즉시 적용 가능하다.
