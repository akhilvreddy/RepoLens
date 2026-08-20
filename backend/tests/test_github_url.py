import pytest

from app.core.exceptions import InvalidGitHubUrlError
from app.utils.github_url import parse_github_repo_url


@pytest.mark.parametrize(
    ("url", "owner", "repo"),
    [
        ("https://github.com/fastapi/fastapi", "fastapi", "fastapi"),
        ("http://github.com/pallets/flask", "pallets", "flask"),
        ("https://github.com/vercel/next.js.git", "vercel", "next.js"),
        ("  https://github.com/octocat/Hello-World/  ", "octocat", "Hello-World"),
        ("https://github.com/foo/bar/tree/main", "foo", "bar"),
        ("https://github.com/foo/bar/blob/main/README.md", "foo", "bar"),
        ("https://github.com/foo/bar/issues/12", "foo", "bar"),
        ("https://github.com/org_name/repo-name", "org_name", "repo-name"),
    ],
)
def test_parse_valid_github_urls(url: str, owner: str, repo: str) -> None:
    ref = parse_github_repo_url(url)
    assert ref.owner == owner
    assert ref.repo == repo
    assert ref.html_url == f"https://github.com/{owner}/{repo}"


@pytest.mark.parametrize(
    "url",
    [
        "not-a-url",
        "https://gitlab.com/foo/bar",
        "https://www.github.com/foo/bar",
        "https://github.com/only-owner",
        "https://github.com/foo/bar/wiki",
        "https://github.com/./repo",
        "https://github.com/foo/repo.",
        "https://github.com/foo/has space",
    ],
)
def test_parse_rejects_invalid_github_urls(url: str) -> None:
    with pytest.raises(InvalidGitHubUrlError) as exc_info:
        parse_github_repo_url(url)
    assert exc_info.value.status_code == 422
    assert exc_info.value.code == "invalid_github_url"
