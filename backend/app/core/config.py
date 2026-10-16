import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = os.getenv("APP_NAME", "EvidentAI - Adaptive Learning & Integrity Engine")
    VERSION: str = "1.2.0"
    API_PREFIX: str = "/api"

    # Integrity Analysis Thresholds
    LARGE_PASTE_CHAR_THRESHOLD: int = int(os.getenv("LARGE_PASTE_CHAR_THRESHOLD", "50"))
    LARGE_PASTE_HIGH_SEVERITY_CHARS: int = int(os.getenv("LARGE_PASTE_HIGH_SEVERITY_CHARS", "150"))
    RAPID_INSERT_CHAR_THRESHOLD: int = int(os.getenv("RAPID_INSERT_CHAR_THRESHOLD", "200"))
    RAPID_INSERT_WINDOW_MS: int = int(os.getenv("RAPID_INSERT_WINDOW_MS", "2000"))
    LOW_EDIT_MAX_DELETES: int = int(os.getenv("LOW_EDIT_MAX_DELETES", "2"))
    LOW_EDIT_MIN_PASTED_CHARS: int = int(os.getenv("LOW_EDIT_MIN_PASTED_CHARS", "30"))

    # Sandbox execution limits
    SANDBOX_TIMEOUT_SECONDS: float = float(os.getenv("SANDBOX_TIMEOUT_SECONDS", "3.0"))
    SANDBOX_MAX_OUTPUT_CHARS: int = int(os.getenv("SANDBOX_MAX_OUTPUT_CHARS", "50000"))

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./evidentai.db")

settings = Settings()
