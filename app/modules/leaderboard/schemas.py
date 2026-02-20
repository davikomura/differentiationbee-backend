from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    points: int


class SeasonLeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    total_score: int
    sessions_played: int
