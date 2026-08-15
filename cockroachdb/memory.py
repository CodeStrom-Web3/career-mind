import json
from sqlalchemy import text
from sentence_transformers import SentenceTransformer

from .connection import engine

# Load embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")


def store_memory(user_id, memory_type, content, metadata=None):
    # Generate 384-dimensional embedding
    embedding = model.encode(content).tolist()
    embedding = "[" + ",".join(map(str, embedding)) + "]"

    query = text("""
        INSERT INTO memories (
            user_id,
            memory_type,
            content,
            metadata,
            embedding
        )
        VALUES (
            :user_id,
            :memory_type,
            :content,
            :metadata,
            :embedding
        )
        RETURNING id
    """)

    with engine.begin() as connection:
        result = connection.execute(
            query,
            {
                "user_id": user_id,
                "memory_type": memory_type,
                "content": content,
                "metadata": json.dumps(metadata) if metadata else None,
                "embedding": embedding,
            },
        )

        return result.scalar()


def get_memory(memory_id):
    query = text("""
        SELECT
            id,
            user_id,
            memory_type,
            content,
            metadata,
            created_at
        FROM memories
        WHERE id = :memory_id
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {"memory_id": memory_id},
        )

        row = result.mappings().first()

        return dict(row) if row else None


def update_memory(memory_id, content, metadata=None):
    # Generate new embedding whenever content changes
    embedding = model.encode(content).tolist()
    embedding = "[" + ",".join(map(str, embedding)) + "]"

    query = text("""
        UPDATE memories
        SET
            content = :content,
            metadata = :metadata,
            embedding = :embedding,
            updated_at = now()
        WHERE id = :memory_id
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "memory_id": memory_id,
                "content": content,
                "metadata": json.dumps(metadata) if metadata else None,
                "embedding": embedding,
            },
        )


def delete_memory(memory_id):
    query = text("""
        DELETE FROM memories
        WHERE id = :memory_id
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {"memory_id": memory_id},
        )


def get_user_memories(user_id, limit=20):
    query = text("""
        SELECT
            id,
            user_id,
            memory_type,
            content,
            metadata,
            created_at
        FROM memories
        WHERE user_id = :user_id
        ORDER BY created_at DESC
        LIMIT :limit
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "user_id": user_id,
                "limit": limit,
            },
        )

        return [dict(row) for row in result.mappings().all()]

def search_memories(user_id, query_text, limit=5):
    # Generate embedding for the search query
    query_embedding = model.encode(query_text).tolist()

    # Convert embedding to CockroachDB VECTOR format
    query_embedding = "[" + ",".join(map(str, query_embedding)) + "]"

    query = text("""
        SELECT
            id,
            user_id,
            memory_type,
            content,
            metadata,
            created_at,
            embedding <=> CAST(:query_embedding AS VECTOR) AS distance
        FROM memories
        WHERE user_id = :user_id
        ORDER BY distance ASC
        LIMIT :limit
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "user_id": user_id,
                "query_embedding": query_embedding,
                "limit": limit,
            },
        )

        return [dict(row) for row in result.mappings().all()]