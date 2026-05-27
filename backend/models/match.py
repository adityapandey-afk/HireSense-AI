from sqlalchemy import Column, Integer, Float, Text, ForeignKey, DateTime, String
from sqlalchemy.sql import func
from database import Base  # Fixed: was "from backend.database import Base"


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    match_score = Column(Float, nullable=False)
    skill_gaps = Column(Text, nullable=True)
    status = Column(String(50), server_default="pending", default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GitHubVerification(Base):
    __tablename__ = "github_verification"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    github_username = Column(String(100), nullable=False)
    project_name = Column(String(200), nullable=False)
    exists = Column(Integer, default=0)
    tech_stack_match = Column(Float, default=0.0)
    authenticity_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
