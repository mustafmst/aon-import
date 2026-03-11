from __future__ import annotations

from aon_import.models import PageType, TypedId


TYPE_TO_ENDPOINT: dict[PageType, str] = {
    "spell": "Spells.aspx",
    "feat": "Feats.aspx",
    "item": "Equipment.aspx",
    "equipment": "Equipment.aspx",
    "action": "Actions.aspx",
    "trait": "Traits.aspx",
    "condition": "Conditions.aspx",
    "ancestry": "Ancestries.aspx",
    "heritage": "Heritages.aspx",
    "background": "Backgrounds.aspx",
    "class": "Classes.aspx",
    "archetype": "Archetypes.aspx",
    "creature": "Monsters.aspx",
    "deity": "Deities.aspx",
    "ritual": "Rituals.aspx",
    "hazard": "Hazards.aspx",
}


def build_detail_url(typed_id: TypedId) -> str:
    endpoint = TYPE_TO_ENDPOINT.get(typed_id.type)
    if endpoint is None:
        raise ValueError(f"Unsupported type: {typed_id.type}")
    return f"https://2e.aonprd.com/{endpoint}?ID={typed_id.id}"
