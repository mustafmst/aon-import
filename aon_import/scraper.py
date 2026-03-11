from __future__ import annotations

from aon_import.config import AppConfig
from aon_import.discover import build_detail_url
from aon_import.fetch import Fetcher
from aon_import.models import ImportReport
from aon_import.parse import parse_entry
from aon_import.render import output_path_for, render_markdown
from aon_import.resolver import resolve_target_ids


def run_import(config: AppConfig) -> ImportReport:
    resolution = resolve_target_ids(config)
    report = ImportReport(total=len(resolution.resolved_ids))
    report.warnings.extend(resolution.warnings)

    with Fetcher(config) as fetcher:
        for typed_id in sorted(resolution.resolved_ids):
            try:
                url = build_detail_url(typed_id)
                html = fetcher.fetch(url)
                parsed_result = parse_entry(typed_id, url, html)
                rendered_result = render_markdown(config, parsed_result.entry)
                output_path = output_path_for(config, parsed_result.entry)

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
