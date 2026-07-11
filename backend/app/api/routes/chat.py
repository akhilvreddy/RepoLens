from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_chat_service
from app.db.session import get_db
from app.schemas.chat import RepositoryChatRequest, RepositoryChatResponse
from app.services.repository_chat_service import RepositoryChatService

router = APIRouter(prefix="/api/repositories", tags=["chat"])


@router.post("/{owner}/{repo}/chat", response_model=RepositoryChatResponse)
async def chat_with_repository(
    owner: str,
    repo: str,
    request: RepositoryChatRequest,
    db: Session = Depends(get_db),
    service: RepositoryChatService = Depends(get_chat_service),
) -> RepositoryChatResponse:
    response = await service.answer(db, owner, repo, request.question, request.session_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Repository analysis not found. Analyze the repository first.")
    return response
