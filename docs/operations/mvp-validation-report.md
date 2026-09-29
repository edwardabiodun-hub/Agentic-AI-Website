# MVP validation report

**Validated:** 2026-09-29  
**Repository mode:** greenfield Native checkout  
**Python:** 3.12.14  
**Environment:** Windows sandbox

## Automated checks

| Check | Result |
| --- | --- |
| `uv sync --locked` | Pass; 81 packages resolved/checked |
| `uv run ruff check .` | Pass |
| `uv run pytest -q --cov=seo_engine --cov-report=term-missing` | Pass; 36 tests, 87% line coverage |
| `uv run alembic check` | Pass; no pending upgrade operations |
| Fixture weekly run | Pass; one complete run, one diagnostic, one brief, no errors |
| Repeat fixture run for same site/date | Pass; idempotent run identity |
| `docker compose config` | Not run; Docker is not installed in the execution environment |

## Verified behavior

- Five provider connector boundaries normalize fixture payloads into the same evidence model.
- Provider failures are represented as partial results rather than zero metrics.
- Diagnostics retain evidence references and rank striking-distance opportunities.
- Generation is constrained to the approved site root and rejects unsafe or unsupported material.
- Site validation blocks duplicate H1s, invalid canonicals, broken internal links, and malformed JSON-LD.
- GitHub delivery is isolated behind a mocked HTTP adapter; no external branch, commit, or PR was created in this run.
- Human approval remains mandatory; the weekly workflow contains no production deployment command.
- Measurement utilities create 30-, 60-, and 90-day windows and calculate baseline lift.

## Known gaps before production activation

1. Configure and exercise live credentials for all five providers, with real request implementations and quota/retry policies.
2. Provide a production PostgreSQL `DATABASE_URL` and run migrations in the deployment environment.
3. Wire the weekly workflow to the live provider adapters and GitHub delivery path after secrets and permissions are reviewed.
4. Connect Vercel to the repository and verify preview and protected-branch production behavior.
5. Add a production status store for PR/deployment/outcome metadata and an approval notification channel if GitHub PR review is insufficient.

No production data or external systems were mutated during validation.
