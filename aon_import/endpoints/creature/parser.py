from __future__ import annotations

from datetime import datetime, timezone
import re

from bs4 import BeautifulSoup

from aon_import.contracts import ParseResult
from aon_import.endpoints.creature.models import CreatureEntry
from aon_import.html_utils import (
    extract_name,
    extract_source,
    extract_text,
    extract_traits,
    pick_root,
    strip_noise,
)
from aon_import.models import TypedId


class CreatureParser:
    def parse(self, typed_id: TypedId, url: str, html: str) -> ParseResult[CreatureEntry]:
        soup = BeautifulSoup(html, "lxml")
        strip_noise(soup)
        root = pick_root(soup)

        text = extract_text(root)
        name = extract_name(soup, root)
        source = extract_source(root)
        traits = extract_traits(root)

        warnings: list[str] = []
        if name == "Unknown Entry":
            warnings.append("Creature name was not found in page structure")

        level = _match_int(r"\bCreature\s*(-?\d+)\b", text)
        ac = _match_int(r"\bAC\s*(\d+)\b", text)
        hp = _match_int(r"\bHP\s*(\d+)\b", text)
        fort = _match_int(r"\bFort\s*\+?(\d+)\b", text)
        ref = _match_int(r"\bRef\s*\+?(\d+)\b", text)
        will = _match_int(r"\bWill\s*\+?(\d+)\b", text)

        speeds = _extract_speeds(text)
        attacks = _extract_attacks(text)
        abilities = _extract_abilities(text)

        if level is None:
            warnings.append("Creature level was not parsed")
        if hp is None:
            warnings.append("Creature HP was not parsed")

        entry = CreatureEntry(
            typed_id=typed_id,
            aon_url=url,
            fetched_at=datetime.now(timezone.utc).isoformat(),
            name=name,
            source=source,
            traits=traits,
            raw_text=text,
            parse_warnings=warnings.copy(),
            level=level,
            ac=ac,
            hp=hp,
            fort=fort,
            ref=ref,
            will=will,
            speeds=speeds,
            attacks=attacks,
            abilities=abilities,
        )
        return ParseResult(entry=entry, warnings=warnings)


def _match_int(pattern: str, text: str) -> int | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if match is None:
        return None
    return int(match.group(1))


def _extract_speeds(text: str) -> list[str]:
    speeds: list[str] = []
    for line in text.splitlines():
        if not line.lower().startswith("speed"):
            continue
        payload = line[len("speed") :].strip(" :")
        if payload:
            speeds.extend(part.strip() for part in payload.split(",") if part.strip())
    return speeds


def _extract_attacks(text: str) -> list[str]:
    attacks: list[str] = []
    for line in text.splitlines():
        lowered = line.lower()
        if lowered.startswith("melee") or lowered.startswith("ranged"):
            attacks.append(line.strip())
    return attacks


def _extract_abilities(text: str) -> list[str]:
    abilities: list[str] = []
    for line in text.splitlines():
        if "[one-action]" not in line and "[two-actions]" not in line and "[reaction]" not in line:
            continue
        if line.lower().startswith(("melee", "ranged", "speed")):
            continue
        abilities.append(line.strip())
    return abilities
