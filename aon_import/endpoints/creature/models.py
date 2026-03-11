from __future__ import annotations

from dataclasses import dataclass, field

from aon_import.models import TypedId


@dataclass
class CreatureEntry:
    typed_id: TypedId
    aon_url: str
    fetched_at: str
    name: str
    source: str | None = None
    traits: list[str] = field(default_factory=list)
    raw_text: str = ""
    parse_warnings: list[str] = field(default_factory=list)

    level: int | None = None
    ac: int | None = None
    hp: int | None = None
    fort: int | None = None
    ref: int | None = None
    will: int | None = None
    speeds: list[str] = field(default_factory=list)
    attacks: list[str] = field(default_factory=list)
    abilities: list[str] = field(default_factory=list)
