# Provider setup

The engine treats provider responses as untrusted evidence. Configure credentials as GitHub Actions secrets or local environment variables; never commit them or place them in generated site files.

## Required configuration

| Feed | Environment values | Scope and cadence |
| --- | --- | --- |
| Google Search Console | `GSC_PROPERTY`, Google service-account/application credentials | Search analytics by query and page; weekly window, with position 8–20 diagnostics. |
| GA4 Data API | `GA4_PROPERTY_ID`, Google credentials | Page views, engaged sessions, conversions, and landing-page behavior. |
| Microsoft Clarity | `CLARITY_PROJECT_ID`, `CLARITY_API_TOKEN` | Export-supported 1–3 day windows for dead clicks, rage clicks, quickbacks, scroll, and script errors. |
| Firecrawl | `FIRECRAWL_API_KEY` | Restricted competitor/page scraping for structure, metadata, schema, and link evidence; do not copy prose. |
| DataForSEO | `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD` | Weekly SERP/keyword collection; reserve live requests for high-priority validation. |

## Credential rules

Use least-privilege service accounts, separate staging and production credentials, and rotate tokens through the provider consoles. Local `.env` files are ignored by Git and `.env.example` contains names only. Provider failures must remain visible as partial-run errors; missing data must not become zero-valued metrics.

## Evidence policy

Every diagnostic should retain its source, observation timestamp, canonical URL/query, and provider reference. Scraped competitor material is structural evidence only. Claims about credentials, reviews, experts, local presence, or third-party proof require human verification before publication.
