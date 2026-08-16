# CareerMind AI Backend

> AI-powered career planning platform with **persistent agentic memory**, semantic retrieval, and Amazon Bedrock integration.

---

## 1. Project Overview

CareerMind is an intelligent career advisor that remembers every user interaction. It uses a **REMEMBER → RETRIEVE → REASON → ACT → REMEMBER AGAIN** lifecycle to provide deeply personalised career guidance that improves over time.

Key capabilities:

- **Persistent Memory** — facts extracted from conversations are stored as vector embeddings in CockroachDB and retrieved semantically in future sessions.
- **Agentic Orchestration** — a 12-step pipeline loads profile, history, and memories before calling the LLM, then extracts and deduplicates new memories after.
- **Vector Similarity Search** — queries are embedded via Amazon Titan and matched against stored memories using cosine similarity with weighted ranking.
- **MCP Tool Integration** — an MCP-compatible `search_user_memory` tool lets external agents query the memory store.

---

## 2. Architecture

```text
React Frontend
      ↓
POST /api/chat
      ↓
FastAPI (Routes → Services → Database/Bedrock)
      ↓
┌──────────────────────────────────────────────┐
│ Agent Service (orchestrator)                 │
│  1. Load Profile                             │
│  2. Load Conversation History                │
│  3. Generate Query Embedding (Titan)         │
│  4. CockroachDB Vector Search                │
│  5. Retrieve Top-K Memories                  │
│  6. Build AI Context (system prompt)         │
│  7. Call Amazon Bedrock (Claude)             │
│  8. Save Conversation                        │
│  9. Extract Persistent Facts (Bedrock)       │
│ 10. Generate Embeddings for New Memories     │
│ 11. Deduplicate Near-Duplicate Memories      │
│ 12. Store in CockroachDB → Return Response   │
└──────────────────────────────────────────────┘
```

---

## 3. Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12+ |
| Framework | FastAPI |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy 2.x (async) |
| Database | CockroachDB (PostgreSQL-compatible) |
| Driver | asyncpg |
| LLM | Amazon Bedrock (Claude 3.5 Sonnet) |
| Embeddings | Amazon Titan Embed Text v2 |
| Auth | JWT + bcrypt |
| Testing | pytest + pytest-asyncio + httpx |
| Containerisation | Docker |

---

## 4. Folder Structure

```text
backend/
├── app/
│   ├── main.py                    # FastAPI entrypoint
│   ├── config/settings.py         # Pydantic Settings
│   ├── api/
│   │   ├── dependencies.py        # JWT auth, DB session
│   │   └── routes/
│   │       ├── auth.py            # Register, login, me
│   │       ├── chat.py            # POST /api/chat
│   │       ├── profile.py         # GET/PUT profile
│   │       ├── memory.py          # CRUD memories
│   │       ├── progress.py        # Skills, projects, courses
│   │       └── health.py          # Health check
│   ├── models/                    # Pydantic schemas
│   ├── services/                  # Business logic
│   │   ├── agent_service.py       # Central orchestrator
│   │   ├── bedrock_service.py     # LLM integration
│   │   ├── embedding_service.py   # Vector embeddings
│   │   ├── memory_service.py      # Memory lifecycle
│   │   ├── retrieval_service.py   # Semantic search
│   │   ├── profile_service.py     # Career profiles
│   │   └── progress_service.py    # Skills/projects/courses
│   ├── db/
│   │   ├── database.py            # Engine & sessions
│   │   ├── models.py              # ORM models
│   │   ├── queries.py             # Centralised queries
│   │   └── migrations/            # SQL schema
│   ├── mcp/                       # MCP tool integration
│   ├── prompts/                   # LLM prompt builders
│   └── utils/                     # Logger, helpers
├── tests/                         # pytest test suite
├── .env / .env.example
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 5. Prerequisites

- Python 3.12+
- CockroachDB (Cloud or local)
- AWS account with Bedrock access (Claude 3.5 Sonnet + Titan Embed v2)
- Docker (optional, for containerised deployment)

---

## 6. CockroachDB Setup

### Local (single-node)

```bash
cockroach start-single-node --insecure --listen-addr=localhost:26257
cockroach sql --insecure -e "CREATE DATABASE careermind;"
```

### CockroachDB Cloud

1. Create a cluster at [cockroachlabs.cloud](https://cockroachlabs.cloud)
2. Create a database named `careermind`
3. Copy the connection string into `DATABASE_URL`

---

## 7. Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```env
DATABASE_URL=postgresql+asyncpg://root:@localhost:26257/careermind?sslmode=disable
SECRET_KEY=your-secure-random-secret
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=           # Optional if using IAM roles
AWS_SECRET_ACCESS_KEY=       # Optional if using IAM roles
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0
EMBEDDING_DIMENSIONS=1024
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
TOP_K_MEMORIES=5
MEMORY_DEDUP_THRESHOLD=0.92
```

---

## 8. Installation

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

---

## 9. Database Migration

Run the initial schema against CockroachDB:

```bash
cockroach sql --url "$DATABASE_URL" < app/db/migrations/001_initial_schema.sql
```

---

## 10. Running Locally

```bash
uvicorn app.main:app --reload --port 8000
```

Visit **http://localhost:8000/docs** for interactive Swagger documentation.

---

## 11. API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/health` | No | Health check |
| `POST` | `/api/auth/register` | No | Register |
| `POST` | `/api/auth/login` | No | Login (JWT) |
| `GET` | `/api/auth/me` | Yes | Current user |
| `GET` | `/api/profile` | Yes | Get profile |
| `PUT` | `/api/profile` | Yes | Update profile |
| `POST` | `/api/chat` | Yes | Chat with AI |
| `GET` | `/api/memory` | Yes | List memories |
| `POST` | `/api/memory` | Yes | Create memory |
| `DELETE` | `/api/memory/{id}` | Yes | Delete memory |
| `GET` | `/api/progress` | Yes | Dashboard |
| `PUT` | `/api/progress` | Yes | Update progress |
| `GET` | `/api/progress/skills` | Yes | List skills |
| `POST` | `/api/progress/skills` | Yes | Add/update skill |
| `GET` | `/api/progress/projects` | Yes | List projects |
| `POST` | `/api/progress/projects` | Yes | Add/update project |
| `GET` | `/api/progress/courses` | Yes | List courses |
| `POST` | `/api/progress/courses` | Yes | Add/update course |

