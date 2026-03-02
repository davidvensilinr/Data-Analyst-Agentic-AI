from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Autonomous Data Analyst"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./data/analyst.db"
    # For production use PostgreSQL:
    # DATABASE_URL: str = "postgresql://user:password@localhost/analyst_db"
    
    # File Storage
    UPLOAD_DIR: str = "./data/uploads"
    PROCESSED_DIR: str = "./data/processed"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DEFAULT_LLM_PROVIDER: str = "openai"  # openai, anthropic, mock
    MAX_TOKENS_PER_REQUEST: int = 4000
    TEMPERATURE: float = 0.1
    
    # Execution Limits
    MAX_QUERY_ROWS: int = 100000
    QUERY_TIMEOUT_SECONDS: int = 30
    MAX_MEMORY_MB: int = 2048
    
    # Safety & Guardrails
    REQUIRE_HUMAN_APPROVAL: bool = True
    READ_ONLY_MODE: bool = False
    SANITIZE_LOGS: bool = True
    SENSITIVE_COLUMNS: List[str] = ["ssn", "credit_card", "password", "email", "phone"]
    
    # WebSocket Configuration
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 100
    
    # Vector DB (Optional)
    ENABLE_VECTOR_DB: bool = False
    VECTOR_DB_PATH: str = "./data/vector_db"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Testing
    MOCK_LLM_MODE: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
