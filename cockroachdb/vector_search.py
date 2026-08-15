from sqlalchemy import text

from connection import engine


def search_similar_memories(user_id, embedding, limit=5):
    query = text("""
        SELECT
            id,
            user_id,
            memory_type,
            content,
            metadata,
            created_at,
            embedding <=> :embedding AS distance
        FROM memories
        WHERE user_id = :user_id
          AND embedding IS NOT NULL
        ORDER BY embedding <=> :embedding
        LIMIT :limit
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "user_id": user_id,
                "embedding": embedding,
                "limit": limit,
            },
        )

        return [dict(row) for row in result.mappings().all()]