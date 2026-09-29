from __future__ import annotations

import asyncio
import json
from datetime import date

import typer

from seo_engine.config import Settings
from seo_engine.workflow import run_weekly


def build_cli() -> typer.Typer:
    app = typer.Typer(name="seo-engine", help="Evidence-backed SEO growth engine.")

    @app.command()
    def health() -> None:
        """Print a local health response."""
        typer.echo("ok")

    def execute_weekly(run_date: str | None, fixture: bool) -> None:
        parsed_date = date.fromisoformat(run_date) if run_date else None
        summary = asyncio.run(run_weekly(Settings.load(), parsed_date, fixture_mode=fixture))
        typer.echo(json.dumps(summary.model_dump(mode="json"), indent=2))

    @app.command()
    def collect(
        run_date: str | None = typer.Option(None, help="Inclusive end date, YYYY-MM-DD."),
        fixture: bool = typer.Option(False, help="Use deterministic local provider fixtures."),
    ) -> None:
        """Collect the configured provider feeds for a weekly window."""
        execute_weekly(run_date, fixture)

    @app.command()
    def diagnose(
        run_date: str | None = typer.Option(None, help="Inclusive end date, YYYY-MM-DD."),
        fixture: bool = typer.Option(False, help="Use deterministic local provider fixtures."),
    ) -> None:
        """Run deterministic diagnostics for a weekly evidence window."""
        execute_weekly(run_date, fixture)

    @app.command("generate-brief")
    def generate_brief(
        run_date: str | None = typer.Option(None, help="Inclusive end date, YYYY-MM-DD."),
        fixture: bool = typer.Option(False, help="Use deterministic local provider fixtures."),
    ) -> None:
        """Generate an evidence-backed brief from a weekly run."""
        execute_weekly(run_date, fixture)

    @app.command("run-weekly")
    def run_weekly_command(
        run_date: str | None = typer.Option(None, help="Inclusive end date, YYYY-MM-DD."),
        fixture: bool = typer.Option(False, help="Use deterministic local provider fixtures."),
    ) -> None:
        """Execute the complete weekly workflow."""
        execute_weekly(run_date, fixture)

    return app


def main() -> None:
    build_cli()()
