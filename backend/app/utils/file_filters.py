from pathlib import PurePosixPath


BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".gz",
    ".tgz",
    ".mp4",
    ".mov",
    ".woff",
    ".woff2",
    ".ttf",
}

GENERATED_OR_LOW_SIGNAL = {
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "poetry.lock",
    "Cargo.lock",
    "go.sum",
    "dist",
    "build",
    ".next",
    "node_modules",
    "__pycache__",
    ".git",
}

IMPORTANT_FILENAMES = {
    "README.md",
    "readme.md",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "Pipfile",
    "poetry.lock",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "Dockerfile",
    "docker-compose.yml",
    "Makefile",
    "next.config.js",
    "next.config.ts",
    "vite.config.ts",
    "tsconfig.json",
}


def is_safe_repo_path(path: str) -> bool:
    normalized = PurePosixPath(path)
    if normalized.is_absolute() or ".." in normalized.parts:
        return False
    return True


def should_download_file(path: str, size: int | None, max_bytes: int) -> bool:
    if not is_safe_repo_path(path):
        return False
    pure_path = PurePosixPath(path)
    if any(part in GENERATED_OR_LOW_SIGNAL for part in pure_path.parts):
        return False
    if pure_path.suffix.lower() in BINARY_EXTENSIONS:
        return False
    if size is not None and size > max_bytes:
        return False
    name = pure_path.name
    if name in IMPORTANT_FILENAMES:
        return True
    if path.startswith(".github/workflows/") and pure_path.suffix in {".yml", ".yaml"}:
        return True
    return pure_path.suffix.lower() in {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".md", ".yml", ".yaml", ".toml", ".json"}


def looks_like_tests(paths: list[str]) -> bool:
    return any(
        "/test/" in f"/{path.lower()}/"
        or "/tests/" in f"/{path.lower()}/"
        or path.lower().startswith("test_")
        or path.lower().endswith((".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx", "_test.go"))
        for path in paths
    )


def looks_like_docs(paths: list[str], readme: str | None) -> bool:
    return bool(readme) or any(path.lower().startswith(("docs/", "documentation/")) for path in paths)


def looks_like_ci(paths: list[str]) -> bool:
    return any(path.startswith(".github/workflows/") or path in {".gitlab-ci.yml", "circle.yml"} for path in paths)


def dependency_files(paths: list[str]) -> list[str]:
    return [path for path in paths if PurePosixPath(path).name in IMPORTANT_FILENAMES and path != "README.md"]
