# Implementation — Author wave-1 SE worker agents

Execution plan for `07-25-worker-agents`. Follow in order. Context order for any
sub-agent: jsonl → prd.md → design.md → this file. All file:line anchors are
from `research/*.md`; re-verify before editing (line numbers drift).

## Step 0 — Re-verify anchors

- `installer/registry.py`: RuntimeProfile dataclass (~43-50), KNOWN_RUNTIME_*
  (~157-160), profile constants (~162-174), assignments (~178-250),
  `validate_runtime_profile` (~253-265), `__all__` (~657-693).
- `.github/scripts/generate-skill-surfaces.py`: `agent_names()` (~613-622),
  `validate_agents()` (~697-719), `main()` validate/render wiring (~1217+).
- `templates/agents/se-smoke.md` present; `templates/skills/se-research/SKILL.md`
  + `templates/skills/se-fact-check/SKILL.md` `## Sub-agent dispatch` sections.
- `tests/test_install.py:344-377`, `tests/test_generate.py:583`.

## Step 1 — Author the two agents

Create `templates/agents/se-source-reader.md` and
`templates/agents/se-claim-verifier.md` per design "Agent bodies". Frontmatter:
`name` (== file stem), `description` (single line, no double quotes, ≤1024, no
`Use when` prefix required). No `tools`/`model`/`sandbox_mode`. Body opens with an
H1; encode the R2/R3/R5/R6 governance invariants; file ends with a newline. Keep
bodies neutral (no brand words).

## Step 2 — Retire se-smoke (D1)

- Delete `templates/agents/se-smoke.md`.
- Add to `installer/removal.py` `RETIRED_TARGETS` (~49-56) both last-shipped
  se-smoke targets: `.claude/agents/se-smoke.md`, `.codex/agents/se-smoke.toml`
  (match the existing entry's shape/scope).

## Step 3 — RuntimeProfile delegation axis (D2/D3)

In `installer/registry.py`:
- Add trailing default fields to `RuntimeProfile`: `delegation: str = "none"`,
  `roles: tuple[str, ...] = ()`.
- Add `KNOWN_RUNTIME_DELEGATIONS = frozenset({"none","optional","required"})`
  next to the other KNOWN_RUNTIME_* sets.
- In `validate_runtime_profile`, add the `delegation` row (value ∈
  KNOWN_RUNTIME_DELEGATIONS) and the coherence check: `none ⇔ roles == ()`;
  `optional|required ⇒ roles` non-empty. Roles must be a tuple of non-empty
  strings. (Agent-existence is NOT checked here — that is the generator gate,
  Step 4.)
- Add `DEEP_ANALYSIS_SOURCE_READING` and `DEEP_ANALYSIS_CLAIM_VERIFYING`
  constants (design D3). In `RUNTIME_PROFILE_ASSIGNMENTS`, remove `se-research`
  and `se-fact-check` from the `DEEP_ANALYSIS` group and add two new
  single-skill groups mapping them to the new constants. Leave the other three
  skills on `DEEP_ANALYSIS`.
- Export `KNOWN_RUNTIME_DELEGATIONS` (and the two new constants if any external
  consumer needs them) in `__all__`.

Validation: `python3 -c "import installer.registry"` must import clean
(import-time `validate_registry` runs).

## Step 4 — Generator delegation-role existence gate (D4)

In `.github/scripts/generate-skill-surfaces.py` add
`validate_delegation_roles(profiles=SKILL_RUNTIME_PROFILES, known_agents=None)`:
when `known_agents` is None, default it to `set(agent_names())`; collect every
role across `profiles.values()`; assert each ∈ `known_agents`; raise
`GenerationError` naming any dangling role. The injectable parameters let the
dangling-role fixture test (Step 8) pass a synthetic profile map + agent set
without mutating `templates/agents/`. Call it in `main()` right after
`validate_agents()` with no args (agents known by then). No renderer change
(delegation does not map to any overlay field).

## Step 5 — Optional role references in pilot dispatch bodies (D5)

Amend the existing `## Sub-agent dispatch` sections (canonical bodies, all
platforms):
- `templates/skills/se-research/SKILL.md`: add one optional-framed clause to the
  Worker input contract naming `se-source-reader` as an enhancement over a
  generic host subagent; run the unit inline where no such role exists.
- `templates/skills/se-fact-check/SKILL.md`: same, naming `se-claim-verifier`
  on the per-claim worker contract.
Keep neutral; keep optional; do not alter scope/verdict-ladder/Final-report
text.

## Step 6 — Version + changelog + docs (AC4)

- Bump `manifest.json` `"version"` 0.66.12 → 0.66.13 **before** `make generate`.
- Prepend `CHANGELOG.md` `## 0.66.13 - 2026-08-05` entry describing the two
  agents, the delegation axis + existence gate, the optional pilot role
  references, and se-smoke retirement.
- `docs/SE_AI_COMMAND_PACK.md`: add a named agent inventory section listing
  `se-source-reader` and `se-claim-verifier` (one line each: role + bounded
  authority). Note se-smoke retired if the surrounding prose warrants.

## Step 7 — Generate + verify scope

- `make generate`. Expect: −2 se-smoke overlays, +4 new agent overlays, manifest
  rows updated, regenerated se-research/se-fact-check Claude SKILL.md (from the
  amended canonical body), skill-catalog/README if version-embedded.
- `git status --name-only`: confirm only intended files (agents, registry,
  generator, removal.py, two pilot skills + their generated, manifest,
  changelog, docs, tests). No stray paths.

## Step 8 — Extend tests (R3)

- `tests/test_generate.py`: replace `test_smoke_agent_round_trips_through_both_dialects`
  with a `se-source-reader` round-trip; add a `se-claim-verifier` round-trip; add
  `test_delegation_role_must_resolve_to_agent` (dangling-role fixture →
  GenerationError); add a delegation `validate_runtime_profile` test (bad value +
  none/roles mismatch rejected).
- `tests/test_install.py`: repoint `test_agent_round_trip_on_claude_and_codex`
  and `test_installed_codex_agent_is_valid_toml` to `se-source-reader`.

## Step 9 — Full gate

- `make check` must exit 0 (test + lint + release-check: generator `--check`
  drift clean, release-payload gate sees 0.66.12 → 0.66.13 + changelog).
- Quote the decisive lines: generator `--check` "match" line + release gate
  version line + test summary.

## Step 10 — Finalize

Mark the four prd.md acceptance criteria, then ship via the loop
(finish-work → review → merge). Verification check (name before running):
`make check` exit 0 AND `python3 -c "import installer.registry"` clean AND the
two agents present in `generated/agents/{claude,codex}/` — any failure blocks.

## Risks

- **Positional-constructor coupling**: only trailing defaults; do not reorder
  fields (breaks all 11 constants).
- **Group-sharing leak**: verify se-knowledge-gap/se-literature-map/se-evaluate
  stay on plain `DEEP_ANALYSIS` and only the two pilots move.
- **se-smoke test coupling**: both hard-coded tests must be repointed or `make
  check` fails.
- **Claude byte drift**: the profile split alone changes no Claude bytes; the
  only pilot skill byte change comes from the Step 5 body edits — if generated
  se-research/se-fact-check change without a Step 5 edit, investigate.
