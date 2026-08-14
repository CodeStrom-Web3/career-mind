CareerMind AI
AI Career Memory Agent

An AI agent that doesn't just answer career questions — it remembers the user's career journey.

CareerMind AI is an agentic career guidance application with persistent memory. It continuously captures, stores, retrieves, and updates a user's career context to provide increasingly personalized and context-aware guidance.

Unlike a traditional stateless chatbot, CareerMind maintains long-term career memory including goals, skills, courses, projects, learning progress, gaps, preferences, and relevant conversation context.

🚀 The Problem

Students often have to repeatedly provide the same career context to AI assistants:

What skills do they have?
What career are they targeting?
Which courses have they completed?
What projects have they built?
What are they currently learning?
What are their skill gaps?

Without persistent memory, AI assistants tend to provide generic recommendations instead of guidance that evolves with the student.

CareerMind AI addresses this by maintaining a persistent and evolving memory of the user's career journey.

💡 The Solution

CareerMind AI follows an agentic memory cycle:

Remember → Retrieve → Reason → Act → Remember Again

The agent retrieves relevant information from the user's previous interactions, combines it with the current query, reasons using an AI foundation model, generates a personalized response, and updates the memory for future interactions.

🧠 Persistent Career Memory

CareerMind continuously maintains a user's career profile.

Memory	Example
Career Goal	Data Analyst
Skills	Python, SQL
Completed Courses	Power BI
Projects	Sales Dashboard
Learning Progress	SQL modules completed
Gaps & Preferences	Statistics gap, career preferences
Conversation Context	Relevant previous interactions

Memory Lifecycle
        ┌──────────┐
        │  CAPTURE │
        └────┬─────┘
             ↓
        ┌──────────┐
        │  STORE   │
        └────┬─────┘
             ↓
        ┌──────────┐
        │ RETRIEVE │
        └────┬─────┘
             ↓
        ┌──────────┐
        │   USE    │
        └────┬─────┘
             ↓
        ┌──────────┐
        │  UPDATE  │
        └──────────┘

The memory lifecycle is designed to continuously evolve as the user's situation changes.

🏗️ System Architecture
┌───────────────────────┐
│     React / Web UI    │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│   AI Agent            │
│   Python / FastAPI    │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│      MCP Server       │
└───────────┬───────────┘
            │
            ▼
┌────────────────────────────────┐
│          CouchbaseDB           │
│                                │
│  Memories • Embeddings         │
│  Metadata • Vector Index       │
└──────────────┬─────────────────┘
               │
               │ Relevant Context
               ▼
┌───────────────────────┐
│    Amazon Bedrock     │
│   AI Reasoning Layer  │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Context-Aware Response│
└───────────┬───────────┘
            │
            ▼
       Update Memory

The proposed architecture uses a React/Web interface, a Python/FastAPI AI agent, MCP connectivity to CouchbaseDB, Couchbase memory and vector indexing, and Amazon Bedrock for AI reasoning.

🔄 Core Execution Flow
1. User Input
      ↓
2. Retrieve Relevant Memory
      ↓
3. AI Reasoning
      ↓
4. Personalized Response
      ↓
5. Update Memory

For every interaction, relevant memories are retrieved from CouchbaseDB before reasoning, and the new interaction is stored afterward for future use.

🔍 Semantic Memory Retrieval

CareerMind uses vector-based retrieval to find memories that are semantically relevant to the user's current question.

User Question
      ↓
Convert to Vector
      ↓
Vector Index Search
      ↓
Find Similar Memories
      ↓
Retrieve Relevant Context
      ↓
AI Agent

Couchbase's distributed vector indexing enables semantic retrieval of relevant memories rather than relying only on exact keyword matches.

🗄️ Why CouchbaseDB?

CouchbaseDB acts as the central persistent memory layer of CareerMind.

It is used to store:

User memories
Conversation context
Embeddings
Metadata
Vector indexes

The architecture also uses MCP to provide a standardized interface between the AI agent and CouchbaseDB.

Couchbase Technologies

The project integrates Couchbase ecosystem capabilities including:

Cloud Managed MCP Server
Distributed Vector Indexing

