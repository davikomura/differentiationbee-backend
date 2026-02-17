# app/modules/tiers/schemas.py
from pydantic import BaseModel
from typing import Optional, List

class TierRead(BaseModel):
    key: str
    min_points: int
    max_points: Optional[int]
    title: str
    description: Optional[str] = None

class TiersListRead(BaseModel):
    items: List[TierRead]

class MyTierRead(BaseModel):
    points: int
    tier: TierRead