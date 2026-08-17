from datetime import datetime, timedelta, timezone
from typing import Any

from app.services.metrics_service import MetricsService


def _iso(days_ago: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _commit(days_ago: int, login: str) -> dict[str, Any]:
    return {
        "author": {"login": login},
        "commit": {
            "author": {"name": login},
            "committer": {"date": _iso(days_ago)},
        },
    }


def _metric(payload, name: str):
    return next(metric for metric in payload.metrics if metric.name == name)


def test_empty_bundle_scores_and_unknown_statuses() -> None:
    payload = MetricsService().compute({})

    assert payload.commits_last_30_days == 0
    assert payload.commits_previous_30_days == 0
    assert payload.commit_momentum_percentage is None
    assert payload.active_contributors == 0
    assert payload.top_contributor_share is None
    assert payload.open_issues == 0
    assert payload.stale_issues == 0
    assert payload.median_issue_age_days is None
    assert payload.has_ci is False
    assert payload.has_tests is False
    assert payload.has_documentation is False
    assert payload.has_dependency_files is False

    assert payload.scores.activity == 50
    assert payload.scores.maintenance == 80
    assert payload.scores.contributor == 20
    assert payload.scores.issue_health == 85
    assert payload.scores.release == 50
    assert payload.scores.documentation == 30
    assert payload.scores.engineering_maturity == 25
    assert payload.scores.overall == 49

    assert _metric(payload, "Commit momentum").status == "unknown"
    assert _metric(payload, "Contributor concentration").status == "unknown"
    assert _metric(payload, "Latest release").status == "unknown"
    assert _metric(payload, "Documentation").status == "risk"
    assert _metric(payload, "CI configuration").status == "warning"
    assert _metric(payload, "Tests").status == "warning"


def test_healthy_bundle_sets_flags_scores_and_statuses() -> None:
    bundle = {
        "commits": [_commit(day, f"dev{day % 4}") for day in range(1, 11)]
        + [_commit(day, f"dev{day % 4}") for day in range(35, 40)],
        "contributors": [
            {"login": "dev0", "contributions": 10},
            {"login": "dev1", "contributions": 10},
            {"login": "dev2", "contributions": 10},
            {"login": "dev3", "contributions": 10},
        ],
        "issues": [
            {"created_at": _iso(5), "updated_at": _iso(1)},
            {"created_at": _iso(5), "updated_at": _iso(1)},
            {"created_at": _iso(5), "updated_at": _iso(1)},
        ],
        "pulls": [
            {"updated_at": _iso(2)},
            {"updated_at": _iso(3)},
        ],
        "releases": [
            {"published_at": _iso(10)},
            {"published_at": _iso(40)},
        ],
        "readme": "# RepoLens",
        "tree": [
            {"path": ".github/workflows/ci.yml"},
            {"path": "tests/test_app.py"},
            {"path": "package.json"},
            {"path": "README.md"},
        ],
    }

    payload = MetricsService().compute(bundle)

    assert payload.commits_last_30_days == 10
    assert payload.commits_previous_30_days == 5
    assert payload.commit_momentum_percentage == 100.0
    assert payload.active_contributors == 4
    assert payload.top_contributor_share == 0.25
    assert payload.stale_issues == 0
    assert payload.median_issue_age_days == 5.0
    assert payload.open_pull_requests == 2
    assert payload.stale_pull_requests == 0
    assert payload.has_ci is True
    assert payload.has_tests is True
    assert payload.has_documentation is True
    assert payload.has_dependency_files is True

    assert payload.scores.activity == 100
    assert payload.scores.maintenance == 80
    assert payload.scores.contributor == 100
    assert payload.scores.issue_health == 83
    assert payload.scores.release == 92
    assert payload.scores.documentation == 80
    assert payload.scores.engineering_maturity == 100
    assert payload.scores.overall == 91

    assert _metric(payload, "Commits in last 30 days").status == "healthy"
    assert _metric(payload, "Commit momentum").status == "healthy"
    assert _metric(payload, "Active contributors").status == "healthy"
    assert _metric(payload, "Contributor concentration").status == "healthy"
    assert _metric(payload, "Stale issues").status == "healthy"
    assert _metric(payload, "CI configuration").display_value == "Present"
    assert _metric(payload, "Tests").display_value == "Detected"


def test_new_activity_without_baseline_is_full_momentum() -> None:
    payload = MetricsService().compute({"commits": [_commit(2, "ada"), _commit(4, "ada")]})
    assert payload.commits_last_30_days == 2
    assert payload.commits_previous_30_days == 0
    assert payload.commit_momentum_percentage == 100.0
    assert _metric(payload, "Commit momentum").status == "healthy"


def test_stale_concentrated_repo_is_marked_risk() -> None:
    bundle = {
        "commits": [_commit(40, "solo")],
        "contributors": [
            {"login": "solo", "contributions": 90},
            {"login": "other", "contributions": 10},
        ],
        "issues": [{"created_at": _iso(120), "updated_at": _iso(80)} for _ in range(20)],
        "pulls": [{"updated_at": _iso(60)} for _ in range(30)],
        "tree": [{"path": "src/app.py"}],
    }

    payload = MetricsService().compute(bundle)

    assert payload.top_contributor_share == 0.9
    assert payload.stale_issues == 20
    assert payload.stale_pull_requests == 30
    assert payload.has_ci is False
    assert _metric(payload, "Contributor concentration").status == "risk"
    assert _metric(payload, "Stale issues").status == "risk"
    assert _metric(payload, "Open pull requests").status == "risk"
    assert _metric(payload, "Commit momentum").status == "unknown"
    assert payload.scores.maintenance == 0
    assert payload.scores.documentation == 30
