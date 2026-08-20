from fastapi import APIRouter, Depends

from app.api.dependencies import get_chat_service
from app.schemas.chat import RepositoryChatRequest, RepositoryChatResponse
from app.services.repository_chat_service import RepositoryChatService

router = APIRouter(prefix="/api/repositories", tags=["chat"])


@router.post("/{owner}/{repo}/chat", response_model=RepositoryChatResponse)
async def chat_with_repository(
    owner: str,
    repo: str,
    request: RepositoryChatRequest,
    service: RepositoryChatService = Depends(get_chat_service),
) -> RepositoryChatResponse:
    return await service.answer(owner, repo, request.question, request.session_id)
