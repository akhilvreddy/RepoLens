from datetime import datetime, timezone
from typing import Any

from app.core.config import Settings
from app.schemas.analysis import (
    CommitSummary,
    ContributorSummary,
    IssueSummary,
    PullRequestSummary,
    ReleaseSummary,
    RepositoryAnalysisResponse,
    RepositoryFileSummary,
    RepositorySummary,
)
from app.services.github_service import GitHubService
from app.services.metrics_service import MetricsService
from app.services.openai_service import OpenAIService
from app.services.technology_detection_service import TechnologyDetectionService
from app.utils.github_url import parse_github_repo_url


class RepositoryAnalysisService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.github = GitHubService(settings)
        self.metrics = MetricsService()
        self.tech = TechnologyDetectionService()
        self.openai = OpenAIService(settings)

    async def analyze(self, url: str, force_refresh: bool = False) -> RepositoryAnalysisResponse:
        _ = force_refresh
        ref = parse_github_repo_url(url)
        return await self._build_response(ref.owner, ref.repo, ref.html_url)

    async def analyze_by_coordinates(self, owner: str, repo: str) -> RepositoryAnalysisResponse:
        return await self._build_response(owner, repo, f"https://github.com/{owner}/{repo}")

    async def _build_response(self, owner: str, repo: str, github_url: str) -> RepositoryAnalysisResponse:
        bundle = await self.github.fetch_repository_bundle(owner, repo)
        repository_summary = self._repository_summary(bundle["repository"], bundle["languages"])
        paths = [item.get("path", "") for item in bundle.get("tree", []) if item.get("path")]
        technologies = self.tech.detect(bundle["languages"], paths, bundle.get("important_files", {}))
        metrics = self.metrics.compute(bundle)
        facts = {
            "repository": repository_summary.model_dump(mode="json"),
            "metrics": metrics.model_dump(mode="json"),
            "readme_excerpt": (bundle.get("readme") or "")[:5000],
            "directory_tree": paths[:300],
            "technologies": technologies.model_dump(mode="json"),
            "recent_commits": [self._commit_summary(item).model_dump(mode="json") for item in bundle.get("commits", [])[:20]],
            "issues": [self._issue_summary(item).model_dump(mode="json") for item in bundle.get("issues", [])[:20]],
            "pull_requests": [self._pull_summary(item).model_dump(mode="json") for item in bundle.get("pulls", [])[:20]],
        }
        overview = await self.openai.generate_overview(facts)
        analyzed_at = datetime.now(timezone.utc)

        return RepositoryAnalysisResponse(
            repository=repository_summary.model_copy(update={"github_url": github_url}),
            metrics=metrics,
            ai_overview=overview,
            recent_commits=[self._commit_summary(item) for item in bundle.get("commits", [])[:50]],
            contributors=[self._contributor_summary(item) for item in bundle.get("contributors", [])[:50]],
            open_issues=[self._issue_summary(item) for item in bundle.get("issues", [])[:50]],
            open_pull_requests=[self._pull_summary(item) for item in bundle.get("pulls", [])[:50]],
            releases=[self._release_summary(item) for item in bundle.get("releases", [])[:20]],
            tree=[self._file_summary(item) for item in bundle.get("tree", [])[:500]],
            readme=bundle.get("readme"),
            important_files=bundle.get("important_files", {}),
            technologies=technologies,
            analyzed_at=analyzed_at,
            expires_at=analyzed_at,
            cached=False,
        )

    def _repository_summary(self, data: dict[str, Any], languages: dict[str, int]) -> RepositorySummary:
        return RepositorySummary(
            owner=data.get("owner", {}).get("login", ""),
            name=data.get("name", ""),
            full_name=data.get("full_name", ""),
            description=data.get("description"),
            github_url=data.get("html_url", ""),
            homepage_url=data.get("homepage"),
            default_branch=data.get("default_branch"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            pushed_at=data.get("pushed_at"),
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            watchers=data.get("watchers_count", 0),
            open_issues_count=data.get("open_issues_count", 0),
            primary_language=data.get("language"),
            languages=languages,
            license=(data.get("license") or {}).get("spdx_id") if data.get("license") else None,
            topics=data.get("topics") or [],
            size=data.get("size") or 0,
            archived=data.get("archived") or False,
        )

    def _commit_summary(self, item: dict[str, Any]) -> CommitSummary:
        commit = item.get("commit", {})
        return CommitSummary(
            sha=item.get("sha", "")[:12],
            message=(commit.get("message") or "").splitlines()[0],
            author=(item.get("author") or {}).get("login") or (commit.get("author") or {}).get("name"),
            date=(commit.get("committer") or {}).get("date"),
            url=item.get("html_url"),
        )

    def _contributor_summary(self, item: dict[str, Any]) -> ContributorSummary:
        return ContributorSummary(
            login=item.get("login") or "unknown",
            avatar_url=item.get("avatar_url"),
            html_url=item.get("html_url"),
            contributions=item.get("contributions", 0),
        )

    def _issue_summary(self, item: dict[str, Any]) -> IssueSummary:
        return IssueSummary(
            number=item.get("number", 0),
            title=item.get("title", ""),
            html_url=item.get("html_url", ""),
            created_at=item.get("created_at"),
            updated_at=item.get("updated_at"),
            labels=[label.get("name", "") for label in item.get("labels", [])],
        )

    def _pull_summary(self, item: dict[str, Any]) -> PullRequestSummary:
        return PullRequestSummary(
            number=item.get("number", 0),
            title=item.get("title", ""),
            html_url=item.get("html_url", ""),
            created_at=item.get("created_at"),
            updated_at=item.get("updated_at"),
        )

    def _release_summary(self, item: dict[str, Any]) -> ReleaseSummary:
        return ReleaseSummary(
            name=item.get("name"),
            tag_name=item.get("tag_name", ""),
            html_url=item.get("html_url"),
            published_at=item.get("published_at"),
        )

    def _file_summary(self, item: dict[str, Any]) -> RepositoryFileSummary:
        return RepositoryFileSummary(path=item.get("path", ""), type=item.get("type", "file"), size=item.get("size"))
