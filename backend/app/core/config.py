import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SecureSupply AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Secret Key for JWT
    SECRET_KEY: str = "securesupply-ai-super-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:////home/tracehanami/Github/SecureSupplyAI/backend/securesupply.db"
    )
    
    # Storage
    UPLOAD_DIR: str = "/home/tracehanami/Github/SecureSupplyAI/backend/uploads"
    REPORT_DIR: str = "/home/tracehanami/Github/SecureSupplyAI/backend/reports"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ]
    
    # External Vulnerability APIs
    OSV_API_URL: str = "https://api.osv.dev/v1/query"
    NVD_API_URL: str = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORT_DIR, exist_ok=True)
