# CockroachDB Memory & MCP Integration

## 1. Overview

The Career-Mind project uses CockroachDB as the persistent memory layer for the AI agent.

This module is responsible for:

* Persisting user memories.
* Generating and storing embeddings.
* Performing semantic/vector-based memory search.
* Retrieving relevant memories for the AI agent.
* Exposing memory retrieval through an MCP server.
* Providing a FastAPI endpoint for application-level integration.
* Providing automated tests for memory and MCP functionality.

The goal is to allow the AI agent to remember relevant information about a user and retrieve that information when required.

---

# 2. Architecture

```text
                         CAREER-MIND
                              │
                              ▼
                    ┌─────────────────┐
                    │    Frontend     │
                    │   React / UI    │
                    └────────┬────────┘
                             │
                             │ HTTP
                             ▼
                    ┌─────────────────┐
                    │     FastAPI     │
                    │   /chat API     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Memory Retrieval│
                    │     Layer       │
                    └────────┬────────┘
                             │
                             ▼
              ┌─────────────────────────────┐
              │        CockroachDB          │
              │                             │
              │  User Memories              │
              │  Metadata                   │
              │  Embeddings                 │
              │  Vector Search              │
              └──────────────┬──────────────┘
                             │
                             ▼
                    Relevant Memories
                             │
                             ▼
                    ┌─────────────────┐
                    │    AI Agent     │
                    └────────┬────────┘
                             │
                             │ MCP
                             ▼
                    ┌─────────────────┐
                    │   MCP Server    │
                    │                 │
                    │ search_user_    │
                    │ memory          │
                    └─────────────────┘
```

---

# 3. Memory Workflow

The complete memory workflow is:

```text
User Information
       │
       ▼
Store Memory
       │
       ▼
Generate Embedding
       │
       ▼
Store Content + Embedding
       │
       ▼
CockroachDB
       │
       │
       │ User asks a question
       ▼
Generate Query Embedding
       │
       ▼
Vector Similarity Search
       │
       ▼
Retrieve Relevant Memories
       │
       ▼
AI Agent / API
       │
       ▼
Context-aware Response
```

---

# 4. What Has Been Implemented

## CockroachDB

Implemented:

* Database connection.
* Memory storage.
* Memory retrieval.
* Embedding generation.
* Vector storage.
* Semantic search.
* Vector similarity search.
* Memory verification utilities.
* Database testing utilities.

Important modules:

```text
cockroachdb/
├── connection.py
├── memory.py
├── embeddings.py
├── vector_search.py
├── semantic_search.py
├── queries/
│   └── queries.py
├── check_schema.py
├── check_memories.py
├── check_bad_embedding.py
├── delete_bad_embedding.py
├── verify_embedding.py
├── test_connection.py
├── test_embedding.py
├── test_memory.py
├── test_retrieval.py
└── test_vector_search.py
```

---

# 5. Agent / MCP Integration

The MCP server provides an interface for the AI agent to access user memories.

Main file:

```text
agent/agent.py
```

Memory tool:

```text
agent/tools/memory_tools.py
```

The MCP server exposes:

```text
search_user_memory
```

The tool accepts:

```text
user_id
query
limit
```

Example:

```python
search_user_memory(
    user_id="user_001",
    query="What career does the user want?",
    limit=5
)
```

The tool performs semantic memory retrieval and returns relevant stored memories.

---

# 6. MCP Workflow

```text
AI Agent
   │
   │ Needs user context
   ▼
search_user_memory
   │
   ├── user_id
   ├── query
   └── limit
   │
   ▼
Memory Search Layer
   │
   ▼
Embedding Generation
   │
   ▼
CockroachDB Vector Search
   │
   ▼
Relevant Memories
   │
   ▼
MCP Response
   │
   ▼
AI Agent
```

This keeps the agent separated from the underlying database implementation.

---

# 7. FastAPI Integration

The memory system is also connected to the FastAPI backend.

Main files:

```text
backend/
├── main.py
├── routes/
│   ├── __init__.py
│   └── chat.py
└── services/
    └── __init__.py
```

The API exposes:

```text
POST /chat
```

Request:

```json
{
  "user_id": "user_001",
  "message": "What career does the user want?"
}
```

The API performs semantic memory search using the user's message.

Example response structure:

```json
{
  "user_id": "user_001",
  "message": "What career does the user want?",
  "memories": [
    {
      "content": "User wants to become a Data Analyst"
    }
  ]
}
```

---

# 8. Running the Project

## Step 1 — Clone the Repository

Clone the repository and switch to the memory branch:

