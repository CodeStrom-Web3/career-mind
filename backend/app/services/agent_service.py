"""
Agent service — the central orchestrator implementing the agentic memory
lifecycle.

Process:
  1.  Validate user
  2.  Load career profile
  3.  Load conversation history
  4.  Load skills, projects, courses (for enriched reasoning)
  5.  Retrieve relevant memories (embed + vector search)
  6.  Build system prompt
  7.  Call Bedrock (or local reasoning engine)
  8.  Save user message
  9.  Save assistant response
  10. Ask Bedrock to extract persistent facts
  11. Deduplicate memories
  12. Save new memories
  13. Return enriched response with reasoning metadata
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import queries
from app.prompts.agent_prompt import build_system_prompt
from app.prompts.memory_prompt import build_extraction_prompt
from app.services.bedrock_service import get_bedrock_service
from app.services.memory_service import get_memory_service
from app.services.profile_service import get_profile_service
from app.services.reasoning_engine import get_reasoning_engine
from app.services.retrieval_service import get_retrieval_service
from app.utils.helpers import format_memories_for_prompt, truncate
from app.utils.logger import get_logger, Timer

logger = get_logger(__name__)


class AgentService:
    """
    Orchestrates the full chat lifecycle:
    REMEMBER → RETRIEVE → REASON → ACT → REMEMBER AGAIN.
    """

    def __init__(self) -> None:
        self._bedrock = get_bedrock_service()
        self._memory = get_memory_service()
        self._profile = get_profile_service()
        self._retrieval = get_retrieval_service()
        self._reasoning = get_reasoning_engine()

    async def process_chat(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        message: str,
        conversation_id: Optional[uuid.UUID] = None,
        user_context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Execute the complete agentic pipeline for a single user message.

        Returns a dict matching the ``ChatResponse`` schema, now enriched
        with reasoning_steps, suggestions, and confidence.
        """
        with Timer() as t:
            # ── 1. Validate user ──────────────────────────────────────
            user = await queries.get_user_by_id(db, user_id)
            if user is None:
                raise ValueError("User not found")

            # ── 2. Load career profile ────────────────────────────────
            profile_dict = await self._profile.get_profile_dict(db, user_id)

            # Merge in any ad-hoc user_context from the request body
            if user_context:
                profile_dict.update(user_context)

            # ── 3. Load / create conversation ─────────────────────────
            if conversation_id:
                conv = await queries.get_conversation(db, conversation_id, user_id)
                if conv is None:
                    conv = await queries.create_conversation(
                        db, user_id, title=truncate(message, 60),
                    )
            else:
                conv = await queries.create_conversation(
                    db, user_id, title=truncate(message, 60),
                )

            recent_messages = await queries.get_recent_messages(db, conv.id, limit=20)
            history = [
                {"role": msg.role, "content": msg.content}
                for msg in recent_messages
            ]

            # ── 4. Load skills, projects, courses for enriched reasoning ─
            skills_raw = await queries.get_user_skills(db, user_id)
            projects_raw = await queries.get_user_projects(db, user_id)
            courses_raw = await queries.get_user_courses(db, user_id)

            skills_list = [
                {"name": s.name, "level": s.level, "status": s.status}
                for s in skills_raw
            ]
            projects_list = [
                {"name": p.name, "description": p.description, "technology": p.technology, "status": p.status}
                for p in projects_raw
            ]
            courses_list = [
                {"name": c.name, "provider": c.provider, "status": c.status, "progress": c.progress}
                for c in courses_raw
            ]

            # ── 5. Retrieve relevant memories ─────────────────────────
            memories = await self._retrieval.retrieve_relevant_memories(
                db, user_id, message,
            )
            memories_text = format_memories_for_prompt(memories)

            # ── 6. Build system prompt (now with skills/projects/courses) ─
            system_prompt = build_system_prompt(
                profile=profile_dict,
                conversation_history=history,
                memories=memories_text,
                user_context=user_context,
                skills=skills_list,
                projects=projects_list,
                courses=courses_list,
            )

            # ── 7. Call Bedrock ────────────────────────────────────────
            converse_messages = history + [{"role": "user", "content": message}]
            ai_response = await self._bedrock.generate_response(
                system_prompt=system_prompt,
                messages=converse_messages,
            )

            # ── 8. Run local reasoning engine for metadata ────────────
            # This always runs to produce suggestions/confidence, even
            # when Bedrock succeeds.
            reasoning_result = self._reasoning.reason_about_career(
                query=message,
                profile=profile_dict,
                skills=skills_list,
                projects=projects_list,
                courses=courses_list,
                memories=memories,
            )

            # ── 9 & 10. Save messages ──────────────────────────────────
            await queries.add_message(db, conv.id, "user", message)
            await queries.add_message(db, conv.id, "assistant", ai_response)

            # ── 11. Extract persistent facts ───────────────────────────
            extraction_text = (
                f"User: {message}\nAssistant: {ai_response}"
            )
            extraction_prompt = build_extraction_prompt()
            raw_memories = await self._bedrock.extract_memories(
                extraction_text, extraction_prompt,
            )

            # ── 12 & 13. Deduplicate & save memories ─────────────────
            new_memories = await self._memory.process_extracted_memories(
                db, user_id, raw_memories, source="conversation",
            )

            logger.info(
                "Chat processed",
                extra={
                    "service": "agent",
                    "user_id": str(user_id),
                    "conversation_id": str(conv.id),
                    "memories_retrieved": len(memories),
                    "memories_created": len(new_memories),
                    "reasoning_steps": reasoning_result.get("reasoning_steps", 0),
                    "confidence": reasoning_result.get("confidence", 0),
                    "duration_ms": t.elapsed_ms,
                },
            )

            # ── 14. Return enriched response ─────────────────────────
            return {
                "response": ai_response,
                "role": "ai",
                "conversation_id": str(conv.id),
                "memories_used": len(memories),
                "reasoning_steps": reasoning_result.get("reasoning_steps", 0),
                "suggestions": reasoning_result.get("suggestions", []),
                "confidence": reasoning_result.get("confidence", 0.0),
            }


# ── Module-level singleton accessor ───────────────────────────────────────

_instance: AgentService | None = None


def get_agent_service() -> AgentService:
    """Return a lazily-initialised singleton."""
    global _instance
    if _instance is None:
        _instance = AgentService()
    return _instance
