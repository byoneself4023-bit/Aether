# local_rag_test.py
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from sentence_transformers import SentenceTransformer

# 경로 설정
BASE_PATH = Path.home() / 'CIVILCOMPLAINT'
MODEL_PATH = BASE_PATH / 'models' / 'embedding'
FAISS_PATH = BASE_PATH / 'data' / 'vectordb' / 'faiss_index'

# 임베딩 모델 로드
class LocalEmbeddings:
    def __init__(self, model_path):
        self.model = SentenceTransformer(str(model_path))
    
    def embed_query(self, text):
        return self.model.encode(text).tolist()
    
    def embed_documents(self, texts):
        return [self.model.encode(t).tolist() for t in texts]
    
    def __call__(self, text):
        return self.embed_query(text)

# 로드
embeddings = LocalEmbeddings(MODEL_PATH)
db = FAISS.load_local(str(FAISS_PATH), embeddings, allow_dangerous_deserialization=True)
print(f"✅ FAISS 로드: {db.index.ntotal:,} vectors")

# Ollama LLM
llm = Ollama(model='gemma2:2b')
print("✅ Ollama 연결 완료")

# RAG 체인
retriever = db.as_retriever(search_kwargs={'k': 3})

template = """당신은 공공기관 민원 상담 AI입니다.
참고 정보를 바탕으로 질문에 답변하세요.

## 참고 정보
{context}

## 질문
{question}

## 답변"""

prompt = ChatPromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join([
        f"[{doc.metadata['domain']}] Q: {doc.metadata['question']}\nA: {doc.metadata['answer']}"
        for doc in docs
    ])

rag_chain = (
    {'context': retriever | format_docs, 'question': RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 테스트
test_questions = [
    "인터넷뱅킹 비밀번호를 5회 틀렸어요",
    "카드를 잃어버렸어요",
    "코로나 검사 어디서 받나요",
    "주민등록등본 발급 방법",
    "택배가 안 와요"
]

for question in test_questions:
    print("\n" + "="*60)
    print(f"Q: {question}")
    print("="*60)
    answer = rag_chain.invoke(question)
    print(f"\nA: {answer}")