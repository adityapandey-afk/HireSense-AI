import logging
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger("hiresense.jd_matcher")

# Load once at module level — avoids reloading on every request
_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Loading SentenceTransformer model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Model loaded.")
    return _model


def match_resume_with_jd(resume_text: str, jd_text: str) -> dict:
    if not resume_text or not jd_text:
        logger.warning("Empty resume or JD text passed to matcher")
        return {"match_score": 0.0, "verdict": "Insufficient Data"}

    model = get_model()
    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    jd_emb = model.encode(jd_text, convert_to_tensor=True)

    similarity = util.cos_sim(resume_emb, jd_emb)
    score = round(float(similarity[0][0]) * 100, 2)

    if score >= 70:
        verdict = "Strong Match"
    elif score >= 50:
        verdict = "Moderate Match"
    else:
        verdict = "Weak Match"

    logger.info(f"JD match score: {score}% — {verdict}")
    return {"match_score": score, "verdict": verdict}
