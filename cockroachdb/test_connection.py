import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

# Convert SQLAlchemy URL to a psycopg2-compatible URL
DATABASE_URL = DATABASE_URL.replace(
    "cockroachdb+psycopg2://",
    "postgresql://",
    1,
)

DATABASE_URL = DATABASE_URL.replace(
    "cockroachdb://",
    "postgresql://",
    1,
)
print("Testing CockroachDB connection...")

conn = psycopg2.connect(DATABASE_URL)

cursor = conn.cursor()
cursor.execute("SELECT 1")
result = cursor.fetchone()

print("Connection successful!")
print("Database response:", result[0])

cursor.close()
conn.close()