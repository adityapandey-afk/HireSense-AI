"""Tests for the ML ranker (no DB/API needed)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from utils.ml_ranker import rank_candidate


def test_strong_candidate():
    resume = {"skills": ["python", "fastapi", "docker", "aws", "sql", "react", "git"], "skills_count": 7}
    github = {"public_repos": 20, "followers": 30, "total_commits": 150, "languages": {"Python": 5, "JS": 3}}
    result = rank_candidate(resume, github, jd_match_score=85.0)
    assert result["grade"] in ["A", "B"]
    assert result["final_score"] > 50


def test_weak_candidate():
    resume = {"skills": ["python"], "skills_count": 1}
    github = {"public_repos": 1, "followers": 0, "total_commits": 5, "languages": {}}
    result = rank_candidate(resume, github, jd_match_score=20.0)
    assert result["grade"] in ["C", "D"]
    assert result["final_score"] < 50


def test_score_is_bounded():
    resume = {"skills": list(range(100)), "skills_count": 100}
    github = {"public_repos": 999, "followers": 9999, "total_commits": 9999, "languages": {str(i): i for i in range(50)}}
    result = rank_candidate(resume, github, jd_match_score=100.0)
    assert result["final_score"] <= 100


def test_breakdown_keys_present():
    resume = {"skills": [], "skills_count": 0}
    github = {}
    result = rank_candidate(resume, github, jd_match_score=0.0)
    assert "breakdown" in result
    assert "jd_match_score" in result["breakdown"]
