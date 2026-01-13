from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from app.chains.rag_chain import RAGChain


class WorkflowState(TypedDict):
    query: str
    category: Optional[str]
    similar_complaints: List[dict]
    draft_answer: Optional[str]
    final_answer: Optional[str]


class ComplaintWorkflow:
    """LangGraph 기반 민원 처리 워크플로우"""

    def __init__(self):
        self.rag_chain = RAGChain()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """워크플로우 그래프 구성"""
        workflow = StateGraph(WorkflowState)

        # 노드 추가
        workflow.add_node("classify", self._classify_node)
        workflow.add_node("search_similar", self._search_similar_node)
        workflow.add_node("generate_draft", self._generate_draft_node)
        workflow.add_node("refine_answer", self._refine_answer_node)

        # 엣지 추가
        workflow.set_entry_point("classify")
        workflow.add_edge("classify", "search_similar")
        workflow.add_edge("search_similar", "generate_draft")
        workflow.add_edge("generate_draft", "refine_answer")
        workflow.add_edge("refine_answer", END)

        return workflow.compile()

    def _classify_node(self, state: WorkflowState) -> WorkflowState:
        """민원 분류"""
        # TODO: ML 서비스 호출
        state["category"] = "일반문의"
        return state

    def _search_similar_node(self, state: WorkflowState) -> WorkflowState:
        """유사 민원 검색"""
        from app.vectorstore.faiss_store import FAISSStore
        store = FAISSStore()
        results = store.search(state["query"], top_k=3)
        state["similar_complaints"] = results
        return state

    def _generate_draft_node(self, state: WorkflowState) -> WorkflowState:
        """초안 생성"""
        context = "\n".join([c["content"] for c in state["similar_complaints"]])
        result = self.rag_chain.generate(state["query"], context=context)
        state["draft_answer"] = result["answer"]
        return state

    def _refine_answer_node(self, state: WorkflowState) -> WorkflowState:
        """답변 정제"""
        state["final_answer"] = state["draft_answer"]
        return state

    def run(self, query: str) -> dict:
        """워크플로우 실행"""
        initial_state = WorkflowState(
            query=query,
            category=None,
            similar_complaints=[],
            draft_answer=None,
            final_answer=None
        )
        result = self.graph.invoke(initial_state)
        return result
