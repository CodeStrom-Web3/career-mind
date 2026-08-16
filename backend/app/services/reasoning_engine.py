"""
Local Reasoning Engine for CareerMind AI.

Provides intelligent, context-aware career guidance using chain-of-thought
reasoning when Amazon Bedrock is unavailable.  Analyses the user's profile,
skills, projects, courses, and memories to generate multi-section responses.

Reasoning pipeline:
  ANALYZE → IDENTIFY GAPS → PRIORITISE → RECOMMEND → CREATE ACTION ITEMS
"""

from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Any, Optional


# ── Role-specific knowledge base ────────────────────────────────────────────

ROLE_SKILL_MAP: dict[str, dict[str, Any]] = {
    "software engineer": {
        "core": ["Python", "JavaScript", "Data Structures", "Algorithms", "System Design", "Git", "SQL", "REST APIs"],
        "advanced": ["Distributed Systems", "Microservices", "Docker", "Kubernetes", "CI/CD", "Cloud (AWS/GCP/Azure)"],
        "projects": [
            "Build a REST API with authentication and rate limiting",
            "Create a microservices-based e-commerce platform",
            "Implement a real-time chat application with WebSockets",
            "Design and deploy a CI/CD pipeline for a production app",
        ],
        "certifications": ["AWS Solutions Architect", "Google Cloud Professional", "Kubernetes CKAD"],
    },
    "data scientist": {
        "core": ["Python", "Statistics", "Machine Learning", "SQL", "Pandas", "NumPy", "Data Visualization"],
        "advanced": ["Deep Learning", "NLP", "MLOps", "Feature Engineering", "A/B Testing", "TensorFlow/PyTorch"],
        "projects": [
            "Build an end-to-end ML pipeline with model monitoring",
            "Sentiment analysis system on real-time social media data",
            "Recommendation engine with collaborative filtering",
            "Time series forecasting for business KPIs",
        ],
        "certifications": ["AWS ML Specialty", "Google Professional ML Engineer", "TensorFlow Developer"],
    },
    "data analyst": {
        "core": ["SQL", "Excel", "Python", "Data Visualization", "Statistics", "Tableau/Power BI"],
        "advanced": ["ETL Pipelines", "Data Modeling", "A/B Testing", "Looker", "dbt", "Airflow"],
        "projects": [
            "Build an interactive dashboard tracking business KPIs",
            "Automate weekly reporting with Python and SQL",
            "Cohort analysis and customer segmentation project",
            "A/B test analysis and recommendation framework",
        ],
        "certifications": ["Google Data Analytics", "Tableau Desktop Specialist", "Microsoft Power BI"],
    },
    "frontend developer": {
        "core": ["HTML", "CSS", "JavaScript", "React", "TypeScript", "Responsive Design", "Git"],
        "advanced": ["Next.js", "Performance Optimization", "Accessibility (a11y)", "Testing (Jest/Cypress)", "State Management", "GraphQL"],
        "projects": [
            "Build a progressive web app (PWA) with offline support",
            "Create a design system with reusable component library",
            "E-commerce storefront with server-side rendering",
            "Real-time collaborative document editor",
        ],
        "certifications": ["Meta Front-End Developer", "AWS Cloud Practitioner", "Google UX Design"],
    },
    "backend developer": {
        "core": ["Python/Node.js/Java", "SQL", "REST APIs", "Authentication", "Database Design", "Git"],
        "advanced": ["GraphQL", "Message Queues", "Caching (Redis)", "Docker", "Kubernetes", "Observability"],
        "projects": [
            "API gateway with rate limiting and API key management",
            "Event-driven microservices with message broker",
            "Search engine with full-text indexing and ranking",
            "Payment processing system with webhook handling",
        ],
        "certifications": ["AWS Solutions Architect", "MongoDB Developer", "Redis Certified Developer"],
    },
    "devops engineer": {
        "core": ["Linux", "Bash/Python", "Docker", "CI/CD", "Git", "Networking", "Cloud (AWS/GCP)"],
        "advanced": ["Kubernetes", "Terraform", "Ansible", "Monitoring (Prometheus/Grafana)", "Service Mesh", "Security"],
        "projects": [
            "Infrastructure-as-code with Terraform for multi-env deployment",
            "Kubernetes cluster with auto-scaling and monitoring",
            "Automated disaster recovery and backup pipeline",
            "Zero-downtime deployment pipeline with canary releases",
        ],
        "certifications": ["AWS DevOps Professional", "CKA (Kubernetes Admin)", "HashiCorp Terraform Associate"],
    },
    "product manager": {
        "core": ["Product Strategy", "User Research", "Data Analysis", "Roadmap Planning", "Agile/Scrum", "Stakeholder Management"],
        "advanced": ["A/B Testing", "SQL", "Pricing Strategy", "Go-to-Market", "OKRs", "Growth Hacking"],
        "projects": [
            "Define and launch a new feature from discovery to delivery",
            "Build a product metrics dashboard with key KPIs",
            "Run a design sprint and prototype validation",
            "Create a product-led growth strategy document",
        ],
        "certifications": ["Pragmatic Institute PMC", "Certified Scrum Product Owner", "Google Project Management"],
    },
    "ui/ux designer": {
        "core": ["Figma", "User Research", "Wireframing", "Prototyping", "Design Systems", "Interaction Design"],
        "advanced": ["Motion Design", "Accessibility", "Design Tokens", "Front-End Basics (HTML/CSS)", "Analytics", "AR/VR Design"],
        "projects": [
            "Redesign a complex enterprise application for usability",
            "Build a comprehensive design system in Figma",
            "Conduct user research and create personas/journey maps",
            "Design a mobile-first responsive web experience",
        ],
        "certifications": ["Google UX Design", "Nielsen Norman UX Certification", "Interaction Design Foundation"],
    },
}

