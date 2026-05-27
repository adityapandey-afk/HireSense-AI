import logging
import time
from github import Github, GithubException
from config import settings

logger = logging.getLogger("hiresense.github")

# Max repos to scan — avoids 100+ API calls on large profiles
MAX_REPOS_TO_SCAN = 20
MAX_COMMITS_PER_REPO = 1  # We only need .totalCount, not all commits


def verify_github_profile(github_username: str) -> dict:
    if not github_username or not github_username.strip():
        return {"error": "GitHub username is required"}

    if not settings.GITHUB_TOKEN:
        logger.warning("No GITHUB_TOKEN set — using unauthenticated requests (rate limited)")

    g = Github(settings.GITHUB_TOKEN or None)

    try:
        user = g.get_user(github_username.strip())
        # Trigger the API call to validate user exists
        _ = user.public_repos
    except GithubException as e:
        if e.status == 404:
            return {"error": f"GitHub user '{github_username}' not found"}
        logger.error(f"GitHub API error for {github_username}: {e}")
        return {"error": f"GitHub API error: {e.data.get('message', str(e))}"}
    except Exception as e:
        logger.error(f"Unexpected GitHub error: {e}")
        return {"error": "Could not connect to GitHub"}

    languages: dict[str, int] = {}
    total_commits = 0
    repo_list = []
    scanned = 0

    try:
        repos = user.get_repos(type="owner", sort="updated")  # Most recent first
        for repo in repos:
            if scanned >= MAX_REPOS_TO_SCAN:
                break
            if repo.fork:
                continue

            scanned += 1
            lang = repo.language
            if lang:
                languages[lang] = languages.get(lang, 0) + 1

            try:
                commits = repo.get_commits(author=github_username)
                total_commits += commits.totalCount
            except GithubException:
                pass  # Some repos disable commit history — skip silently

            repo_list.append(
                {
                    "name": repo.name,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "url": repo.html_url,
                }
            )
    except GithubException as e:
        logger.error(f"Error fetching repos for {github_username}: {e}")

    return {
        "username": github_username,
        "name": user.name or github_username,
        "public_repos": user.public_repos,
        "followers": user.followers,
        "languages": languages,
        "total_commits": total_commits,
        "top_repos": repo_list[:5],
        "repos_scanned": scanned,
    }
