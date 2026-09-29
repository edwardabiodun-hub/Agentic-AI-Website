# RunRate Advisory application import

This repository now includes the RunRate Advisory website application from
`C:\Users\eddie\Eddie Consultancy Project` at the repository root. The
autonomous SEO engine remains under `engine/` and its existing Python test
suite remains under `tests/`.

## Imported runtime

- Next/Vinext application routes in `app/`
- Shared UI in `components/`
- Domain and persistence code in `lib/`, `db/`, and `drizzle/`
- Static assets in `public/`
- Cloudflare Worker entrypoint in `worker/`
- Wrangler/Vite configuration and package scripts

The source `.env`, personal files, logs, caches, dependency directories, and
build output were intentionally excluded.

## Validation status

The Cloudflare deployment configuration test passes. The current source
checkout still references four analytics/admin modules that are not present in
the source worktree or its reachable Git history:

- `lib/admin/access.ts`
- `lib/analytics/site.ts`
- `lib/analytics/site-track.ts`
- `lib/analytics/site-aggregates.ts`

Until those modules are restored or the related routes are completed, the
production build and the analytics-dependent component tests will fail. No
Cloudflare migration or deployment has been run.

## Production decision still required

The app is configured for Cloudflare Workers, D1, R2, and a scheduled Worker,
while the connected GitHub repository currently has a Vercel project. Vercel
can host the repository only after the Cloudflare-specific runtime strategy is
resolved; the two deployment systems do not provision the same bindings.
