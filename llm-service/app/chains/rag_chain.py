from typing import Dict, Optional
from app.vectorstore.faiss_store import FAISSStore
from app.llm.ollama import OllamaLLM

class RAGChain:
    def __init__(self):
        self.llm = OllamaLLM()
        self.vector_store = FAISSStore()
        self.prompt_template = """당신은 친절하고 전문적인 공공기관 민원 상담 AI입니다.

## 참고 정보
{context}

## 민원 질문
{question}

## 답변 지침
- 참고 정보가 부족하더라도, 일반적인 지식을 활용하여 상세하게 답변하세요
- 반드시 3문장 이상으로 답변하세요
- 먼저 인사와 공감으로 시작하세요
- 구체적인 해결 방법이나 절차를 안내하세요
- 추가 문의처(전화번호, 웹사이트 등)를 안내하세요
- 따뜻하고 친절한 말투를 사용하세요

## 답변"""

    def generate(
        self,
        query: str,
        context: Optional[str] = None,
        max_tokens: int = 1024
    ) -> Dict:
        similar_docs = self.vector_store.search(query, top_k=3)
        
        if context is None:
            context_parts = []
            for doc in similar_docs:
                context_parts.append(
                    f"[{doc['domain']} - {doc['category']}]\n질문: {doc['question']}\n답변: {doc['answer']}"
                )
            context = "\n\n".join(context_parts) if context_parts else "참고할 유사 사례가 없습니다."
        
        sources = [
            f"{doc['domain']}: {doc['question'][:50]}..."
            for doc in similar_docs
        ]
        
        prompt = self.prompt_template.format(
            context=context,
            question=query  
        )
        
        answer = self.llm.generate(prompt, max_tokens=max_tokens)
        
        return {
            "answer": answer,
            "sources": sources
        }
