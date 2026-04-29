import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # API Keys
    dashscope_api_key: str = ""

    # Database paths
    metadata_db_path: str = "./data/metadata.db"
    business_db_path: str = "./data/business.db"

    # CORS
    cors_origins: str = "http://localhost:5174,http://127.0.0.1:5174"

    # LLM Config
    llm_model: str = "qwen3-32b"
    llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # App
    app_name: str = "AIData - Intelligent Data Analysis System"
    debug: bool = True

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
