import math
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.models import RepositoryFileChunk
from app.schemas.chat import SourceReference
from app.services.embedding_service import EmbeddingService


@dataclass(frozen=True)
class RetrievedChunk:
    content: str
    source: SourceReference
    score: float


class RetrievalService:
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service

    async def retrieve(self, db: Session, repository_id: int, question: str, limit: int = 6) -> list[RetrievedChunk]:
        query_embedding = await self.embedding_service.embed(question)
        chunks = db.query(RepositoryFileChunk).filter(RepositoryFileChunk.repository_id == repository_id).all()
        ranked = [
            RetrievedChunk(
                content=chunk.content,
                source=SourceReference(path=chunk.path, start_line=chunk.start_line, end_line=chunk.end_line),
                score=self._cosine(query_embedding, chunk.embedding_json or []),
            )
            for chunk in chunks
        ]
        return sorted(ranked, key=lambda item: item.score, reverse=True)[:limit]

    def _cosine(self, left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0
        size = min(len(left), len(right))
        dot = sum(left[index] * right[index] for index in range(size))
        left_norm = math.sqrt(sum(value * value for value in left[:size])) or 1.0
        right_norm = math.sqrt(sum(value * value for value in right[:size])) or 1.0
        return dot / (left_norm * right_norm)
