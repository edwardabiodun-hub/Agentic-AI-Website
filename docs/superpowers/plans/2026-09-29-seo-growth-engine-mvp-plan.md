# Autonomous SEO Growth Engine MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Build a runnable weekly SEO workflow that ingests GSC, GA4, Clarity, Firecrawl, and DataForSEO evidence; produces deterministic diagnostics and an evidence-backed brief; generates bounded website changes; opens a draft GitHub PR; and records 30/60/90-day outcomes.

**Architecture:** Python control plane with typed domain contracts, provider adapters, PostgreSQL persistence, deterministic diagnostics, bounded AI services, policy validation, GitHub delivery, and measurement. The current repository also contains a static demo target under site/. GitHub Actions schedules the workflow, GitHub PRs provide human approval, and Vercel Git integration provides previews and production deployment after merge.

**Tech Stack:** Python 3.12+, uv, FastAPI, Typer, Pydantic v2, SQLAlchemy 2, Alembic, PostgreSQL, httpx, official Google clients, Firecrawl Python SDK, DataForSEO client or typed HTTP adapter, provider-neutral LLMClient, pytest, pytest-asyncio, respx, Ruff, Docker Compose, GitHub REST API, GitHub Actions, and Vercel Git integration.

**Spec:** docs/superpowers/specs/2026-09-29-seo-growth-engine-design.md

## Global Constraints

- The default generated-change root is site/; engine code, workflows, and credentials are protected.
- The MVP creates draft PRs and never merges or deploys production changes automatically.
- Provider failures are recorded as partial-run failures and never converted to zero metrics.
- Every change carries diagnosis, evidence references, strategy alignment, success metrics, and rollback notes.
- The workflow is idempotent by site_id, run date, and opportunity fingerprint.
- External text is untrusted input; unsupported claims require human verification.
- Semrush, Reddit, directories, reviews, backlink outreach, and LLM visibility receive extension contracts only in this MVP.

## Review Focus

1. Partial provider data remains visible and never becomes zero values; test in tests/test_ingestion.py.
2. Clarity requests respect the 1–3 day window and quota; test in tests/connectors/test_clarity.py.
3. Duplicate weekly runs do not create duplicate PRs; test in tests/test_workflow.py.
4. Scraped prompt injection and secrets are blocked; test in tests/test_generation_policy.py.
5. Duplicate H1s, invalid canonicals, and broken links block delivery; test in tests/test_site_validator.py.

## File Structure

