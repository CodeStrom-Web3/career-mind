from sqlalchemy import text
from connection import engine

query = text("""
    DELETE FROM memories
    WHERE id = 'f8fef79d-a598-46de-a883-ad1c79e13958'
""")

with engine.begin() as connection:
    result = connection.execute(query)
    print("Deleted rows:", result.rowcount)