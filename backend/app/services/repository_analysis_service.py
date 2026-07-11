from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models import RepositoryAnalysis, RepositoryFileChunk
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.repository_repository import RepositoryRepository
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
from app.services.embedding_service import EmbeddingService
from app.services.github_service import GitHubService
from app.services.metrics_service import MetricsService
from app.services.openai_service import OpenAIService
from app.services.technology_detection_service import TechnologyDetectionService
from app.utils.github_url import parse_github_repo_url
from app.utils.text_chunking import chunk_text


class RepositoryAnalysisService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.github = GitHubService(settings)
        self.metrics = MetricsService()
        self.tech = TechnologyDetectionService()
        self.openai = OpenAIService(settings)
        self.embeddings = EmbeddingService(settings)
        self.repository_repo = RepositoryRepository()
        self.analysis_repo = AnalysisRepository()

    async def analyze(self, db: Session, url: str, force_refresh: bool = False) -> RepositoryAnalysisResponse:
        ref = parse_github_repo_url(url)
        existing_repo = self.repository_repo.get_by_owner_name(db, ref.owner, ref.repo)
        if existing_repo and not force_refresh:
            fresh = self.analysis_repo.get_fresh(db, existing_repo.id)
            if fresh:
                return self._response_from_analysis(fresh, cached=True)

        bundle = await self.github.fetch_repository_bundle(ref.owner, ref.repo)
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

        repository = self.repository_repo.upsert(
            db,
            owner=repository_summary.owner,
            name=repository_summary.name,
            github_url=repository_summary.github_url,
            description=repository_summary.description,
            default_branch=repository_summary.default_branch,
            metadata=repository_summary.model_dump(mode="json"),
        )
        analyzed_at = datetime.now(timezone.utc)
        expires_at = analyzed_at + timedelta(seconds=self.settings.analysis_cache_ttl_seconds)
        analysis = RepositoryAnalysis(
            repository_id=repository.id,
            metrics_json=metrics.model_dump(mode="json"),
            ai_overview_json=overview.model_dump(mode="json"),
            raw_data_json=self._raw_payload(bundle, repository_summary, technologies),
            analyzed_at=analyzed_at,
            expires_at=expires_at,
        )
        db.add(analysis)
        db.query(RepositoryFileChunk).filter(RepositoryFileChunk.repository_id == repository.id).delete()
        await self._index_chunks(db, repository.id, bundle)
        db.commit()
        db.refresh(analysis)
        return self._response_from_analysis(analysis, cached=False)

    def get_analysis(self, db: Session, owner: str, repo: str) -> RepositoryAnalysisResponse | None:
        repository = self.repository_repo.get_by_owner_name(db, owner, repo)
        if repository is None:
            return None
        analysis = self.analysis_repo.get_latest(db, repository.id)
        if analysis is None:
            return None
        return self._response_from_analysis(analysis, cached=False)

    async def _index_chunks(self, db: Session, repository_id: int, bundle: dict[str, Any]) -> None:
        files: dict[str, str] = {}
        if bundle.get("readme"):
            files["README.md"] = bundle["readme"]
        files.update(bundle.get("important_files", {}))
        for path, content in files.items():
            for chunk in chunk_text(content):
                embedding = await self.embeddings.embed(chunk.content)
                db.add(
                    RepositoryFileChunk(
                        repository_id=repository_id,
                        path=path,
                        start_line=chunk.start_line,
                        end_line=chunk.end_line,
                        content=chunk.content,
                        embedding_json=embedding,
                    )
                )

    def _raw_payload(self, bundle: dict[str, Any], repository: RepositorySummary, technologies: Any) -> dict[str, Any]:
        return {
            "repository": repository.model_dump(mode="json"),
            "recent_commits": [self._commit_summary(item).model_dump(mode="json") for item in bundle.get("commits", [])[:50]],
            "contributors": [self._contributor_summary(item).model_dump(mode="json") for item in bundle.get("contributors", [])[:50]],
            "open_issues": [self._issue_summary(item).model_dump(mode="json") for item in bundle.get("issues", [])[:50]],
            "open_pull_requests": [self._pull_summary(item).model_dump(mode="json") for item in bundle.get("pulls", [])[:50]],
            "releases": [self._release_summary(item).model_dump(mode="json") for item in bundle.get("releases", [])[:20]],
            "tree": [self._file_summary(item).model_dump(mode="json") for item in bundle.get("tree", [])[:500]],
            "readme": bundle.get("readme"),
            "important_files": bundle.get("important_files", {}),
            "technologies": technologies.model_dump(mode="json"),
        }

    def _response_from_analysis(self, analysis: RepositoryAnalysis, cached: bool) -> RepositoryAnalysisResponse:
        raw = analysis.raw_data_json
        return RepositoryAnalysisResponse(
            repository=RepositorySummary.model_validate(raw["repository"]),
            metrics=analysis.metrics_json,
            ai_overview=analysis.ai_overview_json,
            recent_commits=raw.get("recent_commits", []),
            contributors=raw.get("contributors", []),
            open_issues=raw.get("open_issues", []),
            open_pull_requests=raw.get("open_pull_requests", []),
            releases=raw.get("releases", []),
            tree=raw.get("tree", []),
            readme=raw.get("readme"),
            important_files=raw.get("important_files", {}),
            technologies=raw.get("technologies", {}),
            analyzed_at=analysis.analyzed_at,
            expires_at=analysis.expires_at,
            cached=cached,
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
