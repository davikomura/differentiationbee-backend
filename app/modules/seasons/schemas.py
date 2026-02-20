# app/modules/seasons/schemas.py
from pydantic import BaseModel, ConfigDict, StringConstraints
from typing import Annotated, Optional, List
from datetime import datetime

SlugStr = Annotated[str, StringConstraints(min_length=2, max_length=60)]
LocaleStr = Annotated[str, StringConstraints(min_length=2, max_length=16)]
TitleStr = Annotated[str, StringConstraints(min_length=2, max_length=80)]

class SeasonTranslationCreate(BaseModel):
    locale: LocaleStr
    title: TitleStr
    description: Optional[str] = None

class SeasonCreate(BaseModel):
    slug: SlugStr
    starts_at: datetime
    ends_at: datetime
    translations: List[SeasonTranslationCreate]

class SeasonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    starts_at: datetime
    ends_at: datetime
    title: str
    description: Optional[str] = None