~~~text
pyproject.toml
.env.example
.python-version
.gitignore
Dockerfile
docker-compose.yml
README.md
alembic.ini
alembic/env.py
alembic/versions/0001_initial_schema.py
.github/workflows/ci.yml
.github/workflows/weekly-seo.yml
config/strategy.yaml
engine/seo_engine/__init__.py
engine/seo_engine/cli.py
engine/seo_engine/api.py
engine/seo_engine/config.py
engine/seo_engine/domain/models.py
engine/seo_engine/domain/ports.py
engine/seo_engine/connectors/base.py
engine/seo_engine/connectors/gsc.py
engine/seo_engine/connectors/ga4.py
engine/seo_engine/connectors/clarity.py
engine/seo_engine/connectors/firecrawl.py
engine/seo_engine/connectors/dataforseo.py
engine/seo_engine/persistence/db.py
engine/seo_engine/persistence/models.py
engine/seo_engine/persistence/repositories.py
engine/seo_engine/diagnostics.py
engine/seo_engine/strategy.py
engine/seo_engine/briefs.py
engine/seo_engine/llm.py
engine/seo_engine/generation.py
engine/seo_engine/policy.py
engine/seo_engine/site_validator.py
engine/seo_engine/github_delivery.py
engine/seo_engine/measurement.py
engine/seo_engine/workflow.py
site/index.html
site/styles.css
site/pages/example-service.html
tests/conftest.py
tests/fixtures/*.json
tests/connectors/*.py
tests/test_domain_models.py
tests/test_persistence.py
tests/test_ingestion.py
tests/test_diagnostics.py
tests/test_strategy.py
tests/test_generation_policy.py
tests/test_site_validator.py
tests/test_github_delivery.py
tests/test_measurement.py
tests/test_workflow.py
~~~

### Task 1: Scaffold the repository and demo site

**Files:** pyproject.toml, .python-version, .env.example, .gitignore, Dockerfile, docker-compose.yml, README.md, engine/seo_engine/__init__.py, site/index.html, site/styles.css, site/pages/example-service.html, tests/conftest.py, tests/test_scaffold.py.

**Interfaces:**
- Package import name: seo_engine.
- CLI entry point: seo-engine.
- Target root: site/.

- [ ] Write a smoke test that imports the package, parses the CLI, and asserts the example page exists.
- [ ] Add pyproject metadata, runtime dependencies, dev dependencies, Ruff configuration, pytest configuration, and the seo-engine console script.
- [ ] Add .env.example with DATABASE_URL, SITE_ID, SITE_URL, GSC_PROPERTY, GA4_PROPERTY_ID, CLARITY_PROJECT_ID, GITHUB_OWNER, GITHUB_REPOSITORY, GITHUB_BASE_BRANCH, TARGET_SITE_ROOT, and provider credential names without values.
- [ ] Add Docker Compose PostgreSQL 16 with a health check and a named volume; add a Dockerfile that runs the CLI.
- [ ] Build a small static site. The example page must have one H1, title, description, canonical, Service JSON-LD, one CTA, and two internal links.
- [ ] Run:

~~~powershell
uv sync --dev
uv run pytest tests/test_scaffold.py -q
uv run ruff check .
uv run seo-engine --help
~~~

Expected: all commands pass without provider credentials.
- [ ] Commit with message: chore: scaffold SEO growth engine.

### Task 2: Define typed domain contracts

**Files:** engine/seo_engine/config.py, engine/seo_engine/domain/models.py, engine/seo_engine/domain/ports.py, engine/seo_engine/connectors/base.py, tests/test_domain_models.py.

**Interfaces:**
- Settings.load() -> Settings
- DateWindow(start: date, end: date)
- SiteScope(site_id: str, site_url: AnyHttpUrl, target_root: Path, base_branch: str)
- NormalizedObservation(source, observed_at, dimensions, metrics, evidence_ref)
- CollectionResult(source, observations, status, errors, quota)
- DataConnector.collect(window, scope) -> Awaitable[CollectionResult]
- TargetRepository.read_files(paths) and write_files(changes)
- LLMClient.generate_structured(system, input, response_model)

- [ ] Write failing tests for valid observations, invalid CTR/positions, partial results requiring errors, and stable fingerprints.
- [ ] Implement Pydantic settings with SecretStr credentials and typed models for evidence, diagnostics, opportunities, briefs, proposed changes, PRs, deployments, and outcomes.
- [ ] Implement protocols for connectors, persistence, LLM, GitHub delivery, measurement, and target repositories.
- [ ] Add connector_error that redacts credential-like strings.
- [ ] Run:

~~~powershell
uv run pytest tests/test_domain_models.py -q
uv run ruff check engine tests
~~~

- [ ] Commit with message: feat: add typed SEO engine contracts.

### Task 3: Add PostgreSQL persistence

**Files:** engine/seo_engine/persistence/db.py, persistence/models.py, persistence/repositories.py, alembic.ini, alembic/env.py, alembic/versions/0001_initial_schema.py, tests/test_persistence.py.

**Interfaces:**
- Database.create_session_factory(settings)
- RunRepository.start and finish
- ObservationRepository.insert_many
- DiagnosticRepository.upsert
- OutcomeRepository.insert_window
- RunRepository.has_fingerprint

- [ ] Write SQLite repository tests for runs, observations, diagnostics, briefs, pull requests, deployments, and outcome windows. Pin uniqueness for site plus fingerprint and diagnosis plus measurement window.
- [ ] Implement SQLAlchemy models with UUID keys, UTC timestamps, JSON evidence fields, and indexes for site, source, time, and fingerprint.
- [ ] Implement injected async sessions and repositories. Store redacted raw-payload references rather than credentials or unbounded blobs.
- [ ] Run:

~~~powershell
docker compose up -d db
uv run alembic upgrade head
uv run pytest tests/test_persistence.py -q
~~~

- [ ] Commit with message: feat: add evidence and outcome persistence.

### Task 4: Implement the five provider adapters

**Files:** connectors/gsc.py, ga4.py, clarity.py, firecrawl.py, dataforseo.py; tests/fixtures/*.json; tests/connectors/*.py.

**Interfaces:**
- GSCConnector.collect and query
- GA4Connector.collect and run_report
- ClarityConnector.collect and export
- FirecrawlConnector.scrape and collect
- DataForSEOConnector.track_keywords and collect

- [ ] Write fixture-backed tests before each adapter. Cover pagination, empty responses, auth failures, quota responses, missing metrics as None, source URL normalization, competitor tagging, live-task failure, and polling timeout.
- [ ] Implement GSC using read-only Search Console access with separate page and query slices and bounded retries.
- [ ] Implement GA4 runReport with landing page, views, sessions, engagement, conversions, and conversion rate.
- [ ] Implement Clarity export for supported 1–3 day windows, mapping URL, page title, engagement, scroll, dead clicks, rage clicks, quickbacks, and script errors.
- [ ] Implement Firecrawl with domain and URL-pattern restrictions, preserving extracted page evidence without copying competitor prose.
- [ ] Implement DataForSEO with standard weekly collection and live requests only for high-priority validation.
- [ ] Run:

~~~powershell
uv run pytest tests/connectors -q
~~~

- [ ] Commit with message: feat: add search, behavior, crawl, and SERP connectors.

### Task 5: Build ingestion and persistence coordination

**Files:** engine/seo_engine/workflow.py, persistence/repositories.py, tests/test_ingestion.py.

**Interfaces:**
- collect_all(connectors, window, scope, repo) -> IngestionSummary
- IngestionSummary(run_id, status, connector_results)

- [ ] Write tests using fake complete, partial, and failed connectors. Assert every result persists, partial status is visible, failed sources never become zeros, and duplicate fingerprints reuse the existing run.
- [ ] Implement bounded concurrent collection with asyncio.gather and a semaphore of five.
- [ ] Compute a stable SHA-256 fingerprint from site, window, and connector names before collecting.
- [ ] Finish the run in a finally block and retain provider-specific errors and quota metadata.
- [ ] Run:

~~~powershell
uv run pytest tests/test_ingestion.py -q
~~~

- [ ] Commit with message: feat: add quota-aware ingestion workflow.

### Task 6: Implement deterministic diagnostics and ranking

**Files:** engine/seo_engine/diagnostics.py, tests/test_diagnostics.py.

**Interfaces:**
- find_striking_distance
- find_decay
- find_content_gaps
- find_friction
- find_architecture_issues
- rank_diagnostics

- [ ] Write tests for position 8–20, high-impression low-CTR pages, comparable-window decay, demand without a target page, rage/dead-click friction, orphan pages, broken links, and cannibalization.
- [ ] Join observations by canonical URL and query while preserving missing values and exact evidence references.
- [ ] Implement configurable scoring for opportunity size, business relevance, confidence, effort, and risk. Defaults: position 8–20, 100 impressions, 10 clicks for friction, and 20% comparable-window decline.
- [ ] Ensure incomplete evidence lowers confidence rather than generating invented diagnoses.
- [ ] Run:

~~~powershell
uv run pytest tests/test_diagnostics.py -q
~~~

- [ ] Commit with message: feat: add deterministic SEO diagnostics.

### Task 7: Add strategy comparison and reviewed briefs

**Files:** engine/seo_engine/strategy.py, briefs.py, config/strategy.yaml, tests/test_strategy.py.

**Interfaces:**
- Strategy.from_file
- Strategy.compare
- adjust_priorities
- build_brief
- render_brief_markdown

- [ ] Write tests showing priority service pages outrank unrelated topics, excluded paths are rejected, and briefs contain evidence, success metrics, risk, and rollback.
- [ ] Implement strategy YAML with audiences, locations, priority offerings, conversions, page archetypes, excluded paths, proof requirements, and change limits.
- [ ] Implement the sequence compare against strategy, adjust priorities, generate an evidence-backed brief, and save artifacts/briefs/fingerprint.md.
- [ ] Treat brief review as an automated gate before generation; surface the brief and validation report to the human through the draft PR.
- [ ] Run:

~~~powershell
uv run pytest tests/test_strategy.py -q
~~~

- [ ] Commit with message: feat: add strategy alignment and SEO briefs.

### Task 8: Implement bounded AI generation and policy gates

**Files:** engine/seo_engine/llm.py, generation.py, policy.py, tests/test_generation_policy.py.

**Interfaces:**
- LLMClient.generate_structured
- FakeLLMClient.generate_structured
- generate_changes
- validate_generation

- [ ] Write fake-model tests for title/meta, content sections, schema, and internal-link proposals; malformed JSON; prompt-like scraped input; unsupported claims; and secret matches.
- [ ] Implement a provider-neutral LLM port and an optional production adapter with Pydantic structured output. Record model, prompt version, evidence IDs, and usage metadata.
- [ ] Limit generated changes to brief-approved copy, metadata, headings, JSON-LD, canonical metadata, and contextual internal links under site/.
- [ ] Reject excessive diffs, unsupported claims, duplicate links, invalid schema, missing evidence, disallowed paths, and secrets. Return all violations in a report.
- [ ] Commit with message: feat: add bounded AI generation and policy gates.

### Task 9: Validate and apply site changes safely

**Files:** engine/seo_engine/site_validator.py, domain/models.py, tests/test_site_validator.py.

**Interfaces:**
- validate_site(root, changed_paths)
- apply_changes(root, changes)
- check_internal_links(root)
- check_metadata(document, expected_canonical)

- [ ] Write tests for duplicate H1s, missing metadata, invalid JSON-LD, canonical mismatch, broken links, path traversal, disallowed paths, and a valid page.
- [ ] Implement BeautifulSoup HTML validation with exact file and selector context.
- [ ] Normalize paths, require site/ prefix, verify original hashes when present, and apply changes atomically only after policy validation.
- [ ] Commit with message: feat: validate and safely apply site changes.

### Task 10: Deliver branches and draft PRs

**Files:** engine/seo_engine/github_delivery.py, tests/test_github_delivery.py.

**Interfaces:**
- create_branch(branch_name, base_sha)
- commit_files(branch_name, changes, message)
- open_draft_pr(branch_name, base_branch, title, body)
- update_pr(pr_number, body_append)

- [ ] Write respx tests for branch creation, multi-file commit, draft PR body, auth/rate-limit errors, and idempotent reuse of an existing opportunity PR.
- [ ] Implement least-privilege GitHub REST delivery with installation-token support, API version headers, bounded timeouts, and redacted errors.
- [ ] Include brief path, evidence, validation, expected metrics, risks, rollback, and preview status in the PR body.
- [ ] Capture a Vercel preview URL from PR comments/checks when available; do not call Vercel deployment APIs in the MVP.
- [ ] Commit with message: feat: deliver SEO changes as draft PRs.

### Task 11: Measure outcomes and rank strategies

**Files:** engine/seo_engine/measurement.py, tests/test_measurement.py.

**Interfaces:**
- create_measurement_windows
- measure_opportunity
- calculate_lift
- rank_strategy_outcomes

- [ ] Write tests for exact 30/60/90-day boundaries, incomplete windows, positive and negative lift, zero baselines, confounders, and pages changed again during the window.
- [ ] Anchor windows to the deployment timestamp and reuse normalized page/query metrics.
- [ ] Calculate absolute and percentage deltas without divide-by-zero and mark contaminated windows explicitly.
- [ ] Aggregate by strategy type, page archetype, diagnostic family, and confidence band; require a minimum sample before labeling a strategy reliable.
- [ ] Commit with message: feat: add SEO impact measurement.

### Task 12: Wire the weekly workflow, CLI, API, and fixture mode

**Files:** engine/seo_engine/workflow.py, cli.py, api.py, tests/test_workflow.py.

**Interfaces:**
- run_weekly(settings, run_date=None) -> RunSummary
- seo-engine collect
- seo-engine diagnose
- seo-engine generate-brief
- seo-engine run-weekly
- GET /healthz
- GET /runs/{run_id}

- [ ] Write an end-to-end fixture test with fake connectors, fake LLM, temporary site, and fake GitHub delivery.
- [ ] Compose load settings, collect, diagnose, compare strategy, brief, generate, validate, patch temporary checkout, deliver draft PR, persist metadata, and schedule measurement.
- [ ] Add read-only status endpoints; keep manual triggering CLI-only.
- [ ] Run the workflow twice for the same date and assert no duplicate collection or PR. Inject a post-brief failure and assert the run can resume without duplicate delivery.
- [ ] Implement fixture mode so the full workflow runs without provider credentials or network calls.
- [ ] Commit with message: feat: wire the weekly SEO workflow.

### Task 13: Add CI, weekly scheduling, and operations docs

**Files:** .github/workflows/ci.yml, .github/workflows/weekly-seo.yml, README.md, docs/operations/provider-setup.md, docs/operations/vercel-github-setup.md, docs/operations/weekly-runbook.md, tests/test_workflow_files.py.

- [ ] Write YAML tests asserting CI runs Ruff, tests, and Alembic checks; the weekly workflow has schedule and workflow_dispatch; and the weekly job contains no production-deployment command.
- [ ] Run CI on pushes and pull requests to main with uv sync --locked, Ruff, pytest, and alembic check.
- [ ] Schedule the weekly job Monday at 13:00 UTC, support start/end date inputs, run migrations, invoke seo-engine run-weekly, and upload briefs and summaries.
- [ ] Document secrets, permissions, Clarity cadence, Vercel project root site/, preview behavior, rollback, and the rule that merged PRs create production deployments.
- [ ] Run:

~~~powershell
uv run ruff check .
uv run pytest -q
uv run alembic check
docker compose config
~~~

- [ ] Commit with message: ci: schedule and document weekly SEO runs.

### Task 14: Final validation and handoff

**Files:** README.md, docs/operations/mvp-validation-report.md.

- [ ] Run:

~~~powershell
uv sync --locked
uv run ruff check .
uv run pytest -q --cov=seo_engine --cov-report=term-missing
uv run alembic check
docker compose config
~~~

- [ ] Run fixture mode for date 2026-09-29 and confirm a run summary, brief, bounded site diff, validation report, and fake delivery record without network calls.
- [ ] With credentials absent, confirm live mode fails before branch/PR creation. With one provider enabled, confirm the run is partial and identifies missing feeds.
- [ ] Record test counts, coverage, fixture output paths, known limitations, and setup steps for Google, Clarity, Firecrawl, DataForSEO, GitHub, PostgreSQL, and Vercel.
- [ ] Commit with message: docs: record SEO engine MVP validation.

## Phase 2 extension plan

Add provider families behind the connector port only after the MVP produces reliable PRs and outcome data:

1. Authority and backlinks: backlink observations, unlinked mentions, editorial/partner briefs, and no automated outreach.
2. Local and reputation: GBP/citation/review adapters, NAP consistency, review velocity, and local landing-page diagnostics.
3. Off-page distribution: Reddit/forum/social discovery and human-reviewed distribution briefs.
4. Brand demand: branded query trends and branded SERP observations.
5. LLM visibility: repeatable prompt sets, citation observations, and provider-specific reports.
6. Durable orchestration: evaluate Prefect, LangGraph, or Temporal only after GitHub Actions limits or multi-day approvals are demonstrated.

