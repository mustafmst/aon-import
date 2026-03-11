from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Generic, Protocol, TYPE_CHECKING, TypeVar

from aon_import.models import TypedId

if TYPE_CHECKING:
    from aon_import.config import AppConfig


class EntryContext(Protocol):
    typed_id: TypedId
    aon_url: str
    fetched_at: str
    source: str | None
    traits: list[str]
    raw_text: str
    parse_warnings: list[str]


TEntry = TypeVar("TEntry", bound=EntryContext)


@dataclass
class ParseResult(Generic[TEntry]):
    entry: TEntry
    warnings: list[str] = field(default_factory=list)


@dataclass
class RenderResult:
    markdown: str
    relative_dir: Path | None = None
    filename: str | None = None


class Parser(Protocol[TEntry]):
    def parse(self, typed_id: TypedId, url: str, html: str) -> ParseResult[TEntry]: ...


class Renderer(Protocol[TEntry]):
    def render(self, config: "AppConfig", entry: TEntry) -> RenderResult: ...
