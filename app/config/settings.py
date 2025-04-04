import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_KEY: str
    INSTANCE_ID: str
    EVO_C_URL: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    SECRET_KEY: str

    class Config:
        env_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))


settings = Settings()
