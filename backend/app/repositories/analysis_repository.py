from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import RepositoryAnalysis


class AnalysisRepository:
    def get_fresh(self, db: Session, repository_id: int) -> RepositoryAnalysis | None:
        now = datetime.now(timezone.utc)
        return (
            db.query(RepositoryAnalysis)
            .filter(RepositoryAnalysis.repository_id == repository_id, RepositoryAnalysis.expires_at > now)
            .order_by(RepositoryAnalysis.analyzed_at.desc())
            .first()
        )

    def get_latest(self, db: Session, repository_id: int) -> RepositoryAnalysis | None:
        return (
            db.query(RepositoryAnalysis)
            .filter(RepositoryAnalysis.repository_id == repository_id)
            .order_by(RepositoryAnalysis.analyzed_at.desc())
            .first()
        )
