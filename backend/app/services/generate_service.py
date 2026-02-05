"""
생성 서비스 — RAG 기반 답변 생성
"""
from typing import Optional
from loguru import logger

from app.resources.registry import registry
from app.utils.answer_cleaner import clean_answer
from app.core.exceptions import GenerationError

PROMPT_TEMPLATE = """당신은 친절하고 전문적인 공공기관 민원 상담 AI입니다.

## 참고 정보
{context}

## 민원 질문
{question}

## 답변 지침
- 참고 정보가 부족하더라도, 일반적인 지식을 활용하여 상세하게 답변하세요
- 반드시 3문장 이상으로 답변하세요
- 먼저 인사와 공감으로 시작하세요
- 구체적인 해결 방법이나 절차를 안내하세요
- 추가 문의처 안내 시 구체적인 전화번호나 URL을 임의로 생성하지 마세요
- 따뜻하고 친절한 말투를 사용하세요

## 답변"""


class GenerateService:
    def _build_context(
        self, query: str, context: Optional[str] = None, domain: Optional[str] = None
    ) -> tuple[str, list[str], str]:
        """RAG 컨텍스트 구성 → (prompt, sources, domain)"""
        similar_docs = registry.vector_store.search(query, top_k=3, domain=domain)

        detected_domain = domain or "해당 기관"
        if context is None:
            context_parts = []
            for doc in similar_docs:
                context_parts.append(
                    f"[{doc['domain']} - {doc['category']}]\n질문: {doc['question']}\n답변: {doc['answer']}"
                )
                if detected_domain == "해당 기관":
                    detected_domain = doc["domain"]
            context = "\n\n".join(context_parts) if context_parts else "참고할 유사 사례가 없습니다."
        else:
            if similar_docs and detected_domain == "해당 기관":
                detected_domain = similar_docs[0].get("domain", "해당 기관")

        sources = [f"{doc['domain']}: {doc['question'][:50]}..." for doc in similar_docs]
        prompt = PROMPT_TEMPLATE.format(context=context, question=query)
        return prompt, sources, detected_domain

    def generate_answer(
        self,
        query: str,
        context: Optional[str] = None,
        domain: Optional[str] = None,
        max_tokens: int = 1024,
    ) -> dict:
        """RAG 기반 답변 생성"""
        try:
            prompt, sources, detected_domain = self._build_context(query, context, domain)
            answer = registry.llm.generate(prompt, max_tokens=max_tokens)
            cleaned = clean_answer(answer, detected_domain)
            return {"query": query, "answer": cleaned, "sources": sources}
        except Exception as e:
            logger.error(f"답변 생성 실패: {e}")
            raise GenerationError(f"답변 생성 중 오류 발생: {str(e)}")
