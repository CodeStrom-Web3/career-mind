from sqlalchemy import text
from connection import engine

query = text("""
    SELECT id, user_id, content
    FROM memories
    ORDER BY created_at DESC
    LIMIT 10
""")

with engine.connect() as connection:
    result = connection.execute(query)

    for row in result:
        print("ID:", row.id)
        print("User ID:", row.user_id)
        print("Content:", row.content)
        print("-" * 50)