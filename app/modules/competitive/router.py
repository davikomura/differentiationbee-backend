from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.i18n import get_request_locale
from app.db.session import get_db
from app.modules.auth.router import get_current_user
from app.modules.competitive.schemas import RankedQueueRequest, RankedQueueResponse, RankedResolutionRead
from app.modules.competitive.service import join_ranked_queue, ranked_queue_status, resolve_ranked_session
from app.modules.users.models import User

router = APIRouter()


@router.post("/queue", response_model=RankedQueueResponse)
def queue_ranked(
    payload: RankedQueueRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return join_ranked_queue(db, user=current_user, level=payload.level, locale=get_request_locale(request))


@router.get("/queue/status", response_model=RankedQueueResponse)
def queue_status(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return ranked_queue_status(current_user.id, locale=get_request_locale(request))


@router.post("/resolve/{session_id}", response_model=RankedResolutionRead)
def resolve_ranked(
    session_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return resolve_ranked_session(
        db,
        session_id=session_id,
        requester_user_id=current_user.id,
        locale=get_request_locale(request),
    )
