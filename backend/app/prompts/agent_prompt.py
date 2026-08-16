"""
Dynamic system prompt builder for the CareerMind AI agent.

Constructs a structured, deterministic system prompt from:
  - Career profile
  - Recent conversation history
  - Retrieved memories
  - Current user context
  - Tracked skills, projects, and courses
"""

from __future__ import annotations

from typing import Any, Optional


def build_system_prompt(
    profile: dict[str, Any] | None = None,
    conversation_history: list[dict[str, str]] | None = None,
    memories: str = "",
    user_context: dict[str, Any] | None = None,
    skills: list[dict[str, Any]] | None = None,
    projects: list[dict[str, Any]] | None = None,
    courses: list[dict[str, Any]] | None = None,
) -> str:
    """
    Assemble the full system prompt for the Bedrock Converse call.

    Args:
        profile: Career profile dict (dream_role, experience_level, etc.).
        conversation_history: Recent messages for continuity reference.
        memories: Pre-formatted string of retrieved long-term memories.
        user_context: Ad-hoc context fields supplied by the frontend.
        skills: List of user's tracked skills.
        projects: List of user's tracked projects.
        courses: List of user's enrolled courses.

    Returns:
        A single system-prompt string.
    """
    sections: list[str] = [_PREAMBLE]

    # ── Career Profile ────────────────────────────────────────────────
    if profile:
        sections.append(_format_profile(profile))

    # ── User Context ──────────────────────────────────────────────────
    if user_context:
        sections.append(_format_user_context(user_context))

    # ── Skills ────────────────────────────────────────────────────────
    if skills:
        sections.append(_format_skills(skills))

    # ── Projects ──────────────────────────────────────────────────────
    if projects:
        sections.append(_format_projects(projects))

    # ── Courses ───────────────────────────────────────────────────────
    if courses:
        sections.append(_format_courses(courses))

    # ── Long-term Memories ────────────────────────────────────────────
    if memories and memories != "No relevant memories found.":
        sections.append(
            "## LONG-TERM MEMORIES\n"
            "The following facts have been remembered from previous conversations. "
            "Use them to personalise your response.\n\n"
            f"{memories}"
        )

    # ── Conversation Continuity ───────────────────────────────────────
    if conversation_history:
        sections.append(
            "## CONVERSATION CONTEXT\n"
            f"There are {len(conversation_history)} recent messages in this "
            "conversation.  Maintain continuity and avoid repeating advice "
            "the user has already received."
        )

    sections.append(_REASONING_FRAMEWORK)
    sections.append(_GUIDELINES)
    return "\n\n".join(sections)


# ── Static prompt fragments ──────────────────────────────────────────────

_PREAMBLE = """\
# CareerMind AI — Career Planning Assistant

You are **CareerMind**, an expert AI career advisor.  Your role is to
provide personalised, actionable career guidance based on the user's
profile, goals, and learning history.

You have access to the user's career profile, their long-term persistent
memories, their tracked skills, projects, courses, and their recent
conversation history.  Use all available context to deliver the most
relevant and helpful response."""

_REASONING_FRAMEWORK = """\
## REASONING FRAMEWORK

When responding, follow this chain-of-thought process:

1. **ANALYSE** — Review the user's profile, skills, projects, courses, and memories
2. **IDENTIFY** — Determine skill gaps between current state and target role
3. **PRIORITISE** — Rank recommendations by impact and urgency
4. **RECOMMEND** — Provide specific, actionable advice with concrete next steps
5. **VALIDATE** — Cross-reference suggestions against the user's timeline and experience level

Structure your response with clear headings, bullet points, and numbered steps.
Use bold text for key takeaways and italics for supplementary context."""

_GUIDELINES = """\
## RESPONSE GUIDELINES

1. **Be specific and actionable** — give concrete next steps, not generic advice.
2. **Reference the user's context** — mention their dream role, skills, and timeline when relevant.
3. **Acknowledge progress** — recognise what the user has already achieved.
4. **Be encouraging but honest** — provide realistic timelines and expectations.
5. **Suggest resources** — recommend specific courses, projects, or skills when appropriate.
6. **Stay focused** — keep responses relevant to career planning and professional development.
7. **Be concise** — aim for clear, well-structured responses.
8. **Use memory** — reference what you know from previous conversations to show continuity.
9. **Analyse skill gaps** — when the user asks about their progress, compare their tracked skills against what's needed for their target role.
10. **Provide project ideas** — suggest hands-on projects that practise the skills the user needs."""


def _format_profile(profile: dict[str, Any]) -> str:
    """Build the career-profile section of the system prompt."""
    lines = ["## USER CAREER PROFILE"]
    field_labels = {
        "dream_role": "Dream Role",
        "preferred_role": "Preferred Role",
        "experience_level": "Experience Level",
        "education": "Education",
        "industry": "Industry",
        "timeline": "Timeline",
        "bio": "Bio",
    }
    for key, label in field_labels.items():
        value = profile.get(key, "")
        if value:
            lines.append(f"- **{label}:** {value}")
    return "\n".join(lines) if len(lines) > 1 else ""


def _format_user_context(ctx: dict[str, Any]) -> str:
    """Build an ad-hoc context section."""
    lines = ["## ADDITIONAL USER CONTEXT"]
    for key, value in ctx.items():
        if value:
            label = key.replace("_", " ").title()
            lines.append(f"- **{label}:** {value}")
    return "\n".join(lines) if len(lines) > 1 else ""


def _format_skills(skills: list[dict[str, Any]]) -> str:
    """Build the tracked-skills section."""
    if not skills:
        return ""
    lines = ["## TRACKED SKILLS"]
    lines.append(f"The user has {len(skills)} skills being tracked:\n")
    for s in skills:
        name = s.get("name", "Unknown")
        level = s.get("level", "beginner")
        status = s.get("status", "learning")
        lines.append(f"- **{name}** — Level: {level}, Status: {status}")
    return "\n".join(lines)


def _format_projects(projects: list[dict[str, Any]]) -> str:
    """Build the projects section."""
    if not projects:
        return ""
    lines = ["## TRACKED PROJECTS"]
    lines.append(f"The user has {len(projects)} project(s):\n")
    for p in projects:
        name = p.get("name", "Untitled")
        tech = p.get("technology", "")
        status = p.get("status", "planned")
        desc = p.get("description", "")
        line = f"- **{name}** [{status}]"
        if tech:
            line += f" — Tech: {tech}"
        if desc:
            line += f" — {desc[:80]}"
        lines.append(line)
    return "\n".join(lines)


def _format_courses(courses: list[dict[str, Any]]) -> str:
    """Build the courses section."""
    if not courses:
        return ""
    lines = ["## ENROLLED COURSES"]
    lines.append(f"The user is tracking {len(courses)} course(s):\n")
    for c in courses:
        name = c.get("name", "Untitled")
        provider = c.get("provider", "")
        status = c.get("status", "not_started")
        progress = c.get("progress", 0)
        line = f"- **{name}** [{status}, {int(progress)}% complete]"
        if provider:
            line += f" — Provider: {provider}"
        lines.append(line)
    return "\n".join(lines)
