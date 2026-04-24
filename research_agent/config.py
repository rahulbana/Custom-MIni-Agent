import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent   # project root (one level up from research_agent/)
LOGS_DIR = BASE_DIR / "logs"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

class AgentConfig(BaseModel):
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    max_search_results_per_query: int = 5
    max_summary_tokens: int = 1500
    temperature: float = 0.2
    request_timeout: int = 30

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")

config = AgentConfig()