# app/config.py
from typing import Optional

from pydantic import EmailStr


class Settings:
    PROJECT_NAME: str = "MultiTasker API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "jLnqie0CsxebL-F51OU9hUpiwHSvrKDzXlCd1TNwDm0="
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USERNAME: str = "regressor04@gmail.com"
    MAIL_PASSWORD: str = "cakgfppvbmipbikr"
    MAIL_FROM: str = "regressor04@gmail.com"
    BASE_URL: str = "http://localhost:8000"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost", "http://localhost:3000"]
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    FIRST_SUPERUSER: Optional[EmailStr] = None
    FIRST_SUPERUSER_PASSWORD: Optional[str] = None
settings = Settings()