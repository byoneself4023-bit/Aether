"""RAG 파이프라인 - ChromaDB 기반 금융 지식 검색"""

import logging
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings
import google.generativeai as genai

from app.config import get_settings
from app.services.llm import call_llm, LLMError
from app.services.prompt_registry import get_registry

logger = logging.getLogger(__name__)
settings = get_settings()

# 전역 변수
_chroma_client: chromadb.ClientAPI | None = None
_collection: chromadb.Collection | None = None
_initialized: bool = False


# ============================================================
# 임베딩 함수
# ============================================================

def _get_embedding(text: str) -> list[float]:
    """
    Gemini 임베딩 생성

    Args:
        text: 임베딩할 텍스트

    Returns:
        임베딩 벡터 (768차원)
    """
    if not settings.google_api_key:
        raise LLMError("GOOGLE_API_KEY not configured")

    genai.configure(api_key=settings.google_api_key)

    result = genai.embed_content(
        model=settings.embedding_model,
        content=text,
        task_type="retrieval_document",
    )

    return result["embedding"]


def _get_query_embedding(text: str) -> list[float]:
    """
    쿼리용 Gemini 임베딩 생성

    Args:
        text: 쿼리 텍스트

    Returns:
        임베딩 벡터
    """
    if not settings.google_api_key:
        raise LLMError("GOOGLE_API_KEY not configured")

    genai.configure(api_key=settings.google_api_key)

    result = genai.embed_content(
        model=settings.embedding_model,
        content=text,
        task_type="retrieval_query",
    )

    return result["embedding"]


# ============================================================
# ChromaDB 커스텀 임베딩 함수
# ============================================================

class GeminiEmbeddingFunction:
    """ChromaDB용 Gemini 임베딩 함수"""

    def __call__(self, input: list[str]) -> list[list[float]]:
        """문서 임베딩 (배치)"""
        embeddings = []
        for text in input:
            embeddings.append(_get_embedding(text))
        return embeddings


# ============================================================
# 초기화 함수
# ============================================================

def _load_knowledge_base() -> list[dict]:
    """
    knowledge_base 디렉토리에서 문서 로드

    Returns:
        문서 리스트 [{"id": "...", "content": "...", "metadata": {...}}, ...]
    """
    knowledge_dir = Path(__file__).parent.parent / "data" / "knowledge_base"
    documents = []

    if not knowledge_dir.exists():
        logger.warning(f"Knowledge base directory not found: {knowledge_dir}")
        return documents

    for md_file in knowledge_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")

        # 문서를 섹션별로 분할 (## 기준)
        sections = _split_document(content, md_file.stem)
        documents.extend(sections)

    logger.info(f"Loaded {len(documents)} document sections from knowledge base")
    return documents


