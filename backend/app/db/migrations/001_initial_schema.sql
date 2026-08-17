-- =============================================================================
-- CareerMind AI — Initial CockroachDB Schema
-- =============================================================================
-- Run against CockroachDB (PostgreSQL-compatible):
--   cockroach sql --url "$DATABASE_URL" < 001_initial_schema.sql
-- =============================================================================

-- ── Users ────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email      STRING(255) NOT NULL UNIQUE,
    password_hash STRING(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);

-- ── Career Profiles ──────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS career_profiles (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID NOT NULL UNIQUE REFERENCES users (id) ON DELETE CASCADE,
    dream_role       STRING(255) DEFAULT '',
    preferred_role   STRING(255) DEFAULT '',
    experience_level STRING(50)  DEFAULT '',
    education        STRING(255) DEFAULT '',
    industry         STRING(255) DEFAULT '',
    timeline         STRING(100) DEFAULT '',
    bio              TEXT DEFAULT '',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── Memories ─────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS memories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    memory_type STRING(50) NOT NULL DEFAULT 'general',
    content     TEXT NOT NULL,
    embedding   JSONB,              -- vector stored as JSONB array
    importance  FLOAT8 DEFAULT 0.5,
    source      STRING(100) DEFAULT 'conversation',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_memories_user ON memories (user_id);
CREATE INDEX IF NOT EXISTS ix_memories_user_type ON memories (user_id, memory_type);

-- ── Conversations ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS conversations (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    title      STRING(255) DEFAULT 'New Conversation',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_conversations_user ON conversations (user_id);

-- ── Messages ─────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations (id) ON DELETE CASCADE,
    role            STRING(20) NOT NULL,   -- user | assistant | system
    content         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_messages_conversation ON messages (conversation_id);

-- ── Skills ───────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS skills (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    name       STRING(255) NOT NULL,
    level      STRING(50) DEFAULT 'beginner',
    status     STRING(50) DEFAULT 'learning',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_skills_user ON skills (user_id);

-- ── Projects ─────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS projects (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    name        STRING(255) NOT NULL,
    description TEXT DEFAULT '',
    technology  STRING(255) DEFAULT '',
    status      STRING(50) DEFAULT 'planned',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_projects_user ON projects (user_id);

-- ── Courses ──────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS courses (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    name       STRING(255) NOT NULL,
    provider   STRING(255) DEFAULT '',
    status     STRING(50) DEFAULT 'not_started',
    progress   FLOAT8 DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_courses_user ON courses (user_id);

-- ── Learning Progress ────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS learning_progress (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL UNIQUE REFERENCES users (id) ON DELETE CASCADE,
    streak     INT8 DEFAULT 0,
    hours      FLOAT8 DEFAULT 0.0,
    level      STRING(50) DEFAULT 'beginner',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
