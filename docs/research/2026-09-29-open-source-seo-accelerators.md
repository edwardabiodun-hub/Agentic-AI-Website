# Phase 0: Open-Source SEO Automation Research

**Date:** 2026-09-29  
**Purpose:** Identify existing projects, libraries, and workflow patterns that can accelerate the Autonomous SEO Growth Engine without importing an unreviewed monolith.

## Executive conclusion

There is no single open-source project that cleanly covers the required five data feeds, evidence-backed diagnostics, bounded code generation, GitHub PR delivery, Vercel previews, and 30/60/90-day measurement. The strongest approach is compositional:

- reuse official API clients and provider SDKs;
- borrow workflow and agent patterns from existing SEO projects;
- keep the diagnostic contracts, policy gate, outcome model, and PR delivery logic custom;
- pin versions and audit licenses before copying source code.

## Candidate projects

| Project | Useful components | Reuse decision | Main caution |
|---|---|---|---|
| [DafinEdison/agentic-seo-agent](https://github.com/DafinEdison/agentic-seo-agent) | GSC-driven investigation, crawl context, tool-using SEO diagnostics, internal-link suggestions | Reuse workflow ideas and tool boundaries; do not copy the whole application | Opinionated agent/runtime and site-specific assumptions |
| [NeoZi12/dispatchseo](https://github.com/NeoZi12/dispatchseo) | Scheduled SEO research, rank tracking, content workflows, MCP/agent integration, builder execution | Use as a reference for scheduled execution and PR-oriented user experience | Review operational maturity, provider dependencies, and license before source reuse |
| [bamr87/aieo](https://github.com/bamr87/aieo) | Modular content/SEO agents, GA4/GSC/DataForSEO integrations, performance routes, publisher abstractions | Reuse interface ideas and connector boundaries; evaluate selective extraction only | Broad scope, fast-moving project, and source/license audit required |
| [dannwaneri/seo-agent](https://github.com/dannwaneri/seo-agent) | GSC quick wins, cluster audits, backlink relevance, browser checks, SERP feature analysis | Reuse deterministic audit concepts and fixture design | Browser-dependent workflow is not the core MVP execution model |
| [SamurAIGPT/open-ai-seo-agent](https://github.com/SamurAIGPT/open-ai-seo-agent) | Reusable SEO playbooks for coding agents, content-gap and rank-tracking workflows | Use as a prompt/workflow reference | It is primarily an agent playbook, not a durable production service |
| [seoskillsai/seo-skills-ai](https://github.com/seoskillsai/seo-skills-ai) | Modular specialist skills, DataForSEO/Firecrawl adapters, deterministic execution concepts | Compare adapter contracts and specialist decomposition | Treat external skill instructions as untrusted until reviewed; do not import wholesale |
| [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | Web search, scrape, crawl, parse, browser interaction, structured extraction | Use the hosted API and official SDK behind a connector interface | Respect robots, provider terms, privacy constraints, and competitor-content boundaries |
| [firecrawl/firecrawl-py](https://github.com/firecrawl/firecrawl-py) | Python client for Firecrawl API | Directly reusable as a pinned dependency | Wrap it so provider changes do not leak into domain code |
| [dataforseo/PythonClient](https://github.com/dataforseo/PythonClient) / [DataForSEO organization](https://github.com/dataforseo) | Official Python and TypeScript clients, endpoint models, examples | Prefer official client or typed adapter over hand-written endpoint code | API calls incur usage charges and have endpoint-specific quotas |
| [langchain-ai/langgraph](https://langchain-ai.github.io/langgraph/reference/) | Durable agent state, persistence, human-in-the-loop interrupts | Defer from MVP; keep as an upgrade path for long-running agent state | Adds framework and persistence complexity before the PR loop is proven |
| [PrefectHQ/prefect](https://github.com/PrefectHQ/prefect) | Python scheduling, retries, caching, flow state, run visibility | Consider when weekly runs exceed GitHub Actions operational limits | Adds a control-plane deployment and operational dependency |
| [temporalio/samples-python](https://github.com/temporalio/samples-python) | Durable workflow patterns, schedules, retries, replay-safe execution | Consider for multi-site or multi-day approval workflows | Requires a Temporal service and stricter workflow design discipline |

## Official API and platform references

- [Google Search Console Search Analytics API](https://developers.google.com/webmaster-tools/v1/searchanalytics/query): page/query/date grouping, clicks, impressions, CTR, and average position.
- [Google Analytics Data API](https://developers.google.com/analytics/devguides/reporting/data/v1/basics): filtered and paginated `runReport` queries for page and conversion data.
- [Microsoft Clarity Data Export API](https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-data-export-api): dashboard export metrics, including dead clicks, rage clicks, quickbacks, excessive scroll, and script errors.
- [Firecrawl Scrape API](https://docs.firecrawl.dev/api-reference/endpoint/scrape): structured page extraction and optional parsing formats.
- [DataForSEO SERP API](https://docs.dataforseo.com/v3/serp/overview/): standard and live SERP collection across engines, locations, languages, and devices.
- [GitHub REST pull request API](https://docs.github.com/en/rest/pulls): branch-to-PR delivery and review integration.
- [Vercel GitHub integration](https://vercel.com/docs/git/vercel-for-github): preview deployment for PRs and production deployment after merge.

## Reusable versus custom boundary

### Reuse directly

- provider SDKs and official client libraries;
- Google OAuth/client credential primitives;
- HTTP retry, timeout, and rate-limit helpers where maintained and well-tested;
- GitHub REST client primitives;
- Vercel's Git integration rather than a custom deployment API;
- open-source test fixtures for SEO audits after license review.

### Build custom

- normalized evidence schema across five providers;
- coverage-aware ingestion and incremental Clarity retention;
- deterministic diagnostic rules and scoring;
- strategy context and priority adjustment;
- evidence-backed brief schema;
- typed AI service contracts;
- policy gate for claims, paths, links, schema, diff size, and secrets;
- idempotent branch/PR lifecycle;
- deployment attribution and 30/60/90-day outcome windows;
- strategy-outcome ranking and feedback loop;
- Phase 2 adapter contracts for off-page, local, authority, reputation, brand, and LLM visibility.

## License and supply-chain policy

Before copying code rather than consuming a package/API:

1. Confirm the repository's current license at the pinned commit.
2. Check transitive dependencies and known vulnerabilities.
3. Keep attribution and notices where required.
4. Prefer a narrow adapter or isolated module over copying an entire application.
5. Pin versions and record the decision in the repository's dependency documentation.

## Research-driven recommendation

Use GitHub Actions, Python, PostgreSQL, official provider clients, and a custom typed workflow for the first implementation. Do not begin with Temporal, Prefect, or LangGraph. Introduce those only when the observed workload—multiple sites, long-running approvals, or workflow recovery requirements—justifies the operational cost.

