# se-coherence-audit — corpus self-consistency audit skill

## Problem

A knowledge corpus that a person or an agent reads as instruction decays in
four specific ways that no existing pack skill detects:

1. **Contradiction** — two passages that cannot both be followed. In agent
   instruction files (`CLAUDE.md`, `AGENTS.md`, `.claude/rules/*`, `SKILL.md`)
   a contradiction is not a style problem: the reader silently picks one branch
   and the corpus stops meaning what it says.
2. **Vagueness** — a directive with no actionable trigger, threshold, actor, or
   failure branch ("keep it fast", "handle errors appropriately", "as needed").
3. **Bandaid** — guidance shaped as a patch rather than a rule: a workaround
   with no recorded root cause, a "temporary" instruction that outlived its
   cause, an exception stacked on an exception.
4. **Redundancy** — the same rule stated in several places, which drifts:
   editing one copy converts a redundancy into a contradiction.

Today this audit is done ad hoc by hand. Nothing in the pack owns it.

## Boundary against existing skills

The new skill looks **inward** — does this corpus contradict, blur, patch, or
repeat *itself*. The neighbors look elsewhere, and their bodies must state the
boundary:

| Skill | Owns | Not this skill because |
|---|---|---|
| `se-knowledge-gap` | what is **missing** relative to a decision or audience | outward, gap-shaped; needs a stated decision to audit against |
| `se-fact-check` | claims vs **external evidence** | truth, not internal consistency |
| `se-prose-lint` | wording, voice, mechanics | style, not semantics |
| `se-docs-bustest` | can a newcomer **execute** the doc cold | executability, not coherence |
| `se-red-team` | adversarial attack on a plan or artifact | not a corpus sweep |

Decided: ship standalone; do not extend `se-knowledge-gap` and do not move its
`conflicting` / `duplicated` gap types out of it. `se-knowledge-gap` reports
conflict as a *gap symptom* against a decision; this skill reports it as a
*corpus defect* with both sides quoted. Both bodies gain a cross-reference.

## Requirements

R1. **Corpus-agnostic input.** The skill takes any path, glob, or file set the
    user supplies — an Obsidian vault, a `CLAUDE.md` tree, `docs/`, a mixed
    set. No built-in target list, no assumed vault layout. It states the
    resolved file set and the count before auditing, and refuses to widen scope
    beyond what was supplied.

R2. **Four detector classes**, each with explicit criteria in a reference file:
    contradiction, vagueness, bandaid, redundancy. A finding is only reported
    when it names the class-specific criterion it satisfies.

R3. **Evidence per finding.** Every finding carries: class, severity, every
    location as `path:line`, the offending text quoted **verbatim** (both sides
    for contradiction and redundancy), why it satisfies the class criterion,
    and a proposed resolution. A finding without a verbatim quote and a
    location is not reportable.

R4. **Precedence awareness.** When the corpus declares its own precedence (a
    root instruction file that states it overrides others, an explicit
    ordering), an apparent conflict resolved by that precedence is reported as
    `resolved-by-precedence` and not as a contradiction. When two passages
    conflict and **no** precedence is declared, that missing precedence is
    itself the finding.

R5. **Read-only.** The skill never edits, reorganizes, or rewrites the corpus.
    Output is a prioritized findings ledger plus a proposed resolution per
    finding. Fixes are the user's next action, not this skill's.

R6. **Severity model** that ranks by consequence, not by count: whether a
    reader acting on the passage would do the wrong thing, and whether the
    passage is load-bearing.

R7. **Honest coverage reporting.** The report states which files were read in
    full, which were sampled, and which were skipped and why (size, binary,
    unreadable). A corpus too large for one pass is reported as partially
    audited with the unaudited remainder named — never presented as complete.

R8. **Pack integration.** Registered in `installer/registry.py` (`SKILLS` row,
    runtime-profile assignment, shared-reference consumers), added to the
    golden test snapshot and given its own test coverage, regenerated artifacts
    committed, and documented in `README.md`, `docs/SE_AI_COMMAND_PACK.md`, and
    `CHANGELOG.md` under a minor version bump, matching the `se-brand-voice`
    precedent (`47d1fb0`).

R9. **Framework neutrality.** The shipped `SKILL.md` and its references must
    pass the generator's brand-name lint
    (`generate-skill-surfaces.py:170` bans `Claude`, `Codex`, `Gemini`, and
    peers as words). The body describes its targets by capability — "a root
    agent-instruction file", "per-directory rule files" — and never by product
    name, even though this task's own planning artifacts do.

## Non-goals

- No auto-fix, no corpus mutation, no PR creation.
- No prose/style linting; no external fact verification; no gap analysis
  against a decision. Those route to the owning skills named above.
- No new dependency, no vault-format parser, no index or database.

## Acceptance criteria

A1. `templates/skills/se-coherence-audit/SKILL.md` exists with frontmatter
    limited to `name` and `description`, a description that starts with
    `Use when` on a single line, and the five required sections in order
    (`## When to use`, `## Arguments`, `## Workflow`, `## Safety rules`,
    `## Final report`) — the set enforced at
    `generate-skill-surfaces.py:120`.

A1b. `tests/test_skills.py` carries a test class for the new skill in the shape
    the file already uses for its neighbors, and
    `tests/test_generate.py::EXPECTED_SHARED_SOURCES` lists the skill's
    registered shared reference.
A2. Detector criteria for all four classes live in `references/`, each class
    stating what qualifies **and** at least one near-miss that does not.
A3. `make check` passes green, including `prose-lint` and `release-check`.
A4. `installer/registry.py` lists the skill, and `make release-check` passes —
    that target runs `generate-skill-surfaces.py --check`, the canonical proof
    that committed `manifest.json`, `generated/skills/claude/**`,
    `generated/references/skill-catalog.md`, and
    `generated/registry-snapshot.json` match what the generator would write.
A5. `se-knowledge-gap` and this skill each state the boundary against the other
    in their bodies.
A6. A dry run over this repository's own `CLAUDE.md` + `.claude/rules/` +
    `AGENTS.md` produces a ledger where every finding has a `path:line` and a
    verbatim quote, and every reported contradiction is manually confirmed to
    be a real one (zero fabricated pairs).
A7. `manifest.json` `version` bumped one minor by hand before regeneration
    (the generator preserves the committed value rather than computing it), and
    a dated `CHANGELOG.md` heading added.

## Open choice (default locked)

Name: `se-coherence-audit`, family `improve`. Alternatives considered:
`se-coherence` (shorter, less clear), family `engineer` (rejected: the skill is
corpus-agnostic, not an engineering-workflow skill). Change requires only a
rename before implementation starts.
