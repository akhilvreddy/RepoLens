from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.metrics import MetricsPayload


class AIOverview(BaseModel):
    summary: str
    purpose: str
    architecture: str
    technologies: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    onboarding_steps: list[str] = Field(default_factory=list)


class AnalyzeRepositoryRequest(BaseModel):
    url: str
    force_refresh: bool = False


class RepositorySummary(BaseModel):
    owner: str
    name: str
    full_name: str
    description: str | None = None
    github_url: str
    homepage_url: str | None = None
    default_branch: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    pushed_at: datetime | None = None
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    open_issues_count: int = 0
    primary_language: str | None = None
    languages: dict[str, int] = Field(default_factory=dict)
    license: str | None = None
    topics: list[str] = Field(default_factory=list)
    size: int = 0
    archived: bool = False


class CommitSummary(BaseModel):
    sha: str
    message: str
    author: str | None = None
    date: datetime | None = None
    url: str | None = None


class ContributorSummary(BaseModel):
    login: str
    avatar_url: str | None = None
    html_url: str | None = None
    contributions: int


class IssueSummary(BaseModel):
    number: int
    title: str
    html_url: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    labels: list[str] = Field(default_factory=list)


class PullRequestSummary(BaseModel):
    number: int
    title: str
    html_url: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ReleaseSummary(BaseModel):
    name: str | None = None
    tag_name: str
    html_url: str | None = None
    published_at: datetime | None = None


class RepositoryFileSummary(BaseModel):
    path: str
    type: str = "file"
    size: int | None = None


class TechnologyDetection(BaseModel):
    frameworks: list[str] = Field(default_factory=list)
    package_managers: list[str] = Field(default_factory=list)
    dependency_files: list[str] = Field(default_factory=list)
    infrastructure: list[str] = Field(default_factory=list)
    ci_cd: list[str] = Field(default_factory=list)
    testing_tools: list[str] = Field(default_factory=list)


class RepositoryAnalysisResponse(BaseModel):
    repository: RepositorySummary
    metrics: MetricsPayload
    ai_overview: AIOverview
    recent_commits: list[CommitSummary] = Field(default_factory=list)
    contributors: list[ContributorSummary] = Field(default_factory=list)
    open_issues: list[IssueSummary] = Field(default_factory=list)
    open_pull_requests: list[PullRequestSummary] = Field(default_factory=list)
    releases: list[ReleaseSummary] = Field(default_factory=list)
    tree: list[RepositoryFileSummary] = Field(default_factory=list)
    readme: str | None = None
    important_files: dict[str, str] = Field(default_factory=dict)
    technologies: TechnologyDetection = Field(default_factory=TechnologyDetection)
    analyzed_at: datetime
    expires_at: datetime
    cached: bool = False
