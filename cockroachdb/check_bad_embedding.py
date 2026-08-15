from sqlalchemy import text
from connection import engine

query = text("""
    SELECT
        id,
        user_id,
        content,
        embedding
    FROM memories
    WHERE id = 'f8fef79d-a598-46de-a883-ad1c79e13958'
""")

with engine.connect() as connection:
    result = connection.execute(query)

    for row in result:
        print("ID:", row.id)
        print("User ID:", row.user_id)
        print("Content:", row.content)
        print("Embedding:", row.embedding)