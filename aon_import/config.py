from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, ValidationError, model_validator

from aon_import.models import PageType


class OutputConfig(BaseModel):
    vault_root: Path
    folder_by_type: bool = True
    overwrite: bool = True
    filename_template: str = "{name}__{type}__{id}.md"


class HttpConfig(BaseModel):
    user_agent: str = "pf2-obsidian-importer/0.1 (+local use)"
    timeout_seconds: int = 20
    delay_ms: tuple[int, int] = (500, 1200)
    max_retries: int = 4
    backoff_seconds: float = 1.5

    @model_validator(mode="after")
    def check_delay(self) -> "HttpConfig":
        minimum, maximum = self.delay_ms
        if minimum < 0 or maximum < minimum:
            raise ValueError("delay_ms must be [min>=0, max>=min]")
        return self


class CacheConfig(BaseModel):
    enabled: bool = True
    db_path: Path = Path(".cache/aon-import.sqlite")
    raw_html_dir: Path = Path(".cache/raw")
    revalidate: bool = True


class MarkdownConfig(BaseModel):
    include_frontmatter: bool = True
    include_source_block: bool = True
    include_aon_link: bool = True
    compact_mode: bool = True
    link_traits: bool = True
    link_sources: bool = False


class WhereFilter(BaseModel):
    source_in: list[str] = Field(default_factory=list)
    trait_any: list[str] = Field(default_factory=list)


class TargetSpec(BaseModel):
    type: PageType
    ids: list[int] = Field(default_factory=list)
    id_ranges: list[tuple[int, int]] = Field(default_factory=list)
    ids_file: Path | None = None
    exclude_ids: list[int] = Field(default_factory=list)
    where: WhereFilter | None = None

    @model_validator(mode="after")
    def validate_selector_presence(self) -> "TargetSpec":
        has_selector = bool(self.ids or self.id_ranges or self.ids_file or self.where)
        if not has_selector:
            raise ValueError(
                "Target requires at least one selector: ids, id_ranges, ids_file, or where"
            )
        for entry_id in [*self.ids, *self.exclude_ids]:
            if entry_id < 1:
                raise ValueError("All IDs must be >= 1")
        for start, end in self.id_ranges:
            if start < 1 or end < 1:
                raise ValueError("Range bounds must be >= 1")
            if end < start:
                raise ValueError(f"Invalid range [{start}, {end}] (end < start)")
        return self


class ValidationConfig(BaseModel):
    fail_on_missing: bool = False
    fail_on_parse_error: bool = False
    strict_type_check: bool = True


class AppConfig(BaseModel):
    version: Literal[1] = 1
    output: OutputConfig
    http: HttpConfig = HttpConfig()
    cache: CacheConfig = CacheConfig()
    markdown: MarkdownConfig = MarkdownConfig()
    targets: list[TargetSpec]
    validation: ValidationConfig = ValidationConfig()


def load_config(config_path: Path) -> AppConfig:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if raw is None:
        raise ValueError(f"Config file is empty: {config_path}")

    try:
        config = AppConfig.model_validate(raw)
    except ValidationError as exc:
        issues: list[str] = []
        for error in exc.errors():
            loc = ".".join(str(piece) for piece in error["loc"])
            issues.append(f"- {loc}: {error['msg']}")
        details = "\n".join(issues)
        raise ValueError(f"Invalid config:\n{details}") from exc

    base = config_path.parent.resolve()
    config.output.vault_root = _resolve_path(base, config.output.vault_root)
    config.cache.db_path = _resolve_path(base, config.cache.db_path)
    config.cache.raw_html_dir = _resolve_path(base, config.cache.raw_html_dir)
    for target in config.targets:
        if target.ids_file is not None:
            target.ids_file = _resolve_path(base, target.ids_file)

    return config


def _resolve_path(base: Path, candidate: Path) -> Path:
    if candidate.is_absolute():
        return candidate
    return (base / candidate).resolve()
