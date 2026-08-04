# Design: Add `agent` artifact kind to installer and generator

Status: DRAFT for review (authored 2026-08-03, plan-only work-loop `until=design`).
Binding inputs honored: parent `07-25-agent-artifacts/design.md` §1 and
`research/cross-platform-agent-support.md`. Section 1 of the parent is not re-litigated
here; this document is the child's detailed design gate.

## 1. Scope and non-goals

In scope: make `agent` a first-class artifact kind that flows through the existing
`registry → generator → manifest → installer` chain, rendered per platform (Claude MD,
Codex TOML), user-scoped, with the Amp/`agents` anchor excluded. A single minimal smoke
agent ships to prove the plumbing end to end.

Out of scope (owned elsewhere): wave-1 worker-role content (`07-25-worker-agents`);
skill-body dispatch protocols and the `fresh-session` encoding decision
(`07-25-agent-artifacts` R6 / dispatch children); project-scope agents.

## 2. Settled decisions

- **D1 — user scope only.** Agents install to `~/.claude/agents/<name>.md` and
  `~/.codex/agents/<name>.toml`. Project scope is excluded: the research shows Codex
  project-scoped agents load only in *trusted* projects (trust gate), while user-scoped
  agents avoid it. This resolves the PRD "Dependencies / order" open question and the
  A-044 codex-home concern for this surface (the agents dir is a fixed home-relative path,
  not `$CODEX_HOME`-derived, keeping parity with the existing `.codex/skills` anchor).
- **D2 — one canonical source format.** `templates/agents/<name>.md`: YAML frontmatter with
  an allowlist (`name`, `description`, and portable hints `tools`, `model`), body = system
  prompt. Same shape as Trellis `.trellis/agents/*.md`. The neutrality lint
  (`BANNED_PHRASE_PATTERN`) applies to the body; host product names never appear in
  canonical source, only in generated overlays.
- **D3 — anchor reuse, new sub-directory.** No new anchor. Agents gate on the *existing*
  `.claude` / `.codex` anchors (`install: if-anchor-exists`), targeting an `agents/`
  sub-directory. `PlatformInfo` gains an optional `agents_dir`; `claude` →`.claude/agents`,
  `codex` → `.codex/agents`, `agents` (Amp) → `None`.
- **D4 — manifest kind.** `KNOWN_MANIFEST_KINDS` gains `agent`. Agent rows are
  `kind: agent`, `scope: user`, `install: if-anchor-exists` — validated by the existing
  `validate_manifest` path with no new row-shape rules.
- **D5 — Amp exclusion is asserted, not assumed.** `agents_dir=None` yields zero agent rows
  for the `agents` platform; a test asserts no manifest row with `kind: agent` targets
  `.config/agents/**`.
- **D6 — generator renderer hook.** The single hardcoded branch at
  `generate-skill-surfaces.py:524` (`if platform == "claude" and relative == "SKILL.md"`)
  is generalized into a per-`(platform, kind)` renderer lookup. Skill rows keep their
  current behavior byte-for-byte; agent rows are added by a sibling `build_agent_rows()`.

## 3. Data flow

```
templates/agents/<name>.md   (canonical, neutral)
        │  make generate
        ▼
generated/agents/claude/<name>.md      (near-passthrough MD overlay)
generated/agents/codex/<name>.toml     (TOML transform)
        │  rows in manifest.json  (kind: agent, scope: user, install: if-anchor-exists)
        ▼
install.py → ~/.claude/agents/<name>.md   (anchor .claude present)
           → ~/.codex/agents/<name>.toml  (anchor .codex present)
           → agents/Amp: NONE
```

Claude renderer: near-passthrough — strip portable-only frontmatter hints Claude does not
read, keep `name`/`description`/`tools`/`model`, body verbatim. Codex renderer: emit TOML
with `name`, `description`, `developer_instructions` (= body), and optional `model`,
`sandbox_mode`, with correct TOML string escaping (multiline basic strings for the body).

## 4. Contracts and compatibility

- **Registry-snapshot precondition (A-002).** `skill_review.py` AST-parses
  `installer/registry.py` on consumer machines. Adding an `agents_dir` field to
  `PlatformInfo` changes that shape. Therefore `07-25-audit-registry-snapshot-contract`
  must land first (or its snapshot-schema bump must be folded into this task), so installed
  copies detect incompatibility instead of misparsing. **This is a hard precondition, recorded
  as a blocking checklist item in `implement.md`.**
- **Catalog special-case (A-003).** The existing `GENERATED_SHARED_REFERENCES` /
  skill-catalog one-off is absorbed into the same renderer-hook refactor rather than left as
  a parallel exception; coordinate with `07-25-audit-generated-catalog-location`.
- **Manifest schema version** is unchanged (row *shape* is unchanged; only the kind
  vocabulary grows). The release-payload version gate still fires because `templates/**`,
  `generated/**`, and `manifest.json` all change → mandatory manifest version bump +
  dated CHANGELOG heading.
- **Provenance round-trip.** `install`, `status`, `remove`, `update` must treat agent rows
  identically to skill rows (they already key off manifest rows generically); the smoke
  agent proves the full lifecycle.

## 5. Risks and rollback

- Risk: TOML escaping bugs corrupt a Codex agent. Mitigation: renderer unit test with a body
  containing quotes/backslashes/newlines; `--check` drift gate.
- Risk: an agent target collides with a skill target. Mitigation: the existing
  case-folded duplicate-target guard in `build_rows()` extends to the merged row set.
- Rollback: agents are additive rows; removing the canonical source + regenerating drops the
  rows, and `install.py remove`/`update` prune the installed files via provenance. No data
  migration.

## 6. Open questions for reviewer

- OQ1: ship the smoke agent as `se-smoke` (throwaway, later removed) or make wave-1
  `se-source-reader` the first real agent here instead of in `07-25-worker-agents`?
  Recommendation: throwaway smoke agent — keeps this task pure plumbing per R6.
- OQ2: confirm the registry-snapshot-contract sequencing (precondition vs. fold-in). If it
  is not yet designed, this task parks until it is.
