from connection import engine
from sqlalchemy import text
import json


query = text("""
    SELECT
        id,
        content,
        embedding
    FROM memories
    ORDER BY created_at DESC
    LIMIT 1
""")


with engine.connect() as connection:
    result = connection.execute(query).mappings().first()

    if not result:
        print("No memories found.")
        exit()

    print("Content:", result["content"])

    embedding = result["embedding"]

    print("Embedding type:", type(embedding))

    # CockroachDB may return VECTOR as a string
    if isinstance(embedding, str):
        embedding = json.loads(embedding)

    print("Embedding dimensions:", len(embedding))
    print("First 5 values:", embedding[:5])