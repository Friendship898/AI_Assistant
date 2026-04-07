from contextlib import asynccontextmanager

from fastapi import FastAPI
import structlog

from app.api import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger = structlog.get_logger("backend.lifecycle")
    logger.info(
        "backend_starting",
        host=settings.api_host,
        port=settings.api_port,
        step="step0",
    )
    yield
    logger.info("backend_stopping", step="step0")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.include_router(api_router)
    return app


app = create_app()

