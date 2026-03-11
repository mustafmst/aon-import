from __future__ import annotations

import re

from bs4 import BeautifulSoup


MAIN_CONTENT_IDS = [
    "ctl00_RadDrawer1_Content_MainContent_DetailedOutput",
    "MainContent_DetailedOutput",
    "ctl00_RadDrawer1_Content_MainContent_DetailsView",
]


def strip_noise(soup: BeautifulSoup) -> None:
    for selector in ["script", "style", "noscript", "header", "footer", "nav"]:
        for node in soup.select(selector):
            node.decompose()


def pick_root(soup: BeautifulSoup):
    for content_id in MAIN_CONTENT_IDS:
        node = soup.find(id=content_id)
        if node is not None:
            return node
    main = soup.find("main")
    if main is not None:
        return main
    return soup.body or soup


def extract_name(soup: BeautifulSoup, root) -> str:
    h1 = root.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(" ", strip=True)

    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    if title:
        title = re.sub(r"\s*\|\s*Archives of Nethys.*$", "", title).strip()
        title = re.sub(r"\s*-\s*Archives of Nethys.*$", "", title).strip()
    return title or "Unknown Entry"


def extract_traits(root) -> list[str]:
    traits = {
        anchor.get_text(" ", strip=True)
        for anchor in root.select("a[href*='Traits.aspx'], span.trait, a.trait")
        if anchor.get_text(strip=True)
    }
    return sorted(traits)


def extract_source(root) -> str | None:
    source_label = root.find(string=re.compile(r"^\s*Source\b", re.IGNORECASE))
    if not source_label:
        return None

    parent = source_label.parent
    if parent is None:
        return None

    text = parent.get_text(" ", strip=True)
    text = re.sub(r"^Source\s*", "", text, flags=re.IGNORECASE).strip(" :")
    return text or None


def extract_text(root) -> str:
    for tag in root.select(".nethys-search, .print-only, .screen-only"):
        tag.decompose()

    raw = root.get_text("\n", strip=True)
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    condensed = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", condensed).strip()
