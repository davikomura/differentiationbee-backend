from pydantic import BaseModel, StringConstraints
from typing import Annotated, Optional
from datetime import datetime

AnswerStr = Annotated[str, StringConstraints(min_length=1, max_length=800)]

class AttemptCreate(BaseModel):
    question_id: int
    user_answer: AnswerStr
    use_latex: bool = False
    time_taken_ms: int

class AttemptRead(BaseModel):
    id: int
    session_id: int
    level: int
    expression_latex: Optional[str]
    is_correct: bool
    score: int
    time_taken_ms: int
    created_at: datetime

    class Config:
        from_attributes = True

class AttemptResult(BaseModel):
    attempt: AttemptRead
    correct_derivative_latex: str