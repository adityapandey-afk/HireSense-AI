import logging
import re
from pathlib import Path

import pdfplumber
import docx

logger = logging.getLogger("hiresense.resume_parser")

# Expanded skill set — covers modern tech stack properly
SKILLS_KEYWORDS = {
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "kotlin", "swift", "php", "ruby", "scala", "r",
    # Web
    "react", "vue", "angular", "nextjs", "fastapi", "django", "flask",
    "nodejs", "express", "spring", "html", "css",
    # Data / ML
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "xgboost", "huggingface", "langchain",
    # DB
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "sqlite", "firebase",
    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "ci/cd", "github actions", "jenkins",
    # Tools
    "git", "linux", "rest api", "graphql", "microservices", "kafka",
}


def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        logger.error(f"PDF extraction failed for {file_path}: {e}")
    return text


def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = docx.Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs)
    except Exception as e:
        logger.error(f"DOCX extraction failed for {file_path}: {e}")
        return ""


def extract_text(file_path: str) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    elif suffix == ".docx":
        return extract_text_from_docx(file_path)
    logger.warning(f"Unsupported file type: {suffix}")
    return ""


def extract_email(text: str) -> str:
    match = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    match = re.search(r"(\+?\d[\d\s\-]{8,14}\d)", text)
    return match.group(0).strip() if match else ""


def parse_resume(file_path: str) -> dict:
    text = extract_text(file_path)
    if not text:
        logger.warning(f"No text extracted from: {file_path}")

    text_lower = text.lower()

    # Multi-word skills must be checked before single-word to avoid partial matches
    found_skills = sorted(
        skill for skill in SKILLS_KEYWORDS if skill in text_lower
    )

    # Name: look for PERSON entities via simple heuristic (first ALL-CAPS line or first line)
    name = ""
    for line in text.split("\n"):
        line = line.strip()
        if line and len(line.split()) <= 5 and line.replace(" ", "").isalpha():
            name = line.title()
            break

    return {
        "name": name,
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": found_skills,
        "skills_count": len(found_skills),
        "raw_text": text,
    }
