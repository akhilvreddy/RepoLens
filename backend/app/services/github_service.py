import base64
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.core.config import Settings
from app.core.exceptions import ExternalServiceError, GitHubRateLimitError, GitHubRepositoryNotFoundError
from app.utils.file_filters import should_download_file


class GitHubService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "RepoLens",
        }
        if self.settings.github_token:
            headers["Authorization"] = f"Bearer {self.settings.github_token}"
        return headers

    async def fetch_repository_bundle(self, owner: str, repo: str) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=self.settings.github_api_base_url,
            headers=self._headers(),
            timeout=self.settings.github_timeout_seconds,
        ) as client:
            repository = await self._get(client, f"/repos/{owner}/{repo}")
            default_branch = repository.get("default_branch") or "main"

            since = (datetime.now(timezone.utc) - timedelta(days=70)).isoformat()
            languages = await self._get_optional(client, f"/repos/{owner}/{repo}/languages", {})
            commits = await self._paginate(client, f"/repos/{owner}/{repo}/commits", {"per_page": 100, "since": since}, limit=200)
            contributors = await self._paginate(client, f"/repos/{owner}/{repo}/contributors", {"per_page": 100}, limit=100)
            issues_and_prs = await self._paginate(
                client,
                f"/repos/{owner}/{repo}/issues",
                {"per_page": 100, "state": "open", "sort": "updated", "direction": "desc"},
                limit=120,
            )
            releases = await self._paginate(client, f"/repos/{owner}/{repo}/releases", {"per_page": 50}, limit=50)
            tree = await self._get_optional(client, f"/repos/{owner}/{repo}/git/trees/{default_branch}", {"tree": []}, {"recursive": "1"})
            readme = await self._fetch_readme(client, owner, repo)
            important_files = await self._fetch_important_files(client, owner, repo, tree.get("tree", []))

        issues = [item for item in issues_and_prs if "pull_request" not in item]
        pulls = [item for item in issues_and_prs if "pull_request" in item]
        return {
            "repository": repository,
            "languages": languages,
            "commits": commits,
            "contributors": contributors,
            "issues": issues,
            "pulls": pulls,
            "releases": releases,
            "tree": tree.get("tree", []),
            "readme": readme,
            "important_files": important_files,
        }

    async def _get(self, client: httpx.AsyncClient, path: str, params: dict[str, Any] | None = None) -> Any:
        response = await client.get(path, params=params)
        if response.status_code == 404:
            raise GitHubRepositoryNotFoundError("Repository not found or not accessible.")
        if response.status_code in {403, 429}:
            remaining = response.headers.get("x-ratelimit-remaining")
            if remaining == "0" or response.status_code == 429:
                raise GitHubRateLimitError("GitHub API rate limit reached. Add GITHUB_TOKEN or retry later.")
        if response.status_code >= 400:
            raise ExternalServiceError(f"GitHub API request failed with status {response.status_code}.")
        return response.json()

    async def _get_optional(
        self,
        client: httpx.AsyncClient,
        path: str,
        default: Any,
        params: dict[str, Any] | None = None,
    ) -> Any:
        try:
            return await self._get(client, path, params)
        except GitHubRepositoryNotFoundError:
            return default
        except ExternalServiceError:
            return default

    async def _paginate(
        self,
        client: httpx.AsyncClient,
        path: str,
        params: dict[str, Any],
        limit: int,
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        page = 1
        while len(items) < limit:
            page_params = {**params, "page": page}
            data = await self._get_optional(client, path, [], page_params)
            if not data:
                break
            items.extend(data)
            if len(data) < page_params.get("per_page", 30):
                break
            page += 1
        return items[:limit]

    async def _fetch_readme(self, client: httpx.AsyncClient, owner: str, repo: str) -> str | None:
        data = await self._get_optional(client, f"/repos/{owner}/{repo}/readme", None)
        if not data or data.get("encoding") != "base64":
            return None
        try:
            return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        except Exception:
            return None

    async def _fetch_important_files(
        self,
        client: httpx.AsyncClient,
        owner: str,
        repo: str,
        tree: list[dict[str, Any]],
    ) -> dict[str, str]:
        files: dict[str, str] = {}
        candidates = [
            item
            for item in tree
            if item.get("type") == "blob"
            and should_download_file(item.get("path", ""), item.get("size"), self.settings.max_file_bytes)
        ]
        for item in candidates[: self.settings.max_repository_files]:
            path = item["path"]
            data = await self._get_optional(client, f"/repos/{owner}/{repo}/contents/{path}", None)
            if not data or data.get("encoding") != "base64" or data.get("size", 0) > self.settings.max_file_bytes:
                continue
            try:
                files[path] = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            except Exception:
                continue
        return files
