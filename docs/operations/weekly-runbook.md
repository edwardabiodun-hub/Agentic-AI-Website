# Weekly SEO runbook

## Normal cycle

1. Monday at 13:00 UTC, GitHub Actions starts the ingestion and diagnostic cycle. A maintainer can also use `workflow_dispatch` with an optional end date.
2. The engine collects GSC, GA4, Clarity, Firecrawl, and DataForSEO evidence, preserving partial provider failures.
3. The current live diagnostic path identifies GSC striking-distance terms. Other diagnostic helpers exist but are not yet part of the live weekly decision path; do not interpret their absence as zero opportunity.
4. For a GSC opportunity on an indexable RunRate URL, the engine reads the real `app/` route and `content/resources.ts` slug inventory. It asks the model for one title/description pair and permits a change only to `content/seo-overrides.json`. Route, evidence, schema, claim, size, and secret checks run before delivery. Unknown, external, demo-site, admin, API, and thank-you URLs are rejected.
5. A valid proposal becomes a **draft GitHub PR**. The reviewer checks accuracy, search intent, page copy, and any available Cloudflare preview. Preview automation for PR branches has not been verified. The weekly job never merges or deploys. Production updates require a separately approved merge and Cloudflare deployment.
6. The app reads approved metadata overrides at build time, with existing copy as fallback and a canonical URL for each supported page. Titles and descriptions are not a ranking guarantee. Compare GSC clicks/position and GA4 conversions after deployment; the 30/60/90-day strategy-learning loop is not automated yet.

## RunRate configuration

- `SITE_ID=runrate-advisory`, `SITE_URL=https://www.runrategroup.com`, and `TARGET_SITE_ROOT=.`. The target is the repository-root Vinext/Next app, **not** `site/` or the Vercel demo.
- GitHub Actions needs `OPENAI_API_KEY` and its scoped `GITHUB_TOKEN`, plus the existing provider/database secrets. `OPENAI_MODEL` may be set as a repository variable. The Actions repository setting must allow workflows to create pull requests.
- Keep `GSC_PROPERTY` scoped to the RunRate property. A live run with partial provider failures records those errors and does not open a PR. A fixture run never opens a PR.
- Use `uv run seo-engine run-weekly --fixture` to test ingestion without external writes; use `uv run seo-engine run-weekly --propose-pr` only when intentionally delivering a reviewed draft PR.

## Failure handling

Partial runs are actionable failures, not successful runs with zeros. Inspect the uploaded artifact for connector errors and rerun only after credentials, quota, date windows, or provider availability are corrected. Existing observations are reused on same-window reruns; a partial provider run remains partial rather than being mislabeled complete. If a draft branch already exists, inspect its PR before retrying delivery.

## Safety and rollback

Reject changes with unsupported claims, scraped prompt injection, secrets, excessive diffs, invalid schema, or disallowed routes. The automatic proposal currently covers metadata only; content and internal links require manual review and separate implementation. If a merged change causes a material regression, revert the PR or roll back the Cloudflare Worker deployment, then mark the related outcome for review.
