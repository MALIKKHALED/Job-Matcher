"""Application settings + LLM factories. Provider is swappable via .env."""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: str = "openrouter"   # openrouter
    llm_temperature: float = 0

    openrouter_api_key: str | None = None
    openrouter_model: str = "openrouter/auto-beta"

    scraper: str = "scrapegraph"
    sgai_api_key: str | None = None

@lru_cache
def get_settings() -> Settings:
    s = Settings()
    # Export keys to the process env so LiteLLM (CrewAI's OpenRouter path and scrapegraph) finds them.
    if s.openrouter_api_key:
        os.environ.setdefault("OPENROUTER_API_KEY", s.openrouter_api_key)
    if s.sgai_api_key:
        os.environ.setdefault("SGAI_API_KEY", s.sgai_api_key)    
    return s

def build_llm():
    """CrewAI LLM instance for the configured provider."""
    from crewai import LLM

    s = get_settings()

    if s.llm_provider == "openrouter":
        return LLM(
            model=f"openrouter/{s.openrouter_model}",
            base_url=OPENROUTER_BASE_URL,
            api_key=s.openrouter_api_key,
            temperature=s.llm_temperature,
        )
   
    raise ValueError(f"Unsupported LLM_PROVIDER: {s.llm_provider!r}")

def build_scrapegraph_client():
    """ScrapeGraphAI cloud API client."""
    from scrapegraph_py import ScrapeGraphAI

    s = get_settings()
    if s.scraper == "scrapegraph":
        return ScrapeGraphAI(api_key=s.sgai_api_key)
    raise ValueError(f"Unsupported scraper: {s.scraper!r}")