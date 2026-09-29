from __future__ import annotations

from pydantic import SecretStr

from seo_engine.config import redact_secrets
from seo_engine.domain.models import CollectionResult


def connector_error(
    source: str,
    message: str,
    secrets: list[SecretStr | None] | None = None,
    quota: dict | None = None,
) -> CollectionResult:
    safe = redact_secrets(message, secrets or [])
    return CollectionResult(
        source=source, observations=[], status="failed", errors=[safe], quota=quota or {}
    )
