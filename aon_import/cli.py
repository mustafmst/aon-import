from __future__ import annotations

from pathlib import Path

import typer

from aon_import.config import load_config
from aon_import.resolver import resolve_target_ids, summarize_resolution
from aon_import.scraper import run_import


app = typer.Typer(help="Import selected PF2e AoN entries as compact markdown.")


@app.command()
def plan(config: Path = typer.Option(..., "--config", "-c", exists=True, readable=True)) -> None:
    """Show resolved target IDs from config."""
    loaded = load_config(config)
    result = resolve_target_ids(loaded)
    typer.echo(summarize_resolution(result))


@app.command("import")
def import_command(
    config: Path = typer.Option(..., "--config", "-c", exists=True, readable=True),
) -> None:
    """Fetch target IDs and write markdown notes."""
    loaded = load_config(config)
    report = run_import(loaded)

    typer.echo(f"Total targets: {report.total}")
    typer.echo(f"Imported: {report.succeeded}")
    typer.echo(f"Skipped: {report.skipped}")
    typer.echo(f"Failed: {report.failed}")

    if report.warnings:
        typer.echo("Warnings:")
        for warning in report.warnings:
            typer.echo(f"- {warning}")

    if report.failures:
        typer.echo("Failures:")
        for failure in report.failures:
            typer.echo(f"- {failure}")


@app.command()
def stats(config: Path = typer.Option(..., "--config", "-c", exists=True, readable=True)) -> None:
    """Show what would be imported by type."""
    loaded = load_config(config)
    result = resolve_target_ids(loaded)
    typer.echo(summarize_resolution(result))


if __name__ == "__main__":
    app()
