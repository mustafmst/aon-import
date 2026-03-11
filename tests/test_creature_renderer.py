from aon_import.config import AppConfig, MarkdownConfig, OutputConfig
from aon_import.endpoints.creature.models import CreatureEntry
from aon_import.endpoints.creature.renderer import CreatureRenderer
from aon_import.models import TypedId


def test_creature_renderer_only_shows_parsed_sections(tmp_path) -> None:
    config = AppConfig(
        output=OutputConfig(vault_root=tmp_path),
        markdown=MarkdownConfig(include_frontmatter=True, include_aon_link=False),
        targets=[{"type": "creature", "ids": [1]}],
    )
    entry = CreatureEntry(
        typed_id=TypedId(type="creature", id=1),
        aon_url="https://example.test",
        fetched_at="2026-01-01T00:00:00+00:00",
        name="Sparse Creature",
        hp=30,
    )

    rendered = CreatureRenderer().render(config, entry).markdown

    assert "## Defenses" in rendered
    assert "HP 30" in rendered
    assert "## Attacks" not in rendered
    assert "## Speeds" not in rendered
    assert "## Abilities" not in rendered
