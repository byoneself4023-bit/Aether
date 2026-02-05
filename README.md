# 🏛️ Claro - 민원 AI 어시스턴트

> 공공기관 상담원을 위한 AI 업무 지원 시스템

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)

## 📋 프로젝트 소개

**Claro**는 공공기관 콜센터 상담원들의 업무 효율성을 높이기 위한 AI 어시스턴트입니다.

하루 80콜 이상 처리하면서 2,000여 개 매뉴얼에서 정보를 찾느라 시간을 쓰는 상담원들을 위해, AI가 민원을 자동 분류하고, 유사 사례를 검색하며, 답변 초안을 생성합니다.

## ✨ 주요 기능

| 기능 | 설명 | 성능 |
|------|------|------|
| **도메인 분류** | 민원 내용 → 14개 도메인 자동 분류 | 81.1% 정확도 |
| **카테고리 분류** | 민원 내용 → 63개 세부 카테고리 분류 | WeightedTrainer + 오버샘플링 |
| **유사 민원 검색** | 과거 처리된 비슷한 민원과 답변 검색 | 57,402건 DB |
| **답변 초안 생성** | RAG 기반 매뉴얼 + 과거 사례로 답변 생성 | Gemma/Gemini |
| **LLM 비교** | 로컬 LLM vs 클라우드 API 동시 비교 | 속도/품질 비교 |
| **대시보드** | 모델 KPI, 쿼리 트렌드, 도메인 분포 시각화 | 실시간 통계 |

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│                      localhost:3010                          │
└─────────────────────────┬───────────────────────────────────┘
                          │ /api/* (Next.js rewrites)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                           │
│                   localhost:8010                              │
├─────────────────────────────────────────────────────────────┤
│ • 도메인 분류 (BERT)    • RAG 답변 생성                       │
│ • 카테고리 분류 (BERT)  • FAISS 벡터 검색                     │
│ • 14 도메인 / 63 카테고리 • LLM 비교                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                ┌─────────┴─────────┐
                ▼                   ▼
        ┌─────────────┐     ┌─────────────┐
        │   Ollama    │     │ Gemini API  │
        │ (로컬 LLM)  │     │ (클라우드)  │
        │ gemma2:2b   │     │ 2.5 Flash   │
        │ civil-qwen  │     │    Lite     │
        └─────────────┘     └─────────────┘
```

## 🛠️ 기술 스택

### Backend
- **FastAPI** - ML/LLM 서비스 API
- **PyTorch** - 딥러닝 프레임워크
- **Transformers** - BERT 분류 모델
- **LangChain** - RAG 체인 구성
- **FAISS** - 벡터 유사도 검색
- **Sentence-Transformers** - 임베딩 모델

### Frontend
- **Next.js 14** - React 프레임워크
- **TypeScript** - 타입 안정성
- **Tailwind CSS** - 스타일링
- **Recharts** - 대시보드 차트
- **Lucide React** - 아이콘

### LLM
- **Ollama** - 로컬 LLM 서버
- **Gemma 2B** - 로컬 추론
- **Qwen 2.5 7B** - 파인튜닝 모델 (LoRA)
- **GGUF** - 로컬 GGUF 모델 추론 (llama-cpp-python)
- **Gemini API** - 클라우드 LLM

### DevOps
- **Docker** - 컨테이너화
- **Docker Compose** - 멀티 컨테이너 관리

## 📁 프로젝트 구조

```
CivilComplaint/
├── docker-compose.yml          # Docker 컨테이너 설정
├── .env.example                # 환경 변수 템플릿
├── README.md
│
├── backend/                    # 통합 백엔드 (FastAPI)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI 앱 진입점
│       ├── core/config.py      # 설정
│       ├── api/
│       │   ├── routes/
│       │   │   ├── classify.py     # 도메인+카테고리 분류 API
│       │   │   ├── generate.py     # RAG 답변 생성
│       │   │   ├── search.py       # 유사 민원 검색
│       │   │   ├── compare.py      # LLM 비교
│       │   │   ├── pipeline.py     # SSE 파이프라인
│       │   │   ├── feedback.py     # 피드백
│       │   │   ├── stats.py        # 통계
│       │   │   ├── models.py       # 모델 정보
│       │   │   └── settings.py     # 설정
│       │   ├── controllers/        # 요청→서비스→응답 변환
│       │   ├── middleware/         # 에러 핸들러
│       │   └── schemas/            # Pydantic 스키마
│       ├── models/
│       │   └── classifier.py   # Domain + Category 분류기
│       ├── services/           # 비즈니스 로직
│       ├── vectorstore/
│       │   └── faiss_store.py  # FAISS 벡터DB
│       ├── pipeline/           # SSE 파이프라인 오케스트레이션
│       │   ├── orchestrator.py
│       │   └── steps.py
│       ├── db/                 # SQLite (피드백, 통계)
│       ├── resources/          # 리소스 레지스트리
│       ├── utils/
│       │   └── answer_cleaner.py  # 답변 후처리
│       └── llm/
│           ├── base.py         # LLM 베이스 인터페이스
│           ├── ollama.py       # 로컬 LLM (Gemma)
│           ├── gemini.py       # Gemini API
│           └── gguf_llm.py     # 로컬 GGUF 모델
│
├── frontend/                   # Next.js 프론트엔드
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js          # /api/* → backend 프록시
│   └── src/
│       ├── app/
│       │   ├── page.tsx            # 메인 (상담) 페이지
│       │   ├── dashboard/page.tsx  # 대시보드
│       │   ├── history/page.tsx    # 상담 히스토리
│       │   ├── settings/page.tsx   # 설정
│       │   └── models/page.tsx     # 모델 정보
│       ├── components/
│       │   ├── common/             # 공통 컴포넌트 (Modal, Toast)
│       │   └── layout/            # 레이아웃 (AppLayout, Header, Sidebar)
│       ├── services/              # API 서비스 레이어
│       ├── hooks/                 # 커스텀 훅 (usePipeline, useTimer, useToast)
│       └── types/                 # TypeScript 타입 정의
│
├── notebooks/                  # ML 파이프라인 (10단계)
│   ├── 01_data_exploration.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_task_definition.ipynb
│   ├── 04_baseline_ml.ipynb
│   ├── 05_deep_classification.ipynb
│   ├── 06_bm25_retrieval.ipynb
│   ├── 07_sbert_faiss.ipynb
│   ├── 08_rag_pipeline.ipynb
│   ├── 09_lora_finetuning.ipynb
│   ├── 10_gguf_deploy.ipynb
│   └── 11_results_summary.ipynb
│
├── scripts/
│   ├── start-dev.sh            # 로컬 개발 서버 실행
│   ├── evaluate_e2e.py         # E2E 평가
│   └── evaluate_rag.py         # RAG 평가
│
└── models/                     # 학습된 모델
    ├── domain_classifier/      # 도메인 분류 모델 (14 클래스)
    ├── category_classifier/    # 카테고리 분류 모델 (63 클래스)
    ├── embedding/              # 임베딩 모델
    └── llm_qwen/               # 파인튜닝 LLM
        ├── civil-lora.gguf
        └── Modelfile
```

## 🚀 실행 방법

### 사전 요구사항

- Docker & Docker Compose
- Ollama (로컬 LLM용)
- Google API Key (Gemini용)

### 1. 레포지토리 클론

```bash
git clone https://github.com/byoneself4023-bit/CivilComplaint.git
cd CivilComplaint
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일에 GOOGLE_API_KEY 입력
```

### 3. 모델 다운로드

모델 파일은 용량이 커서 별도 다운로드가 필요합니다.

- [모델 다운로드 링크] (추후 추가)

### 4. Ollama 설정

```bash
# Ollama 설치 후
ollama pull gemma2:2b

# 파인튜닝 모델 사용 시 (선택)
ollama pull qwen2.5:7b-instruct
cd models/llm_qwen
ollama create civil-qwen -f Modelfile
```

### 5. Docker로 실행

```bash
docker-compose up
```

### 6. 접속

브라우저에서 http://localhost:3010 접속

## 📊 성능 지표

| 지표 | 값 |
|------|-----|
| 도메인 분류 정확도 | 81.1% (14 클래스) |
| 도메인 F1 macro | 67.7% → 오버샘플링으로 개선 |
| 카테고리 분류 | 63 클래스 (WeightedTrainer) |
| 벡터 DB 문서 수 | 57,402건 |
| 학습 데이터 | 352,280건 (콜센터 + 대화) |
| QA 쌍 | 176,544건 |
| Gemma 2B 응답 시간 | 25~35초 |
| Gemini API 응답 시간 | 1~3초 |

## 📚 데이터셋

AI Hub 공공 데이터 활용:

| 데이터셋 | 용도 |
|----------|------|
| 한국어 대화 (공공민원) | 분류 모델 학습 |
| 민원 콜센터 질의응답 | RAG 지식베이스 |
| 민간 민원 LLM 데이터 | LLM 파인튜닝 |

## 🔧 개발 환경 실행 (Docker 없이)

```bash
# 간편 실행 (권장)
./scripts/start-dev.sh

# 또는 수동 실행:

# 1. Backend
cd backend
conda activate claro
uvicorn app.main:app --port 8010 --reload

# 2. Frontend
cd frontend
npm install
npm run dev

# 3. Ollama
ollama serve
```

## 📝 API 엔드포인트

### Backend (8010)

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/classify` | 도메인 분류 |
| POST | `/api/v1/classify/category` | 카테고리 분류 |
| POST | `/api/v1/classify/batch` | 배치 분류 |
| GET | `/api/v1/classify/labels` | 도메인 레이블 목록 |
| GET | `/api/v1/classify/category/labels` | 카테고리 레이블 목록 |
| POST | `/api/v1/search/similar` | 유사 민원 검색 |
| POST | `/api/v1/generate/` | RAG 답변 생성 |
| POST | `/api/v1/compare/` | LLM 비교 |
| POST | `/api/v1/pipeline/process` | SSE 실시간 파이프라인 |
| POST | `/api/v1/feedback/` | 피드백 저장 |
| GET | `/api/v1/stats/` | 통계 조회 |
| GET | `/health` | 헬스 체크 |

## 🗺️ 로드맵

- [x] 도메인 분류 (BERT, 14 클래스)
- [x] 카테고리 분류 (BERT, 63 클래스)
- [x] 소수 클래스 오버샘플링 (RandomOverSampler)
- [x] 유사 민원 검색 (FAISS)
- [x] 답변 초안 생성 (RAG)
- [x] LLM 비교 기능
- [x] Docker 컨테이너화
- [x] LLM 파인튜닝 (Qwen + LoRA)
- [x] GGUF 변환 및 로컬 추론 연동
- [x] SSE 실시간 파이프라인
- [x] 피드백 시스템
- [x] 대시보드 (KPI, 트렌드, 도메인 분포)
- [x] 상담 히스토리
- [x] 도메인 기반 답변 필터링 (후처리)
- [ ] 실시간 상담 지원

## 👤 만든 사람

- **쿠카** - [GitHub](https://github.com/byoneself4023-bit)

---
