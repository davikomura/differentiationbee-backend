from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class IssueQuestionRequest(BaseModel):
    session_id: int
    level: int

class IssuedQuestionRead(BaseModel):
    question_id: int
    session_id: int
    level: int
    expression_str: str
    expression_latex: Optional[str] = None
    issued_at: datetime
    time_limit_ms: int