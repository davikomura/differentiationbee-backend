# app/api/endpoints/validate.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.validator import validate_answer

router = APIRouter()

class ValidationRequest(BaseModel):
    question_str: str
    user_input: str
    time_taken: float

@router.post("/answer")
def validate_user_answer(payload: ValidationRequest):
    result = validate_answer(payload.question_str, payload.user_input, payload.time_taken)
    return result