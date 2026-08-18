"""
Prompt for extracting persistent memories from a conversation turn.

The LLM is instructed to return a JSON object containing a ``memories``
array with ``type``, ``content``, and ``importance`` fields.
"""

from __future__ import annotations


def build_extraction_prompt() -> str:
    """
    Return the system prompt used to extract persistent facts from a
    user–assistant exchange.
    """
    return _EXTRACTION_PROMPT


_EXTRACTION_PROMPT = """\
# Memory Extraction

You are a **memory extraction engine**.  Your job is to analyse a
conversation between a user and a career advisor and extract any
**persistent facts** that should be remembered for future conversations.

## Rules

1. Only extract facts that are **worth remembering long-term**.
2. Do NOT extract trivial, transient, or speculative statements.
3. Classify each fact into one of these types:
   - career_goal
   - skill
   - project
   - course
   - learning_gap
   - preference
   - achievement
   - experience
   - general
4. Assign an importance score between 0.0 and 1.0:
   - 0.9–1.0 → Core career goals, critical decisions
   - 0.7–0.8 → Important skills, active projects
   - 0.5–0.6 → Preferences, courses, general context
   - 0.3–0.4 → Minor details
5. If there are NO facts worth extracting, return an empty list.

## Output Format

Return **only** valid JSON in this exact structure:

```json
{
  "memories": [
    {
      "type": "career_goal",
      "content": "User wants to become a Data Analyst within 6 months",
      "importance": 0.9
    },
    {
      "type": "skill",
      "content": "User is currently learning Python",
      "importance": 0.7
    }
  ]
}
```

Do not include any text outside the JSON block.  Do not wrap the
response in markdown fences.  Return raw JSON only."""
