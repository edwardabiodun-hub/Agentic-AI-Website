# GitHub and Vercel setup

## Repository and preview behavior

Connect the GitHub repository to Vercel with `site/` configured as the project root when the target is the static demo site. Pull requests should create Vercel preview deployments. The engine creates a bounded draft PR containing generated metadata, content, schema, and internal-link changes; a human reviews the diagnostic evidence and preview before merge.

## Production deployment rule

The weekly automation does not deploy production. Vercel's normal Git integration deploys the production branch after a reviewed PR is merged. This keeps approval, preview inspection, and rollback visible in GitHub/Vercel rather than hiding them inside an agent run.

## Rollback

Revert the merged PR in GitHub or promote the previous known-good Vercel deployment. Record the rollback reason in the weekly run artifact, then pause the affected strategy or URL pattern until the diagnostic and validation rules are updated.

## Required GitHub settings

- Protect `main` and require CI checks before merge.
- Require at least one human review for generated PRs.
- Store provider credentials and `DATABASE_URL` as Actions secrets; use repository variables for non-secret site identifiers.
- Keep workflow permissions read-only unless a future delivery job specifically needs PR creation, and then scope that job separately.
