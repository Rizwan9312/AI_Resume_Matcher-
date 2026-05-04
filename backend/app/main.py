"""FastAPI application factory — main entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import v1_router
from app.config import settings
from app.middleware import register_middleware
from app.utils.cache import close_redis, redis_health_check
from app.utils.logger import get_logger, setup_logging

# Import all models so SQLAlchemy mappers can resolve string relationships
import app.models  # noqa: F401
from app.database import engine, Base

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    setup_logging()
    logger.info("app.startup", version=settings.APP_VERSION, env=settings.ENVIRONMENT.value)

    # Auto-create tables in dev (use Alembic in production)
    if not settings.is_production:
        from sqlalchemy.ext.asyncio import AsyncConnection

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("db.tables_created")

    # Initialize Sentry if configured
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1)
            logger.info("sentry.initialized")
        except Exception as exc:
            logger.warning("sentry.init_failed", error=str(exc))

    yield

    # Shutdown
    await close_redis()
    logger.info("app.shutdown")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # Register middleware
    register_middleware(app)

    # Include API routers
    app.include_router(v1_router)

    # Health check
    @app.get("/health", tags=["Health"])
    async def health():
        redis_ok = await redis_health_check()
        return {
            "status": "ok",
            "db": "ok",
            "redis": "ok" if redis_ok else "unavailable",
            "version": settings.APP_VERSION,
        }

    # Global exception handler (dev only)
    if not settings.is_production:
        @app.exception_handler(Exception)
        async def debug_exception_handler(request: Request, exc: Exception):
            import traceback
            tb = traceback.format_exc()
            logger.error("unhandled_exception", path=str(request.url.path), error=str(exc), traceback=tb)
            return JSONResponse(
                status_code=500,
                content={"detail": str(exc), "traceback": tb},
            )

    return app


app = create_app()
