import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = os.getenv("APP_NAME", "EvidentAI - Session Replay & Integrity Engine")
    VERSION = "1.1.0"
    API_PREFIX = "/api"
    LARGE_PASTE_CHAR_THRESHOLD = int(os.getenv("LARGE_PASTE_CHAR_THRESHOLD", "50"))
    LARGE_PASTE_HIGH_SEVERITY_CHARS = int(os.getenv("LARGE_PASTE_HIGH_SEVERITY_CHARS", "150"))
    RAPID_INSERT_CHAR_THRESHOLD = int(os.getenv("RAPID_INSERT_CHAR_THRESHOLD", "200"))
    RAPID_INSERT_WINDOW_MS = int(os.getenv("RAPID_INSERT_WINDOW_MS", "2000"))
    LOW_EDIT_MAX_DELETES = int(os.getenv("LOW_EDIT_MAX_DELETES", "2"))
    LOW_EDIT_MIN_PASTED_CHARS = int(os.getenv("LOW_EDIT_MIN_PASTED_CHARS", "30"))
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./evidentai.db")

settings = Settings()
