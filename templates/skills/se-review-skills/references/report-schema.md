# Review Report and Selection Schema

Use stable hierarchical IDs within one inventory snapshot. Sort repositories
by verified identity, families by declared order, and skills by registry order
when available. Put undeclared families under `Uncategorized`.

## Layout

```text
1. <repository>
   1.1 Package-wide
       1.1.1 <finding>
   1.2 <family>
       1.2.1 <skill>
           1.2.1.1 <finding>
           Do all: apply=skill:<skill>
       Do all: apply=family:<family>
   Do all: apply=repo:<repo-id>
Do all: apply=all
```

Use equivalent `task=` selectors when the user wants Trellis tasks without
implementation. Individual selection uses comma-separated finding IDs.

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

Package-wide findings appear once. An overlap belongs to the skill whose
trigger or contract should change. If both repositories must change, create
one owner-specific remediation record for each and cross-reference the shared
finding.

## Snapshot and selectors

The analyzer snapshot hashes selected files, package identity, family and
target metadata, ownership evidence, and schema version. Before `task=` or
`apply=`:

1. recompute the inventory;
2. require the same snapshot ID;
3. resolve the selector only inside that snapshot;
4. preview findings, destinations, priorities, and exact template files; and
5. reject missing, stale, ambiguous, escaped, or non-template paths.

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

## No-findings result

When no material finding survives verification, say so. Still report snapshot,
repositories, skills, dimensions, target coverage, tests observed, independent
passes, unavailable capabilities, excluded scope, residual uncertainty, and
the selectors that would be valid if a later review produces findings.
