# Weekly SEO runbook

## Normal cycle

1. Monday at 13:00 UTC, GitHub Actions starts the ingestion and diagnostic cycle. A maintainer can also use `workflow_dispatch` with an optional end date.
2. The engine collects GSC, GA4, Clarity, Firecrawl, and DataForSEO evidence, preserving partial provider failures.
3. Diagnostics rank striking-distance terms, missing-demand gaps, decay, friction, architecture, and conversion opportunities against the approved strategy.
4. A brief records evidence IDs, expected outcomes, risk, effort, and rollback notes. Generated changes are limited to the approved `site/` root and are validated for title, metadata, H1, canonical, JSON-LD, and internal-link integrity.
5. A human reviews the brief, changed files, and Vercel preview. Only an approved merge makes a production deployment.
6. Record the deployment timestamp and measure 30-, 60-, and 90-day position, click, and conversion outcomes.

## Failure handling

Partial runs are actionable failures, not successful runs with zeros. Inspect the uploaded artifact for connector errors and rerun only after credentials, quota, date windows, or provider availability are corrected. Idempotent fingerprints prevent duplicate collection for the same site, window, and connector set.

## Safety and rollback

Reject changes with unsupported claims, scraped prompt injection, secrets, excessive diffs, invalid schema, broken internal links, or disallowed paths. If a merged change causes a material regression, revert the PR or promote the previous Vercel deployment, then mark the related strategy outcome for review before the next cycle.
