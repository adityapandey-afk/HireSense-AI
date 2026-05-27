import logging
from fastapi import APIRouter, Depends
from models.user import User
from routes.auth import get_current_user
from utils.github_verifier import verify_github_profile

logger = logging.getLogger("hiresense.github_route")

router = APIRouter(prefix="/github", tags=["GitHub"])


@router.get("/verify/{username}")
def verify_github(
    username: str,
    current_user: User = Depends(get_current_user),  # Auth required
):
    logger.info(f"GitHub verify requested by user {current_user.id} for: {username}")
    return verify_github_profile(username)
