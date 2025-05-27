import os
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_KEY: str
    INSTANCE_ID: str
    EVO_C_URL: str
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
    DATABASE_URL: PostgresDsn

    @property # Hot fix: cast env variable to a list
    def ALLOWED_EMAILS(self) -> list[str]:
        return [email.strip() for email in self.ALLOWED_EMAILS_RAW.split(",") if email.strip()]
    
    class Config:
        env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))


settings = Settings()
