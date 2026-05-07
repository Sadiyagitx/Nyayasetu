"""
NyayaSetu — Configuration
"""
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # API
    GEMINI_API_KEY    = os.environ.get("GEMINI_API_KEY", "")
    PRIMARY_MODEL     = "gemini-2.0-flash"
    FALLBACK_MODEL    = "gemini-1.5-flash"

    # Retry
    MAX_RETRIES       = 3
    RETRY_BASE_DELAY  = 2      # seconds
    REQUEST_TIMEOUT   = 30     # seconds

    # App
    SECRET_KEY        = os.environ.get("SECRET_KEY", "nyayasetu-secret-2024")
    DEBUG             = False
    PORT              = int(os.environ.get("PORT", 8080))

    # Demo mode — auto-activates when API fails
    DEMO_MODE_ENABLED = True
