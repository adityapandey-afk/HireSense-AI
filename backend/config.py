import secrets
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GITHUB_TOKEN: str = ""
    EMAIL_USER: str = ""
    EMAIL_PASSWORD: str = ""

    # CORS - set to your frontend URL in production
    # e.g. "http://localhost:8501" for local Streamlit
    ALLOWED_ORIGINS: list[str] = ["http://localhost:8501", "http://127.0.0.1:8501"]

    class Config:
        env_file = ".env"


settings = Settings()
