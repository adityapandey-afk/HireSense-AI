import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.user import User
from models.job import Job
from routes.auth import get_current_user, require_role

logger = logging.getLogger("hiresense.jobs")

router = APIRouter(prefix="/jobs", tags=["Jobs"])


class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    required_skills: str


class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    description: str
    required_skills: str
    recruiter_id: int

    class Config:
        from_attributes = True


@router.post("/", status_code=201)
def create_job(
    payload: JobCreate,
    current_user: User = Depends(require_role("recruiter")),
    db: Session = Depends(get_db),
):
    job = Job(
        recruiter_id=current_user.id,
        title=payload.title,
        company=payload.company,
        description=payload.description,
        required_skills=payload.required_skills,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    logger.info(f"Job created: {job.id} by recruiter {current_user.id}")
    return {"message": "Job created", "job_id": job.id}


@router.get("/")
def list_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    jobs = db.query(Job).order_by(Job.created_at.desc()).limit(50).all()
    return [
        {
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "description": j.description[:200] + "..." if len(j.description) > 200 else j.description,
            "required_skills": j.required_skills,
        }
        for j in jobs
    ]


@router.get("/{job_id}")
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/{job_id}", status_code=204)
def delete_job(
    job_id: int,
    current_user: User = Depends(require_role("recruiter")),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own jobs")
    db.delete(job)
    db.commit()
