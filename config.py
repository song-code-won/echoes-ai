import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database
DB_PATH = os.getenv("ECHOES_DB_PATH", str(DATA_DIR / "echoes_memories.db"))

# Ollama Settings
DEFAULT_OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.getenv("ECHOES_MODEL", "qwen2.5:3b")
ALTERNATIVE_MODELS = [
    "qwen2.5:3b",
    "qwen2.5:7b",
    "qwen2.5:1.5b",
    "llama3.2:3b",
    "mistral:7b"
]

# Application Info
APP_NAME = "Echoes AI"
APP_TAGLINE = "Every memory deserves to live on."
APP_SUBTITLE = "A Private, Local-First Memory Journal & Story Preserver"

# Categories
MEMORY_CATEGORIES = [
    "Childhood",
    "Family Traditions",
    "Celebrations & Milestones",
    "Travel & Adventures",
    "Friendship & Bonds",
    "Remembrance & Tribute",
    "Daily Life & Wisdom",
    "Other"
]

# Story Styles
STORY_STYLES = {
    "warm": {
        "label": "Warm & Heartfelt",
        "description": "Emphasizes tenderness, emotional connection, and cherished family warmth."
    },
    "conversational": {
        "label": "Simple & Conversational",
        "description": "Natural, clear, and easy to read aloud as if sharing over tea or a fireside chat."
    },
    "nostalgic": {
        "label": "Nostalgic & Reflective",
        "description": "Evocative and sensory-rich, lingering on sights, sounds, scents, and passage of time."
    }
}
