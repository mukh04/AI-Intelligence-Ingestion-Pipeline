from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_ARXIV_RESULTS = int(os.getenv("MAX_ARXIV_RESULTS", "1000"))
REQUEST_CONCURRENCY = int(os.getenv("REQUEST_CONCURRENCY", "8"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "25"))
