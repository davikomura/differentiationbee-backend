# app/api/router.py
from fastapi import APIRouter
from app.modules.auth.router import router as auth_router
from app.modules.seasons.router import router as seasons_router
from app.modules.tiers.router import router as tiers_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(seasons_router, prefix="/seasons", tags=["Seasons"])
api_router.include_router(tiers_router, prefix="/tiers", tags=["Tiers"])