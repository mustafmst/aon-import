from __future__ import annotations

from pathlib import Path

import typer

from aon_import.config import AppConfig, load_config
from aon_import.models import PageType, ResolutionResult
from aon_import.registry import build_default_registry
from aon_import.resolver import resolve_target_ids, summarize_resolution
from aon_import.scraper import run_import


app = typer.Typer(help="Import selected PF2e AoN entries as compact markdown.")


@app.command()
def plan(config: Path = typer.Option(..., "--config", "-c", exists=True, readable=True)) -> None:
    """Show resolved target IDs from config."""
    loaded = load_config(config)
    result = resolve_target_ids(loaded)
    _validate_registry_support(loaded, result)
    typer.echo(summarize_resolution(result))


@app.command("import")
def import_command(
    config: Path = typer.Option(..., "--config", "-c", exists=True, readable=True),
) -> None:
    """Fetch target IDs and write markdown notes."""
    loaded = load_config(config)
    _validate_registry_support(loaded, resolve_target_ids(loaded))
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
    _validate_registry_support(loaded, result)
    typer.echo(summarize_resolution(result))


def _validate_registry_support(config: AppConfig, resolution: ResolutionResult) -> None:
    registry = build_default_registry()
    target_types: set[PageType] = {typed_id.type for typed_id in resolution.resolved_ids}
    unsupported = registry.missing_types(target_types)
    if not unsupported:
        return

    message = f"Unsupported target types: {', '.join(sorted(unsupported))}"
    if config.validation.strict_type_check:
        raise typer.BadParameter(message)
    typer.echo(f"Warning: {message}")


if __name__ == "__main__":
    app()
