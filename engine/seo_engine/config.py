from __future__ import annotations

from pathlib import Path

from pydantic import AnyHttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./seo_engine.db"
    site_id: str = "demo-site"
    site_url: AnyHttpUrl = "https://example.com/"
    target_site_root: Path = Path("site")
    github_owner: str = ""
    github_repository: str = ""
    github_base_branch: str = "main"
    gsc_property: str = ""
    ga4_property_id: str = ""
    google_application_credentials: str = ""
    google_service_account_json: SecretStr | None = None
    clarity_project_id: str = ""
    clarity_api_token: SecretStr | None = None
    firecrawl_api_key: SecretStr | None = None
    dataforseo_login: SecretStr | None = None
    dataforseo_password: SecretStr | None = None
    seo_keywords: str = ""
    dataforseo_location_code: int = 2840
    dataforseo_language_code: str = "en"
    dataforseo_device: str = "desktop"
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4.1-mini"

    @classmethod
    def load(cls) -> Settings:
        return cls()


def redact_secrets(value: str, secrets: list[SecretStr | None]) -> str:
    for secret in secrets:
        if secret and secret.get_secret_value():
            value = value.replace(secret.get_secret_value(), "[REDACTED]")
    return value
