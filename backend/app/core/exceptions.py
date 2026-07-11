class RepoLensError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class InvalidGitHubUrlError(RepoLensError):
    status_code = 422
    code = "invalid_github_url"


class GitHubRepositoryNotFoundError(RepoLensError):
    status_code = 404
    code = "repository_not_found"


class GitHubRateLimitError(RepoLensError):
    status_code = 429
    code = "github_rate_limited"


class ExternalServiceError(RepoLensError):
    status_code = 502
    code = "external_service_error"
