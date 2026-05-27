import os
import uuid
import logging
import shutil
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from routes.auth import get_current_user
from utils.resume_parser import parse_resume
from utils.jd_matcher import match_resume_with_jd

logger = logging.getLogger("hiresense.resume")

router = APIRouter(prefix="/resume", tags=["Resume"])

UPLOAD_DIR = "uploads/"
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE_MB = 5
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _save_file(file: UploadFile) -> str:
    """Save uploaded file with a unique name. Returns saved path."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF or DOCX allowed")

    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Check size after saving
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size is {MAX_FILE_SIZE_MB}MB",
        )

    return file_path


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),  # Auth required
    db: Session = Depends(get_db),
):
    file_path = _save_file(file)
    try:
        parsed = parse_resume(file_path)
    finally:
        # Clean up temp file after parsing
        if os.path.exists(file_path):
            os.remove(file_path)

    logger.info(f"Resume parsed for user {current_user.id}: {len(parsed['skills'])} skills found")
    return {
        "message": "Resume uploaded and parsed successfully",
        "original_filename": file.filename,
        "name": parsed["name"],
        "email": parsed["email"],
        "phone": parsed["phone"],
        "skills": parsed["skills"],
        "skills_count": parsed["skills_count"],
    }


@router.post("/match")
async def match_with_jd(
    file: UploadFile = File(...),
    jd_text: str = "",
    current_user: User = Depends(get_current_user),  # Auth required
):
    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")

    file_path = _save_file(file)
    try:
        parsed = parse_resume(file_path)
        result = match_resume_with_jd(parsed["raw_text"], jd_text)
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return {
        "original_filename": file.filename,
        "skills": parsed["skills"],
        "match_score": result["match_score"],
        "verdict": result["verdict"],
    }
