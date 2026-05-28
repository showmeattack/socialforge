"""SocialForge configuration."""
from pathlib import Path
from pydantic_settings import BaseSettings

ENV_PATH = Path(__file__).parent / ".env"


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./socialforge.db"
    secret_key: str = "socialforge-dev-secret-change-me"
    openrouter_api_key: str = ""
    openrouter_model: str = "minimax/minimax-m2.5:free"
    debug: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"

    def save_to_env(self):
        """Persist API key and model to .env so they survive restarts."""
        lines = {}
        if ENV_PATH.exists():
            for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1)
                    lines[k.strip()] = v.strip()
        if self.openrouter_api_key:
            lines["OPENROUTER_API_KEY"] = self.openrouter_api_key
        if self.openrouter_model:
            lines["OPENROUTER_MODEL"] = self.openrouter_model
        ENV_PATH.write_text(
            "\n".join(f"{k}={v}" for k, v in lines.items()) + "\n",
            encoding="utf-8",
        )


settings = Settings()
