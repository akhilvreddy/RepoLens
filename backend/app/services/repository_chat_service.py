from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models import ChatMessage, ChatSession
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.repository_repository import RepositoryRepository
from app.schemas.chat import RepositoryChatResponse
from app.services.embedding_service import EmbeddingService
from app.services.openai_service import OpenAIService
from app.services.retrieval_service import RetrievalService


class RepositoryChatService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.repository_repo = RepositoryRepository()
        self.analysis_repo = AnalysisRepository()
        self.openai = OpenAIService(settings)
        self.retrieval = RetrievalService(EmbeddingService(settings))

    async def answer(self, db: Session, owner: str, repo: str, question: str, session_id: int | None) -> RepositoryChatResponse | None:
        repository = self.repository_repo.get_by_owner_name(db, owner, repo)
        if repository is None:
            return None
        analysis = self.analysis_repo.get_latest(db, repository.id)
        if analysis is None:
            return None
        session = self._get_or_create_session(db, repository.id, session_id)
        db.add(ChatMessage(session_id=session.id, role="user", content=question, sources_json=[]))
        chunks = await self.retrieval.retrieve(db, repository.id, question)
        chunk_payload = [
            {
                "path": chunk.source.path,
                "start_line": chunk.source.start_line,
                "end_line": chunk.source.end_line,
                "content": chunk.content,
                "score": chunk.score,
            }
            for chunk in chunks
        ]
        response = await self.openai.answer_question(
            question=question,
            repository_label=f"{owner}/{repo}",
            metrics=analysis.metrics_json,
            chunks=chunk_payload,
            session_id=session.id,
        )
        db.add(
            ChatMessage(
                session_id=session.id,
                role="assistant",
                content=response.answer,
                sources_json=[source.model_dump() for source in response.sources],
            )
        )
        db.commit()
        return response

    def _get_or_create_session(self, db: Session, repository_id: int, session_id: int | None) -> ChatSession:
        if session_id:
            session = (
                db.query(ChatSession)
                .filter(ChatSession.id == session_id, ChatSession.repository_id == repository_id)
                .first()
            )
            if session:
                return session
        session = ChatSession(repository_id=repository_id)
        db.add(session)
        db.flush()
        return session
