"""V1 API router — aggregates all sub-routers."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.matches import router as matches_router
from app.api.v1.rewriter import router as rewriter_router
from app.api.v1.users import router as users_router
from app.api.v1.tenants import router as tenants_router
from app.api.v1.billing import router as billing_router
from app.api.v1.jobs_feed import router as jobs_feed_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(auth_router)
v1_router.include_router(resumes_router)
v1_router.include_router(jobs_router)
v1_router.include_router(matches_router)
v1_router.include_router(rewriter_router)
v1_router.include_router(users_router)
v1_router.include_router(tenants_router)
v1_router.include_router(billing_router)
v1_router.include_router(jobs_feed_router)
