# 🧠 CareerMind AI — Autonomous Career Planning Platform

> **Production-grade, end-to-end full-stack AI career operating system** featuring a modern React frontend, FastAPI backend, CockroachDB persistent AI memory with vector similarity search, Amazon Bedrock (Claude 3.5 Sonnet / Haiku), Amazon Titan Embeddings, and MCP tool integrations.

---

## 🏛️ System Architecture

```text
                         CAREERMIND AI
                              │
                   ┌──────────▼──────────┐
                   │    React Frontend   │  (Vite + React 19 + Lucide Icons)
                   │                     │
                   │ • Login / Register  │
                   │ • Dashboard         │
                   │ • AI Chat (Agent)   │
                   │ • Career Profile    │
                   │ • Memory Vault      │
                   │ • Skill Tracker     │
                   │ • Portfolio Builder │
                   │ • Courses & Certs   │
                   │ • Growth Progress   │
                   └──────────┬──────────┘
                              │ REST / JSON (Bearer JWT)
                   ┌──────────▼──────────┐
                   │   FastAPI Backend   │  (Python 3.12+ / SQLAlchemy 2.0 async)
                   │                     │
                   │ • /api/auth         │
                   │ • /api/chat         │
                   │ • /api/profile      │
                   │ • /api/memory       │
                   │ • /api/progress     │
                   │ • /api/health       │
                   └──────────┬──────────┘
                              │
                     ┌────────┴─────────┐
                     │                  │
                     ▼                  ▼
              ┌──────────────┐   ┌───────────────┐
              │ CockroachDB  │   │ Amazon        │
              │              │   │ Bedrock       │
              │ • Users      │   │ • Claude 3.5  │
              │ • Profiles   │   │ • Titan Vector│
              │ • Memories   │   │   (1024-dim)  │
              │ • Vectors    │   └───────────────┘
              │ • Chats      │
              │ • Skills     │
              │ • Projects   │
              │ • Courses    │
              │ • Progress   │
              └──────────────┘
                      ▲
                      │
                 MCP Protocol
                      │
              AI Agent Tools Layer
```

---

## 🔁 Agent Memory & Reasoning Lifecycle

CareerMind AI adheres to an autonomous multi-stage cognitive cycle:

```text
1. REMEMBER  ──► User prompt received & converted to 1024-d Titan Vector
2. RETRIEVE  ──► Semantic search in CockroachDB for relevant goals, skills, gaps
3. REASON    ──► Bedrock Claude reasons with profile context, chat history & memory
4. ACT       ──► Agent crafts personalized response, roadmap & recommendations
5. STORE     ──► Automated background memory extraction & deduplicated vector storage
```

---

## 📁 Repository Structure

