from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import chat, repositories
from app.core.config import get_settings
from app.core.exceptions import RepoLensError
from app.core.logging import configure_logging
from app.db.base import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    create_db_and_tables()
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RepoLensError)
async def repolens_error_handler(request: Request, exc: RepoLensError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message, "code": exc.code})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(repositories.router)
app.include_router(chat.router)
