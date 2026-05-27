import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes import auth, resume, github, ranking, notify, jobs, candidate, recruiter
from config import settings

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("hiresense")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HireSense AI",
    description="Intelligent Recruitment Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Fixed: no more wildcard *
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(github.router)
app.include_router(ranking.router)
app.include_router(notify.router)
app.include_router(jobs.router)
app.include_router(candidate.router)
app.include_router(recruiter.router)


@app.get("/")
def root():
    return {"message": "HireSense AI is running!", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
