# app/schemas/ranking.py
from pydantic import BaseModel

class FinishSessionRequest(BaseModel):
    session_id: int