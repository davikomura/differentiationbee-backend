from fastapi import APIRouter
from app.api.endpoints import question, validate, ranking, auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(question.router, prefix="/question", tags=["Question"])
api_router.include_router(validate.router, prefix="/validate", tags=["Validation"])
api_router.include_router(ranking.router, prefix="/ranking", tags=["Ranking"])