The hackathon requires meaningful integration of at least two CouchbaseDB ecosystem tools.

☁️ Why AWS?

AWS provides the AI reasoning and application infrastructure.

Amazon Bedrock

Amazon Bedrock provides access to foundation models used for:

AI reasoning
Response generation
Context-aware recommendations
Agent functionality

The core integration is:

AI Agent
    ↓
Couchbase Memory
    ↓
Amazon Bedrock
    ↓
Personalized Response
🛠️ Technology Stack
Layer	Technology
Frontend	React
Backend / API	FastAPI
AI	Custom AI Agent
Memory	CouchbaseDB
Agent-DB Interface	MCP
Retrieval	Vector Search
AI Reasoning	Amazon Bedrock

These technologies are the stack identified for CareerMind AI in the project concept.

💬 Example User Journey
Interaction 1 — Build Memory

"I know Python and SQL and want to become a Data Analyst."

CareerMind stores:

Goal: Data Analyst
Skills: Python, SQL
Interaction 2 — Update Memory

"I completed a Power BI project."

CareerMind updates the profile:

Goal: Data Analyst
Skills: Python, SQL, Power BI
Interaction 3 — Use Memory

"What should I learn next?"

The agent retrieves the relevant career memory through vector search and uses it during AI reasoning.

Instead of giving a generic learning path, CareerMind can account for the user's existing Python, SQL, and Power BI experience.

📁 Project Structure
career-mind/
│
├── agent/
│   ├── prompts/
│   │   └── system_prompt.txt
│   ├── tools/
│   ├── agent.py
│   └── README.md
│
├── aws/
│   ├── bedrock/
│   ├── deployment/
│   └── README.md
│
├── backend/
│   ├── models/
│   ├── routes/
│   │   └── chat.py
│   ├── services/
│   │   └── bedrock.py
│   └── main.py
│
├── couchbase/
│   ├── queries/
│   │   └── queries.py
│   ├── connection.py
│   ├── memory.py
│   ├── vector_search.py
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   ├── App.jsx
│   ├── package.json
│   └── README.md
│
├── docs/
│   └── integration.md
│
├── tests/
│   ├── test_agent.py
│   ├── test_api.py
│   └── test_memory.py
│
├── .env.example
├── .gitignore
└── README.md
🌿 Git Workflow

The project follows a protected-branch workflow.

Branches
main
│
└── develop
    │
    ├── feature/ai-agent
    ├── feature/aws-backend
    ├── feature/couchbase-memory
    ├── feature/frontend
    └── feature/integration
Development Flow
Feature Branch
      ↓
Commit & Push
      ↓
Pull Request
      ↓
develop
      ↓
Integration & Testing
      ↓
Pull Request
      ↓
main
Rules
No direct pushes to main
No direct pushes to develop
Feature work must happen on feature/* branches
Pull Requests target develop
develop is used for integration and testing
Only stable, tested code moves from develop to main
🧪 Testing & Validation

Testing focuses on:

Agent behavior
Memory storage
Memory retrieval accuracy
Vector search
API integration
End-to-end interaction flow

The hackathon specifically evaluates the quality of memory retrieval and overall agent behavior.

🔐 Security & Configuration

Never commit:

API keys
AWS credentials
Database credentials
Access tokens
Secrets

Use environment variables through a local .env file.

Provide configuration through:

.env.example
🚀 Development Roadmap
01. Setup
      ↓
02. AI Agent
      ↓
03. Memory
      ↓
04. Application
      ↓
05. Testing
      ↓
06. Deployment
      ↓
07. Submission

The hackathon roadmap follows these seven phases from environment setup through final submission.

📦 Hackathon Deliverables

The final project should provide:

Public GitHub Repository
Complete source code
Comprehensive README
Setup instructions
Dependencies and configuration details
System architecture diagram
Functional deployed application
Demo video under 3 minutes
Clear identification of Couchbase and AWS technologies used

🎯 Vision

CareerMind is built around one simple idea:

Don't just build an AI agent that answers questions. Build an AI agent that remembers.

The goal is to transform persistent memory into actionable, personalized career intelligence that becomes more useful as the user's career journey evolves.

CareerMind AI
AI Career Memory Agent