# Fallback for roles not explicitly mapped
DEFAULT_ROLE = {
    "core": ["Communication", "Problem Solving", "Data Analysis", "Project Management", "Technical Writing"],
    "advanced": ["Leadership", "Strategic Thinking", "Cross-functional Collaboration", "Mentoring"],
    "projects": [
        "Build a portfolio website showcasing your domain expertise",
        "Create a case study documenting a problem you solved",
        "Develop an automation tool for a repetitive workflow",
        "Write a technical blog series on your area of expertise",
    ],
    "certifications": ["Google Project Management", "AWS Cloud Practitioner", "LinkedIn Learning Path"],
}

# ── Experience-level context ────────────────────────────────────────────────

EXPERIENCE_GUIDANCE: dict[str, dict[str, str]] = {
    "beginner": {
        "focus": "building strong fundamentals and completing guided projects",
        "priority": "Learn one thing well before moving to the next. Focus on core skills first.",
        "timeline_advice": "Expect 6-12 months of dedicated effort to be job-ready for entry-level positions.",
    },
    "intermediate": {
        "focus": "deepening expertise, building production-quality projects, and contributing to open-source",
        "priority": "Move beyond tutorials — build end-to-end projects that solve real problems.",
        "timeline_advice": "3-6 months of focused portfolio building can significantly improve your candidacy.",
    },
    "advanced": {
        "focus": "system design, leadership, mentoring, and specializing in high-impact domains",
        "priority": "Position yourself as a domain expert. Write, speak, and contribute at a senior level.",
        "timeline_advice": "Focus on strategic skill additions and thought leadership to reach principal/lead roles.",
    },
    "expert": {
        "focus": "strategic leadership, architecture decisions, and industry influence",
        "priority": "Mentor others, drive architectural decisions, and build your professional brand.",
        "timeline_advice": "Your next career move is about influence and impact, not just technical depth.",
    },
}