```text
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── dependencies.py
│   │   │   └── routes/
│   │   │       ├── auth.py
│   │   │       ├── chat.py
│   │   │       ├── health.py
│   │   │       ├── memory.py
│   │   │       ├── profile.py
│   │   │       └── progress.py
│   │   ├── config/
│   │   │   └── settings.py
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   ├── models.py
│   │   │   ├── queries.py
│   │   │   └── migrations/
│   │   │       └── 001_initial_schema.sql
│   │   ├── mcp/
│   │   │   ├── client.py
│   │   │   └── tools.py
│   │   ├── models/
│   │   │   ├── chat.py
│   │   │   ├── conversation.py
│   │   │   ├── memory.py
│   │   │   ├── profile.py
│   │   │   └── user.py
│   │   ├── prompts/
│   │   │   ├── agent_prompt.py
│   │   │   └── memory_prompt.py
│   │   ├── services/
│   │   │   ├── agent_service.py
│   │   │   ├── bedrock_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── memory_service.py
│   │   │   ├── profile_service.py
│   │   │   ├── progress_service.py
│   │   │   └── retrieval_service.py
│   │   ├── utils/
│   │   │   ├── helpers.py
│   │   │   └── logger.py
│   │   └── main.py
│   ├── tests/
│   │   ├── test_chat.py
│   │   ├── test_memory.py
│   │   ├── test_profile.py
│   │   └── test_retrieval.py
│   ├── .env.example
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.js
│   │   │   ├── auth.js
│   │   │   ├── chat.js
│   │   │   ├── profile.js
│   │   │   ├── memory.js
│   │   │   ├── progress.js
│   │   │   ├── health.js
│   │   │   └── index.js
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   └── ProtectedRoute.jsx
│   │   │   └── layout/
│   │   │       ├── Layout.jsx
│   │   │       ├── Navbar.jsx
│   │   │       └── Sidebar.jsx
│   │   ├── context/
│   │   │   ├── AuthContext.jsx
│   │   │   └── HealthContext.jsx
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── ChatPage.jsx
│   │   │   ├── ProfilePage.jsx
│   │   │   ├── MemoryPage.jsx
│   │   │   ├── SkillsPage.jsx
│   │   │   ├── ProjectsPage.jsx
│   │   │   ├── CoursesPage.jsx
│   │   │   └── ProgressPage.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── .env.example
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- **Python 3.12+**
- **Node.js 18+ & npm**
- **CockroachDB Cloud** or local CockroachDB instance
- **AWS Credentials** with Amazon Bedrock access

---

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

#### Backend `.env` Configuration:
```env
DATABASE_URL=postgresql+asyncpg://<username>:<password>@<host>:26257/<database>?sslmode=require
SECRET_KEY=your-super-secure-jwt-secret-key-32-chars-min
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0
EMBEDDING_DIMENSIONS=1024
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
TOP_K_MEMORIES=5
MEMORY_DEDUP_THRESHOLD=0.92
```

#### Apply Database Schema Migration:
```bash
# Run initial CockroachDB schema creation
# (or execute backend/app/db/migrations/001_initial_schema.sql in CockroachDB SQL client)
```

#### Start FastAPI Server:
```bash
uvicorn app.main:app --reload --port 8000
```
API Documentation will be accessible at: `http://localhost:8000/docs`

---

### 3. Frontend Setup

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env

# Start Vite dev server
npm run dev
```

The application UI will open at: `http://localhost:5173`

---

## 🌐 API Contract Reference

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register` | Register new user account | ❌ |
| `POST` | `/api/auth/login` | Login and receive Bearer JWT | ❌ |
| `GET` | `/api/auth/me` | Fetch authenticated user data | ✅ |
| `POST` | `/api/chat` | AI chat with memory retrieval | ✅ |
| `GET` | `/api/profile` | Retrieve career profile | ✅ |
| `PUT` | `/api/profile` | Update target role, timeline, industry | ✅ |
| `GET` | `/api/memory` | List semantic vector memories | ✅ |
| `POST` | `/api/memory` | Manually store memory vector | ✅ |
| `DELETE` | `/api/memory/{id}` | Delete memory from CockroachDB | ✅ |
| `GET` | `/api/progress` | Aggregated dashboard metrics | ✅ |
| `PUT` | `/api/progress` | Update streak, hours, mastery level | ✅ |
| `GET` | `/api/progress/skills` | List tracked skills | ✅ |
| `POST` | `/api/progress/skills` | Add or update skill | ✅ |
| `GET` | `/api/progress/projects` | List portfolio projects | ✅ |
| `POST` | `/api/progress/projects` | Add or update project | ✅ |
| `GET` | `/api/progress/courses` | List learning courses | ✅ |
| `POST` | `/api/progress/courses` | Add or update course | ✅ |
| `GET` | `/api/health` | System and DB health status | ❌ |

---

## 🧪 Automated Testing

To run the automated backend test suite:

```bash
cd backend
pytest tests/ -v --asyncio-mode=auto
```

To run frontend production build validation:

```bash
cd frontend
npm run build
```

---

## 🐳 Docker Deployment

To build and run the backend container:

```bash
cd backend
docker build -t careermind-api .
docker run -p 8000:8000 --env-file .env careermind-api
```

---

## 🔒 Security & Data Isolation

- **User Scoping:** Every database query and vector retrieval operation is strictly filtered by the authenticated user's `user_id`.
- **JWT Protection:** State is securely authenticated via Bearer tokens stored in browser memory/local storage and validated on every API call.
- **Zero Raw Secrets:** Database credentials and AWS keys reside exclusively in backend environment variables.
- **CORS Protection:** Configured to permit explicit frontend dev & production origins.
career mind
