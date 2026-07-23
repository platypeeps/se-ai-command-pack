# Review Report and Selection Schema

Use stable hierarchical IDs within one inventory snapshot. Sort repositories
by verified identity, families by declared order, and skills by registry order
when available. Put undeclared families under `Uncategorized`.

Before the hierarchy, state every bounded installation root, whether it was
scanned, missing, invalid, or skipped, and the number of installed copies
collapsed into each canonical review record. For every mapped copy, show its
path and `canonical-match` or `installed-drift` status. Review findings and
mutation selectors always point at the canonical repository source. Unowned
copies remain separate unless normalized name and content hash both match.

## Layout

```text
1. <repository>
   Safety: <alerted-count> alerted, <clean-count> clean, <indeterminate-count> indeterminate
   1.1 Package-wide
       1.1.1 <finding>
   1.2 <family> — Safety: <verdict counts>
       1.2.1 <skill> — Safety verdict: alerted | clean | indeterminate
           Guarded operations and unresolved candidates: <evidence or none>
           Observed use: <coverage, invocations, mistakes, controls, or limits>
           Structural recommendations and gotchas: <records or none>
           1.2.1.1 <finding>
           Do all: apply=skill:<skill>
       Do all: apply=family:<family>
   Do all: apply=repo:<repo-id>
Do all: apply=all
```

Use equivalent `task=` selectors when the user wants Trellis tasks without
implementation. Individual selection uses comma-separated finding IDs.

Before scores or ordinary findings, add a **Critical safety alerts** callout
when any P0 safety, data-loss, security, or authority alert exists. List its ID,
skill, affected capability, and consequence there; keep the complete finding
record in its one canonical hierarchy location.

## Security and safety coverage

Every selected skill must have one explicit `alerted`, `clean`, or
`indeterminate` verdict. Roll the counts up at family and repository levels.
List guarded risky operations and unresolved candidate signals beneath the
skill so a clean verdict remains auditable, but do not assign them finding IDs
unless they meet the semantic finding threshold.

Safety alert IDs use the normal stable hierarchy and participate in individual,
`skill:`, `family:`, `repo:`, and `all` selectors. Package-wide hazards appear
once under Package-wide and participate in the enclosing repository and `all`
selectors.

## Finding fields

Every finding includes:

- immutable ID inside the snapshot;
- category, priority, and effort;
- owning repository, family, and primary skill;
- exact file/line or reproducible-command evidence;
- issue or opportunity and observable consequence;
- smallest proposed template change;
- capability-ledger impact and preservation argument;
- expected line/word reduction for brevity findings;
- regression risk, dependencies, and validation; and
- peer-skill or cross-repository references without duplicate findings.

## Interaction-design findings

Every verified missing-question finding includes the owning skill and exact
source locator; the missing decision or approval; why structured input is
appropriate; its `required`, `useful-but-non-blocking`, or `inappropriate`
classification and blocking state; and the smallest capability-preserving
instruction change. Also record suggested placement and prompt intent,
platform fallback behavior, behavior when the user does not answer, and a
validation method.

When mutually exclusive options are appropriate, show two or three choices,
mark the recommended option, and state its tradeoff. When free-form input is
necessary, describe the needed input without inventing an option list. Keep
keyword-only candidates, discoverable answers, and existing safe defaults as
rejected signals rather than numbered findings.

Every session-derived finding also includes:

- a minimal redacted session locator and relevant turn or event range;
- `strong-activation` or `corroborated-use` invocation evidence;
- `current-canonical`, `installed-drift`, `historical-version`, or `unknown`
  skill provenance;
- causal class `skill-contract`, `execution-deviation`,
  `tool-or-environment`, `user-intent-change`, or `indeterminate`, plus
  confidence;
- the redacted observed behavior and consequence;
- a successful or neutral control comparison when available;
- the exact current canonical source locator that remains remediable; and
- the structural remedy and, for an edge-case gotcha, trigger, failure,
  prevention, recovery, and regression method.

Do not include raw dialogue, secrets, personal or confidential data,
machine-specific host paths, or full tool output. Mention-only matches and
session errors without confirmed invocation and current source causality remain
coverage limits, not findings.

