import logging

logger = logging.getLogger("hiresense.ranker")

# Scoring weights — must sum to 100
WEIGHTS = {
    "jd_match": 35,       # How well resume matches job description
    "skills": 25,         # Number of relevant skills detected
    "repos": 15,          # GitHub public repos (original, not forks)
    "commits": 15,        # Total commits across repos
    "languages": 5,       # Programming language diversity
    "followers": 5,       # GitHub social proof
}


def rank_candidate(
    resume_data: dict, github_data: dict, jd_match_score: float
) -> dict:
    skills_count = resume_data.get("skills_count", len(resume_data.get("skills", [])))
    has_github = bool(github_data and "error" not in github_data and github_data.get("username"))
    
    public_repos = github_data.get("public_repos", 0) if has_github else 0
    followers = github_data.get("followers", 0) if has_github else 0
    total_commits = github_data.get("total_commits", 0) if has_github else 0
    languages_count = len(github_data.get("languages", {})) if has_github else 0

    if not has_github:
        # Redistribute the 40% github weights to jd_match (35) and skills (25)
        # Total base = 35 + 25 = 60
        jd_weight = (WEIGHTS["jd_match"] / 60.0) * 100.0
        skills_weight = (WEIGHTS["skills"] / 60.0) * 100.0
        
        jd_score      = (min(jd_match_score, 100) / 100) * jd_weight
        skills_score  = min(skills_count / 15, 1)  * skills_weight
        repos_score   = 0.0
        commits_score = 0.0
        lang_score    = 0.0
        follow_score  = 0.0
    else:
        # Standard weights
        jd_score      = (min(jd_match_score, 100) / 100) * WEIGHTS["jd_match"]
        skills_score  = min(skills_count / 15, 1)  * WEIGHTS["skills"]    # 15 skills = full score
        repos_score   = min(public_repos / 15, 1)  * WEIGHTS["repos"]     # 15 repos = full score
        commits_score = min(total_commits / 100, 1) * WEIGHTS["commits"]  # 100 commits = full score
        lang_score    = min(languages_count / 5, 1) * WEIGHTS["languages"]
        follow_score  = min(followers / 20, 1)      * WEIGHTS["followers"]

    final_score = round(
        jd_score + skills_score + repos_score + commits_score + lang_score + follow_score,
        2,
    )

    if final_score >= 70:
        grade = "A"
        recommendation = "Strongly Recommended"
    elif final_score >= 55:
        grade = "B"
        recommendation = "Recommended"
    elif final_score >= 40:
        grade = "C"
        recommendation = "Maybe"
    else:
        grade = "D"
        recommendation = "Not Recommended"

    logger.info(
        f"Candidate ranked: score={final_score}, grade={grade}, "
        f"jd={round(jd_score,1)}, skills={round(skills_score,1)}, "
        f"has_github={has_github}"
    )

    return {
        "final_score": final_score,
        "grade": grade,
        "recommendation": recommendation,
        "breakdown": {
            "jd_match_score": round(jd_score, 2),
            "skills_score": round(skills_score, 2),
            "repos_score": round(repos_score, 2),
            "commits_score": round(commits_score, 2),
            "languages_score": round(lang_score, 2),
            "followers_score": round(follow_score, 2),
        },
        "raw": {
            "jd_match_pct": jd_match_score,
            "skills_count": skills_count,
            "github_repos": public_repos,
            "github_commits": total_commits,
        },
    }
