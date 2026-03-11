from __future__ import annotations

from pathlib import Path

from aon_import.config import AppConfig, TargetSpec
from aon_import.models import DeferredTarget, ResolutionResult, TypedId


def _read_ids_file(path: Path) -> tuple[set[int], list[str]]:
    ids: set[int] = set()
    warnings: list[str] = []

    if not path.exists():
        return ids, [f"ids_file not found: {path}"]

    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        try:
            value = int(cleaned)
            if value < 1:
                warnings.append(f"Skipped invalid ID {value} in {path}:{line_no}")
                continue
            ids.add(value)
        except ValueError:
            warnings.append(f"Skipped non-integer line in {path}:{line_no}")

    return ids, warnings


def _resolve_target(target: TargetSpec) -> tuple[set[int], list[str]]:
    warnings: list[str] = []
    merged: set[int] = set(target.ids)

    for start, end in target.id_ranges:
        merged.update(range(start, end + 1))

    if target.ids_file is not None:
        file_ids, file_warnings = _read_ids_file(target.ids_file)
        merged.update(file_ids)
        warnings.extend(file_warnings)

    before_exclusions = len(merged)
    merged.difference_update(target.exclude_ids)
    if target.exclude_ids and before_exclusions == len(merged):
        warnings.append(f"exclude_ids had no effect for target type '{target.type}'")

    return merged, warnings


def resolve_target_ids(config: AppConfig) -> ResolutionResult:
    result = ResolutionResult()

    for target in config.targets:
        ids, warnings = _resolve_target(target)
        result.warnings.extend(warnings)

        if not ids and target.where is not None:
            result.deferred_targets.append(
                DeferredTarget(type=target.type, where=target.where.model_dump())
            )
            continue

        for value in ids:
            result.resolved_ids.add(TypedId(type=target.type, id=value))

    return result


def summarize_resolution(result: ResolutionResult) -> str:
    lines: list[str] = []
    lines.append(f"Resolved IDs: {len(result.resolved_ids)}")

    by_type: dict[str, list[int]] = {}
    for entry in sorted(result.resolved_ids):
        by_type.setdefault(entry.type, []).append(entry.id)

    for page_type, ids in sorted(by_type.items()):
        lines.append(f"- {page_type}: {len(ids)} ({min(ids)}..{max(ids)})")

    if result.deferred_targets:
        deferred_types = ", ".join(sorted(target.type for target in result.deferred_targets))
        lines.append(f"Deferred targets: {len(result.deferred_targets)} ({deferred_types})")

    if result.warnings:
        lines.append(f"Warnings: {len(result.warnings)}")
        lines.extend(f"- {warning}" for warning in result.warnings)

    return "\n".join(lines)
