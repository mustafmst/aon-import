from __future__ import annotations

from aon_import.config import AppConfig
from aon_import.contracts import ParseResult, RenderResult
from aon_import.models import ParsedEntry, TypedId
from aon_import.parse import parse_entry
from aon_import.render import render_markdown


class GenericParser:
    def parse(self, typed_id: TypedId, url: str, html: str) -> ParseResult[ParsedEntry]:
        return parse_entry(typed_id, url, html)


class GenericRenderer:
    def render(self, config: AppConfig, entry: ParsedEntry) -> RenderResult:
        return render_markdown(config, entry)
