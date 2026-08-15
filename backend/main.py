from fastapi import FastAPI
from backend.routes.chat import router as chat_router
app = FastAPI(
    title="Career Mind API",
    version="1.0.0",
)
app.include_router(chat_router)
@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "career-mind",
    }
@app.get("/health")
def health():
    return {
        "status": "healthy",
    }
