from fastapi import APIRouter
from app.api.auth.router import router as auth_router
from app.api.candidates.router import router as candidates_router
from app.api.jobs.router import router as jobs_router
from app.api.scoring.router import router as scoring_router
from app.api.templates.router import router as templates_router
from app.api.outreach.router import router as outreach_router
from app.api.dashboard.router import router as dashboard_router
from app.api.subscriptions.router import router as subscriptions_router
from app.api.teams.router import router as teams_router
from app.api.interviews.router import router as interviews_router
from app.api.onboarding.router import router as onboarding_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(candidates_router)
api_router.include_router(jobs_router)
api_router.include_router(scoring_router)
api_router.include_router(templates_router)
api_router.include_router(outreach_router)
api_router.include_router(dashboard_router)
api_router.include_router(subscriptions_router)
api_router.include_router(teams_router)
api_router.include_router(interviews_router)
api_router.include_router(onboarding_router)
