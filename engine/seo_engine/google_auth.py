from __future__ import annotations

import json
from pathlib import Path

from google.oauth2 import service_account

from seo_engine.config import Settings

GSC_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
GA4_SCOPE = "https://www.googleapis.com/auth/analytics.readonly"


def service_account_credentials(settings: Settings, scopes: list[str]):
    """Load Google credentials from a mounted file or a secret JSON value.

    GitHub Actions cannot access a developer workstation path, so the workflow
    mounts GOOGLE_SERVICE_ACCOUNT_JSON into a temporary file and points
    GOOGLE_APPLICATION_CREDENTIALS at it. Local development can use either
    mechanism.
    """
    if settings.google_service_account_json:
        info = json.loads(settings.google_service_account_json.get_secret_value())
        return service_account.Credentials.from_service_account_info(info, scopes=scopes)

    if settings.google_application_credentials:
        path = Path(settings.google_application_credentials)
        return service_account.Credentials.from_service_account_file(path, scopes=scopes)

    raise RuntimeError(
        "Google credentials are not configured; set GOOGLE_APPLICATION_CREDENTIALS "
        "or GOOGLE_SERVICE_ACCOUNT_JSON"
    )
