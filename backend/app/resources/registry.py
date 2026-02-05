"""
리소스 레지스트리 — ML 모델·벡터스토어·LLM 라이프사이클 관리 (mock mode 지원)
"""
from typing import Optional
from loguru import logger

from app.core.config import settings
from app.core.exceptions import ResourceNotReadyError
from app.models.classifier import (
    DomainClassifier, CategoryClassifier,
    MockDomainClassifier, MockCategoryClassifier,
)


class ResourceRegistry:
    """리소스 라이프사이클 관리 (초기화·헬스체크·셧다운)"""

    def __init__(self):
        self._domain_clf = None
        self._category_clf = None
        self._vector_store = None
        self._ollama = None
        self._gemini = None
        self._gguf = None
        self._mock_mode: dict[str, bool] = {}

    async def startup(self):
        """앱 시작 시 모든 리소스 초기화 (실패 시 mock fallback)"""
        logger.info("리소스 초기화 시작...")

        # Domain Classifier (필수 → mock fallback)
        self._domain_clf = self._safe_load("DomainClassifier", DomainClassifier)
        if self._domain_clf is None:
            logger.warning("DomainClassifier 로드 실패 → mock mode 전환")
            self._domain_clf = MockDomainClassifier()
            self._mock_mode["domain_classifier"] = True
        else:
            self._mock_mode["domain_classifier"] = False

        # Category Classifier (선택 → mock fallback)
        self._category_clf = self._safe_load("CategoryClassifier", CategoryClassifier)
        if self._category_clf is None or not self._category_clf.available:
            logger.warning("CategoryClassifier 로드 실패 → mock mode 전환")
            self._category_clf = MockCategoryClassifier()
            self._mock_mode["category_classifier"] = True
        else:
            self._mock_mode["category_classifier"] = False

        # FAISS Vector Store (mock fallback)
        self._vector_store = self._safe_load_vectorstore()

        # LLMs (경량 — 실패해도 연결 시점에 재시도 가능)
        self._ollama = self._safe_load_llm("ollama")
        self._gemini = self._safe_load_llm("gemini")
        self._gguf = self._safe_load_llm("gguf")

        logger.info(f"LLM 백엔드 설정: {settings.LLM_BACKEND}")

        mode_str = ", ".join(f"{k}={'mock' if v else 'real'}" for k, v in self._mock_mode.items())
        logger.info(f"리소스 초기화 완료 [{mode_str}]")

    async def shutdown(self):
        """그레이스풀 셧다운"""
        logger.info("리소스 정리 중...")
        self._domain_clf = None
        self._category_clf = None
        self._vector_store = None
        self._ollama = None
        self._gemini = None
        self._gguf = None
        logger.info("리소스 정리 완료")

    # ---- 헬스체크 ----
    def health_check(self) -> dict:
        return {
            "domain_classifier": {
                "loaded": self._domain_clf is not None,
                "mock": self._mock_mode.get("domain_classifier", True),
            },
            "category_classifier": {
                "loaded": getattr(self._category_clf, "available", False),
                "mock": self._mock_mode.get("category_classifier", True),
            },
            "faiss_store": {
                "loaded": self._vector_store is not None and getattr(self._vector_store, "index", None) is not None,
                "mock": self._mock_mode.get("faiss_store", True),
            },
            "ollama": {
                "loaded": self._ollama is not None,
                "reachable": self._check_ollama(),
                "mock": self._mock_mode.get("ollama", True),
            },
            "gemini": {
                "loaded": self._gemini is not None,
                "api_key": bool(settings.GOOGLE_API_KEY),
                "mock": self._mock_mode.get("gemini", True),
            },
            "gguf": {
                "loaded": self._gguf is not None and getattr(self._gguf, "available", False),
                "mock": self._mock_mode.get("gguf", True),
            },
            "llm_backend": settings.LLM_BACKEND,
            "database": {
                "loaded": self._check_db(),
            },
        }

    def is_mock(self, resource: str) -> bool:
        return self._mock_mode.get(resource, True)

    @staticmethod
    def _check_db() -> bool:
        from app.db.database import DB_PATH
        return DB_PATH.exists()

    # ---- 프로퍼티 접근자 ----
    @property
    def domain_classifier(self):
        if self._domain_clf is None:
            raise ResourceNotReadyError("DomainClassifier")
        return self._domain_clf

    @property
    def category_classifier(self):
        if self._category_clf is None:
            raise ResourceNotReadyError("CategoryClassifier")
        return self._category_clf

    @property
    def vector_store(self):
        if self._vector_store is None:
            raise ResourceNotReadyError("FAISSStore")
        return self._vector_store

    @property
    def ollama(self):
        if self._ollama is None:
            raise ResourceNotReadyError("OllamaLLM")
        return self._ollama

    @property
    def gemini(self):
        if self._gemini is None:
            raise ResourceNotReadyError("GeminiLLM")
        return self._gemini

    @property
    def gguf(self):
        if self._gguf is None:
            raise ResourceNotReadyError("GgufLLM")
        return self._gguf

    @property
    def llm(self):
        """LLM_BACKEND 설정에 따라 적절한 LLM 반환 (통합 접근자)"""
        backend = settings.LLM_BACKEND
        if backend == "gguf" and self._gguf is not None and getattr(self._gguf, "available", False):
            return self._gguf
        elif backend == "gemini" and self._gemini is not None:
            return self._gemini
        elif self._ollama is not None:
            return self._ollama
        # Fallback chain: ollama → gemini → gguf → mock
        for llm in [self._ollama, self._gemini, self._gguf]:
            if llm is not None:
                return llm
        return _MockLLM("fallback")

    # ---- 내부 헬퍼 ----
    @staticmethod
    def _safe_load(name: str, cls, *args, **kwargs):
        try:
            instance = cls(*args, **kwargs)
            logger.info(f"{name} 로드 완료")
            return instance
        except Exception as e:
            logger.warning(f"{name} 로드 실패: {e}")
            return None

    def _safe_load_vectorstore(self):
        try:
            from app.vectorstore.faiss_store import FAISSStore
            store = FAISSStore()
            if store.index is not None:
                self._mock_mode["faiss_store"] = False
                logger.info("FAISSStore 로드 완료")
                return store
        except Exception as e:
            logger.warning(f"FAISSStore 로드 실패: {e}")

        # Mock vector store
        self._mock_mode["faiss_store"] = True
        logger.warning("FAISSStore → mock mode (검색 시 샘플 결과 반환)")
        return _MockVectorStore()

    def _safe_load_llm(self, kind: str):
        try:
            if kind == "ollama":
                from app.llm.ollama import OllamaLLM
                llm = OllamaLLM()
                self._mock_mode["ollama"] = False
                return llm
            elif kind == "gemini":
                from app.llm.gemini import GeminiLLM
                llm = GeminiLLM()
                self._mock_mode["gemini"] = False
                return llm
            elif kind == "gguf":
                from app.llm.gguf_llm import GgufLLM
                llm = GgufLLM()
                if llm.available:
                    self._mock_mode["gguf"] = False
                    return llm
                else:
                    self._mock_mode["gguf"] = True
                    return llm  # 로드됐지만 모델 파일 없음
        except Exception as e:
            logger.warning(f"{kind} LLM 초기화 실패: {e}")
            self._mock_mode[kind] = True
            return _MockLLM(kind)

    def _check_ollama(self) -> bool:
        if self._ollama is None:
            return False
        try:
            import httpx
            r = httpx.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=3.0)
            return r.status_code == 200
        except Exception:
            return False


class _MockVectorStore:
    """모델/인덱스 없이 샘플 결과 반환"""

    def __init__(self):
        self.index = None  # 인덱스는 None 이지만 search 가능

    def search(self, query: str, top_k: int = 5, domain: str = None) -> list[dict]:
        return [
            {
                "question": f"[Mock] {query}와 유사한 질문입니다",
                "answer": "현재 데모 모드로 실행 중입니다. 실제 검색 결과를 보려면 FAISS 인덱스를 배치하세요.",
                "domain": "일반행정",
                "category": "일반상담",
                "score": round(0.95 - i * 0.05, 2),
            }
            for i in range(min(top_k, 3))
        ]


class _MockLLM:
    """LLM 미연결 시 고정 답변"""

    def __init__(self, name: str):
        self._name = name

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> str:
        return (
            "안녕하세요, 민원 상담 AI Claro입니다.\n\n"
            "현재 데모 모드로 운영 중이며, AI 답변 생성 기능이 비활성 상태입니다. "
            "실제 서비스를 이용하시려면 Ollama 또는 Gemini API 연결이 필요합니다.\n\n"
            "추가 문의사항이 있으시면 담당 부서에 연락 부탁드립니다."
        )


# 글로벌 싱글톤
registry = ResourceRegistry()
