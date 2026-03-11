from aon_import.endpoints.creature.parser import CreatureParser
from aon_import.models import TypedId


SAMPLE_HTML = """
<html>
  <head><title>Test Creature | Archives of Nethys</title></head>
  <body>
    <div id="MainContent_DetailedOutput">
      <h1>Test Creature</h1>
      <p>Creature 5</p>
      <p>Source Bestiary</p>
      <p>AC 22; Fort +14, Ref +10, Will +12</p>
      <p>HP 85</p>
      <p>Speed 25 feet, fly 40 feet</p>
      <p>Melee jaws +15 (reach 10 feet), Damage 2d10+7 piercing</p>
      <p>Ranged spit +13 (range 30 feet), Damage 2d6 acid</p>
    </div>
  </body>
</html>
"""


def test_creature_parser_extracts_core_fields() -> None:
    parser = CreatureParser()
    result = parser.parse(TypedId(type="creature", id=42), "https://example.test", SAMPLE_HTML)

    assert result.entry.name == "Test Creature"
    assert result.entry.level == 5
    assert result.entry.ac == 22
    assert result.entry.hp == 85
    assert result.entry.fort == 14
    assert result.entry.ref == 10
    assert result.entry.will == 12
    assert "25 feet" in result.entry.speeds
    assert len(result.entry.attacks) == 2
