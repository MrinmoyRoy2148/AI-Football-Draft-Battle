import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# App configurations
APP_NAME = "AI Football Battle"
VERSION = "1.0.0"
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# Data paths
DATA_PATH = BASE_DIR / "data" / "players.json"

# Deterministic engine parameters
# Logistic steepness constant k (from blueprint: k=12.0)
PROBABILITY_K = 12.0

# Formation category weights for (Attack, Midfield, Defense)
# Each position's contribution weight row: [att_w, mid_w, def_w]
POSITION_WEIGHTS = {
    "GK": {"attack": 0.10, "midfield": 0.10, "defense": 0.80},
    "DEF": {"attack": 0.20, "midfield": 0.25, "defense": 0.55},
    "MID": {"attack": 0.30, "midfield": 0.50, "defense": 0.20},
    "FWD": {"attack": 0.65, "midfield": 0.25, "defense": 0.10},
}

# Supported 5-player formations
SUPPORTED_FORMATIONS = {
    "1-1-1-2": {"name": "Aggressive (1 DEF, 1 MID, 2 FWD)", "GK": 1, "DEF": 1, "MID": 1, "FWD": 2},
    "1-1-2-1": {"name": "Balanced Control (1 DEF, 2 MID, 1 FWD)", "GK": 1, "DEF": 1, "MID": 2, "FWD": 1},
    "1-2-1-1": {"name": "Solid Defense (2 DEF, 1 MID, 1 FWD)", "GK": 1, "DEF": 2, "MID": 1, "FWD": 1},
}

DEFAULT_FORMATION = "1-1-1-2"

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip() or None