class LocalReasoningEngine:
    """
    Chain-of-thought reasoning engine for career guidance.

    When Bedrock is unavailable, this engine analyses the user's complete
    context and generates structured, actionable career advice.
    """

    def reason_about_career(
        self,
        query: str,
        profile: dict[str, Any] | None = None,
        skills: list[dict[str, Any]] | None = None,
        projects: list[dict[str, Any]] | None = None,
        courses: list[dict[str, Any]] | None = None,
        memories: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Execute the full reasoning pipeline and return a structured result.

        Returns a dict with keys: response, reasoning_steps, suggestions, confidence.
        """
        profile = profile or {}
        skills = skills or []
        projects = projects or []
        courses = courses or []
        memories = memories or []

        # ── Step 1: Classify the query intent ────────────────────────
        intent = self._classify_intent(query)

        # ── Step 2: Look up role knowledge ───────────────────────────
        dream_role = (profile.get("dream_role") or profile.get("preferred_role") or "").strip().lower()
        role_knowledge = self._get_role_knowledge(dream_role)

        # ── Step 3: Analyse current state ────────────────────────────
        current_skills = [s.get("name", "") for s in skills if s.get("name")]
        current_projects = [p.get("name", "") for p in projects if p.get("name")]
        current_courses = [c.get("name", "") for c in courses if c.get("name")]
        experience = (profile.get("experience_level") or "beginner").lower()
        exp_guidance = EXPERIENCE_GUIDANCE.get(experience, EXPERIENCE_GUIDANCE["beginner"])

        # ── Step 4: Generate response based on intent ────────────────
        reasoning_steps = 0

        if intent == "skill_gap":
            response, reasoning_steps = self._analyze_skill_gaps(
                query, profile, current_skills, role_knowledge, exp_guidance, memories,
            )
        elif intent == "learning_path":
            response, reasoning_steps = self._suggest_learning_path(
                query, profile, current_skills, current_courses, role_knowledge, exp_guidance, memories,
            )
        elif intent == "project_ideas":
            response, reasoning_steps = self._generate_project_ideas(
                query, profile, current_skills, current_projects, role_knowledge, exp_guidance,
            )
        elif intent == "timeline":
            response, reasoning_steps = self._create_timeline(
                query, profile, current_skills, current_courses, current_projects, role_knowledge, exp_guidance,
            )
        elif intent == "certification":
            response, reasoning_steps = self._recommend_certifications(
                query, profile, current_skills, role_knowledge, exp_guidance,
            )
        elif intent == "career_advice":
            response, reasoning_steps = self._general_career_advice(
                query, profile, current_skills, current_projects, current_courses, role_knowledge, exp_guidance, memories,
            )
        else:
            response, reasoning_steps = self._general_career_advice(
                query, profile, current_skills, current_projects, current_courses, role_knowledge, exp_guidance, memories,
            )

        # ── Step 5: Generate follow-up suggestions ───────────────────
        suggestions = self._generate_suggestions(intent, profile, current_skills, role_knowledge)

        # ── Step 6: Calculate confidence ─────────────────────────────
        confidence = self._calculate_confidence(profile, skills, memories)

        return {
            "response": response,
            "reasoning_steps": reasoning_steps,
            "suggestions": suggestions,
            "confidence": confidence,
        }

    # ── Intent Classification ────────────────────────────────────────────

    def _classify_intent(self, query: str) -> str:
        """Classify the user query into a reasoning intent category."""
        q = query.lower()

        skill_keywords = ["skill", "gap", "learn", "missing", "need to know", "competenc", "proficien"]
        path_keywords = ["path", "roadmap", "plan", "order", "sequence", "curriculum", "what should i learn"]
        project_keywords = ["project", "build", "portfolio", "hands-on", "practical", "create"]
        timeline_keywords = ["timeline", "how long", "months", "weeks", "schedule", "milestone", "when"]
        cert_keywords = ["certif", "credential", "exam", "badge", "accredit"]
        career_keywords = ["career", "job", "interview", "resume", "salary", "switch", "transition", "role"]

        if any(kw in q for kw in skill_keywords):
            return "skill_gap"
        if any(kw in q for kw in path_keywords):
            return "learning_path"
        if any(kw in q for kw in project_keywords):
            return "project_ideas"
        if any(kw in q for kw in timeline_keywords):
            return "timeline"
        if any(kw in q for kw in cert_keywords):
            return "certification"
        if any(kw in q for kw in career_keywords):
            return "career_advice"
        return "general"

    # ── Role Knowledge Lookup ────────────────────────────────────────────

    def _get_role_knowledge(self, dream_role: str) -> dict[str, Any]:
        """Match the user's dream role to the knowledge base."""
        if not dream_role:
            return DEFAULT_ROLE

        # Fuzzy matching
        for role_key, knowledge in ROLE_SKILL_MAP.items():
            if role_key in dream_role or dream_role in role_key:
                return knowledge

        # Partial keyword matching
        for role_key, knowledge in ROLE_SKILL_MAP.items():
            role_words = set(role_key.split())
            query_words = set(dream_role.split())
            if role_words & query_words:
                return knowledge

        return DEFAULT_ROLE

    # ── Skill Gap Analysis ───────────────────────────────────────────────

    def _analyze_skill_gaps(
        self,
        query: str,
        profile: dict[str, Any],
        current_skills: list[str],
        role_knowledge: dict[str, Any],
        exp_guidance: dict[str, str],
        memories: list[dict[str, Any]],
    ) -> tuple[str, int]:
        """Perform detailed skill-gap analysis."""
        dream_role = profile.get("dream_role") or profile.get("preferred_role") or "your target role"
        current_lower = {s.lower() for s in current_skills}

        required_core = role_knowledge.get("core", [])
        required_advanced = role_knowledge.get("advanced", [])

        missing_core = [s for s in required_core if s.lower() not in current_lower]
        missing_advanced = [s for s in required_advanced if s.lower() not in current_lower]
        matched_core = [s for s in required_core if s.lower() in current_lower]
        matched_advanced = [s for s in required_advanced if s.lower() in current_lower]

        total_required = len(required_core) + len(required_advanced)
        total_matched = len(matched_core) + len(matched_advanced)
        coverage_pct = round((total_matched / max(total_required, 1)) * 100)

        # Build memory context
        memory_notes = self._extract_memory_context(memories)

        sections = []
        sections.append(f"## 🔍 Skill Gap Analysis for **{dream_role}**\n")
        sections.append(f"Based on your profile and {len(current_skills)} tracked skills, here's my analysis:\n")

        # Coverage summary
        sections.append(f"### 📊 Coverage Score: **{coverage_pct}%**")
        sections.append(f"You currently match **{total_matched}** out of **{total_required}** recommended skills.\n")

        # Strengths
        if matched_core or matched_advanced:
            sections.append("### ✅ Your Strengths")
            if matched_core:
                sections.append("**Core skills you already have:**")
                for s in matched_core:
                    sections.append(f"  - ✓ {s}")
            if matched_advanced:
                sections.append("**Advanced skills you possess:**")
                for s in matched_advanced:
                    sections.append(f"  - ✓ {s}")
            sections.append("")

        # Gaps
        if missing_core:
            sections.append("### 🎯 Priority Gaps (Core Skills)")
            sections.append("These are essential — focus here first:")
            for i, s in enumerate(missing_core, 1):
                sections.append(f"  {i}. **{s}** — High priority")
            sections.append("")

        if missing_advanced:
            sections.append("### 📈 Growth Opportunities (Advanced Skills)")
            sections.append("Add these as you build confidence:")
            for i, s in enumerate(missing_advanced, 1):
                sections.append(f"  {i}. **{s}**")
            sections.append("")

        # Experience-level advice
        sections.append(f"### 💡 Guidance for Your Level")
        sections.append(f"As someone at the **{profile.get('experience_level', 'beginner')}** level, your priority should be {exp_guidance['focus']}.")
        sections.append(f"\n> {exp_guidance['priority']}\n")

        if memory_notes:
            sections.append(f"### 🧠 From Your Previous Conversations")
            sections.append(memory_notes)

        response = "\n".join(sections)
        reasoning_steps = 5  # classify → lookup → compare → score → recommend
        return response, reasoning_steps

    # ── Learning Path ────────────────────────────────────────────────────

    def _suggest_learning_path(
        self,
        query: str,
        profile: dict[str, Any],
        current_skills: list[str],
        current_courses: list[str],
        role_knowledge: dict[str, Any],
        exp_guidance: dict[str, str],
        memories: list[dict[str, Any]],
    ) -> tuple[str, int]:
        """Generate a structured learning path."""
        dream_role = profile.get("dream_role") or profile.get("preferred_role") or "your target role"
        current_lower = {s.lower() for s in current_skills}
        course_lower = {c.lower() for c in current_courses}

        required_core = role_knowledge.get("core", [])
        required_advanced = role_knowledge.get("advanced", [])
        missing_core = [s for s in required_core if s.lower() not in current_lower]
        missing_advanced = [s for s in required_advanced if s.lower() not in current_lower]

        sections = []
        sections.append(f"## 🗺️ Personalised Learning Roadmap → **{dream_role}**\n")
        sections.append(f"Based on your current {len(current_skills)} skills and {len(current_courses)} courses, here's your optimised path:\n")

        # Phase 1: Foundations
        if missing_core:
            sections.append("### Phase 1: Core Foundations (Weeks 1-8)")
            sections.append("Master these essential skills first:\n")
            for i, skill in enumerate(missing_core[:4], 1):
                weeks = f"Weeks {(i-1)*2+1}-{i*2}"
                sections.append(f"**{weeks}: {skill}**")
                sections.append(f"  - Complete a structured course or tutorial series")
                sections.append(f"  - Build a mini-project applying {skill}")
                sections.append(f"  - Practice with real-world exercises\n")

        # Phase 2: Intermediate
        remaining_core = missing_core[4:]
        if remaining_core or missing_advanced[:2]:
            phase2_skills = remaining_core + missing_advanced[:2]
            sections.append("### Phase 2: Skill Deepening (Weeks 9-16)")
            sections.append("Expand your competencies:\n")
            for i, skill in enumerate(phase2_skills[:4], 1):
                sections.append(f"  {i}. **{skill}** — Build intermediate proficiency")
            sections.append(f"\n  ➡️ Goal: Complete a medium-complexity project combining 2-3 skills\n")

        # Phase 3: Advanced
        if missing_advanced[2:]:
            sections.append("### Phase 3: Advanced Specialisation (Weeks 17-24)")
            sections.append("Differentiate yourself with advanced capabilities:\n")
            for i, skill in enumerate(missing_advanced[2:5], 1):
                sections.append(f"  {i}. **{skill}** — Production-grade proficiency")
            sections.append(f"\n  ➡️ Goal: Build a portfolio-worthy capstone project\n")

        # Certifications
        certs = role_knowledge.get("certifications", [])
        if certs:
            sections.append("### 🏅 Recommended Certifications")
            for cert in certs:
                enrolled = "✓ Already enrolled" if cert.lower() in course_lower else "→ Consider enrolling"
                sections.append(f"  - **{cert}** — {enrolled}")
            sections.append("")

        # Level-specific advice
        sections.append(f"### 💡 Note for Your Level")
        sections.append(f"{exp_guidance['timeline_advice']}\n")

        memory_notes = self._extract_memory_context(memories)
        if memory_notes:
            sections.append(f"### 🧠 Based on Your History")
            sections.append(memory_notes)

        response = "\n".join(sections)
        return response, 6

    # ── Project Ideas ────────────────────────────────────────────────────

    def _generate_project_ideas(
        self,
        query: str,
        profile: dict[str, Any],
        current_skills: list[str],
        current_projects: list[str],
        role_knowledge: dict[str, Any],
        exp_guidance: dict[str, str],
    ) -> tuple[str, int]:
        """Generate role-specific project recommendations."""
        dream_role = profile.get("dream_role") or profile.get("preferred_role") or "your target role"
        suggested_projects = role_knowledge.get("projects", [])
        project_lower = {p.lower() for p in current_projects}

        sections = []
        sections.append(f"## 🛠️ Project Ideas for **{dream_role}**\n")
        sections.append(f"You currently have **{len(current_projects)}** project(s) tracked. Here are targeted recommendations:\n")

        for i, proj in enumerate(suggested_projects, 1):
            already = " _(Similar project in progress)_" if any(
                w in proj.lower() for w in (p.lower() for p in current_projects)
            ) else ""
            sections.append(f"### Project {i}: {proj}{already}")

            # Generate skill tags
            skills_needed = random.sample(
                role_knowledge.get("core", []),
                min(3, len(role_knowledge.get("core", []))),
            )
            skills_str = ", ".join(f"`{s}`" for s in skills_needed)
            sections.append(f"  - **Skills practiced:** {skills_str}")
            sections.append(f"  - **Complexity:** {'Intermediate' if i <= 2 else 'Advanced'}")
            sections.append(f"  - **Estimated duration:** {2 + i} weeks")

            # Check if user has the skills
            matched = [s for s in skills_needed if s.lower() in {sk.lower() for sk in current_skills}]
            if matched:
                sections.append(f"  - **You already know:** {', '.join(matched)}")
            sections.append("")

        # Portfolio advice
        sections.append("### 🎯 Portfolio Strategy")
        sections.append(f"As a **{profile.get('experience_level', 'beginner')}**, {exp_guidance['priority']}")
        sections.append("\n**Pro tip:** Each project should have a clear README, live demo, and documented architecture decisions.\n")

        response = "\n".join(sections)
        return response, 5

    # ── Timeline ─────────────────────────────────────────────────────────

    def _create_timeline(
        self,
        query: str,
        profile: dict[str, Any],
        current_skills: list[str],
        current_courses: list[str],
        current_projects: list[str],
        role_knowledge: dict[str, Any],
        exp_guidance: dict[str, str],
    ) -> tuple[str, int]:
        """Generate a milestone-based career timeline."""
        dream_role = profile.get("dream_role") or profile.get("preferred_role") or "your target role"
        timeline = profile.get("timeline") or "6-12 months"
        current_lower = {s.lower() for s in current_skills}
        required = role_knowledge.get("core", []) + role_knowledge.get("advanced", [])
        missing = [s for s in required if s.lower() not in current_lower]
        coverage = round(((len(required) - len(missing)) / max(len(required), 1)) * 100)

        sections = []
        sections.append(f"## ⏱️ Career Timeline → **{dream_role}**\n")
        sections.append(f"Target timeline: **{timeline}** | Current skill coverage: **{coverage}%**\n")

        # Month-by-month milestones
        sections.append("### 📅 Milestone Roadmap\n")

        month_plan = [
            ("Month 1-2", "Foundation Building", "Master 2-3 core skills with structured learning"),
            ("Month 3-4", "Project Development", "Build your first portfolio project end-to-end"),
            ("Month 5-6", "Skill Deepening", "Add advanced skills and complete a certification"),
            ("Month 7-8", "Portfolio & Networking", "2-3 portfolio projects live, start networking"),
            ("Month 9-10", "Interview Preparation", "Practice system design, coding challenges, and behavioral questions"),
            ("Month 11-12", "Job Applications", "Targeted applications with a polished portfolio"),
        ]

        for month, title, desc in month_plan:
            sections.append(f"**{month}: {title}**")
            sections.append(f"  _{desc}_\n")

        # Current progress assessment
        sections.append("### 📊 Where You Stand Today")
        sections.append(f"  - **Skills tracked:** {len(current_skills)}")
        sections.append(f"  - **Projects in progress:** {len(current_projects)}")
        sections.append(f"  - **Courses enrolled:** {len(current_courses)}")
        sections.append(f"  - **Skills remaining:** {len(missing)}")
        sections.append(f"\n{exp_guidance['timeline_advice']}\n")

        response = "\n".join(sections)
        return response, 6

    # ── Certifications ───────────────────────────────────────────────────

    def _recommend_certifications(
        self,
        query: str,
        profile: dict[str, Any],
        current_skills: list[str],
        role_knowledge: dict[str, Any],
        exp_guidance: dict[str, str],
    ) -> tuple[str, int]:
        """Recommend certifications based on role and current skills."""
        dream_role = profile.get("dream_role") or profile.get("preferred_role") or "your target role"
        certs = role_knowledge.get("certifications", [])

        sections = []
        sections.append(f"## 🏅 Certification Recommendations for **{dream_role}**\n")

        if certs:
            sections.append("### Top Recommended Certifications\n")
            for i, cert in enumerate(certs, 1):
                sections.append(f"**{i}. {cert}**")
                sections.append(f"  - Highly valued for {dream_role} positions")
                sections.append(f"  - Study time: typically 4-8 weeks of focused preparation")
                sections.append(f"  - ROI: Demonstrates verified expertise to employers\n")
        else:
            sections.append("No specific certifications mapped for this role yet, but consider general cloud or project management certifications.\n")

        sections.append("### 💡 Certification Strategy")
        sections.append(f"For a **{profile.get('experience_level', 'beginner')}** level:")
        sections.append(f"  - {exp_guidance['priority']}")
        sections.append(f"\n> Certifications are most valuable when combined with practical project experience.\n")

        response = "\n".join(sections)
        return response, 4

    # ── General Career Advice ────────────────────────────────────────────

    def _general_career_advice(
        self,
        query: str,
        profile: dict[str, Any],
        current_skills: list[str],
        current_projects: list[str],
        current_courses: list[str],
        role_knowledge: dict[str, Any],
        exp_guidance: dict[str, str],
        memories: list[dict[str, Any]],
    ) -> tuple[str, int]:
        """Provide comprehensive, contextual career advice."""
        dream_role = profile.get("dream_role") or profile.get("preferred_role") or "your target role"
        experience = profile.get("experience_level") or "beginner"
        current_lower = {s.lower() for s in current_skills}
        required = role_knowledge.get("core", []) + role_knowledge.get("advanced", [])
        missing = [s for s in required if s.lower() not in current_lower]
        matched = [s for s in required if s.lower() in current_lower]

        sections = []
        sections.append(f"## 🧠 CareerMind Analysis for: **\"{query}\"**\n")

        # Profile context
        if profile.get("dream_role"):
            sections.append(f"**Your Profile:** {experience.title()} level → targeting **{dream_role}**")
            if profile.get("industry"):
                sections.append(f"**Industry:** {profile['industry']}")
            if profile.get("timeline"):
                sections.append(f"**Timeline:** {profile['timeline']}")
            sections.append("")

        # Current state analysis
        sections.append("### 📊 Your Current Position\n")
        if matched:
            sections.append(f"**Skills you have:** {', '.join(matched[:6])}")
        if current_projects:
            sections.append(f"**Active projects:** {', '.join(current_projects[:4])}")
        if current_courses:
            sections.append(f"**Courses in progress:** {', '.join(current_courses[:4])}")
        sections.append("")

        # Strategic recommendations
        sections.append("### 🎯 Strategic Recommendations\n")

        recommendations = []
        if missing:
            top_gaps = missing[:3]
            recommendations.append(
                f"1. **Close your top skill gaps:** Focus on **{', '.join(top_gaps)}** — these are the highest-priority skills for {dream_role} positions."
            )
        if len(current_projects) < 2:
            recommendations.append(
                f"2. **Build portfolio projects:** You need at least 2-3 production-quality projects. Consider: *{role_knowledge.get('projects', ['a relevant project'])[0]}*"
            )
        if len(current_courses) < 1:
            certs = role_knowledge.get("certifications", [])
            if certs:
                recommendations.append(
                    f"3. **Get certified:** Consider **{certs[0]}** to validate your expertise."
                )
        recommendations.append(
            f"4. **Level-appropriate focus:** {exp_guidance['priority']}"
        )

        for rec in recommendations:
            sections.append(rec)
        sections.append("")

        # Next steps
        sections.append("### ⚡ Immediate Next Steps\n")
        sections.append("1. Update your career profile with your latest goals and preferences")
        sections.append("2. Track your current skills so I can provide better gap analysis")
        sections.append("3. Start a focused learning sprint on your highest-priority gap")
        sections.append(f"4. {exp_guidance['timeline_advice']}")
        sections.append("")

        # Memory context
        memory_notes = self._extract_memory_context(memories)
        if memory_notes:
            sections.append("### 🧠 From Our Previous Conversations\n")
            sections.append(memory_notes)

        response = "\n".join(sections)
        return response, 7

    # ── Helper Methods ───────────────────────────────────────────────────

    def _extract_memory_context(self, memories: list[dict[str, Any]]) -> str:
        """Format relevant memories into a context note."""
        if not memories:
            return ""

        lines = []
        for mem in memories[:3]:
            content = mem.get("content", "")
            mem_type = mem.get("memory_type", "general")
            if content:
                lines.append(f"  - _[{mem_type}]_ {content}")

        return "\n".join(lines) if lines else ""

    def _generate_suggestions(
        self,
        intent: str,
        profile: dict[str, Any],
        current_skills: list[str],
        role_knowledge: dict[str, Any],
    ) -> list[str]:
        """Generate contextual follow-up question suggestions."""
        dream_role = profile.get("dream_role") or "my target role"

        suggestion_map: dict[str, list[str]] = {
            "skill_gap": [
                f"Create a learning plan for my top 3 skill gaps",
                f"What projects can help me practice these missing skills?",
                f"How long will it take to close these gaps?",
                f"Which skill should I prioritize first?",
            ],
            "learning_path": [
                f"Suggest projects for each phase of this roadmap",
                f"What certifications should I add to this plan?",
                f"How should I adjust this path for my timeline?",
                f"What free resources cover these topics best?",
            ],
            "project_ideas": [
                f"Help me plan the architecture for Project 1",
                f"What technologies should I use for these projects?",
                f"How do I make these projects stand out in a portfolio?",
                f"Analyze my current skills against these project requirements",
            ],
            "timeline": [
                f"What should I focus on this week specifically?",
                f"How do I stay accountable to this timeline?",
                f"Adjust this timeline for a more aggressive pace",
                f"What milestones should I celebrate along the way?",
            ],
            "certification": [
                f"How should I prepare for the first certification?",
                f"Are there free study resources for these certs?",
                f"Which certification has the best ROI?",
                f"How do I balance cert prep with project work?",
            ],
            "career_advice": [
                f"Analyze the skill gaps between my profile and {dream_role}",
                f"Create a 6-month learning roadmap for me",
                f"Suggest portfolio projects aligned with {dream_role}",
                f"What certifications would strengthen my candidacy?",
            ],
        }

        return suggestion_map.get(intent, suggestion_map["career_advice"])[:4]

    def _calculate_confidence(
        self,
        profile: dict[str, Any],
        skills: list[dict[str, Any]],
        memories: list[dict[str, Any]],
    ) -> float:
        """
        Calculate a confidence score (0.0–1.0) based on the amount of
        user context available for personalised advice.
        """
        score = 0.3  # base confidence

        # Profile completeness
        profile_fields = ["dream_role", "experience_level", "education", "industry", "timeline"]
        filled = sum(1 for f in profile_fields if profile.get(f))
        score += (filled / len(profile_fields)) * 0.3

        # Skills tracked
        if len(skills) >= 5:
            score += 0.15
        elif len(skills) >= 1:
            score += 0.08

        # Memory context
        if len(memories) >= 3:
            score += 0.15
        elif len(memories) >= 1:
            score += 0.08

        # Conversation depth bonus
        score += 0.1

        return min(round(score, 2), 1.0)


# ── Module-level singleton ───────────────────────────────────────────────

_instance: LocalReasoningEngine | None = None


def get_reasoning_engine() -> LocalReasoningEngine:
    """Return a lazily-initialised singleton."""
    global _instance
    if _instance is None:
        _instance = LocalReasoningEngine()
    return _instance
