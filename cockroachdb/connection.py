import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(ENV_FILE)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(f"DATABASE_URL is not set. Looking for: {ENV_FILE}")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "options": "-c application_name=career-mind"
    }
)