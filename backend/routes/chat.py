from fastapi import APIRouter
from pydantic import BaseModel
from cockroachdb.memory import search_memories
router = APIRouter(prefix="/chat", tags=["chat"])
class ChatRequest(BaseModel):
    user_id: str
    message: str
@router.post("")
def chat(request: ChatRequest):
    memories = search_memories(
        user_id=request.user_id,
        query_text=request.message,
        limit=5,
    )
    return {
        "user_id": request.user_id,
        "message": request.message,
        "memories": memories,
    }
