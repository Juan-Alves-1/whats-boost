import os
from enum import Enum
from typing import List
from pydantic import Field 
from pydantic_settings import BaseSettings

class Env(Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"

class Settings(BaseSettings):
    ENV: Env

    HOST: str
    PORT: int

    EVO_SERVER_URL: str
    EVO_API_KEY: str
    EVO_INSTANCE_ID: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    SECRET_KEY: str
    ALLOWED_EMAILS: str
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")

    AMAZON_ACCESS_KEY: str
    AMAZON_SECRET_KEY: str
    AMAZON_PARTNER_TAG: str
    AMAZON_MARKETPLACE: str
    AMAZON_HOST: str
    AMAZON_REGION: str

    BTN_SESSION: str
    BTN_SESSION_SIG: str
    BTN_LOGGED_IN: str
    BTN_LOGGED_IN_SIG: str
    BTN_PROFILE_REMINDER: str

    OPENAI_HOST: str
    OPENAI_KEY: str
    OPENAI_MODEL: str

    MIN_TYPING_SPEED: int = 10
    MAX_TYPING_SPEED: int = 18

    MAX_REDIS_QUEUE_PER_USER: int = 25

    @property # Hot fix: cast env variable to a list
    def ALLOWED_EMAILS(self) -> list[str]:
        return [email.strip() for email in self.ALLOWED_EMAILS_RAW.split(",") if email.strip()]
    
    class Config:
        env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
        extra = "allow"


settings = Settings()
