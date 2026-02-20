from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic import Field

class IssueQuestionRequest(BaseModel):
    session_id: int
    level: int = Field(ge=1, le=12)

class IssuedQuestionRead(BaseModel):
    question_id: int
    session_id: int
    level: int
    expression_str: str
    expression_latex: Optional[str] = None
    issued_at: datetime
    time_limit_ms: int


class DailyChallengeRead(BaseModel):
    challenge_date: str
    level: int
    expression_str: str
    expression_latex: Optional[str] = None
