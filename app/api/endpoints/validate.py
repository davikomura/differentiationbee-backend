# app/api/endpoints/validate.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.validator import validate_answer

router = APIRouter()

class ValidationRequest(BaseModel):
    question_str: str
    user_input: str
    time_taken: float
    level: int
    use_latex: bool = False

@router.post("/answer")
def validate_user_answer(payload: ValidationRequest):
    result = validate_answer(
        original_expr_str=payload.question_str,
        user_input_str=payload.user_input,
        time_taken=payload.time_taken,
        level=payload.level,
        use_latex=payload.use_latex
    )
    return result
