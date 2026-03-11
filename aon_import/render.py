from __future__ import annotations

from pathlib import Path
import re

from aon_import.config import AppConfig
from aon_import.models import ParsedEntry


TYPE_TO_FOLDER = {
    "spell": "spells",
    "feat": "feats",
    "item": "items",
    "equipment": "equipment",
    "action": "actions",
    "trait": "traits",
    "condition": "conditions",
    "ancestry": "ancestries",
    "heritage": "heritages",
    "background": "backgrounds",
    "class": "classes",
    "archetype": "archetypes",
    "creature": "creatures",
    "deity": "deities",
    "ritual": "rituals",
    "hazard": "hazards",
}


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-") or "unnamed"


def filename_for(entry: ParsedEntry, template: str) -> str:
    raw = template.format(
        name=slugify(entry.name),
        type=entry.typed_id.type,
        id=entry.typed_id.id,
    )
    return raw if raw.endswith(".md") else f"{raw}.md"


def render_markdown(config: AppConfig, entry: ParsedEntry) -> str:
    chunks: list[str] = []

    if config.markdown.include_frontmatter:
        traits_literal = ", ".join(f'"{trait}"' for trait in entry.traits)
        chunks.extend(
            [
                "---",
                f'id: "aon-{entry.typed_id.type}-{entry.typed_id.id}"',
                f'name: "{entry.name}"',
                f'type: "{entry.typed_id.type}"',
                f"aon_id: {entry.typed_id.id}",
                f'aon_url: "{entry.aon_url}"',
                f'source: "{entry.source or ""}"',
                f"traits: [{traits_literal}]",
                f'fetched_at: "{entry.fetched_at}"',
                "---",
                "",
            ]
        )

    chunks.append(f"# {entry.name}")
    chunks.append("")

    if config.markdown.include_source_block and entry.source:
        chunks.append(f"**Source:** {entry.source}")
        chunks.append("")

    body_text = entry.text
    if config.markdown.compact_mode:
        body_text = _compact_text(body_text)
    chunks.append(body_text)

    if config.markdown.include_aon_link:
        chunks.extend(["", "## AoN", f"- {entry.aon_url}"])

    return "\n".join(chunks).strip() + "\n"


def output_path_for(config: AppConfig, entry: ParsedEntry) -> Path:
    root = config.output.vault_root
    if config.output.folder_by_type:
        root = root / TYPE_TO_FOLDER.get(entry.typed_id.type, f"{entry.typed_id.type}s")
    root.mkdir(parents=True, exist_ok=True)
    return root / filename_for(entry, config.output.filename_template)


def _compact_text(value: str) -> str:
    value = re.sub(r"[ \t]{2,}", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()
