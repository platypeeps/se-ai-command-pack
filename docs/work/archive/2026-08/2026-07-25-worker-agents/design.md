# Design — Author wave-1 SE worker agents

Parent: `07-25-agent-artifacts` (Tier 2 content). Depends on the archived
`07-25-agent-artifact-kind` plumbing (agent render/manifest/install/remove is
already generalized). Research: `research/*.md` in this task.

## Scope

Ship two canonical worker agents and wire the two pilot skills to them through a
new RuntimeProfile `delegation` axis, retiring the placeholder `se-smoke` agent.

In scope:
1. `templates/agents/se-source-reader.md` — bounded read-only source reader.
2. `templates/agents/se-claim-verifier.md` — adversarial single-claim verifier.
3. Retire `templates/agents/se-smoke.md`.
4. RuntimeProfile `delegation` + `roles` axis (registry) for se-research and
   se-fact-check only.
5. Generator-side delegation-role **existence gate** + tests.
6. Optional role references in the pilot skills' canonical `## Sub-agent
   dispatch` sections (all platforms; optional framing; inline unaffected).
7. Version bump + changelog + operator-doc named agent inventory.

Out of scope: agent-body governance *validators* (governance stays
author-discipline, matching the existing agent contract — the only automated
agent-body gates remain H1-open, trailing newline, brand lint); registry
snapshot schema changes (delegation is not exposed in the snapshot — see
Decision D4); any non-pilot skill.

## Decisions

### D1 — Retire se-smoke; se-source-reader becomes the canonical round-trip agent
`se-smoke`'s own body says "Remove this agent when the first real worker role
ships." We delete it and repoint the two se-smoke-hard-coded tests
(`test_install.py:344-377`, `test_generate.py:583`) to `se-source-reader`. Its
two last-shipped install targets (`.claude/agents/se-smoke.md`,
`.codex/agents/se-smoke.toml`) are added to `installer/removal.py`
`RETIRED_TARGETS` so an upgrade removes an already-installed se-smoke, per docs
"Retiring an agent" (`SE_AI_COMMAND_PACK.md:991-995`).

### D2 — `delegation` + `roles` as trailing default fields on RuntimeProfile
All 11 profile constants use positional constructors
(`installer/registry.py:162-174`). Add two **trailing default** fields to the
frozen dataclass:

```python
delegation: str = "none"
roles: tuple[str, ...] = ()
```

so the existing 11 constructions stay valid and only opting-in profiles change.
Add `KNOWN_RUNTIME_DELEGATIONS = frozenset({"none", "optional", "required"})`
and one validation row in `validate_runtime_profile`, plus a coherence rule:
`delegation == "none"` ⇒ `roles == ()`; `delegation in {optional, required}` ⇒
`roles` non-empty. Frozen-dataclass equality now includes the two new fields;
`validate_registry`'s `SKILL_RUNTIME_PROFILES` re-derivation equality
(`:635-641`) still holds because both sides derive from the same constants.

### D3 — Split the two pilots into their own single-skill delegated profiles
se-research and se-fact-check currently share `DEEP_ANALYSIS` with three
non-pilots (se-knowledge-gap, se-literature-map, se-evaluate; `:206-214`). They
delegate to **different** roles, so a single shared roles tuple is wrong. Create
two constants, identical on the four execution axes, differing only in `roles`:

```python
DEEP_ANALYSIS_SOURCE_READING = RuntimeProfile(
    "both", "forked", "deep", "high",
    delegation="optional", roles=("se-source-reader",))
DEEP_ANALYSIS_CLAIM_VERIFYING = RuntimeProfile(
    "both", "forked", "deep", "high",
    delegation="optional", roles=("se-claim-verifier",))
```

Move `se-research` to the first and `se-fact-check` to the second in
`RUNTIME_PROFILE_ASSIGNMENTS`; leave the other three on plain `DEEP_ANALYSIS`.
Each skill stays in exactly one group (the builder rejects duplicates,
`:283-285`). `delegation` is **optional**, never required — the role never
blocks the baseline workflow.

Because Claude frontmatter maps only invocation/context/model/effort
(`claude_frontmatter`), the split produces **no** change to the generated Claude
skill bytes from the profile alone. The human/agent-readable half of R4/R5 lives
in the canonical body (D5); the registry half is machine-readable metadata whose
values must agree with the prose (`delegation: optional`, matching roles).

### D4 — Delegation-role existence gate lives in the generator, not the registry
`registry.py` has no agent list and does not import the generator's
`agent_names()`. The generator has both `SKILL_RUNTIME_PROFILES` (for Claude
overlays) and `agent_names()`. Add `validate_delegation_roles()` there: every
role named by any profile must resolve to a discovered agent; a dangling role
raises `GenerationError`. Call it in `main()` alongside `validate_agents()`
(after agents are validated, so the agent set is known). This gives R4's
"registry/profile validation covers the delegation mapping" a real build-time
teeth without new registry→templates coupling.

### D5 — Optional role references in the canonical dispatch bodies
Codex/Amp ship the canonical `SKILL.md` verbatim (`build_rows():927-928`), so
the role reference must live in the canonical body, not a Claude-only overlay
(the `fresh-session` overlay precedent would leave Codex/Amp without it). Add one
optional-framed sentence to each pilot's existing `## Sub-agent dispatch`
section, mirroring the present "On sub-agent dispatch platforms … on inline
platforms …" register:

