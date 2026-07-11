from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    path: str
    start_line: int
    end_line: int


class RepositoryChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    session_id: int | None = None


class RepositoryChatResponse(BaseModel):
    answer: str
    sources: list[SourceReference] = Field(default_factory=list)
    confidence: str = Field(pattern="^(high|medium|low)$")
    session_id: int
