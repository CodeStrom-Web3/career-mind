from connection import engine
from sqlalchemy import text

query = text("""
    SELECT
        column_name,
        data_type,
        udt_name
    FROM information_schema.columns
    WHERE table_name = 'memories'
    ORDER BY ordinal_position
""")

with engine.connect() as connection:
    rows = connection.execute(query).fetchall()

    for row in rows:
        print(row)