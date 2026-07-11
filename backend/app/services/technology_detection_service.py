from pathlib import PurePosixPath

from app.schemas.analysis import TechnologyDetection


class TechnologyDetectionService:
    def detect(self, languages: dict[str, int], paths: list[str], files: dict[str, str]) -> TechnologyDetection:
        lower_paths = [path.lower() for path in paths]
        package_json = files.get("package.json", "")
        pyproject = files.get("pyproject.toml", "")
        requirements = files.get("requirements.txt", "")

        frameworks: set[str] = set()
        package_managers: set[str] = set()
        infrastructure: set[str] = set()
        ci_cd: set[str] = set()
        testing_tools: set[str] = set()

        if "next" in package_json:
            frameworks.add("Next.js")
        if "react" in package_json:
            frameworks.add("React")
        if "fastapi" in requirements.lower() or "fastapi" in pyproject.lower():
            frameworks.add("FastAPI")
        if "django" in requirements.lower() or "django" in pyproject.lower():
            frameworks.add("Django")
        if "pytest" in requirements.lower() or "pytest" in pyproject.lower():
            testing_tools.add("pytest")
        if "vitest" in package_json:
            testing_tools.add("Vitest")
        if "jest" in package_json:
            testing_tools.add("Jest")

        names = {PurePosixPath(path).name for path in paths}
        if "package.json" in names:
            package_managers.add("npm")
        if "pnpm-lock.yaml" in names:
            package_managers.add("pnpm")
        if "yarn.lock" in names:
            package_managers.add("Yarn")
        if "requirements.txt" in names or "pyproject.toml" in names:
            package_managers.add("pip")
        if "Dockerfile" in names or "docker-compose.yml" in names:
            infrastructure.add("Docker")
        if any(path.startswith(".github/workflows/") for path in lower_paths):
            ci_cd.add("GitHub Actions")

        dependency_files = [
            path
            for path in paths
            if PurePosixPath(path).name
            in {"package.json", "pyproject.toml", "requirements.txt", "go.mod", "Cargo.toml", "pom.xml", "Dockerfile", "docker-compose.yml"}
        ]

        for language in languages:
            if language in {"Python", "TypeScript", "JavaScript", "Go", "Rust", "Java"}:
                frameworks.add(language)

        return TechnologyDetection(
            frameworks=sorted(frameworks),
            package_managers=sorted(package_managers),
            dependency_files=sorted(dependency_files),
            infrastructure=sorted(infrastructure),
            ci_cd=sorted(ci_cd),
            testing_tools=sorted(testing_tools),
        )
