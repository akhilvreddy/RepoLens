from functools import lru_cache

from app.core.config import Settings, get_settings
from app.services.repository_analysis_service import RepositoryAnalysisService
from app.services.repository_chat_service import RepositoryChatService


@lru_cache
def get_analysis_service() -> RepositoryAnalysisService:
    return RepositoryAnalysisService(get_settings())


@lru_cache
def get_chat_service() -> RepositoryChatService:
    return RepositoryChatService(get_settings())


def settings_dependency() -> Settings:
    return get_settings()
