# app/schemas/session_question.py
from pydantic import BaseModel, Field

class QuestionAnswerCreate(BaseModel):
    question_instance_id: str = Field(min_length=10, max_length=64)
    user_answer: str
    use_latex: bool = False