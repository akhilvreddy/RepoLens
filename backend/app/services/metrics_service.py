from datetime import datetime, timezone
from statistics import median
from typing import Any

from app.schemas.metrics import HealthScores, MetricsPayload, RepositoryMetric
from app.utils.file_filters import dependency_files, looks_like_ci, looks_like_docs, looks_like_tests


class MetricsService:
    def compute(self, bundle: dict[str, Any]) -> MetricsPayload:
        now = datetime.now(timezone.utc)
        commits = bundle.get("commits", [])
        issues = bundle.get("issues", [])
        pulls = bundle.get("pulls", [])
        releases = bundle.get("releases", [])
        contributors = bundle.get("contributors", [])
        tree_paths = [item.get("path", "") for item in bundle.get("tree", []) if item.get("path")]
        readme = bundle.get("readme")

        commit_dates = [self._parse_commit_date(commit) for commit in commits]
        commit_dates = [date for date in commit_dates if date is not None]
        commits_last_30 = sum(1 for date in commit_dates if 0 <= (now - date).days < 30)
        commits_prev_30 = sum(1 for date in commit_dates if 30 <= (now - date).days < 60)
        momentum = None if commits_prev_30 == 0 else round(((commits_last_30 - commits_prev_30) / commits_prev_30) * 100, 1)
        if commits_prev_30 == 0 and commits_last_30 > 0:
            momentum = 100.0

        active_contributors = len({self._commit_author(commit) for commit in commits if self._commit_author(commit)})
        contribution_total = sum(max(0, c.get("contributions", 0)) for c in contributors)
        top_contributor_share = None
        if contribution_total:
            top_contributor_share = max(c.get("contributions", 0) for c in contributors) / contribution_total

        stale_issues = sum(1 for issue in issues if self._age_days(issue.get("updated_at"), now) > 30)
        issue_ages = [self._age_days(issue.get("created_at"), now) for issue in issues if issue.get("created_at")]
        median_issue_age = float(median(issue_ages)) if issue_ages else None
        stale_prs = sum(1 for pr in pulls if self._age_days(pr.get("updated_at"), now) > 30)

        release_dates = [self._parse_date(release.get("published_at")) for release in releases if release.get("published_at")]
        release_dates = [date for date in release_dates if date is not None]
        days_since_latest_release = min((now - date).days for date in release_dates) if release_dates else None
        release_cadence = self._release_cadence_days(sorted(release_dates, reverse=True))

        has_ci = looks_like_ci(tree_paths)
        has_tests = looks_like_tests(tree_paths)
        has_docs = looks_like_docs(tree_paths, readme)
        has_deps = bool(dependency_files(tree_paths))

        activity = self._bounded_score(50 + commits_last_30 * 8 + (momentum or 0) * 0.2)
        maintenance = self._bounded_score(80 - stale_issues * 4 - stale_prs * 6)
        contributor = self._bounded_score((active_contributors * 18) - ((top_contributor_share or 1) * 35) + 55)
        issue_health = self._bounded_score(85 - stale_issues * 5 - ((median_issue_age or 0) * 0.4))
        release = 50 if days_since_latest_release is None else self._bounded_score(95 - days_since_latest_release * 0.25)
        documentation = 80 if has_docs else 30
        engineering_maturity = self._bounded_score((25 if has_ci else 0) + (25 if has_tests else 0) + (25 if has_deps else 0) + 25)
        overall = round((activity + maintenance + contributor + issue_health + release + documentation + engineering_maturity) / 7)

        metrics = [
            self._metric("Commits in last 30 days", commits_last_30, str(commits_last_30), self._status(commits_last_30, 8, 2), "Recent commit activity from the GitHub commit feed."),
            self._metric("Commit momentum", momentum, "Unknown" if momentum is None else f"{momentum:+.1f}%", self._momentum_status(momentum), "Change compared with the previous 30-day period."),
            self._metric("Active contributors", active_contributors, str(active_contributors), self._status(active_contributors, 4, 1), "Unique commit authors seen in the fetched recent commit window."),
            self._metric("Contributor concentration", top_contributor_share, "Unknown" if top_contributor_share is None else f"{top_contributor_share:.0%}", self._concentration_status(top_contributor_share), "Share of all listed contributions made by the top contributor."),
            self._metric("Stale issues", stale_issues, str(stale_issues), "healthy" if stale_issues < 5 else "warning" if stale_issues < 20 else "risk", "Open issues not updated in the last 30 days."),
            self._metric("Median issue age", median_issue_age, "Unknown" if median_issue_age is None else f"{median_issue_age:.0f} days", "unknown" if median_issue_age is None else "healthy" if median_issue_age < 21 else "warning" if median_issue_age < 90 else "risk", "Median age for currently open issues."),
            self._metric("Open pull requests", len(pulls), str(len(pulls)), "healthy" if len(pulls) < 10 else "warning" if len(pulls) < 30 else "risk", "Open pull requests returned by GitHub."),
            self._metric("Latest release", days_since_latest_release, "No releases" if days_since_latest_release is None else f"{days_since_latest_release} days ago", "unknown" if days_since_latest_release is None else "healthy" if days_since_latest_release < 120 else "warning" if days_since_latest_release < 365 else "risk", "Time since the most recent published release."),
            self._metric("Release cadence", release_cadence, "Unknown" if release_cadence is None else f"Every {release_cadence:.0f} days", "unknown" if release_cadence is None else "healthy" if release_cadence < 90 else "warning" if release_cadence < 180 else "risk", "Average gap between recent releases."),
            self._metric("CI configuration", has_ci, "Present" if has_ci else "Not detected", "healthy" if has_ci else "warning", "Detected from common CI configuration paths."),
            self._metric("Tests", has_tests, "Detected" if has_tests else "Not detected", "healthy" if has_tests else "warning", "Detected from common test directory and filename conventions."),
            self._metric("Documentation", has_docs, "Present" if has_docs else "Not detected", "healthy" if has_docs else "risk", "README or documentation directory detection."),
            self._metric("Dependency files", has_deps, "Present" if has_deps else "Not detected", "healthy" if has_deps else "warning", "Presence of common dependency manifests."),
        ]

        return MetricsPayload(
            scores=HealthScores(
                overall=overall,
                activity=activity,
                maintenance=maintenance,
                contributor=contributor,
                issue_health=issue_health,
                release=release,
                documentation=documentation,
                engineering_maturity=engineering_maturity,
            ),
            metrics=metrics,
            commits_last_30_days=commits_last_30,
            commits_previous_30_days=commits_prev_30,
            commit_momentum_percentage=momentum,
            active_contributors=active_contributors,
            top_contributor_share=top_contributor_share,
            open_issues=len(issues),
            stale_issues=stale_issues,
            median_issue_age_days=median_issue_age,
            open_pull_requests=len(pulls),
            stale_pull_requests=stale_prs,
            has_ci=has_ci,
            has_tests=has_tests,
            has_documentation=has_docs,
            has_dependency_files=has_deps,
        )

    def _metric(self, name: str, value: Any, display_value: str, status: str, explanation: str) -> RepositoryMetric:
        return RepositoryMetric(name=name, value=value, display_value=display_value, status=status, explanation=explanation)

    def _parse_commit_date(self, commit: dict[str, Any]) -> datetime | None:
        return self._parse_date(commit.get("commit", {}).get("committer", {}).get("date"))

    def _commit_author(self, commit: dict[str, Any]) -> str | None:
        return commit.get("author", {}).get("login") or commit.get("commit", {}).get("author", {}).get("name")

    def _parse_date(self, value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _age_days(self, value: str | None, now: datetime) -> int:
        date = self._parse_date(value)
        return 0 if date is None else max(0, (now - date).days)

    def _release_cadence_days(self, dates: list[datetime]) -> float | None:
        if len(dates) < 2:
            return None
        gaps = [(dates[index] - dates[index + 1]).days for index in range(len(dates) - 1)]
        return sum(gaps) / len(gaps)

    def _bounded_score(self, value: float) -> int:
        return round(max(0, min(100, value)))

    def _status(self, value: int, healthy_at: int, warning_at: int) -> str:
        if value >= healthy_at:
            return "healthy"
        if value >= warning_at:
            return "warning"
        return "risk"

    def _momentum_status(self, momentum: float | None) -> str:
        if momentum is None:
            return "unknown"
        if momentum >= 0:
            return "healthy"
        if momentum > -50:
            return "warning"
        return "risk"

    def _concentration_status(self, share: float | None) -> str:
        if share is None:
            return "unknown"
        if share < 0.45:
            return "healthy"
        if share < 0.7:
            return "warning"
        return "risk"
