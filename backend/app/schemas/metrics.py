from pydantic import BaseModel, Field


MetricStatus = str


class RepositoryMetric(BaseModel):
    name: str
    value: float | int | str | bool | None
    display_value: str
    status: MetricStatus = Field(pattern="^(healthy|warning|risk|unknown)$")
    explanation: str


class HealthScores(BaseModel):
    overall: int
    activity: int
    maintenance: int
    contributor: int
    issue_health: int
    release: int
    documentation: int
    engineering_maturity: int


class MetricsPayload(BaseModel):
    scores: HealthScores
    metrics: list[RepositoryMetric]
    commits_last_30_days: int
    commits_previous_30_days: int
    commit_momentum_percentage: float | None
    active_contributors: int
    top_contributor_share: float | None
    open_issues: int
    stale_issues: int
    median_issue_age_days: float | None
    open_pull_requests: int
    stale_pull_requests: int
    has_ci: bool
    has_tests: bool
    has_documentation: bool
    has_dependency_files: bool
