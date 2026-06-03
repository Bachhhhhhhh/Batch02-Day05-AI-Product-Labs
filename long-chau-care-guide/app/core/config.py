import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the long-chau-care-guide root directory
# app/core/config.py -> app/core -> app -> root
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=True)

# Define environment variables with fallbacks
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))  # Default 10 seconds timeout

# Model configuration
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.5"))
ALLOW_OUT_OF_SCOPE = os.getenv("ALLOW_OUT_OF_SCOPE", "False").lower() in ("true", "1", "yes")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))

# Internal Mock API configuration
INTERNAL_API_PORT = int(os.getenv("PORT", "8000"))
INTERNAL_API_HOST = os.getenv("HOST", "127.0.0.1")
INTERNAL_API_URL = f"http://{INTERNAL_API_HOST}:{INTERNAL_API_PORT}/api/internal"

# Define log level: INFO by default, can be set to DEBUG
# Log level remains for logger.py to import
LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)
