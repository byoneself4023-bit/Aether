"""
GGUF 로컬 LLM — llama-cpp-python 기반
NB10에서 생성한 양자화 모델(Q4_K_M 등)을 직접 서빙
"""
from typing import Optional
from loguru import logger
from app.core.config import settings
from app.llm.base import BaseLLM


class GgufLLM(BaseLLM):
    """llama-cpp-python 기반 로컬 GGUF 추론"""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or settings.GGUF_MODEL_PATH
        self.n_ctx = settings.GGUF_N_CTX
        self._llm = None
        self._load_model()

    def _load_model(self):
        from pathlib import Path

        path = Path(self.model_path)
        if not path.exists():
            logger.warning(f"GGUF 모델 파일 없음: {self.model_path}")
            return

        try:
            from llama_cpp import Llama

            self._llm = Llama(
                model_path=str(path),
                n_ctx=self.n_ctx,
                n_threads=4,
                verbose=False,
            )
            logger.info(f"GGUF 모델 로드 완료: {path.name}")
        except ImportError:
            logger.warning("llama-cpp-python 미설치 — pip install llama-cpp-python")
        except Exception as e:
            logger.error(f"GGUF 모델 로드 실패: {e}")

    @property
    def available(self) -> bool:
        return self._llm is not None

    def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        if not self._llm:
            return "GGUF 모델이 로드되지 않았습니다."

        try:
            output = self._llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["### 질문", "\n\n\n"],
                echo=False,
            )
            return output["choices"][0]["text"].strip()
        except Exception as e:
            logger.error(f"GGUF 생성 오류: {e}")
            return f"오류가 발생했습니다: {str(e)}"