Every harmful-instruction alert also includes:

- exact source file and line evidence; candidate-only or execution-derived
  evidence is prohibited;
- affected capability and the precise unsafe instruction;
- plausible harm or abuse path and required preconditions;
- severity using P0-P3 plus `high`, `medium`, or `low` confidence;
- authorization, preview, scope, validation, failure-stop, and recovery gates
  that are absent, ineffective, or bypassable;
- the smallest safe remediation that preserves legitimate capability; and
- a non-executing validation method, such as content inspection, fixture tests,
  or a mocked or isolated contract test.

Package-wide findings appear once. An overlap belongs to the skill whose
trigger or contract should change. If both repositories must change, create
one owner-specific remediation record for each and cross-reference the shared
finding.

## Snapshot and selectors

The analyzer snapshot hashes selected files, package identity, family and
target metadata, ownership evidence, and schema version. Session evidence is a
separate private evidence layer and does not change that deterministic source
snapshot. Before `task=` or `apply=`:

1. recompute the inventory;
2. require the same snapshot ID;
3. resolve the selector only inside that snapshot;
4. revalidate selected session records against the project boundary, invocation
   evidence, provenance, causal class, current canonical locator, and redaction;
5. preview findings, destinations, priorities, and exact template files; and
6. reject missing, stale, ambiguous, escaped, or non-template paths or session
   evidence.

`apply=all` means all accepted findings in this bounded snapshot. It never
waives safety gates, newly discovered tradeoffs, per-skill checkpoints, or
cross-repository handoffs.

## Trellis routing

Reconcile active and archived tasks using snapshot ID, finding IDs, skill, and
affected paths. Classify selected work as:

- `tracked-accurate` — reuse the existing open task;
- `tracked-stale` — report it for review and do not silently append; or
- `untracked` — create at most one planning task per skill and snapshot.

Use the destination repository's own task entrypoint with its no-start option.
Preview title, priority, destination, parent decision, finding IDs, and affected
templates before writing. Preserve the current active task.

Route only after verifying canonical source, package identity, provenance when
needed, Git root and remote, and Trellis tooling:

- SD templates -> verified `platypeeps/sd-ai-command-pack` upstream;
- SE templates -> verified `platypeeps/se-ai-command-pack` upstream; and
- all other skills -> the Git repository owning their canonical source.

For SD and SE, task affected paths must remain under their template allowlists.
Installed copies are evidence only. When the destination is missing, wrong,
dirty in an ambiguous way, or lacks Trellis, return a paste-ready task proposal
and exact blocker; do not clone or bootstrap.

## Apply state

Apply one skill-sized batch in the current verified owner repository. Report:

- selected findings and reconciled task;
- templates changed and unrelated changes preserved;
- checks run and their results;
- newly exposed decisions or blockers;
- completed, skipped, failed, and not-started findings; and
- exact safe resume selector.

Stop after a failed check or material unaccepted tradeoff. Do not imply an
atomic multi-repository operation.

## Suggested next steps

End every report with **Suggested next steps**. Order the smallest useful
follow-ups and include exact valid selectors where findings exist. Distinguish:

- repository remediation through `task=` or `apply=` against the canonical
  source;
- installation refresh advice when one or more installed copies differ from
  that source;
- verification needed before an unresolved copy can be mapped or changed; and
- no-action or later-review advice when no material finding survives.

These suggestions are advisory. They do not create tasks, edit repositories,
refresh installations, or grant any authority not already present in the mode.

## No-findings result

When no material finding survives verification, say so. Still report the
explicit safety verdict for every skill, guarded operations and unresolved
candidates, snapshot, repositories, skills, dimensions, target coverage, tests
observed, independent passes, session mode and budget, confirmed invocations,
successful or neutral controls, rejected mention-only candidates, privacy or
provider limits, unavailable capabilities, excluded scope, residual
uncertainty, and the selectors that would be valid if a later review produces
findings. Finish with **Suggested next steps**, even when the only recommendation
is no action or a later bounded review.
