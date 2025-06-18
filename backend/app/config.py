import os
from dotenv import load_dotenv
from typing import ClassVar
from pydantic_settings import BaseSettings

load_dotenv()

LOGSTASH_PORT = os.getenv('LOGSTASH_PORT', '9601')
LOGSTASH_HOST = os.getenv('LOGSTASH_HOST', 'localhost')


class Settings(BaseSettings):
    app_environment: str = os.environ.get("APP_ENVIRONMENT", "development")
    app_name: str = os.environ.get("APP_NAME", "eels-and-escalators-backend")
    api_info_title: str = "Eels and Escalators API"
    api_info_description: str = "Eels and Escalators Backend"
    api_info_version: str = "0.0.0"
    api_info_port: int = 8000
    api_info_host: str = "0.0.0.0"
    debug: ClassVar[bool]
    log_level: ClassVar[str]
    if app_environment == "development":
        debug = (os.getenv('DEBUG', 'True').lower() == 'true')
        log_level = os.environ.get('LOG_LEVEL', 'DEBUG')
    else:
        debug = (os.getenv('DEBUG', 'False').lower() == 'false')
        log_level = os.environ.get('LOG_LEVEL', 'INFO')

    root_path_prefix: str = "/eels-and-escalators/api/v1"


settings = Settings()
