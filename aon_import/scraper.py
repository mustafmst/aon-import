from __future__ import annotations

from pathlib import Path
from typing import Any

from aon_import.config import AppConfig
from aon_import.contracts import RenderResult
from aon_import.discover import build_detail_url
from aon_import.fetch import Fetcher
from aon_import.models import ImportReport, PageType
from aon_import.registry import build_default_registry
from aon_import.render import output_path_for
from aon_import.resolver import resolve_target_ids


def run_import(config: AppConfig) -> ImportReport:
    resolution = resolve_target_ids(config)
    report = ImportReport(total=len(resolution.resolved_ids))
    report.warnings.extend(resolution.warnings)
    registry = build_default_registry()

    target_types: set[PageType] = {typed_id.type for typed_id in resolution.resolved_ids}
    unsupported_types = registry.missing_types(target_types)
    if unsupported_types:
        message = f"Unsupported target types: {', '.join(sorted(unsupported_types))}"
        if config.validation.strict_type_check:
            raise ValueError(message)
        report.warnings.append(message)

    with Fetcher(config) as fetcher:
        for typed_id in sorted(resolution.resolved_ids):
            if not registry.supports(typed_id.type):
                report.skipped += 1
                continue
            try:
                url = build_detail_url(typed_id)
                html = fetcher.fetch(url)
                handler = registry.get(typed_id.type)
                parsed_result = handler.parser.parse(typed_id, url, html)
                rendered_result = handler.renderer.render(config, parsed_result.entry)
                output_path = _output_path(config, parsed_result.entry, rendered_result)

                if parsed_result.warnings:
                    report.warnings.extend(
                        [f"{typed_id.type}:{typed_id.id} -> {warning}" for warning in parsed_result.warnings]
                    )

                if output_path.exists() and not config.output.overwrite:
                    report.skipped += 1
                    continue

                output_path.write_text(rendered_result.markdown, encoding="utf-8")
                report.succeeded += 1
            except Exception as exc:  # noqa: BLE001
                report.failed += 1
                report.failures.append(f"{typed_id.type}:{typed_id.id} -> {exc}")
                if config.validation.fail_on_parse_error:
                    raise

    return report


def _output_path(config: AppConfig, entry: Any, rendered_result: RenderResult) -> Path:
    if rendered_result.filename is None:
        return output_path_for(config, entry)

    root = config.output.vault_root
    if config.output.folder_by_type:
        relative_dir = rendered_result.relative_dir or Path(f"{entry.typed_id.type}s")
        root = root / relative_dir
    root.mkdir(parents=True, exist_ok=True)
    return root / rendered_result.filename
