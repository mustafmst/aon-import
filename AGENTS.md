# AGENTS.md

Repository guidance for autonomous coding agents working in `pf2-data-import`.

## 1) Project overview

- Language: Python 3.11+
- Packaging: `pyproject.toml` with `setuptools`
- Entry point: `aon-import` -> `aon_import.cli:app`
- Runtime libs: `typer`, `pydantic`, `pyyaml`, `httpx`, `beautifulsoup4`, `lxml`
- Primary goal: import selected AoN PF2e pages into compact Obsidian markdown

## 2) Repository layout

- `aon_import/cli.py`: Typer CLI commands (`plan`, `import`, `stats`)
- `aon_import/config.py`: Pydantic config models + YAML loading
- `aon_import/resolver.py`: target expansion (`ids`, ranges, file, excludes)
- `aon_import/discover.py`: type/id -> AoN URL mapping
- `aon_import/fetch.py`: HTTP client with retries, backoff, delay, raw cache
- `aon_import/parse.py`: HTML parsing using BeautifulSoup + `lxml`
- `aon_import/render.py`: markdown and output path rendering
- `aon_import/scraper.py`: orchestration (resolve -> fetch -> parse -> write)
- `config.example.yaml`: reference config

## 3) Cursor/Copilot rule files

- No `.cursor/rules/` directory found.
- No `.cursorrules` file found.
- No `.github/copilot-instructions.md` file found.
- If any of these files are added later, treat them as higher-priority repository policy and update this file.

## 4) Setup commands

Use one of these setups (agent may pick the simplest working option).

### Option A: venv + pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

### Option B: direct install (if already in managed env)

```bash
pip install -e .
```

## 5) Build commands

There is no compile step; "build" means package build or CLI smoke run.

```bash
python -m pip install build
python -m build
```

CLI smoke checks:

```bash
aon-import plan -c config.example.yaml
python -m aon_import.cli plan -c config.example.yaml
```

## 6) Lint/format/type-check commands

No linter/formatter/type-checker is currently configured in `pyproject.toml`.
When validating changes, use this practical baseline:

```bash
python -m compileall aon_import
```

If you add tooling, prefer:

```bash
ruff check .
ruff format .
mypy aon_import
```

Do not introduce tool configs unless task requires it.

## 7) Test commands

No test suite exists yet. If tests are added (recommended: `pytest`):

Run all tests:

```bash
pytest
```

Run one file:

```bash
pytest tests/test_resolver.py
```

Run one test function:

```bash
pytest tests/test_resolver.py::test_expand_ranges
```

Run tests by keyword expression:

```bash
pytest -k "resolver and not slow"
```

Stop early on first failure:

```bash
pytest -x
```

## 8) Coding style guidelines

### Imports

- Use absolute imports from `aon_import.*`.
- Group imports: stdlib, third-party, local.
- Keep imports deterministic and minimal.
- Avoid runtime-heavy imports in module top-level unless needed.

### Formatting

- Follow PEP 8 with 4-space indentation.
- Keep functions focused and small.
- Prefer explicit names over inline cleverness.
- Preserve existing quote/style patterns in touched files.

### Types

- Add type hints to public functions and return values.
- Use concrete container types where useful (`list[str]`, `set[int]`).
- Preserve use of `Literal` for constrained enums (`PageType`).
- Keep dataclasses/Pydantic models typed end-to-end.

### Naming

- `snake_case` for variables/functions/modules.
- `PascalCase` for classes.
- `UPPER_SNAKE_CASE` for constants.
- Use domain names matching AoN/PF2e terminology (typed id, traits, source).

### Error handling

- Fail fast for invalid user config with actionable messages.
- Catch broad exceptions only at orchestration boundaries (e.g., import loop).
- Prefer raising specific exceptions inside low-level helpers.
- Include context in errors (`type:id`, URL, file path).

### I/O and paths

- Resolve relative paths against config location (already implemented in config loader).
- Use `Path` APIs, UTF-8 text I/O.
- Avoid deleting user files unless explicitly requested.
- Respect `overwrite` behavior when writing notes.

### HTTP/scraping

- Keep polite scraping defaults (delay jitter, retries, clear user-agent).
- Reuse HTTP client; avoid creating one client per request.
- Preserve caching behavior; do not disable by default.
- Do not widen scraping scope beyond configured targets unless asked.

### Parsing/rendering

- Parser should be tolerant to minor HTML structure changes.
- Keep markdown compact and stable for Obsidian diffs.
- Avoid injecting noisy metadata into output files.
- Keep slugification deterministic.

### CLI behavior

- Maintain current command semantics (`plan`, `import`, `stats`).
- Keep output human-readable and concise.
- Do not break existing flags without migration notes.

## 9) Change management expectations for agents

- Make minimal, targeted changes.
- Do not refactor unrelated modules in the same patch.
- Update docs/config examples when behavior changes.
- If adding a dependency, justify it and update `pyproject.toml`.
- Prefer backward-compatible config evolution.

## 10) Suggested verification before finishing a task

```bash
python -m compileall aon_import
aon-import plan -c config.example.yaml
```

If tests exist in your branch:

```bash
pytest
pytest tests/test_x.py::test_y
```

## 11) Known current gaps (do not assume implemented)

- `where`-only targets are currently deferred, not fully discovered/imported.
- No built-in automated test suite yet.
- No pinned lint/type toolchain yet.

When implementing these gaps, keep behavior explicit and documented.
