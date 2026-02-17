from pydantic import BaseModel, StringConstraints
from typing import Annotated, Optional
from datetime import datetime

ModeStr = Annotated[str, StringConstraints(min_length=3, max_length=20)]

class GameSessionCreate(BaseModel):
    mode: ModeStr = "practice"
    level: Optional[int] = None
    seed: Optional[int] = None

class GameSessionRead(BaseModel):
    id: int
    mode: str
    level: Optional[int]
    seed: Optional[int]
    started_at: datetime
    ended_at: Optional[datetime]
    is_active: bool
    total_questions: int
    correct_answers: int
    total_score: int

    class Config:
        from_attributes = True

class TierRead(BaseModel):
    key: str
    min_points: int
    max_points: Optional[int]
    title: str
    description: Optional[str] = None

class SessionFinishResult(BaseModel):
    session: GameSessionRead
    delta_points: int
    points_before: int
    points_after: int
    tier_before: TierRead
    tier_after: TierRead