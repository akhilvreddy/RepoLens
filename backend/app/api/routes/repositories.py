from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_analysis_service
from app.db.session import get_db
from app.schemas.analysis import AnalyzeRepositoryRequest, RepositoryAnalysisResponse
from app.services.repository_analysis_service import RepositoryAnalysisService

router = APIRouter(prefix="/api/repositories", tags=["repositories"])


@router.post("/analyze", response_model=RepositoryAnalysisResponse)
async def analyze_repository(
    request: AnalyzeRepositoryRequest,
    db: Session = Depends(get_db),
    service: RepositoryAnalysisService = Depends(get_analysis_service),
) -> RepositoryAnalysisResponse:
    return await service.analyze(db, request.url, request.force_refresh)


@router.get("/{owner}/{repo}", response_model=RepositoryAnalysisResponse)
def get_repository_analysis(
    owner: str,
    repo: str,
    db: Session = Depends(get_db),
    service: RepositoryAnalysisService = Depends(get_analysis_service),
) -> RepositoryAnalysisResponse:
    analysis = service.get_analysis(db, owner, repo)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Repository analysis not found. Analyze the repository first.")
    return analysis


@router.get("/{owner}/{repo}/metrics")
def get_repository_metrics(owner: str, repo: str, db: Session = Depends(get_db), service: RepositoryAnalysisService = Depends(get_analysis_service)):
    analysis = service.get_analysis(db, owner, repo)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Repository analysis not found.")
    return analysis.metrics


@router.get("/{owner}/{repo}/activity")
def get_repository_activity(owner: str, repo: str, db: Session = Depends(get_db), service: RepositoryAnalysisService = Depends(get_analysis_service)):
    analysis = service.get_analysis(db, owner, repo)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Repository analysis not found.")
    return {"recent_commits": analysis.recent_commits, "releases": analysis.releases, "metrics": analysis.metrics}


@router.get("/{owner}/{repo}/issues")
def get_repository_issues(owner: str, repo: str, db: Session = Depends(get_db), service: RepositoryAnalysisService = Depends(get_analysis_service)):
    analysis = service.get_analysis(db, owner, repo)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Repository analysis not found.")
    return {"open_issues": analysis.open_issues, "open_pull_requests": analysis.open_pull_requests}


@router.get("/{owner}/{repo}/contributors")
def get_repository_contributors(owner: str, repo: str, db: Session = Depends(get_db), service: RepositoryAnalysisService = Depends(get_analysis_service)):
    analysis = service.get_analysis(db, owner, repo)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Repository analysis not found.")
    return {"contributors": analysis.contributors}


@router.get("/{owner}/{repo}/files")
def get_repository_files(owner: str, repo: str, db: Session = Depends(get_db), service: RepositoryAnalysisService = Depends(get_analysis_service)):
    analysis = service.get_analysis(db, owner, repo)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Repository analysis not found.")
    return {"tree": analysis.tree, "readme": analysis.readme, "important_files": analysis.important_files}
