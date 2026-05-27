import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.job import Job
from models.match import MatchResult
from routes.auth import get_current_user, require_role

logger = logging.getLogger("hiresense.candidate")

router = APIRouter(prefix="/candidate", tags=["Candidate"])


@router.get("/profile")
def get_profile(current_user: User = Depends(require_role("candidate"))):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
    }


@router.get("/applications")
def get_applications(
    current_user: User = Depends(require_role("candidate")),
    db: Session = Depends(get_db),
):
    results = db.query(MatchResult, Job).join(
        Job, MatchResult.job_id == Job.id
    ).filter(MatchResult.candidate_id == current_user.id).order_by(MatchResult.created_at.desc()).all()
    
    return [
        {
            "match_id": m.id,
            "job_id": j.id,
            "job_title": j.title,
            "company": j.company,
            "match_score": m.match_score,
            "status": m.status,
            "skill_gaps": m.skill_gaps,
            "applied_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m, j in results
    ]
