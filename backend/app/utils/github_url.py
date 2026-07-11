from dataclasses import dataclass
from urllib.parse import urlparse

from app.core.exceptions import InvalidGitHubUrlError


@dataclass(frozen=True)
class GitHubRepoRef:
    owner: str
    repo: str

    @property
    def html_url(self) -> str:
        return f"https://github.com/{self.owner}/{self.repo}"


def parse_github_repo_url(value: str) -> GitHubRepoRef:
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != "github.com":
        raise InvalidGitHubUrlError("Enter a valid GitHub repository URL, for example https://github.com/fastapi/fastapi.")

    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        raise InvalidGitHubUrlError("GitHub repository URLs must include an owner and repository name.")
    if len(parts) > 2 and parts[2] not in {"tree", "blob", "issues", "pulls", "releases"}:
        raise InvalidGitHubUrlError("Only GitHub repository URLs are supported.")

    owner, repo = parts[0], parts[1]
    repo = repo.removesuffix(".git")
    if not _is_safe_segment(owner) or not _is_safe_segment(repo):
        raise InvalidGitHubUrlError("The GitHub owner or repository name contains unsupported characters.")
    return GitHubRepoRef(owner=owner, repo=repo)


def _is_safe_segment(value: str) -> bool:
    if not value or value.startswith(".") or value.endswith("."):
        return False
    return all(ch.isalnum() or ch in {"-", "_", "."} for ch in value)
