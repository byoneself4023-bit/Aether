"""
비교 서비스 — Ollama vs Gemini 비교
"""
import time
from loguru import logger

from app.resources.registry import registry
from app.utils.answer_cleaner import clean_answer
from app.core.exceptions import GenerationError
from app.services.generate_service import PROMPT_TEMPLATE


class CompareService:
    def compare(self, query: str, max_tokens: int = 512) -> dict:
        """Ollama vs Gemini 비교"""
        try:
            # 컨텍스트 구성
            similar_docs = registry.vector_store.search(query, top_k=3)

            domain = "해당 기관"
            context_parts = []
            for doc in similar_docs:
                context_parts.append(
                    f"[{doc['domain']} - {doc['category']}]\n질문: {doc['question']}\n답변: {doc['answer']}"
                )
                if domain == "해당 기관":
                    domain = doc["domain"]

            context = "\n\n".join(context_parts) if context_parts else "참고할 유사 사례가 없습니다."
            sources = [f"{doc['domain']}: {doc['question'][:50]}..." for doc in similar_docs]
            prompt = PROMPT_TEMPLATE.format(context=context, question=query)

            # Ollama 호출
            ollama_start = time.time()
            ollama_answer = registry.ollama.generate(prompt, max_tokens=max_tokens)
            ollama_time = time.time() - ollama_start

            # Gemini 호출
            gemini_start = time.time()
            gemini_answer = registry.gemini.generate(prompt, max_tokens=max_tokens)
            gemini_time = time.time() - gemini_start

            return {
                "query": query,
                "ollama": {
                    "answer": clean_answer(ollama_answer, domain),
                    "elapsed_time": round(ollama_time, 2),
                    "model_name": "Gemma 2B (로컬)",
                },
                "gemini": {
                    "answer": clean_answer(gemini_answer, domain),
                    "elapsed_time": round(gemini_time, 2),
                    "model_name": "Gemini 2.5 Flash Lite (API)",
                },
                "sources": sources,
            }
        except Exception as e:
            logger.error(f"비교 실패: {e}")
            raise GenerationError(f"LLM 비교 중 오류 발생: {str(e)}")
