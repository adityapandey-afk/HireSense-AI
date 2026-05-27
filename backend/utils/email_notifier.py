import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings

logger = logging.getLogger("hiresense.email")

SHORTLIST_TEMPLATE = """Dear {name},

Congratulations!

We are pleased to inform you that your application has been SHORTLISTED.

Your HireSense AI Score: {score}%

Our team will contact you shortly regarding the next steps.

Best Regards,
HireSense AI Team"""

REJECT_TEMPLATE = """Dear {name},

Thank you for applying.

After careful review, we regret to inform you that your application has not been
selected at this time.

Your HireSense AI Score: {score}%

We encourage you to keep improving and apply again in the future.

Best Regards,
HireSense AI Team"""


def send_email(to_email: str, candidate_name: str, decision: str, score: float) -> dict:
    if not settings.EMAIL_USER or not settings.EMAIL_PASSWORD:
        logger.warning("Email credentials not configured — skipping send")
        return {"status": "skipped", "reason": "Email not configured"}

    subject = "HireSense AI — Application Update"
    template = SHORTLIST_TEMPLATE if decision == "shortlist" else REJECT_TEMPLATE
    body = template.format(name=candidate_name, score=round(score, 1))

    msg = MIMEMultipart()
    msg["From"] = settings.EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
            server.starttls()
            server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_USER, to_email, msg.as_string())
        logger.info(f"Email sent to {to_email} — decision: {decision}")
        return {"status": "sent"}
    except smtplib.SMTPAuthenticationError:
        logger.error("Email auth failed — check EMAIL_USER and EMAIL_PASSWORD in .env")
        return {"status": "error", "reason": "Authentication failed"}
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending to {to_email}: {e}")
        return {"status": "error", "reason": str(e)}
    except Exception as e:
        logger.error(f"Unexpected email error: {e}")
        return {"status": "error", "reason": "Unexpected error"}
