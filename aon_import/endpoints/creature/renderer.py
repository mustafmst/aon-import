from __future__ import annotations

from pathlib import Path

from aon_import.config import AppConfig
from aon_import.contracts import RenderResult
from aon_import.endpoints.creature.models import CreatureEntry
from aon_import.render import slugify


class CreatureRenderer:
    def render(self, config: AppConfig, entry: CreatureEntry) -> RenderResult:
        chunks: list[str] = []

        if config.markdown.include_frontmatter:
            chunks.extend(["---"])
            chunks.append(f'id: "aon-creature-{entry.typed_id.id}"')
            chunks.append(f'name: "{entry.name}"')
            chunks.append('type: "creature"')
            chunks.append(f"aon_id: {entry.typed_id.id}")
            chunks.append(f'aon_url: "{entry.aon_url}"')
            if entry.level is not None:
                chunks.append(f"level: {entry.level}")
            if entry.source:
                chunks.append(f'source: "{entry.source}"')
            if entry.traits:
                traits_literal = ", ".join(f'"{trait}"' for trait in entry.traits)
                chunks.append(f"traits: [{traits_literal}]")
            chunks.append(f'fetched_at: "{entry.fetched_at}"')
            chunks.extend(["---", ""])

        chunks.append(f"# {entry.name}")
        chunks.append("")

        if entry.level is not None:
            chunks.append(f"**Level:** {entry.level}")

        defense_bits: list[str] = []
        if entry.ac is not None:
            defense_bits.append(f"AC {entry.ac}")
        if entry.hp is not None:
            defense_bits.append(f"HP {entry.hp}")

        saves: list[str] = []
        if entry.fort is not None:
            saves.append(f"Fort +{entry.fort}")
        if entry.ref is not None:
            saves.append(f"Ref +{entry.ref}")
        if entry.will is not None:
            saves.append(f"Will +{entry.will}")
        if saves:
            defense_bits.append("Saves " + ", ".join(saves))

        if defense_bits:
            chunks.append("")
            chunks.append("## Defenses")
            chunks.extend(f"- {value}" for value in defense_bits)

        if entry.speeds:
            chunks.append("")
            chunks.append("## Speeds")
            chunks.extend(f"- {value}" for value in entry.speeds)

        if entry.attacks:
            chunks.append("")
            chunks.append("## Attacks")
            chunks.extend(f"- {value}" for value in entry.attacks)

        if entry.abilities:
            chunks.append("")
            chunks.append("## Abilities")
            chunks.extend(f"- {value}" for value in entry.abilities)

        if config.markdown.include_aon_link:
            chunks.extend(["", "## AoN", f"- {entry.aon_url}"])

        markdown = "\n".join(chunks).strip() + "\n"
        filename = f"{slugify(entry.name)}__creature__{entry.typed_id.id}.md"
        return RenderResult(markdown=markdown, relative_dir=Path("creatures"), filename=filename)
