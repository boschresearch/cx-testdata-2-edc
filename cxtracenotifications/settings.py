import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    EDC_ENDPOINT = ''
    EDC_API_KEY_NAME = 'X-Api-Key'
    EDC_API_KEY = '123456'
    class Config:
        env_file = os.getenv('ENV_FILE', '.env') # if ENV_FILE is not set, we read env vars from .env by default

settings: Settings = Settings()

QUALITY_INVESTIGATION_NOTIFICATION_ASSET_ID = "qualityinvestigationnotification-receive"
