import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_KEY: str
    INSTANCE_ID: str
    EVO_C_URL: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    SECRET_KEY: str
    ALLOWED_EMAILS: List[str] # Needs to be fixed in order to accommodate more emails
    ALLOWED_EMAILS1: List[str] # Needs to be fixed in order to accommodate more emails

    class Config:
        env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))


settings = Settings()
