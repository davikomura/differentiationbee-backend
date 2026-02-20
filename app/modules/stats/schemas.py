from pydantic import BaseModel


class MyStatsRead(BaseModel):
    total_sessions: int
    total_attempts: int
    correct_attempts: int
    accuracy_pct: float
    total_score: int
    best_score: int
    average_time_ms: int
