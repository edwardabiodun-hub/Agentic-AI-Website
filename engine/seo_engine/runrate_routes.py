from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

PUBLIC_ROUTES = (
    "/",
    "/assessment",
    "/diagnostic",
    "/how-i-help",
    "/founder-resources",
    "/about",
    "/contact",
)
OVERRIDES_PATH = "content/seo-overrides.json"


def indexable_routes(root: Path) -> set[str]:
    """Return only routes backed by the RunRate application and its resource data."""
    sitemap = (root / "app/sitemap.ts").read_text(encoding="utf-8")
    static_routes = set(re.findall(r'"(/[^"$]*)"', sitemap.split("...resources.map", 1)[0]))
    static_routes.add("/")
    if not set(PUBLIC_ROUTES).issubset(static_routes):
        raise ValueError("RunRate sitemap and route allowlist have drifted")
    for route in PUBLIC_ROUTES:
        page = (
            root / "app" / route.lstrip("/") / "page.tsx" if route != "/" else root / "app/page.tsx"
        )
        if not page.is_file():
            raise ValueError(f"Sitemap route has no application page: {route}")
    resource_page = root / "app/founder-resources/[slug]/page.tsx"
    if not resource_page.is_file():
        raise ValueError("Resource route has no application page")
    resources = (root / "content/resources.ts").read_text(encoding="utf-8")
    slugs = re.findall(r'\bslug:\s*"([a-z0-9]+(?:-[a-z0-9]+)*)"', resources)
    if not slugs or len(slugs) != len(set(slugs)):
        raise ValueError("Resource slugs are missing or duplicated")
    return set(PUBLIC_ROUTES) | {f"/founder-resources/{slug}" for slug in slugs}


def resolve_target_route(target_url: str | None, site_url: str, routes: set[str]) -> str:
    if not target_url:
        raise ValueError("A GSC opportunity needs an existing target URL")
    site = urlsplit(site_url)
    target = urlsplit(target_url)
    if site.scheme != "https" or site.netloc.lower() != "www.runrategroup.com":
        raise ValueError("SEO engine is not configured for the RunRate production host")
    if target.netloc and not target.scheme:
        raise ValueError("Target URL must not use a protocol-relative host")
    if target.scheme and (target.scheme != "https" or target.netloc.lower() != site.netloc.lower()):
        raise ValueError("Target URL is not on the configured RunRate host")
    if target.query or target.fragment or "%" in target.path:
        raise ValueError("Target URL must be a clean canonical route")
    route = unquote(target.path).rstrip("/") or "/"
    if route not in routes:
        raise ValueError(f"Target URL is not an indexable RunRate route: {route}")
    return route
