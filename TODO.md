# TODO.md

## Project Vision

Build a robust AoN -> Obsidian importer that supports multiple endpoint-specific parsers/renderers while sharing a common import pipeline.

Core idea:
- Keep one orchestration flow (`resolve -> fetch -> parse -> render -> write`)
- Plug in endpoint-specific logic for parsing and markdown rendering
- Scale endpoint support incrementally with predictable quality gates

---

## Milestone 1: Multi-parser / multi-renderer architecture

Goal:
Refactor current script into a modular plugin-style system that can route each `(type, id)` target to the correct parser and renderer.

### 1.1 Define architecture contracts
- [ ] Create parser interface/protocol:
  - Input: `TypedId`, `url`, `html`
  - Output: typed domain model (not generic raw dict)
- [ ] Create renderer interface/protocol:
  - Input: typed domain model + config
  - Output: markdown string + output path metadata
- [ ] Define shared context object for common fields (url, source, traits, raw text fallback, fetched_at)

### 1.2 Add registry/routing layer
- [ ] Implement endpoint registry keyed by `PageType`
- [ ] Register parser+renderer pairs per endpoint
- [ ] Add startup validation that configured types are supported
- [ ] Add fallback policy for unsupported types (warning vs fail-fast)

### 1.3 Refactor scraper pipeline
- [ ] Replace generic parse/render calls with registry-dispatched handlers
- [ ] Keep existing fetch/cache/retry behavior unchanged
- [ ] Preserve current CLI behavior (`plan`, `import`, `stats`)
- [ ] Ensure failures are reported with clear `type:id` context

### 1.4 Shared utilities extraction
- [ ] Move common HTML helpers into reusable module:
  - root selection
  - whitespace normalization
  - source/traits extraction helpers
- [ ] Move markdown utilities into reusable module:
  - slugify
  - frontmatter helpers
  - safe escaping for YAML strings

### 1.5 Tests for architecture
- [ ] Add unit tests for registry dispatch
- [ ] Add tests for unsupported type behavior
- [ ] Add test that scraper calls the correct parser/renderer pair
- [ ] Add fixture-based test for generic fallback behavior

### 1.6 Definition of done (Milestone 1)
- [ ] Import flow supports multiple parser/renderer implementations
- [ ] Existing endpoint behavior remains functional
- [ ] Errors and logs identify parser/renderer by endpoint type
- [ ] Basic tests exist for routing + integration seam

---

## Milestone 2: Creature endpoint implementation

Goal:
Deliver high-quality creature parser + renderer with stable, compact markdown suitable for Obsidian gameplay prep.

### 2.1 Creature domain model
- [ ] Define `CreatureEntry` model with key fields:
  - name, level, rarity, alignment (if present), size
  - traits
  - perception, languages, skills
  - ability modifiers
  - items
  - defenses (AC, saves, HP, immunities, resistances, weaknesses)
  - speeds
  - attacks
  - spellcasting blocks
  - abilities/actions/reactions
  - source, aon_url, aon_id, fetched_at
- [ ] Explicitly model optional fields and repeated blocks

### 2.2 Creature parser
- [ ] Implement HTML block extraction for creature statblock structure
- [ ] Parse fields with resilient selectors and label-based fallback
- [ ] Normalize numeric/text values where practical
- [ ] Preserve unknown/unparsed sections in a structured fallback block
- [ ] Add parser warnings for partially parsed sections (non-fatal)

### 2.3 Creature renderer
- [ ] Design compact markdown layout optimized for session use
- [ ] Include stable frontmatter for indexing/filtering in Obsidian
- [ ] Keep body sections predictable and concise
- [ ] Preserve important tactical text without noisy boilerplate
- [ ] Ensure deterministic ordering for clean diffs

### 2.4 Creature tests and fixtures
- [ ] Add HTML fixtures for diverse creature pages
- [ ] Add parser tests covering:
  - simple creatures
  - spellcasters
  - edge cases with missing fields
- [ ] Add markdown snapshot tests for stable output
- [ ] Add regression tests for known parsing pitfalls

### 2.5 Definition of done (Milestone 2)
- [ ] Creature import works end-to-end via CLI
- [ ] Output is compact, readable, and stable across reruns
- [ ] Parser tolerates minor AoN structure differences
- [ ] Test coverage exists for representative creature variants

---

## Future Milestones (placeholder)

To be defined after Milestone 2:
- [ ] Spells parser+renderer
- [ ] Feats parser+renderer
- [ ] Items/Equipment parser+renderer
- [ ] Actions parser+renderer
- [ ] Trait/Condition enrichments
- [ ] Link graph improvements (`[[...]]`) and cross-note references

---

## Cross-cutting quality work

- [ ] Add structured logging with per-target timing
- [ ] Add import summary metrics by endpoint type
- [ ] Improve incremental update logic (content hash + skip unchanged)
- [ ] Expand config validation for endpoint-specific options
- [ ] Document contributor workflow in README/AGENTS

---

## Risks and mitigations

- AoN HTML variability:
  - Mitigation: selector fallback + label-based parsing + fixtures
- Overly rigid schema:
  - Mitigation: optional fields + unknown-section capture
- Markdown churn/noisy diffs:
  - Mitigation: deterministic ordering and stable rendering rules

---

## Suggested execution order

1. Milestone 1 architecture (registry + interfaces + dispatch tests)
2. Creature model design
3. Creature parser implementation + fixtures
4. Creature renderer implementation + snapshots
5. End-to-end creature import smoke checks
6. Iterate based on real output in Obsidian
