from pydantic import BaseModel


class MyStatsRead(BaseModel):
    total_sessions: int
    total_attempts: int
    correct_attempts: int
    accuracy_pct: float
    total_score: int
    best_score: int
    average_time_ms: int


class LevelTimeStat(BaseModel):
    level: int
    attempts: int
    average_time_ms: int


class DailyEvolutionPoint(BaseModel):
    date: str
    attempts: int
    correct_attempts: int
    accuracy_pct: float
    total_score: int


class AdvancedStatsRead(BaseModel):
    total_sessions: int
    total_attempts: int
    correct_attempts: int
    accuracy_pct: float
    total_score: int
    best_score: int
    average_time_ms: int
    current_streak_days: int
    best_streak_days: int
    average_time_ms_by_level: list[LevelTimeStat]


class EvolutionRead(BaseModel):
    days: int
    points: list[DailyEvolutionPoint]
