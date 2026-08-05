# Research: Pilot skill dispatch sections + attaching optional role references

- **Query**: Where do se-research / se-fact-check dispatch sections live, and how would R4/R5 optional role references attach without requiring them, staying neutral, leaving inline platforms unaffected? Version + operator-docs agent listing.
- **Scope**: internal
- **Date**: 2026-08-05

## Findings

### se-research `## Sub-agent dispatch` (`templates/skills/se-research/SKILL.md:71-109`)

Key bullets that a role reference would attach to:

- Header (`:73-76`): "On sub-agent dispatch platforms, run the units below in parallel; on inline platforms, work through them sequentially in one context. Dispatch is an execution strategy layered over the Workflow above — it never changes the scope, the verification bar, or the `## Final report` contract."
- **Worker input contract** (`:89-100`): "Each worker receives the smallest complete input for its unit (its lane or its claim), explicit exclusions ..., an authority boundary (read-only source gathering; no posting, subscribing, or purchasing), an **expected artifact** ..., and a **stop condition** .... Cap concurrency to the host and task budget." — this is where a se-source-reader role maps (search-lane worker = bounded read-only source consumption → structured extract).
- **No recursion when already dispatched** (`:101-104`).
- **Active task prefix** (`:105-109`): "When a Trellis task is active, open each dispatch prompt with `Active task: <task path from task.py current>` before the role-specific instructions, so platforms that do not hook-inject context still receive it." — this is the existing R5 "explicit context line for class-2 platforms" pattern already in prose.

### se-fact-check `## Sub-agent dispatch` (`templates/skills/se-fact-check/SKILL.md:83-116`)

- Header (`:85-88`): same framing, "it never changes the scope, the verdict ladder, or the `## Final report` contract."
- **One worker per atomic claim** (`:90-94`): per-claim evidence work is mutually independent → maps to se-claim-verifier (one claim + evidence → verdict).
- **The orchestrator owns the ledger** (`:95-98`): "Workers never assign claim IDs and never write the final report" — R6's "parent owns the final report."
- **Worker input contract** (`:99-107`): claim ID, exact wording, locator, as-of date; exclusions; read-only authority boundary; expected artifact = "the single verdict record for its claim — one verdict, decisive evidence ...; stop condition (exactly one verdict assigned)." — directly the se-claim-verifier contract.
- **No recursion when already dispatched** (`:108-111`); **Active task prefix** (`:112-116`) — identical R5 pattern.

### How an OPTIONAL role reference attaches without requiring it

The dispatch sections already describe **worker roles abstractly** (search-lane worker, per-claim verifier worker) with input/authority/artifact/stop contracts. R4 wants these to optionally name the canonical agents (`se-source-reader`, `se-claim-verifier`) as an enhancement over host built-in generic subagents. Constraints from the codebase:

1. **Neutrality lint applies to skill bodies too** (`.github/scripts/generate-skill-surfaces.py:283-288`, `BANNED_PHRASE_PATTERN` `:140-142`). Referencing an agent by its neutral name `se-source-reader` / `se-claim-verifier` is fine (no banned brand word). Do **not** name platforms.
2. **Inline platforms unaffected**: the canonical SKILL.md body ships verbatim to Codex + Amp (`build_rows()` `:927-928` only swaps the Claude SKILL.md source). So any role-reference text lives in the **canonical body** and must be phrased conditionally — "On platforms that expose a bounded read-only worker agent, you may dispatch the `se-source-reader` role; otherwise run the unit inline" — mirroring the existing "On sub-agent dispatch platforms ... on inline platforms ..." framing (`se-research:73`, `se-fact-check:85`). This keeps inline platforms doing exactly what they do today.
3. **Optional, not required**: the wording should present the role as an enhancement, not a precondition — same register as the runtime-routing contract `delegation: optional` (`runtime-routing.md:18`) and "The optional peer review never blocks the baseline workflow" (`:136`). The RuntimeProfile `delegation` metadata (see `registry-delegation.md`) is the machine-readable side; the SKILL.md prose is the human/agent-readable side. They should agree (`delegation: optional`, `roles: [se-source-reader / se-claim-verifier]`).
4. **R5 context line already exists** as the "Active task prefix" bullet — the agents' own bodies must document that class-2 platforms get no hook injection so the dispatch prompt must carry the `Active task:` line explicitly.

### Version + operator docs listing agents

- Current pack version: `manifest.json:4` → `"version": "0.66.12"`. A payload change (new agents + generated files + registry) requires a bump + dated `CHANGELOG.md` entry (release gate — see `install-remove-and-tests.md`).
- Operator docs listing agents: `docs/SE_AI_COMMAND_PACK.md`:
  - `:13` — `templates/agents/<name>.md` canonical agent definitions row.
  - `:15` — `generated/agents/claude/<name>.md`, `generated/agents/codex/<name>.toml` overlays row.
  - `:972-989` — **"Adding an agent"** procedure (frontmatter allowlist, `make generate`, install dirs).
  - `:991-995` — **"Retiring an agent"** procedure.
  - The docs currently describe agents **generically** (`<name>`); there is **no explicit named list** of shipped agents (se-smoke is not enumerated by name in the docs). Acceptance criterion "operator docs list the new agents" (PRD `:34`) implies adding a named agents inventory/section, since none exists today.

## Caveats / Not Found

- No existing named agent catalog in `docs/SE_AI_COMMAND_PACK.md` or README — "operator docs list the new agents" likely means creating a new named list, not editing an existing one. (README has a marker-bounded **skill** catalog only; there is no agent catalog surface, and the generator does not produce one.)
- The dispatch sections do not currently name any agent role — the role text is generic. R4 requires inserting the specific `se-source-reader`/`se-claim-verifier` names in a way that (a) passes the neutrality lint (safe — neutral names) and (b) reads as optional. The exact placement (new bullet vs. amend "Worker input contract") is a design decision; both sections are structurally parallel, so mirror the wording across both.
- The canonical body is the correct home for the role reference (reaches all platforms); a Claude-only generated overlay note (the `fresh-session` precedent) would leave Codex/Amp without it, which contradicts "inline platforms unaffected but still consistent."
</content>
