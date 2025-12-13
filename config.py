import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Google API configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./careerflow.db")
    
    # Security configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "careerflow_default_secret_key")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # Frontend configuration
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Application configuration
    APP_TITLE = "CareerFlow AI"
    APP_DESCRIPTION = "The All-in-One AI Companion for Your Career Journey"
    APP_VERSION = "1.0.0"

# Create settings instance
settings = Settings()