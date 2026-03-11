# AoN PF2e Importer

Import selected Pathfinder 2e entries from Archives of Nethys into compact Markdown files for Obsidian.

## Quick start

1. Create a virtual environment and install dependencies.
2. Copy `config.example.yaml` to `config.yaml` and edit targets.
3. Run:

```bash
aon-import plan -c config.yaml
aon-import import -c config.yaml
```

## Notes

- This tool is target-first: it imports only IDs/types configured under `targets`.
- `where`-only targets are accepted but currently deferred until listing-page discovery is added.
- HTML parsing uses BeautifulSoup with `lxml` backend.
