# Claro 프로젝트 정리 가이드

> 마이크로서비스 아키텍처 전환을 위한 파일 정리

---

## 1. 목표 아키텍처

```
Frontend (3010) → Gateway (8080) → Auth Service (8081)
                                 → Core Service (8082) → ML Service (8010)
```

| 서비스 | 기술 | 포트 | 상태 |
|--------|------|------|------|
| auth-service | Spring Boot | 8081 | 새로 생성 |
| core-service | Spring Boot | 8082 | 새로 생성 |
| gateway | Spring Cloud Gateway | 8080 | 새로 생성 |
| backend (ML) | FastAPI | 8010 | 기존 유지 |
| frontend | Next.js | 3010 | 기존 유지 |

---

## 2. 유지할 파일/폴더 (KEEP)

### backend/ (FastAPI ML Service)
```
backend/
├── app/
│   ├── main.py              # FastAPI 진입점
│   ├── api/                  # REST API 라우트
│   ├── services/             # 비즈니스 로직
│   ├── llm/                  # LLM 프로바이더 (Gemini, Ollama)
│   ├── pipeline/             # 파이프라인 오케스트레이션
│   ├── vectorstore/          # 벡터 DB
│   └── ...
├── Dockerfile
└── requirements.txt
```
**역할**: 분류, 검색, 답변 생성 (ML/LLM 담당)

---

### frontend/ (Next.js UI)
```
frontend/
├── src/
│   ├── app/                  # Next.js App Router
│   │   ├── dashboard/        # 대시보드
│   │   ├── history/          # 히스토리
│   │   └── settings/         # 설정
│   ├── components/           # UI 컴포넌트
│   ├── services/             # API 클라이언트
│   ├── hooks/                # Custom Hooks
│   └── types/                # TypeScript 타입
├── Dockerfile
└── package.json
```
**역할**: 사용자 인터페이스

---

### data/ (데이터셋)
```
data/
├── raw/                      # 원본 데이터
└── processed/                # 전처리된 데이터
    ├── train_classification.parquet
    ├── test_classification.parquet
    ├── label_mapping.json
    └── qa_pairs.parquet
```
**역할**: 학습/평가 데이터 저장

---

### models/ (모델 가중치)
```
models/
└── classification/
    └── ml_baseline/
```
**역할**: 학습된 모델 저장 (gitignore)

---

### notebooks/ (연구 노트북)
```
notebooks/
├── 01_data_exploration.ipynb
├── 02_preprocessing.ipynb
├── 03_task_definition.ipynb
├── 04_baseline_ml.ipynb
├── 05_deep_classification.ipynb
├── 06_bm25_retrieval.ipynb
├── 07_sbert_faiss.ipynb
├── 08_rag_pipeline.ipynb
├── 09_lora_finetuning.ipynb
├── 10_gguf_deploy.ipynb
└── 11_results_summary.ipynb
```
**역할**: 연구, 실험, 문서화

---

### 기타 유지 파일
| 파일 | 역할 |
|------|------|
| `docker-compose.yml` | Docker 구성 (업데이트 예정) |
| `.gitignore` | Git 제외 설정 |
| `.env.example` | 환경변수 템플릿 |
| `requirements-eval.txt` | 평가용 의존성 |
| `scripts/evaluate_*.py` | 평가 스크립트 |
| `scripts/start-dev.sh` | 개발 실행 스크립트 |

---

## 3. 삭제할 파일/폴더 (DELETE)

### 구버전 서비스 (이미 삭제됨, git 커밋 필요)

| 폴더 | 이유 |
|------|------|
| `gateway/` | Spring Cloud Gateway로 교체 |
| `llm-service/` | backend/로 통합됨 |
| `ml-service/` | backend/로 통합됨 |
| `configs/` | 각 서비스 내부로 이동 |

---

### 구버전 프론트엔드

| 파일 | 이유 |
|------|------|
| `frontend/src/app/consultation/` | 새 구조로 대체 |
| `frontend/src/app/login/` | Auth 연동 후 새로 작성 |
| `frontend/src/components/ui/*.tsx` | 새 컴포넌트로 대체 |
| `frontend/src/lib/api.ts` | services/로 이동 |
| `frontend/src/lib/utils.ts` | 새 유틸로 대체 |

---

### 구버전 노트북

| 삭제 | 대체됨 |
|------|--------|
| `03_classification_model.ipynb` | → `05_deep_classification.ipynb` |
| `04_embedding_model.ipynb` | → `07_sbert_faiss.ipynb` |
| `05_rag_vectordb.ipynb` | → `08_rag_pipeline.ipynb` |
| `06_llm_finetuning_*.ipynb` | → `09_lora_finetuning.ipynb` |
| `07_convert_gguf.ipynb` | → `10_gguf_deploy.ipynb` |
| `notebooks/mlflow/` | 사용 안 함 |
| `notebooks/scripts/` | 새 스크립트로 대체 |

---

### 기타 삭제

| 파일 | 이유 |
|------|------|
| 루트 `package.json` | frontend/에 별도 존재 |
| `scripts/deploy.sh` | 새 배포 방식 |
| `scripts/setup.sh` | 새 설정 방식 |
| `scripts/download_data.sh` | 사용 안 함 |

---

## 4. 최종 프로젝트 구조

```
Claro/
├── auth-service/          ← 새로 생성 (Spring Boot)
├── core-service/          ← 새로 생성 (Spring Boot)
├── gateway/               ← 새로 생성 (Spring Cloud Gateway)
├── backend/               ← 기존 유지 (FastAPI ML)
├── frontend/              ← 기존 유지 (Next.js)
├── data/                  ← 기존 유지
├── models/                ← 기존 유지
├── notebooks/             ← 기존 유지
├── docs/                  ← 새로 생성 (문서)
├── scripts/               ← 기존 유지
├── docker-compose.yml     ← 업데이트 예정
├── .env.example
├── .gitignore
└── README.md
```

---

## 5. Git 정리 완료 체크리스트

- [x] 구버전 서비스 삭제 커밋
- [x] 새 파일 추가 커밋
- [ ] auth-service 생성
- [ ] core-service 생성
- [ ] gateway 생성
- [ ] docker-compose.yml 업데이트
