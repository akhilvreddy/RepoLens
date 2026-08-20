import math

from app.core.config import Settings
from app.services.embedding_service import EmbeddingService


def _service() -> EmbeddingService:
    return EmbeddingService(Settings(openai_api_key=None))


def test_deterministic_embedding_is_stable_unit_and_64d() -> None:
    service = _service()
    first = service._deterministic_embedding("FastAPI metrics engine")
    second = service._deterministic_embedding("FastAPI metrics engine")

    assert first == second
    assert len(first) == 64
    assert math.isclose(math.sqrt(sum(value * value for value in first)), 1.0, rel_tol=1e-9)


async def test_embed_uses_fallback_when_openai_key_is_missing() -> None:
    service = _service()
    vector = await service.embed("repository chat retrieval")
    assert vector == service._deterministic_embedding("repository chat retrieval")


def test_different_text_produces_different_embeddings() -> None:
    service = _service()
    left = service._deterministic_embedding("alpha beta")
    right = service._deterministic_embedding("gamma delta")
    assert left != right


def test_empty_text_is_zero_vector() -> None:
    vector = _service()._deterministic_embedding("")
    assert vector == [0.0] * 64
