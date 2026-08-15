import math
from dataclasses import dataclass
from typing import Any

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

    async def retrieve(self, question: str, chunks: list[dict[str, Any]], limit: int = 6) -> list[RetrievedChunk]:
        if not chunks:
            return []
        query_embedding = await self.embedding_service.embed(question)
        ranked: list[RetrievedChunk] = []
        for chunk in chunks:
            content = chunk.get("content", "")
            if not content:
                continue
            chunk_embedding = await self.embedding_service.embed(content)
            ranked.append(
                RetrievedChunk(
                    content=content,
                    source=SourceReference(
                        path=chunk.get("path", "unknown"),
                        start_line=chunk.get("start_line", 1),
                        end_line=chunk.get("end_line", 1),
                    ),
                    score=self._cosine(query_embedding, chunk_embedding),
                )
            )
        return sorted(ranked, key=lambda item: item.score, reverse=True)[:limit]

    def _cosine(self, left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0
        size = min(len(left), len(right))
        dot = sum(left[index] * right[index] for index in range(size))
        left_norm = math.sqrt(sum(value * value for value in left[:size])) or 1.0
        right_norm = math.sqrt(sum(value * value for value in right[:size])) or 1.0
        return dot / (left_norm * right_norm)
