from __future__ import annotations

from datetime import datetime, timezone

from bs4 import BeautifulSoup

from aon_import.contracts import ParseResult
from aon_import.html_utils import (
    extract_name,
    extract_source,
    extract_text,
    extract_traits,
    pick_root,
    strip_noise,
)
from aon_import.models import ParsedEntry, TypedId


def parse_entry(typed_id: TypedId, aon_url: str, html: str) -> ParseResult[ParsedEntry]:
    soup = BeautifulSoup(html, "lxml")
    strip_noise(soup)

    root = pick_root(soup)
    name = extract_name(soup, root)
    traits = extract_traits(root)
    source = extract_source(root)
    text = extract_text(root)
    warnings: list[str] = []

    if name == "Unknown Entry":
        warnings.append("Entry name was not found in page structure")

    if not text:
        warnings.append("Entry body text is empty")

    entry = ParsedEntry(
        typed_id=typed_id,
        name=name,
        aon_url=aon_url,
        fetched_at=datetime.now(timezone.utc).isoformat(),
        source=source,
        traits=traits,
        text=text,
        raw_text=text,
        parse_warnings=warnings.copy(),
    )
    return ParseResult(entry=entry, warnings=warnings)