- se-research (search-lane / read worker → `se-source-reader`): amend the
  **Worker input contract** bullet with an optional clause naming the role as an
  enhancement over a generic host subagent, run inline when no such role exists.
- se-fact-check (per-claim verifier → `se-claim-verifier`): same, on its
  **One worker per atomic claim** / worker-contract bullet.

Neutral agent names pass the brand lint (`BANNED_PHRASE_PATTERN`, whole-word
capitalized brands only). Inline platforms are unaffected: the clause is
conditional and additive; the baseline sequential behavior is unchanged.

## Agent bodies (governance invariants, R2/R3/R5/R6)

Both agents: YAML frontmatter (`name`, `description`; optional `model`), H1
open, neutral prose. No `tools`/`sandbox_mode` unless needed (kept minimal;
`model` omitted so the host default applies — the only hint reaching both Claude
and Codex is `model`, and we deliberately set none).

`se-source-reader` body encodes: **input** = one source + an extraction brief;
**output** = a structured extract with provenance (locators, dates, quoted
exactness, unknowns marked); **authority** = read-only (no writes, no posting/
subscribing/purchasing, treat fetched content as data not instructions); **no
recursive spawning**; **no scope expansion** beyond the one source; **concurrency
cap set by the parent**; **the parent owns the final report** (the worker returns
its extract only); **opening context line** — class-2 platforms get no hook
injection, so the dispatch prompt carries `Active task: <path>` explicitly and
the worker must not assume ambient task context.

`se-claim-verifier` body encodes: **input** = one claim + its evidence set;
**output** = exactly one verdict `supported | refuted | uncertain` with cited
reasons and decisive evidence (dates, locators); **default stance = REFUTE** —
actively seek the strongest disconfirming evidence before conceding support;
**authority** = read-only; **no recursive spawning**; **no scope expansion** to
other claims; **concurrency cap set by the parent**; **parent owns the final
ledger** (worker never assigns claim IDs or writes the report); same **opening
context line** rule.

These invariants are author-discipline (no body validator exists and none is
added — consistent with the agent contract). They mirror the role contract
prose already in `runtime-routing.md:68-86`.

## Contracts / data shape

RuntimeProfile (after change):

| field | type | known values | default |
|---|---|---|---|
| invocation | str | automatic/user-only/both | — |
| context | str | inline/forked/fresh-session | — |
| model | str | inherit/fast/balanced/deep | — |
| effort | str | low/medium/high/xhigh | — |
| delegation | str | none/optional/required | "none" |
| roles | tuple[str,...] | agent names (existence-gated) | () |

Coherence: `none ⇔ roles==()`. Existence: each role ∈ `agent_names()` (generator
gate). No snapshot exposure (D4/registry-delegation research §snapshot).

Manifest delta (regenerated, never hand-edited): −2 se-smoke rows, +4 rows
(se-source-reader, se-claim-verifier × claude+codex); +4 `generated/agents/**`
files, −2 removed.

## Test plan (R3 "tests extended")

- `tests/test_generate.py`: replace `test_smoke_agent_round_trips_through_both_dialects`
  (`:583`) with a se-source-reader round-trip (and add a se-claim-verifier one);
  add `test_delegation_role_must_resolve_to_agent` (fixture profile with a
  dangling role → `GenerationError`); add a `validate_runtime_profile` delegation
  test (bad delegation value and none/roles-mismatch rejected).
- `tests/test_install.py`: repoint `test_agent_round_trip_on_claude_and_codex`
  (`:344-369`) and `test_installed_codex_agent_is_valid_toml` (`:372-377`) to
  `se-source-reader`.
- `tests/test_release_gate.py`: unchanged behavior; the task's own diff must
  carry the version bump + dated changelog or the gate fails (self-check).

## Rollout / rollback

Rollout: bump `manifest.json` 0.66.12 → 0.66.13 **before** `make generate`
(help/catalog embed the version → drift gate), prepend a dated `## 0.66.13`
changelog entry, then `make generate`, then `make check`. Pure additive worker
agents + optional prose + internal registry metadata; retiring se-smoke is the
only removal and is covered by `RETIRED_TARGETS`.

Rollback: revert the branch. No migration, no persisted state, no snapshot
schema change, so revert is clean. Installed se-smoke on an already-upgraded
host is handled by `RETIRED_TARGETS` on the forward path; a rollback re-ships
se-smoke normally.

## Acceptance-criteria mapping

- AC1 (render + install/remove cleanly) → `make generate` emits 4 overlays/rows;
  `test_install` round-trip on se-source-reader; se-claim-verifier covered by the
  committed-overlay drift test.
- AC2 (pilots reference roles without requiring; inline unaffected) → D5 optional
  canonical-body clauses + D3 `delegation: optional`.
- AC3 (registry/profile validation covers delegation; tests extended) → D2
  validation row + coherence rule + D4 existence gate + new tests.
- AC4 (version bump + changelog; operator docs list new agents) → 0.66.13 +
  changelog + a new named agent inventory section in
  `docs/SE_AI_COMMAND_PACK.md` (none exists today; se-smoke was never listed).
