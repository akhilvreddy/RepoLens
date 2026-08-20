from app.utils.file_filters import (
    dependency_files,
    is_safe_repo_path,
    looks_like_ci,
    looks_like_docs,
    looks_like_tests,
    should_download_file,
)


def test_rejects_unsafe_paths() -> None:
    assert is_safe_repo_path("src/app.py") is True
    assert is_safe_repo_path("../secret") is False
    assert is_safe_repo_path("/etc/passwd") is False
    assert should_download_file("../secret", 10, 1000) is False


def test_skips_binaries_generated_dirs_and_oversized_files() -> None:
    assert should_download_file("logo.png", 100, 1000) is False
    assert should_download_file("node_modules/left-pad/index.js", 100, 1000) is False
    assert should_download_file("package-lock.json", 100, 1000) is False
    assert should_download_file("app.py", 5000, 1000) is False


def test_downloads_source_important_files_and_github_workflows() -> None:
    assert should_download_file("app/main.py", 100, 1000) is True
    assert should_download_file("package.json", 100, 1000) is True
    assert should_download_file(".github/workflows/ci.yml", 100, 1000) is True
    assert should_download_file("notes.txt", 100, 1000) is False


def test_looks_like_tests_docs_and_ci() -> None:
    assert looks_like_tests(["src/app.py", "tests/test_app.py"]) is True
    assert looks_like_tests(["frontend/components/search.test.tsx"]) is True
    assert looks_like_tests(["src/app.py"]) is False
    assert looks_like_docs(["docs/intro.md"], None) is True
    assert looks_like_docs(["src/app.py"], "# Hello") is True
    assert looks_like_docs(["src/app.py"], None) is False
    assert looks_like_ci([".github/workflows/ci.yml"]) is True
    assert looks_like_ci(["src/app.py"]) is False


def test_dependency_files_excludes_readme() -> None:
    paths = ["README.md", "package.json", "src/app.py", "requirements.txt"]
    assert dependency_files(paths) == ["package.json", "requirements.txt"]
