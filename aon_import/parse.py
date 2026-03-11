from __future__ import annotations

from datetime import datetime, timezone
import re

from bs4 import BeautifulSoup

from aon_import.contracts import ParseResult
from aon_import.models import ParsedEntry, TypedId


MAIN_CONTENT_IDS = [
    "ctl00_RadDrawer1_Content_MainContent_DetailedOutput",
    "MainContent_DetailedOutput",
    "ctl00_RadDrawer1_Content_MainContent_DetailsView",
]


def parse_entry(typed_id: TypedId, aon_url: str, html: str) -> ParseResult[ParsedEntry]:
    soup = BeautifulSoup(html, "lxml")
    _strip_noise(soup)

    root = _pick_root(soup)
    name = _extract_name(soup, root)
    traits = _extract_traits(root)
    source = _extract_source(root)
    text = _extract_text(root)
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


def _strip_noise(soup: BeautifulSoup) -> None:
    for selector in ["script", "style", "noscript", "header", "footer", "nav"]:
        for node in soup.select(selector):
            node.decompose()


def _pick_root(soup: BeautifulSoup):
    for content_id in MAIN_CONTENT_IDS:
        node = soup.find(id=content_id)
        if node is not None:
            return node
    main = soup.find("main")
    if main is not None:
        return main
    return soup.body or soup


def _extract_name(soup: BeautifulSoup, root) -> str:
    h1 = root.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(" ", strip=True)

    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    if title:
        title = re.sub(r"\s*\|\s*Archives of Nethys.*$", "", title).strip()
        title = re.sub(r"\s*-\s*Archives of Nethys.*$", "", title).strip()
    return title or "Unknown Entry"


def _extract_traits(root) -> list[str]:
    traits = {
        anchor.get_text(" ", strip=True)
        for anchor in root.select("a[href*='Traits.aspx'], span.trait, a.trait")
        if anchor.get_text(strip=True)
    }
    return sorted(traits)


def _extract_source(root) -> str | None:
    source_label = root.find(string=re.compile(r"^\s*Source\b", re.IGNORECASE))
    if not source_label:
        return None

    parent = source_label.parent
    if parent is None:
        return None

    text = parent.get_text(" ", strip=True)
    text = re.sub(r"^Source\s*", "", text, flags=re.IGNORECASE).strip(" :")
    return text or None


def _extract_text(root) -> str:
    for tag in root.select(".nethys-search, .print-only, .screen-only"):
        tag.decompose()

    raw = root.get_text("\n", strip=True)
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    condensed = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", condensed).strip()
