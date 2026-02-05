import httpx
from typing import Optional
from app.core.config import settings
from app.llm.base import BaseLLM


class OllamaLLM(BaseLLM):
    def __init__(self, model_name: Optional[str] = None):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model_name = model_name or settings.OLLAMA_MODEL

    def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        try:
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature,
                    },
                },
                timeout=120.0,
            )
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            print(f"Ollama 오류: {e}")
            return f"오류가 발생했습니다: {str(e)}"
