import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_KEY: str
    INSTANCE_ID: str
    EVO_C_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
