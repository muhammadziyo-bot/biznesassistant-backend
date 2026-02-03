from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:rakhmonov@localhost:5432/biznes_assistant"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "KctdGJjaKFvOM1G1O5RK4-HL3jzgqUvwLA0Mg4W8suQ"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Payment Gateways
    CLICK_MERCHANT_ID: Optional[str] = None
    CLICK_SERVICE_ID: Optional[str] = None
    CLICK_SECRET_KEY: Optional[str] = None
    
    PAYME_MERCHANT_ID: Optional[str] = None
    PAYME_SECRET_KEY: Optional[str] = None
    
    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    
    # Email (for future use)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".jpeg", ".png"]
    
    # Uzbekistan Tax Settings
    VAT_RATE: float = 0.12  # 12% VAT
    INCOME_TAX_RATE: float = 0.15  # 15% income tax for SMEs
    SOCIAL_TAX_RATE: float = 0.01  # 1% social tax
    
    class Config:
        env_file = ".env"

settings = Settings()
