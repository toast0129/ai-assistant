from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(Path(__file__).parent.parent / ".env", override=True)

class Settings(BaseSettings):
    anthropic_api_key: str
    openai_api_key: str = ""
    supabase_url: str
    supabase_key: str
    database_url: str
    github_token: str
    google_client_id: str
    google_client_secret: str
    google_refresh_token: str
    youtube_api_key: str
    backend_port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000"]
    cost_budget_daily_usd: float = 0.50

settings = Settings()