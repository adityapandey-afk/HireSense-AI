# 🧠 HireSense AI — Intelligent Recruitment Platform

AI-powered recruitment tool that parses resumes, matches them against job descriptions, verifies GitHub profiles, and ranks candidates automatically.

---

## Features
- **Resume Parsing** — PDF & DOCX, extracts skills, email, phone
- **JD Matching** — Semantic similarity using SentenceTransformers
- **GitHub Verification** — Repos, commits, language diversity
- **AI Ranking** — Weighted scoring with grade & recommendation
- **Email Notifications** — Shortlist/reject emails via Gmail
- **Role-based Auth** — Separate flows for candidates and recruiters

---

## Quick Start (Local)

### 1. Clone & setup
```bash
cd backend
cp ../.env.example .env
# Fill in your values in .env
```

### 2. Generate a secure SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Paste the output into `.env` as `SECRET_KEY`.

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run backend
```bash
cd backend
uvicorn main:app --reload
# API docs at: http://localhost:8000/docs
```

### 5. Run frontend
```bash
streamlit run frontend/app.py
# Opens at: http://localhost:8501
```

---

## Docker (Recommended)
```bash
# Set your env variables first
export MYSQL_ROOT_PASSWORD=your_password
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export GITHUB_TOKEN=your_github_pat
export EMAIL_USER=your_gmail@gmail.com
export EMAIL_PASSWORD=your_app_password

docker-compose up --build
```

---

## Run Tests
```bash
pip install pytest httpx
pytest tests/ -v
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | ❌ | Register user |
| POST | `/auth/login` | ❌ | Login, get token |
| GET | `/auth/me` | ✅ | Get current user |
| POST | `/resume/upload` | ✅ | Parse resume |
| POST | `/resume/match` | ✅ | Match resume with JD |
| POST | `/rank/candidate` | ✅ | Full candidate ranking |
| GET | `/github/verify/{username}` | ✅ | GitHub profile data |
| POST | `/notify/email` | ✅ Recruiter | Send decision email |
| POST | `/jobs/` | ✅ Recruiter | Post a job |
| GET | `/jobs/` | ✅ | List jobs |
| GET | `/health` | ❌ | Health check |

---

## Security Notes
- **Never commit `.env`** — it's in `.gitignore`
- Use `python -c "import secrets; print(secrets.token_hex(32))"` for SECRET_KEY
- Use Gmail App Password (not your Gmail password) for EMAIL_PASSWORD
- Rotate your GitHub PAT regularly
