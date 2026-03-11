from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


PageType = Literal[
    "spell",
    "feat",
    "item",
    "action",
    "trait",
    "condition",
    "ancestry",
    "heritage",
    "background",
    "class",
    "archetype",
    "creature",
    "deity",
    "equipment",
    "ritual",
    "hazard",
]


@dataclass(frozen=True, order=True)
class TypedId:
    type: PageType
    id: int


@dataclass
class DeferredTarget:
    type: PageType
    where: dict[str, list[str]]


@dataclass
class ResolutionResult:
    resolved_ids: set[TypedId] = field(default_factory=set)
    deferred_targets: list[DeferredTarget] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ParsedEntry:
    typed_id: TypedId
    name: str
    aon_url: str
    fetched_at: str
    source: str | None
    traits: list[str]
    text: str
    raw_text: str = ""
    parse_warnings: list[str] = field(default_factory=list)
    output_path: Path | None = None


@dataclass
class ImportReport:
    total: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
