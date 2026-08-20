from app.core.config import Settings
from app.schemas.chat import RepositoryChatResponse
from app.services.embedding_service import EmbeddingService
from app.services.github_service import GitHubService
from app.services.metrics_service import MetricsService
from app.services.openai_service import OpenAIService
from app.services.retrieval_service import RetrievalService
from app.utils.text_chunking import chunk_text


class RepositoryChatService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.github = GitHubService(settings)
        self.metrics = MetricsService()
        self.openai = OpenAIService(settings)
        self.retrieval = RetrievalService(EmbeddingService(settings))

    async def answer(self, owner: str, repo: str, question: str, session_id: int | None) -> RepositoryChatResponse:
        bundle = await self.github.fetch_repository_bundle(owner, repo)
        metrics = self.metrics.compute(bundle).model_dump(mode="json")
        indexed_chunks = self._build_chunk_index(bundle)
        chunks = await self.retrieval.retrieve(question, indexed_chunks)
        chunk_payload = [{"path": chunk.source.path, "start_line": chunk.source.start_line, "end_line": chunk.source.end_line, "content": chunk.content, "score": chunk.score} for chunk in chunks]
        ephemeral_session_id = session_id or 1
        response = await self.openai.answer_question(
            question=question,
            repository_label=f"{owner}/{repo}",
            metrics=metrics,
            chunks=chunk_payload,
            session_id=ephemeral_session_id,
        )
        return response

    def _build_chunk_index(self, bundle: dict) -> list[dict]:
        files: dict[str, str] = {}
        if bundle.get("readme"):
            files["README.md"] = bundle["readme"]
        files.update(bundle.get("important_files", {}))
        index: list[dict] = []
        for path, content in files.items():
            for chunk in chunk_text(content):
                index.append({"path": path, "start_line": chunk.start_line, "end_line": chunk.end_line, "content": chunk.content})
        return index