---

## 12. Chat Workflow

```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret123"}'

# 2. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 3. Set profile
curl -X PUT http://localhost:8000/api/profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dream_role": "Data Analyst", "timeline": "6 months", "experience_level": "beginner"}'

# 4. Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What should I learn first to become a data analyst?"}'
```

---

## 13. Agentic Memory Lifecycle

```text
REMEMBER → RETRIEVE → REASON → ACT → REMEMBER AGAIN

1.  Load career profile from CockroachDB
2.  Load recent conversation history
3.  Generate embedding for current user message (Titan)
4.  Perform vector similarity search in CockroachDB
5.  Retrieve top-K relevant memories (weighted ranking)
6.  Build structured AI context (system prompt)
7.  Call Amazon Bedrock (Claude 3.5 Sonnet)
8.  Save user and assistant messages
9.  Extract persistent facts from the exchange
10. Generate embeddings for extracted memories
11. Deduplicate near-duplicate memories (threshold = 0.92)
12. Store new/updated memories in CockroachDB
```

---

## 14. MCP Integration

The backend exposes an MCP-compatible `search_user_memory` tool:

```python
from app.mcp.client import get_mcp_client

client = get_mcp_client()
results = await client.call_tool(
    db=session,
    tool_name="search_user_memory",
    arguments={
        "user_id": "uuid-string",
        "query": "What career does the user want?",
        "limit": 5,
    },
)
```

---

## 15. Running Tests

```bash
pytest tests/ -v --asyncio-mode=auto
```

All tests use mocked DB sessions, Bedrock responses, and embeddings — **no real credentials required**.

---

## 16. Docker Instructions

```bash
# Build
docker build -t careermind-api .

# Run
docker run -p 8000:8000 --env-file .env careermind-api
```

The image uses Python 3.12-slim, runs as a non-root user, and never bakes credentials into the image.

---

## 17. AWS / Bedrock Configuration

1. Enable **Amazon Bedrock** in your AWS account (us-east-1 recommended)
2. Request access to:
   - `anthropic.claude-3-5-sonnet-20241022-v2:0`
   - `amazon.titan-embed-text-v2:0`
3. Option A — set `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` in `.env`
4. Option B — use IAM roles (recommended for EC2/ECS) — leave AWS key fields empty

---

## 18. Troubleshooting

| Issue | Fix |
|-------|-----|
| `Connection refused` on DB | Ensure CockroachDB is running and `DATABASE_URL` is correct |
| `Bedrock API error: AccessDeniedException` | Request model access in the AWS Bedrock console |
| `Embedding dimension mismatch` | Ensure `EMBEDDING_DIMENSIONS` matches the model's output (1024 for Titan v2) |
| `Invalid or expired token` | Re-login to get a fresh JWT |
| Tests fail with import errors | Run `pip install -r requirements.txt` |

---

## 19. Security Notes

- Passwords are hashed with **bcrypt** — never stored in plain text
- JWT tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60)
- AWS credentials are **optional** (IAM roles preferred in production)
- The `.env` file is in `.gitignore` and must **never** be committed
- All queries are **user-scoped** — users cannot access each other's data
- Internal stack traces are **never** exposed to API clients

---

## 20. Deployment

### EC2 / ECS

1. Push the Docker image to ECR
2. Deploy with an IAM role that has Bedrock invoke permissions
3. Set environment variables via Secrets Manager or Parameter Store
4. Use a load balancer with HTTPS termination
5. Point `DATABASE_URL` to your CockroachDB Cloud cluster

### Environment Checklist

- [ ] `SECRET_KEY` is a cryptographically random value
- [ ] `DATABASE_URL` points to production CockroachDB
- [ ] AWS credentials are handled via IAM roles (not env vars)
- [ ] CORS origins are restricted to your frontend domain
- [ ] HTTPS is enforced at the load balancer
