from sqlalchemy.orm import Session

from app.db.models import Repository


class RepositoryRepository:
    def get_by_owner_name(self, db: Session, owner: str, name: str) -> Repository | None:
        return db.query(Repository).filter(Repository.owner == owner, Repository.name == name).first()

    def upsert(self, db: Session, owner: str, name: str, github_url: str, description: str | None, default_branch: str | None, metadata: dict) -> Repository:
        repository = self.get_by_owner_name(db, owner, name)
        if repository is None:
            repository = Repository(owner=owner, name=name, github_url=github_url)
            db.add(repository)
        repository.description = description
        repository.default_branch = default_branch
        repository.metadata_json = metadata
        db.flush()
        return repository
