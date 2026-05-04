"""CORS, request logging, and rate-limiting middleware."""

from __future__ import annotations

import time

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings
from app.utils.logger import generate_trace_id

logger = structlog.get_logger("middleware")

# ── Rate Limiter ──────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


def register_middleware(app: FastAPI) -> None:
    """Attach all middleware to the FastAPI app."""

    # ── Step 1: Logging middleware (registered first = runs LAST)
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next) -> Response:
        trace_id = generate_trace_id()
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(trace_id=trace_id)

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 1)

        logger.info(
            "http.request",
            method=request.method,
            path=str(request.url.path),
            status=response.status_code,
            duration_ms=duration_ms,
            trace_id=trace_id,
        )

        response.headers["X-Trace-ID"] = trace_id
        return response

    # ── Step 2: CORS (registered last = runs FIRST)
    if settings.is_production:
        origins = [settings.FRONTEND_URL]
    else:
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            settings.FRONTEND_URL,
        ]

    origins = list(dict.fromkeys(origins))

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )  