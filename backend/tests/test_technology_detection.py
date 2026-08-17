from app.services.technology_detection_service import TechnologyDetectionService


def test_empty_inputs_return_empty_detection() -> None:
    detection = TechnologyDetectionService().detect({}, [], {})
    assert detection.frameworks == []
    assert detection.package_managers == []
    assert detection.dependency_files == []
    assert detection.infrastructure == []
    assert detection.ci_cd == []
    assert detection.testing_tools == []


def test_detects_stack_from_manifests_paths_and_languages() -> None:
    detection = TechnologyDetectionService().detect(
        languages={"TypeScript": 80, "Python": 20, "HTML": 1},
        paths=[
            "package.json",
            "pnpm-lock.yaml",
            "pyproject.toml",
            "requirements.txt",
            "Dockerfile",
            ".github/workflows/ci.yml",
            "src/app.py",
        ],
        files={
            "package.json": '{"dependencies":{"next":"16.0.0","react":"19.0.0","vitest":"2.1.8"}}',
            "pyproject.toml": '[project]\ndependencies=["fastapi","pytest"]',
            "requirements.txt": "fastapi==0.116.1\npytest==8.3.4\n",
        },
    )

    assert detection.frameworks == ["FastAPI", "Next.js", "Python", "React", "TypeScript"]
    assert detection.package_managers == ["npm", "pip", "pnpm"]
    assert detection.testing_tools == ["Vitest", "pytest"]
    assert detection.infrastructure == ["Docker"]
    assert detection.ci_cd == ["GitHub Actions"]
    assert detection.dependency_files == [
        "Dockerfile",
        "package.json",
        "pyproject.toml",
        "requirements.txt",
    ]


def test_detects_django_jest_yarn_and_github_actions_case_insensitively() -> None:
    detection = TechnologyDetectionService().detect(
        languages={},
        paths=["yarn.lock", "package.json", ".GitHub/workflows/test.yaml"],
        files={
            "package.json": '{"devDependencies":{"jest":"29.0.0"}}',
            "requirements.txt": "Django>=5.0",
        },
    )

    assert "Django" in detection.frameworks
    assert "Jest" in detection.testing_tools
    assert "Yarn" in detection.package_managers
    assert detection.ci_cd == ["GitHub Actions"]