def _split_document(
    content: str,
    source: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[dict]:
    """
    마크다운 문서를 섹션/문단 기반으로 분할

    1단계: ## 헤더 기준으로 섹션 분할
    2단계: chunk_size보다 긴 섹션은 문단(빈 줄) 기준으로 추가 분할
    3단계: overlap으로 문맥 연결

    Args:
        content: 전체 문서 내용
        source: 문서 소스 이름
        chunk_size: 최대 청크 크기 (None이면 설정값 사용)
        chunk_overlap: 오버랩 크기 (None이면 설정값 사용)

    Returns:
        분할된 섹션 리스트
    """
    if chunk_size is None:
        chunk_size = settings.rag_chunk_size
    if chunk_overlap is None:
        chunk_overlap = settings.rag_chunk_overlap

    # 1단계: ## 헤더 기준 섹션 분할
    raw_sections = []
    current_section = []
    current_title = source

    for line in content.split("\n"):
        if line.startswith("## "):
            if current_section:
                section_content = "\n".join(current_section).strip()
                if len(section_content) > 50:
                    raw_sections.append((current_title, section_content))

            current_title = line.replace("## ", "").strip()
            current_section = [line]
        else:
            current_section.append(line)

    if current_section:
        section_content = "\n".join(current_section).strip()
        if len(section_content) > 50:
            raw_sections.append((current_title, section_content))

    # 2단계: 긴 섹션을 문단 기반으로 추가 분할 (+ overlap)
    chunks = []
    global_idx = 0

    for title, section_text in raw_sections:
        if len(section_text) <= chunk_size:
            chunks.append((title, section_text, global_idx, 0, 1))
            global_idx += 1
        else:
            sub_chunks = _split_by_paragraphs(section_text, chunk_size, chunk_overlap)
            total_sub = len(sub_chunks)
            for sub_idx, sub_text in enumerate(sub_chunks):
                chunks.append((title, sub_text, global_idx, sub_idx, total_sub))
                global_idx += 1

    # 3단계: 최종 문서 리스트 생성
    total_chunks = len(chunks)
    sections = []
    for i, (title, text, idx, sub_idx, sub_total) in enumerate(chunks):
        sections.append({
            "id": f"{source}_{idx}",
            "content": text,
            "metadata": {
                "source": source,
                "title": title,
                "section_idx": idx,
                "chunk_index": i,
                "total_chunks": total_chunks,
            }
        })

    return sections


def _split_by_paragraphs(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    """
    텍스트를 문단(빈 줄) 기준으로 분할.

    Args:
        text: 분할할 텍스트
        chunk_size: 최대 청크 크기
        chunk_overlap: 오버랩 크기

    Returns:
        분할된 텍스트 리스트
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_size = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        para_size = len(para)

        if current_size + para_size > chunk_size and current_chunk:
            chunks.append("\n\n".join(current_chunk))

            # overlap: 마지막 몇 문단을 유지
            overlap_parts = []
            overlap_size = 0
            for p in reversed(current_chunk):
                if overlap_size + len(p) > chunk_overlap:
                    break
                overlap_parts.insert(0, p)
                overlap_size += len(p)

            current_chunk = overlap_parts
            current_size = overlap_size

        current_chunk.append(para)
        current_size += para_size

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks if chunks else [text]


def init_vectorstore(force_reload: bool = False) -> bool:
    """
    ChromaDB 벡터스토어 초기화 + 문서 임베딩

    Args:
        force_reload: True면 기존 데이터 삭제 후 재로드

    Returns:
        초기화 성공 여부
    """
    global _chroma_client, _collection, _initialized

    if _initialized and not force_reload:
        logger.info("Vectorstore already initialized")
        return True

    try:
        # ChromaDB 클라이언트 생성 (로컬 persistent)
        persist_dir = Path(settings.chroma_persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)

        _chroma_client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # 컬렉션 생성 또는 가져오기
        collection_name = "aether_knowledge"

        if force_reload:
            # 기존 컬렉션 삭제
            try:
                _chroma_client.delete_collection(collection_name)
                logger.info(f"Deleted existing collection: {collection_name}")
            except Exception:
                pass

        # 컬렉션 생성/가져오기
        _collection = _chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Aether financial knowledge base"},
        )

        # 문서가 없거나 force_reload면 로드
        existing_count = _collection.count()
        if existing_count == 0 or force_reload:
            documents = _load_knowledge_base()

            if documents:
                # API 키 확인
                if not settings.google_api_key:
                    logger.warning("GOOGLE_API_KEY not set, skipping embedding")
                    _initialized = True
                    return True

                # 임베딩 생성 및 저장
                ids = [doc["id"] for doc in documents]
                contents = [doc["content"] for doc in documents]
                metadatas = [doc["metadata"] for doc in documents]

                # 배치로 임베딩 생성
                logger.info(f"Generating embeddings for {len(documents)} documents...")
                embeddings = []
                for i, content in enumerate(contents):
                    try:
                        emb = _get_embedding(content)
                        embeddings.append(emb)
                        if (i + 1) % 10 == 0:
                            logger.info(f"Embedded {i + 1}/{len(documents)} documents")
                    except Exception as e:
                        logger.error(f"Failed to embed document {i}: {e}")
                        embeddings.append([0.0] * 768)  # 더미 임베딩

                # ChromaDB에 저장
                _collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=contents,
                    metadatas=metadatas,
                )
                logger.info(f"Added {len(documents)} documents to vectorstore")
        else:
            logger.info(f"Using existing vectorstore with {existing_count} documents")

        _initialized = True
        return True

    except Exception as e:
        logger.error(f"Failed to initialize vectorstore: {e}")
        return False


def get_vectorstore_status() -> dict:
    """벡터스토어 상태 확인"""
    global _collection, _initialized

    if not _initialized or _collection is None:
        return {
            "initialized": False,
            "document_count": 0,
        }

    return {
        "initialized": True,
        "document_count": _collection.count(),
        "persist_dir": settings.chroma_persist_dir,
    }


# ============================================================
# 검색 함수
# ============================================================

def query(
    question: str,
    k: int = 3,
    filter_source: str | None = None,
) -> list[dict]:
    """
    유사 문서 검색

    Args:
        question: 검색 질문
        k: 반환할 문서 수
        filter_source: 특정 소스로 필터링 (예: "portfolio_theory")

    Returns:
        유사 문서 리스트 [{
            "id": "...",
            "content": "...",
            "metadata": {...},
            "distance": 0.123
        }, ...]
    """
    global _collection, _initialized

    if not _initialized:
        init_vectorstore()

    if _collection is None:
        raise LLMError("Vectorstore not initialized")

    # 쿼리 임베딩 생성
    query_embedding = _get_query_embedding(question)

    # 필터 조건
    where = None
    if filter_source:
        where = {"source": filter_source}

    # 검색
    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    # 결과 정리
    documents = []
    if results["ids"] and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            documents.append({
                "id": doc_id,
                "content": results["documents"][0][i] if results["documents"] else "",
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else 0,
            })

    logger.info(f"Found {len(documents)} documents for query: {question[:50]}...")
    return documents


def extract_relevant_paragraphs(
    text: str,
    query_words: list[str],
    max_chars: int = 500,
) -> str:
    """
    쿼리 관련 문단만 추출.

    각 문단에 대해 쿼리 단어 overlap 기반 관련성 스코어를 계산하고
    상위 문단을 max_chars 이내로 반환.

    Args:
        text: 전체 문서 텍스트
        query_words: 쿼리에서 추출한 단어 목록
        max_chars: 최대 문자 수

    Returns:
        관련성 높은 문단만 포함된 텍스트
    """
    if not query_words or not text:
        return text[:max_chars]

    paragraphs = text.split("\n\n")
    if not paragraphs:
        return text[:max_chars]

    query_words_lower = {w.lower() for w in query_words if len(w) > 1}

    # 문단별 관련성 스코어 계산
    scored = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        para_lower = para.lower()
        overlap = sum(1 for w in query_words_lower if w in para_lower)
        scored.append((overlap, para))

    # 스코어 높은 순으로 정렬
    scored.sort(key=lambda x: x[0], reverse=True)

    # max_chars 이내로 문단 선택
    selected = []
    total_chars = 0
    for score, para in scored:
        if total_chars + len(para) > max_chars and selected:
            break
        selected.append(para)
        total_chars += len(para)

    return "\n\n".join(selected) if selected else text[:max_chars]


def build_optimized_context(
    documents: list[dict],
    query_text: str,
    max_context_chars: int = 3000,
) -> tuple[str, list[dict]]:
    """
    토큰 제한을 고려한 최적화된 컨텍스트 빌드.

    문서가 길면 쿼리 관련 문단만 추출하여 max_context_chars 이내로 구성.

    Args:
        documents: 검색된 문서 리스트
        query_text: 원본 쿼리
        max_context_chars: 최대 컨텍스트 문자 수

    Returns:
        (컨텍스트 텍스트, 소스 정보 리스트)
    """
    if not documents:
        return "", []

    # 쿼리 단어 추출 (한국어 + 영어)
    import re
    query_words = re.findall(r'[가-힣]+|[a-zA-Z]{2,}', query_text)

    # 문서당 할당 가능한 최대 크기
    per_doc_budget = max_context_chars // len(documents)

    context_parts = []
    sources = []
    total_chars = 0

    for doc in documents:
        content = doc.get("content", "")
        title = doc["metadata"].get("title", "Unknown")

        # 남은 여유 공간
        remaining = max_context_chars - total_chars
        if remaining <= 0:
            break

        # 예산 내로 문서 축약
        budget = min(per_doc_budget, remaining)
        if len(content) > budget:
            content = extract_relevant_paragraphs(content, query_words, max_chars=budget)

        header = f"### {title}"
        part = f"{header}\n{content}"
        context_parts.append(part)
        total_chars += len(part)

        sources.append({
            "title": title,
            "source": doc["metadata"].get("source", "Unknown"),
            "relevance": 1 - doc.get("distance", 0),
        })

    context = "\n\n---\n\n".join(context_parts)
    return context, sources


def query_with_llm(
    question: str,
    k: int = 3,
    include_sources: bool = True,
) -> dict[str, Any]:
    """
    RAG 검색 + LLM 답변 생성

    Args:
        question: 사용자 질문
        k: 참조할 문서 수
        include_sources: 출처 포함 여부

    Returns:
        {
            "answer": "LLM 답변",
            "sources": [...],  # include_sources=True일 때
        }
    """
    # 유사 문서 검색
    relevant_docs = query(question, k=k)

    if not relevant_docs:
        return {
            "answer": "관련 정보를 찾을 수 없습니다. 다른 질문을 시도해주세요.",
            "sources": [],
        }

    # 최적화된 컨텍스트 빌드
    context, sources = build_optimized_context(relevant_docs, question)

    # RAG 프롬프트 생성 (prompt_registry 단일 진입점)
    registry = get_registry()
    prompt = registry.get("rag_user", "1.0").template.format(
        context=context, question=question
    )
    system_prompt = registry.get("rag_system", "1.0").template

    # LLM 호출
    try:
        answer = call_llm(prompt, system_prompt=system_prompt)
    except LLMError as e:
        answer = f"답변 생성 중 오류가 발생했습니다: {e}"

    result = {"answer": answer}
    if include_sources:
        result["sources"] = sources

    return result


# ============================================================
# 문서 관리 함수
# ============================================================

def add_document(
    doc_id: str,
    content: str,
    metadata: dict | None = None,
) -> bool:
    """
    문서 추가

    Args:
        doc_id: 문서 ID
        content: 문서 내용
        metadata: 메타데이터

    Returns:
        성공 여부
    """
    global _collection, _initialized

    if not _initialized:
        init_vectorstore()

    if _collection is None:
        return False

    try:
        embedding = _get_embedding(content)
        _collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata or {}],
        )
        logger.info(f"Added document: {doc_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to add document: {e}")
        return False


def delete_document(doc_id: str) -> bool:
    """
    문서 삭제

    Args:
        doc_id: 문서 ID

    Returns:
        성공 여부
    """
    global _collection

    if _collection is None:
        return False

    try:
        _collection.delete(ids=[doc_id])
        logger.info(f"Deleted document: {doc_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        return False


def list_documents(limit: int = 100) -> list[dict]:
    """
    저장된 문서 목록 조회

    Args:
        limit: 최대 반환 수

    Returns:
        문서 목록
    """
    global _collection

    if _collection is None:
        return []

    try:
        results = _collection.get(
            limit=limit,
            include=["metadatas"],
        )

        documents = []
        for i, doc_id in enumerate(results["ids"]):
            documents.append({
                "id": doc_id,
                "metadata": results["metadatas"][i] if results["metadatas"] else {},
            })

        return documents
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        return []
