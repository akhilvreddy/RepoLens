from fastapi import APIRouter, Depends

from app.api.dependencies import get_analysis_service
from app.schemas.analysis import AnalyzeRepositoryRequest, RepositoryAnalysisResponse
from app.services.repository_analysis_service import RepositoryAnalysisService

router = APIRouter(prefix="/api/repositories", tags=["repositories"])


@router.post("/analyze", response_model=RepositoryAnalysisResponse)
async def analyze_repository(
    request: AnalyzeRepositoryRequest,
    service: RepositoryAnalysisService = Depends(get_analysis_service),
) -> RepositoryAnalysisResponse:
    return await service.analyze(request.url, request.force_refresh)


@router.get("/{owner}/{repo}", response_model=RepositoryAnalysisResponse)
async def get_repository_analysis(
    owner: str,
    repo: str,
    service: RepositoryAnalysisService = Depends(get_analysis_service),
) -> RepositoryAnalysisResponse:
    return await service.analyze_by_coordinates(owner, repo)


@router.get("/{owner}/{repo}/metrics")
async def get_repository_metrics(owner: str, repo: str, service: RepositoryAnalysisService = Depends(get_analysis_service)):
    analysis = await service.analyze_by_coordinates(owner, repo)
    return analysis.metrics


@router.get("/{owner}/{repo}/activity")
async def get_repository_activity(owner: str, repo: str, service: RepositoryAnalysisService = Depends(get_analysis_service)):
    analysis = await service.analyze_by_coordinates(owner, repo)
    return {"recent_commits": analysis.recent_commits, "releases": analysis.releases, "metrics": analysis.metrics}


@router.get("/{owner}/{repo}/issues")
async def get_repository_issues(owner: str, repo: str, service: RepositoryAnalysisService = Depends(get_analysis_service)):
    analysis = await service.analyze_by_coordinates(owner, repo)
    return {"open_issues": analysis.open_issues, "open_pull_requests": analysis.open_pull_requests}


@router.get("/{owner}/{repo}/contributors")
async def get_repository_contributors(owner: str, repo: str, service: RepositoryAnalysisService = Depends(get_analysis_service)):
    analysis = await service.analyze_by_coordinates(owner, repo)
    return {"contributors": analysis.contributors}


@router.get("/{owner}/{repo}/files")
async def get_repository_files(owner: str, repo: str, service: RepositoryAnalysisService = Depends(get_analysis_service)):
    analysis = await service.analyze_by_coordinates(owner, repo)
    return {"tree": analysis.tree, "readme": analysis.readme, "important_files": analysis.important_files}
