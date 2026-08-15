from cockroachdb.memory import search_memories


def search_memory(user_id: str, query: str, limit: int = 5) -> list[dict]:
    """Search a user's memories using semantic vector similarity."""
    return search_memories(
        user_id=user_id,
        query_text=query,
        limit=limit,
    )