```bash
git clone <repository-url>
cd career-mind
git checkout feature/cockroachdb-memory
```

---

# 9. Environment Configuration

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL=<your-cockroachdb-connection-string>
```

Do not commit `.env` to GitHub.

The project already includes `.env` in `.gitignore`.

Each developer should use their own local environment variables.

---

# 10. Install Dependencies

Make sure Python is installed.

Then install the project's required dependencies:

```bash
pip install -r requirements.txt
```

If a requirements file is not yet available, install the required packages used by the project environment.

Important packages include:

```text
fastapi
uvicorn
psycopg2
python-dotenv
pytest
mcp
```

---

# 11. Verify CockroachDB Connection

Run:

```bash
python cockroachdb/test_connection.py
```

Expected output:

```text
Testing CockroachDB connection...
Connection successful!
Database response: 1
```

If the connection fails, check:

* `.env` exists.
* `DATABASE_URL` is correct.
* CockroachDB cluster is running.
* Network access is available.

---

# 12. Run Memory Tests

Run:

```bash
python -m pytest tests/test_memory.py -v
```

The tests verify:

* Memory storage.
* Memory retrieval.
* Semantic/vector search.

---

# 13. Run MCP Tests

Run:

```bash
python -m pytest tests/test_agent.py -v
```

The tests verify:

* MCP tool registration.
* MCP memory search.
* Memory retrieval through the MCP interface.

---

# 14. Run All Tests

Run:

```bash
python -m pytest tests -v
```

Current implementation status:

```text
4 passed
```

Tests currently cover:

```text
test_mcp_tool_is_registered       PASSED
test_mcp_memory_search             PASSED
test_memory_store_and_retrieve     PASSED
test_memory_vector_search          PASSED
```

---

# 15. Run the FastAPI Backend

From the project root:

```bash
python -m uvicorn backend.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Health check:

```text
GET /health
```

Expected:

```json
{
  "status": "healthy"
}
```

Root endpoint:

```text
GET /
```

Expected:

```json
{
  "status": "ok",
  "service": "career-mind"
}
```

---

# 16. Test the Chat API

Example PowerShell request:

```powershell
$body = @{
    user_id = "user_001"
    message = "What career does the user want?"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/chat" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

The API should return relevant memories.

Example:

```text
User wants to become a Data Analyst
```

This confirms the flow:

```text
HTTP Request
     ↓
FastAPI
     ↓
Memory Search
     ↓
CockroachDB
     ↓
Semantic Retrieval
     ↓
Relevant Memory
     ↓
API Response
```

---

# 17. Folder Structure

Relevant project structure:

```text
career-mind/
│
├── agent/
│   ├── agent.py
│   ├── README.md
│   ├── prompts/
│   │   └── system_prompt.txt
│   └── tools/
│       └── memory_tools.py
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── chat.py
│   └── services/
│       └── __init__.py
│
├── cockroachdb/
│   ├── connection.py
│   ├── memory.py
│   ├── embeddings.py
│   ├── vector_search.py
│   ├── semantic_search.py
│   └── queries/
│       └── queries.py
│
├── tests/
│   ├── test_agent.py
│   ├── test_api.py
│   └── test_memory.py
│
├── frontend/
│   └── ...
│
├── aws/
│   └── README.md
│
├── docs/
│   └── cockroachdb-memory.md
│
├── .env
├── .env.example
├── .gitignore
└── README.md
```

---

# 18. How the Frontend Developer Connects

The frontend should **not connect directly to CockroachDB**.

The recommended flow is:

```text
React Frontend
      │
      │ POST /chat
      ▼
FastAPI Backend
      │
      ▼
Memory Layer
      │
      ▼
CockroachDB
```

Example frontend request:

```javascript
fetch("http://127.0.0.1:8000/chat", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    user_id: "user_001",
    message: userMessage
  })
});
```

The frontend receives the API response and displays the relevant information.

---

# 19. How the Backend Developer Connects

The backend developer can integrate with the existing memory layer instead of creating another memory system.

Python-level integration:

```python
from cockroachdb.memory import search_memories

