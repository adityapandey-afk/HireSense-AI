import os
import uuid
import logging
import shutil
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.job import Job
from models.match import MatchResult
from routes.auth import get_current_user
from utils.resume_parser import parse_resume
from utils.jd_matcher import match_resume_with_jd
from utils.github_verifier import verify_github_profile
from utils.ml_ranker import rank_candidate

logger = logging.getLogger("hiresense.ranking")

router = APIRouter(prefix="/rank", tags=["Ranking"])

UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/candidate")
async def rank_candidate_api(
    file: UploadFile = File(...),
    jd_text: str = "",
    github_username: str = "",
    job_id: int = Query(None),
    current_user: User = Depends(get_current_user),  # Auth required
    db: Session = Depends(get_db),
):
    if job_id:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        jd_text = job.description

    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="Job description is required")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {".pdf", ".docx"}:
        raise HTTPException(status_code=400, detail="Only PDF or DOCX allowed")

    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        resume_data = parse_resume(file_path)
        jd_result = match_resume_with_jd(resume_data["raw_text"], jd_text)
        github_data = verify_github_profile(github_username) if github_username else {}
        ranking = rank_candidate(resume_data, github_data, jd_result["match_score"])
        
        # Save to database if matching against a job
        match_id = None
        if job_id:
            cand_email = resume_data.get("email") or current_user.email
            cand_name = resume_data.get("name") or current_user.full_name
            
            candidate_user = db.query(User).filter(User.email == cand_email, User.role == "candidate").first()
            if not candidate_user:
                # Create placeholder user
                from routes.auth import hash_password
                import secrets
                candidate_user = User(
                    full_name=cand_name,
                    email=cand_email,
                    hashed_password=hash_password(secrets.token_hex(16)),
                    role="candidate"
                )
                db.add(candidate_user)
                db.commit()
                db.refresh(candidate_user)
            
            # Match required skills
            req_skills = [s.strip().lower() for s in job.required_skills.split(",") if s.strip()]
            candidate_skills = [s.lower() for s in resume_data.get("skills", [])]
            gaps = [s for s in req_skills if s not in candidate_skills]
            skill_gaps_str = ", ".join(gaps)
            
            match_res = MatchResult(
                candidate_id=candidate_user.id,
                job_id=job_id,
                match_score=ranking["final_score"],
                skill_gaps=skill_gaps_str,
                status="pending"
            )
            db.add(match_res)
            db.commit()
            db.refresh(match_res)
            match_id = match_res.id
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    logger.info(
        f"Ranking done for user {current_user.id} — score: {ranking['final_score']}"
    )

    return {
        "candidate_name": resume_data["name"] or current_user.full_name,
        "candidate_email": resume_data["email"] or current_user.email,
        "skills": resume_data["skills"],
        "jd_match": jd_result,
        "github": {
            "repos": github_data.get("public_repos", 0),
            "commits": github_data.get("total_commits", 0),
            "languages": github_data.get("languages", {}),
            "top_repos": github_data.get("top_repos", []),
        },
        "ranking": ranking,
        "match_id": match_id,
    }
