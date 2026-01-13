from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import generate, search, compare

app = FastAPI(title="LLM Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router, prefix="/generate", tags=["Generate"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(compare.router, prefix="/compare", tags=["Compare"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "llm-service"}
