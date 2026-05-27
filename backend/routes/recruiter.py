import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import sqlalchemy
from database import get_db
from models.user import User
from models.job import Job
from models.match import MatchResult
from routes.auth import require_role

logger = logging.getLogger("hiresense.recruiter")

router = APIRouter(prefix="/recruiter", tags=["Recruiter"])


@router.get("/dashboard")
def dashboard(
    current_user: User = Depends(require_role("recruiter")),
    db: Session = Depends(get_db)
):
    # count jobs posted by this recruiter
    jobs_count = db.query(Job).filter(Job.recruiter_id == current_user.id).count()
    
    # get all job IDs posted by this recruiter
    job_ids = [j.id for j in db.query(Job.id).filter(Job.recruiter_id == current_user.id).all()]
    
    app_count = 0
    shortlisted_count = 0
    rejected_count = 0
    avg_score = 0.0
    
    if job_ids:
        app_count = db.query(MatchResult).filter(MatchResult.job_id.in_(job_ids)).count()
        shortlisted_count = db.query(MatchResult).filter(
            MatchResult.job_id.in_(job_ids), MatchResult.status == "shortlist"
        ).count()
        rejected_count = db.query(MatchResult).filter(
            MatchResult.job_id.in_(job_ids), MatchResult.status == "reject"
        ).count()
        
        # calculate average score
        res = db.query(sqlalchemy.func.avg(MatchResult.match_score)).filter(MatchResult.job_id.in_(job_ids)).scalar()
        avg_score = round(float(res), 2) if res is not None else 0.0
    
    return {
        "recruiter": current_user.full_name,
        "jobs_posted": jobs_count,
        "total_applications": app_count,
        "shortlisted": shortlisted_count,
        "rejected": rejected_count,
        "average_match_score": avg_score,
    }


@router.get("/jobs")
def get_recruiter_jobs(
    current_user: User = Depends(require_role("recruiter")),
    db: Session = Depends(get_db),
):
    jobs = db.query(Job).filter(Job.recruiter_id == current_user.id).order_by(Job.created_at.desc()).all()
    return [
        {
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "description": j.description,
            "required_skills": j.required_skills,
            "created_at": j.created_at.isoformat() if j.created_at else None,
        }
        for j in jobs
    ]


@router.get("/jobs/{job_id}/applications")
def get_job_applications(
    job_id: int,
    current_user: User = Depends(require_role("recruiter")),
    db: Session = Depends(get_db),
):
    # Verify recruiter owns the job
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to view applications for this job")

    applications = db.query(MatchResult, User).join(
        User, MatchResult.candidate_id == User.id
    ).filter(MatchResult.job_id == job_id).order_by(MatchResult.match_score.desc()).all()

    return [
        {
            "match_id": m.id,
            "candidate_id": u.id,
            "candidate_name": u.full_name,
            "candidate_email": u.email,
            "match_score": m.match_score,
            "skill_gaps": m.skill_gaps,
            "status": m.status,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m, u in applications
    ]


@router.post("/applications/{match_id}/status")
def update_application_status(
    match_id: int,
    status: str,
    current_user: User = Depends(require_role("recruiter")),
    db: Session = Depends(get_db),
):
    if status not in ["shortlist", "reject", "pending"]:
        raise HTTPException(status_code=400, detail="Status must be shortlist, reject, or pending")

    match_res = db.query(MatchResult).filter(MatchResult.id == match_id).first()
    if not match_res:
        raise HTTPException(status_code=404, detail="Application not found")

    # Verify recruiter owns the job
    job = db.query(Job).filter(Job.id == match_res.job_id).first()
    if not job or job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to modify this application")

    match_res.status = status
    db.commit()
    db.refresh(match_res)
    logger.info(f"Recruiter {current_user.id} updated application {match_id} status to {status}")
    return {"message": "Status updated successfully", "status": status}
