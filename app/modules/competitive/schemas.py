from pydantic import BaseModel, Field


class RankedQueueRequest(BaseModel):
    level: int | None = Field(default=None, ge=1, le=12)


class RankedQueueResponse(BaseModel):
    status: str
    message: str
    session_id: int | None = None
    opponent_username: str | None = None
    level: int | None = None


class RankedResolutionRead(BaseModel):
    status: str
    detail: str
    delta_points: int = 0
    points_after: int
