from pydantic_settings import BaseSettings
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    ALPHA_VANTAGE_KEY: str = os.getenv("ALPHA_VANTAGE_KEY")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    LOG_LEVEL: str = "INFO"

    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    
    # Cache settings
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", 300)) 
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"



    AGENT_CONFIGS: Dict[str, Dict] = {
        "technical": {
            "class": "TechnicalAgent",
            "enabled": True,
            "confidence_threshold": 0.5
        },
        "sentiment": {
            "class": "SentimentAgent",
            "enabled": True,
            "confidence_threshold": 0.6
        },
        "risk": {
            "class": "RiskAgent",
            "enabled": True,
            "confidence_threshold": 0.7
        },
        "portfolio": {
            "class": "PortfolioAgent",
            "enabled": True,
            "confidence_threshold": 0.5
        }
    }

settings = Settings()