from fastapi import APIRouter, Query
from app.services.generator import generate_random_function

router = APIRouter()

@router.get("/generate")
def generate_question(level: int = Query(1, ge=1, le=10)):
    data = generate_random_function(level)
    
    return {
        "question_id": data["id"],
        "expression_latex": data["expression_latex"],
        "expression_str": data["expression_str"],
    }
