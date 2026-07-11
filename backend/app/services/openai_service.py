import json
import logging
from typing import Any

from openai import AsyncOpenAI
from pydantic import ValidationError

from app.core.config import Settings
from app.schemas.analysis import AIOverview
from app.schemas.chat import RepositoryChatResponse, SourceReference

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def generate_overview(self, facts: dict[str, Any]) -> AIOverview:
        if not self.client:
            return self._fallback_overview(facts)

        prompt = {
            "instruction": "Return grounded JSON only. Use only the repository facts supplied. Do not invent files or behavior.",
            "schema": {
                "summary": "string",
                "purpose": "string",
                "architecture": "string",
                "technologies": ["string"],
                "strengths": ["string"],
                "risks": ["string"],
                "recommendations": ["string"],
                "onboarding_steps": ["string"],
            },
            "facts": facts,
        }
        for attempt in range(2):
            try:
                response = await self.client.chat.completions.create(
                    model=self.settings.openai_model,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": "You generate concise, grounded repository intelligence for engineers."},
                        {"role": "user", "content": json.dumps(prompt, default=str)[:12000]},
                    ],
                    temperature=0.2,
                )
                content = response.choices[0].message.content or "{}"
                return AIOverview.model_validate_json(content)
            except (ValidationError, json.JSONDecodeError, Exception) as exc:
                logger.warning("AI overview generation failed on attempt %s: %s", attempt + 1, exc)
        return self._fallback_overview(facts)

    async def answer_question(
        self,
        question: str,
        repository_label: str,
        metrics: dict[str, Any],
        chunks: list[dict[str, Any]],
        session_id: int,
    ) -> RepositoryChatResponse:
        sources = [
            SourceReference(path=chunk["path"], start_line=chunk["start_line"], end_line=chunk["end_line"])
            for chunk in chunks
        ]
        if not chunks:
            return RepositoryChatResponse(
                answer="I do not have enough indexed repository context to answer that question reliably.",
                sources=[],
                confidence="low",
                session_id=session_id,
            )
        if not self.client:
            top = chunks[0]
            return RepositoryChatResponse(
                answer=(
                    f"Based on the indexed context for {repository_label}, the most relevant material is in "
                    f"{top['path']} lines {top['start_line']}-{top['end_line']}. "
                    "Configure OPENAI_API_KEY for a richer natural-language answer grounded in these sources."
                ),
                sources=sources[:3],
                confidence="medium",
                session_id=session_id,
            )

        payload = {
            "repository": repository_label,
            "question": question,
            "metrics": metrics,
            "context_chunks": chunks,
            "response_schema": {"answer": "string", "sources": [{"path": "string", "start_line": 1, "end_line": 2}], "confidence": "high|medium|low"},
        }
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.openai_model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Answer only from the supplied repository context. Do not invent files, dependencies, or behavior. "
                            "Say when there is insufficient information. Reference source paths and distinguish metrics from interpretation."
                        ),
                    },
                    {"role": "user", "content": json.dumps(payload, default=str)[:14000]},
                ],
                temperature=0.1,
            )
            content = response.choices[0].message.content or "{}"
            parsed = RepositoryChatResponse.model_validate_json(content)
            parsed.session_id = session_id
            return parsed
        except Exception as exc:
            logger.warning("Repository chat generation failed: %s", exc)
            return RepositoryChatResponse(
                answer="I could not generate an AI answer right now, but these sources are the most relevant retrieved context.",
                sources=sources[:3],
                confidence="low",
                session_id=session_id,
            )

    def _fallback_overview(self, facts: dict[str, Any]) -> AIOverview:
        repo = facts.get("repository", {})
        metrics = facts.get("metrics", {})
        tech = facts.get("technologies", {})
        name = repo.get("full_name", "this repository")
        description = repo.get("description") or "No repository description was provided."
        technologies = tech.get("frameworks") or list((repo.get("languages") or {}).keys())[:5]
        risks: list[str] = []
        if not metrics.get("has_ci"):
            risks.append("CI configuration was not detected in the fetched repository tree.")
        if not metrics.get("has_tests"):
            risks.append("Tests were not detected from common file and directory conventions.")
        if metrics.get("stale_issues", 0) > 0:
            risks.append(f"{metrics['stale_issues']} open issues appear stale by the 30-day heuristic.")

        return AIOverview(
            summary=f"{name} appears to be {description}",
            purpose=description,
            architecture="Architecture could not be inferred deeply without an OpenAI API key, but the README, tree, and important files are indexed for chat.",
            technologies=technologies,
            strengths=["Repository metadata, activity, contributors, and file structure were fetched from GitHub."],
            risks=risks or ["No major deterministic risks were detected from the available metadata."],
            recommendations=["Review the README, dependency manifests, CI configuration, and recent issues before contributing."],
            onboarding_steps=["Read the README.", "Inspect dependency files.", "Review recent commits and open issues.", "Ask RepoLens chat targeted questions about indexed files."],
        )