memories = search_memories(
    user_id=user_id,
    query_text=user_message,
    limit=5,
)
```

This allows the backend to retrieve relevant user memories.

Alternatively, the backend can use:

```text
POST /chat
```

depending on the final project architecture.

---

# 20. How the Agent Developer Connects

The agent can access memory through the MCP tool:

```text
search_user_memory
```

Parameters:

```text
user_id
query
limit
```

Example:

```python
search_user_memory(
    user_id="user_001",
    query="What are the user's career goals?",
    limit=5
)
```

The agent does not need to directly manage database connections.

---

# 21. How the Testing Developer Connects

The testing developer can run the complete test suite:

```bash
python -m pytest tests -v
```

Memory-specific tests:

```bash
python -m pytest tests/test_memory.py -v
```

MCP-specific tests:

```bash
python -m pytest tests/test_agent.py -v
```

Connection test:

```bash
python cockroachdb/test_connection.py
```

API verification can be performed against:

```text
GET  /
GET  /health
POST /chat
```

---

# 22. Responsibilities Between Team Members

The current division of work is:

```text
Member 1 — AI Memory / Infrastructure
    ├── CockroachDB
    ├── Embeddings
    ├── Vector Search
    ├── Semantic Memory
    ├── MCP Server
    └── Initial Backend Integration

Member 2 — Frontend
    └── React UI

Member 3 — Frontend
    └── UI / User Experience / API Integration

Member 4 — Backend
    └── Main application backend and agent orchestration

Member 5 — Testing
    └── Unit / Integration / End-to-End testing
```

The frontend and backend developers should build on top of the existing interfaces rather than modifying the database implementation unnecessarily.

---

# 23. Git Workflow

The memory implementation is currently on:

```text
feature/cockroachdb-memory
```

The changes have been committed and pushed.

Developers should first synchronize their local repository:

```bash
git fetch origin
```

Then they can inspect the branch:

```bash
git checkout feature/cockroachdb-memory
git pull origin feature/cockroachdb-memory
```

For final integration, the team can merge the feature branch into the project's main integration branch after review.

---

# 24. Important Integration Rule

The CockroachDB layer should remain the single source of truth for persistent AI memory.

Avoid creating separate memory databases in:

* Frontend
* Backend
* Agent
* Testing

Instead:

```text
Frontend
    ↓
Backend
    ↓
Agent / MCP
    ↓
CockroachDB Memory
```

This prevents duplicated memory logic and inconsistent user context.

---

# 25. AWS Status

AWS integration is currently **not completed** because AWS access/credentials were not available during this implementation phase.

AWS-related work is intentionally kept separate.

Do not block the CockroachDB memory implementation on AWS.

AWS integration can be added later without redesigning the CockroachDB memory layer.

---

# 26. Troubleshooting

## DATABASE_URL is not set

Check that `.env` exists in the project root:

```text
career-mind/
├── .env
├── backend/
├── agent/
└── cockroachdb/
```

And contains:

```env
DATABASE_URL=<connection-string>
```

---

## CockroachDB connection failed

Verify:

1. CockroachDB cluster is running.
2. Connection string is correct.
3. `.env` is loaded.
4. Internet/network access is available.
5. Required Python packages are installed.

Run:

```bash
python cockroachdb/test_connection.py
```

---

## FastAPI does not start

Run:

```bash
python -m uvicorn backend.main:app --reload
```

Make sure you execute the command from the project root:

```text
E:\career-mind
```

---

## Tests are not discovered

Run:

```bash
python -m pytest tests -v
```

Test files must follow the pytest naming convention:

```text
test_*.py
```

---

# 27. Current Verification Status

The current implementation has been verified successfully.

```text
CockroachDB Connection       ✓
Memory Storage               ✓
Memory Retrieval             ✓
Embedding Generation         ✓
Vector Search                ✓
Semantic Search              ✓
MCP Tool Registration        ✓
MCP Memory Search            ✓
FastAPI Root Endpoint        ✓
FastAPI Health Endpoint      ✓
FastAPI Chat Endpoint        ✓
Automated Tests              ✓
```

Current test result:

```text
4 passed
```

---

# 28. Summary

The CockroachDB memory module provides the persistent memory foundation for Career-Mind.

It enables the system to:

* Store user information.
* Convert memory into embeddings.
* Persist embeddings in CockroachDB.
* Search memories using semantic similarity.
* Retrieve relevant user context.
* Expose memory retrieval through MCP.
* Provide memory access through the FastAPI backend.
* Support future AI-agent workflows.

The other project modules can integrate through the defined API and MCP interfaces without directly depending on the internal database implementation.

The intended architecture is:

```text
              ┌─────────────┐
              │   Frontend  │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │   FastAPI   │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │ AI / Agent  │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │ MCP Memory  │
              └──────┬──────┘
                     │
                     ▼
          ┌─────────────────────┐
          │    CockroachDB      │
          │ Memory + Embeddings │
          │   + Vector Search   │
          └─────────────────────┘
```

This module is designed to be consumed by the rest of the Career-Mind application rather than functioning as a standalone user-facing interface.
