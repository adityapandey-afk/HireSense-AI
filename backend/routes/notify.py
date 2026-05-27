import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from models.user import User
from routes.auth import get_current_user, require_role
from utils.email_notifier import send_email

logger = logging.getLogger("hiresense.notify")

router = APIRouter(prefix="/notify", tags=["Notifications"])


class EmailRequest(BaseModel):
    to_email: EmailStr
    candidate_name: str
    decision: str
    score: float


@router.post("/email")
def send_notification(
    req: EmailRequest,
    current_user: User = Depends(require_role("recruiter")),  # Only recruiters can notify
):
    if req.decision not in ["shortlist", "reject"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Decision must be 'shortlist' or 'reject'")

    logger.info(
        f"Recruiter {current_user.id} sending {req.decision} email to {req.to_email}"
    )
    result = send_email(req.to_email, req.candidate_name, req.decision, req.score)
    return result
