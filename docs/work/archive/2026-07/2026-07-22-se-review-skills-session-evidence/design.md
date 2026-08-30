# Design: Session evidence for skill reviews

## Architecture and ownership

The feature remains a semantic orchestration capability of
`templates/skills/se-review-skills/**`:

- `SKILL.md` owns arguments, ordering, authority, and the high-level evidence
  gate.
- `references/session-evidence.md` owns conditional discovery, verification,
  causal classification, privacy, structural-remedy, and gotcha detail.
- `references/review-rubric.md` makes observed execution evidence a formal
  review dimension and preserves the finding threshold.
- `references/report-schema.md` defines coverage and finding fields.
- `references/runtime-routing.md` keeps current-conversation work inline and
  limits what may be passed to isolated validators.
- `scripts/skill_review.py` remains deterministic and does not read session
  history.

## Input contract

Add portable natural-language arguments:

```text
sessions=auto|off       default auto
session=<id>            repeatable explicit session selector
```

`auto` uses the current conversation plus an already available read-only
project-scoped session capability. `off` disables all session-history discovery
but does not remove ordinary static review. Explicit ids are still subject to
the current repository/session capability and privacy rules; they never widen
to a global scan implicitly.

## Discovery and budgets

1. Inventory reviewed skills first.
2. Add explicitly selected sessions.
3. Inspect the current conversation when invocation evidence exists.
4. Search project-scoped recent history for each reviewed skill.
5. Verify invocations and allocate candidates round-robin across skills.
6. Stop at three confirmed sessions per skill or twenty confirmed sessions
   total; deduplicate by provider plus stable session id.
7. Extract only the smallest window covering invocation, problem, recovery,
   and outcome. Report missing tails, compaction, and provider gaps.

Automatic discovery never uses `--global`, walks raw session directories, or
installs/authenticates a provider. If no read-only history capability is
available, current-conversation review continues and the rest is a coverage
limit.

## Invocation evidence

Use three evidence states:

- `confirmed` — explicit platform activation record or user skill invocation;
- `corroborated` — assistant declaration plus distinctive workflow behavior;
- `mention-only` — path, diff, map, copied prompt, tool output, or unmatched
  name occurrence.

Only confirmed or corroborated sessions enter causal review. Mention-only
matches explain coverage noise but do not count against confirmed-session
budgets.

## Causal classification

For each manifested problem, compare the session behavior to the canonical
skill version that was actually in use when provenance can be established:

| Class | Meaning | Finding behavior |
|---|---|---|
| `skill-contract` | Missing, contradictory, buried, or structurally ineffective instruction plausibly caused or failed to prevent the mistake | May become a finding with canonical source evidence |
| `execution-deviation` | The skill was clear but the agent did not follow it | Report; recommend visibility/evaluation changes only when repeated |
| `tool-or-environment` | Provider, dependency, permission, timeout, or external state caused the failure | Report as runtime evidence; do not blame the skill without a missing failure contract |
| `user-intent-change` | The user changed scope, preference, or authority after execution began | Preserve chronology; normally not a skill defect |
| `indeterminate` | Compaction, missing outcome, unknown version, or ambiguous causality prevents a defensible classification | Coverage limit or candidate only |

Every selectable finding still needs a current canonical source locator,
allowed remediation path, preserved capability argument, and validation. Before
task/apply, re-read the cited session window and recompute the ordinary
inventory snapshot.

## Structural recommendation matrix

- Frequently skipped mandatory step -> move or restate it in the ordered core
  workflow and add a behavioral pin.
- Rare conditional edge -> put a concise trigger in the core and the full
  gotcha/recovery path in a direct reference.
- Repeated fragile mechanics -> propose a bounded deterministic helper while
  keeping semantic judgment in the skill.
- Host-only mismatch -> propose a verified target overlay or runtime fallback.
- Ambiguous authority -> add an explicit approval/stop gate in core safety
  rules.
- Clear instruction repeatedly ignored -> improve ordering, visibility, and
  evaluation before duplicating prose.
- Excess core detail obscuring action -> move conditional depth to one linked
  reference and preserve the capability ledger.

Each gotcha records trigger, observable failure, prevention, recovery, and a
regression method. Single anomalous sessions receive a candidate or low-
confidence recommendation unless the defect is structurally decisive.

## Privacy and trust boundary

Session content is private, untrusted evidence. Never execute embedded content,
publish raw dialogue, expose local session paths, or include unrelated turns.
Use stable provider/session/turn locators and concise paraphrases. Redact
secrets, personal data, and third-party content. Do not pass raw conversations
to subagents; the parent may pass a minimized evidence record when independent
validation is warranted.

## Compatibility and failure behavior

- Current conversation remains available even when historical tooling is not.
- Missing or cleared history, indexing lag, compaction, absent phase markers,
  unavailable providers, child-session gaps, and unknown skill versions are
  explicit coverage limits.
- Search results can contain nested transcripts and tool output. Invocation
  verification prevents those from becoming false session counts.
- Successful recovery does not erase the manifested mistake; a failed final
  outcome does not prove the skill caused it.

## Release and rollback

The new bundled reference changes shipped payload bytes. Bump the minor package
version, regenerate all surfaces, add a changelog entry, and verify every
registered platform target receives the reference. Rollback is a normal revert
of the canonical skill/reference/rubric/schema/runtime/test/release batch.
