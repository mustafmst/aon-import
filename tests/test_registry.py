from aon_import.endpoints.creature.parser import CreatureParser
from aon_import.endpoints.creature.renderer import CreatureRenderer
from aon_import.registry import build_default_registry


def test_registry_has_creature_specific_handler() -> None:
    registry = build_default_registry()
    handler = registry.get("creature")

    assert isinstance(handler.parser, CreatureParser)
    assert isinstance(handler.renderer, CreatureRenderer)
