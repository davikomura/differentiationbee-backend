# app/api/router.py
from fastapi import APIRouter
from app.modules.auth.router import router as auth_router
from app.modules.seasons.router import router as seasons_router
from app.modules.tiers.router import router as tiers_router
from app.modules.sessions.router import router as sessions_router
from app.modules.attempts.router import router as attempts_router
from app.modules.game.router import router as game_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(seasons_router, prefix="/seasons", tags=["Seasons"])
api_router.include_router(tiers_router, prefix="/tiers", tags=["Tiers"])
api_router.include_router(sessions_router, prefix="/sessions", tags=["Sessions"])
api_router.include_router(attempts_router, prefix="/attempts", tags=["Attempts"])
api_router.include_router(game_router, prefix="/game", tags=["Game"])