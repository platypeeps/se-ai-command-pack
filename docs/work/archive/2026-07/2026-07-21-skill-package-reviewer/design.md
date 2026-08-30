# Add `se-review-skills` Design

## Overview

Add a framework-neutral Improve-family product skill backed by a small,
adapter-based deterministic inventory analyzer. The analyzer supplies facts for
arbitrary skill roots; the skill makes bounded judgments, requests an optional
independent pass, synthesizes findings, routes accepted work to the canonical
owner's Trellis repository, and applies only user-selected local batches.

The initial release must not rewrite all existing skills. It establishes a
review contract that can safely create that follow-up backlog.

## Architecture

### 1. Deterministic inventory

Add `scripts/se-ai-command-pack-skill-review.py` with a read-only `inventory`
mode. It should expose a common skill-record schema and use adapters rather than
assuming every target is an SE package. It should:

- accept exact skill paths or a bounded Git/package root and reject unbounded
  machine-wide discovery;
- use an SE adapter for `installer.registry.SKILLS`, `FAMILY_LABELS`, platform
  rows, and shared references;
- use an SD adapter for that package's declared skill registry and install
  provenance;
- use a generic adapter for `SKILL.md` trees, declared Agent Skills metadata,
  and optional repository-owned family metadata; assign no inferred family;
- use one standard-library, bounded metadata parser so the installed analyzer
  remains portable across packages; keep the generator authoritative for SE
  write validation and pin compatible observable fields in shared fixtures;
- emit stable JSON containing source hash, repository/package identity,
  canonical and observed paths, provenance class, package version,
  skill/family, description, sections, arguments, sibling names, reference
  files, platform targets, line/word counts, and pinned-test references;
- calculate candidate signals such as repeated paragraphs, duplicated section
  text, description similarity, sibling-name density, and unusually large
  sections; and
- label those values as signals, never findings.

The review snapshot ID should hash the analyzer schema, repository/package
identities, registry/family data, ownership evidence, and selected source files.
Task creation and apply modes must recompute and match it.

Registries, manifests, generators, tests, and installed copies are read-only
evidence for source resolution and platform behavior. The analyzer must not
turn those evidence paths into skill remediation targets.

Inventory existing bundled scripts and command blocks per skill. Record only
deterministic script-candidate signals such as repeated structured parsing,
schema validation, hashing, path mapping, or stable transformations. The
semantic reviewer decides whether extraction improves reliability and context
cost after accounting for runtime availability, dependencies, portability,
side effects, idempotence, dry-run behavior, and testability.

### 2. Canonical template boundary

Add a source-role classifier before review:

```text
source-role: authored-template | generated-template-adapter |
             installed-copy | local-override
reviewable: true | false
changeable: true | false
canonical-template: <absolute path or unresolved>
```

The SE adapter allows review and remediation only below
`templates/skills/**`. The SD adapter allows them only below `templates/**`,
while distinguishing primary authored sources in
`templates/.agents/skills/**` and `templates/.commands/**` from generated
Claude, Gemini, GitHub, and other target adapters. Generated adapters may
produce parity or target-correctness evidence, but their fixes normally flow
from the neutral authored template and the established generation process.

An observed installed-copy problem is selectable only after it reproduces in,
and maps to, an allowed canonical template. A generated-adapter mismatch must
map to an authored template change or remain a non-selectable packaging/tooling
limit. Both task creation and apply recompute the allowlist and reject escaped,
symlinked, stale, or non-template affected paths. Generic repositories keep
their declared canonical source rules.

### 3. Canonical skill orchestrator

Create `templates/skills/se-review-skills/SKILL.md` with the package's required
sections and concise, imperative instructions. Keep the body focused on:

1. resolve scope and inventory;
2. build per-skill capability ledgers;
3. review dimensions and overlap;
4. evaluate brevity and runtime routing;
5. optionally obtain an independent review;
6. synthesize the numbered report; and
7. preview, apply, and validate an explicitly selected batch.

Move detailed rubrics and report schemas to directly linked references:

- `references/review-rubric.md` — dimensions, capability ledger, priority and
  effort definitions, brevity rules, and context/model decision matrix;
- `references/report-schema.md` — numbered layout, finding fields, selectors,
  snapshot contract, and partial-state report; and
- an optional platform overlay/reference for Claude-specific plugin routing if
  the generator gains platform-selective payload support.

Do not duplicate the registry-derived catalog inside the skill.

### 4. Runtime recommendation model

Each skill receives a recommendation record:

```text
invocation: automatic | user-only | both
context: inline | forked | fresh-session
delegation: none | optional | required
roles: [<bounded role, model-profile, effort, output contract>]
model-profile: inherit | fast | balanced | deep
effort: low | medium | high | xhigh
rationale: one evidence-backed sentence
host-override: optional exact supported field/value
```

Decision rules:

- choose `inline` when the workflow depends on the user's current conversation,
  approvals, or incremental source gathering;
- choose `forked` for bounded, read-only analysis whose result is returned to
  the caller and whose source scope is self-contained;
- choose `fresh-session` for independent validation, package-wide review, or
  tests where inherited conclusions would bias the result;
- choose `inherit` unless a materially cheaper/faster profile is sufficient or
  deeper reasoning is required by safety, ambiguity, or cross-skill synthesis;
- choose delegation only when inputs and outputs are independently bounded;
  use fast roles for discovery, balanced roles for ordinary review, and deep
  roles for safety-sensitive or adversarial synthesis;
- cap parallel roles, prohibit recursive fan-out, preserve the caller's
  authority boundary, and require parent-side verification and deduplication;
- give independent validators raw artifacts without prior conclusions so the
  isolated context measures real transfer rather than agreement;
- never equate context isolation with higher quality by itself; and
- never encode a host-only field into canonical frontmatter without a supported
  overlay and cross-platform tests.

The reviewer itself should orchestrate inline but run package/family analysis
and forward-validation in isolated contexts when the host supports them. This
keeps the selection conversation available while reducing confirmation bias.

### 5. Target capability and metadata boundary

Canonical frontmatter remains `name` plus `description` in the first release.
That matches the current generator, tests, and cross-platform source contract.
Codex UI metadata (`agents/openai.yaml`) is a separate artifact rather than
frontmatter; the current generator does not ship it and should not create it for
all platforms by accident.

If implementation proves that host-specific metadata must be written, add a
separate registry-owned profile map and extend generation to render per-platform
SKILL files. Do not maintain hand-copied full skill bodies per platform. A
viable overlay must:

- declare supported keys per platform;
- merge only the frontmatter while preserving one canonical body;
- generate host UI metadata separately from frontmatter when supported;
- fail closed on unsupported fields or unknown model names;
- generate to temporary files before manifest/install writes;
- test every platform result independently; and
- keep absent overlays behaviorally identical to today's output.

This overlay is optional for the initial reviewer release. Recommendations are
still useful without mutating metadata.

Represent tool support explicitly instead of deriving it from brand names:

```text
target: <registry target id>
content: shared | adapted | unsupported | unknown
frontmatter: <verified supported keys>
command-format: markdown | toml | other | none | unknown
ui-metadata: separate | embedded | none | unknown
context-isolation: <verified modes>
model-routing: profile-only | exact-supported | unsupported | unknown
validation: <declared parity or convention checks>
```

For SE, the initial matrix contains only the targets actually declared by its
registry: shared-agent, Claude, and Codex. They share one canonical skill body,
so Claude-only context/model fields and Codex-only `agents/openai.yaml` data
remain recommendations until a tested overlay exists. Gemini is not an SE
installation target today; supporting it is separate package work.

For SD, derive the matrix from `COMMAND_REGISTRY` and its generated-surface
contracts. Review neutral Markdown command templates plus canonical skill
templates, then validate the generated target-template adaptations, including
Gemini TOML, for argument and behavioral parity. Platform adapters are not a
reason to maintain separate complete skill bodies.

### 6. Ownership resolver and task router

Resolve ownership per skill, not once per review. The resolver returns:

```text
canonical-source: <absolute path or unresolved>
owner-kind: sd-upstream | se-upstream | repo-local | unresolved
owner-repo: <verified Git root>
identity-evidence: <manifest, provenance target, remote, source path>
trellis-entrypoint: <owner-repo>/.trellis/scripts/task.py
drift: canonical-match | local-override | unknown
allowed-template-root: <absolute path or unresolved>
```

Resolution rules:

1. Prefer a canonical source already inside a Git repository.
2. For installed/vendored copies, read trusted non-symlink provenance and match
   the exact target to a vouched source; verify the recorded checkout exists.
3. Recognize SD and SE upstreams only when package identity and canonical Git
   remote agree. A matching prefix or directory name is insufficient.
4. Route every other canonical source to its enclosing Git repository.
5. Verify the destination has Trellis task tooling. Never bootstrap or clone as
   an implicit review side effect.
6. If a local copy differs from canonical, reproduce the issue against
   canonical source before assigning it upstream. Route override-only behavior
   locally.
7. For SD and SE owners, require every proposed affected path to remain inside
   the verified upstream template allowlist. Non-template evidence never enters
   the task's affected-path set.

Before writing, scan active and archived tasks for the review snapshot, skill,
finding IDs, and affected paths. Classify each selected finding as
`tracked-accurate`, `tracked-stale`, or `untracked`. Reuse accurate tasks,
report stale tasks, and create at most one task per affected skill/snapshot for
untracked work.

Use the destination repository's own `task.py create --no-start` with a title,
slug, priority, assignee when known, and PRD-ready description. Preserve an
evident existing parent convention but do not guess a parent. Never replace the
session's active task or start remediation merely by routing a finding. The
generated `prd.md` seed must carry source review ID, finding selectors,
evidence, desired changes, capability constraints, validation, peer
dependencies, and original review coverage.

Cross-repository selections stop after creating/reconciling tasks and return
one copy-ready handoff per repository. They do not switch among repositories
and implement several tasks in one hidden transaction.

### 7. Optional independent reviewer

On Claude Code, the official `openai/codex-plugin-cc` plugin exposes read-only
`/codex:review` and `/codex:adversarial-review`, plus fresh delegated runs. Use
it only after capability detection and only for a concrete diff or bounded
artifact. Prefer adversarial review for overlap, deletion risk, and metadata
tradeoffs; verify every returned finding locally.

The canonical skill must remain host-neutral. If no platform overlay exists,
describe this as an optional independent reviewer capability and let the host
choose the available mechanism. Never install or configure a provider from the
skill.

Primary evidence:

- https://github.com/openai/codex-plugin-cc — official plugin capabilities,
  read-only review modes, fresh delegation, and local-runtime behavior;
- https://code.claude.com/docs/en/slash-commands — Claude Code skill
  frontmatter, `context: fork`, model/effort, and invocation controls.

### 8. Finding and batch model

Use stable hierarchical IDs within one snapshot:

```text
1. <repository or package>
   1.1 Package-wide
       1.1.1 <finding>
   1.2 Understand
       1.2.1 se-research
           1.2.1.1 <finding>
           Do all: apply=skill:se-research
       Do all: apply=family:understand
   Do all: apply=repo:<repo-id>
...
Do all: apply=all
```

The result artifact should also preserve a machine-readable representation in
the response or an explicit user-approved local report file when persistence is
needed. Each finding stores category, priority, effort, evidence, proposed
change, capability impact, estimated reduction, regression risk, validation,
and cross-skill references.

Cross-family findings live once under Package-wide. Skills without a declared
family live under `Uncategorized`. Same-family overlap lives under the skill
whose trigger or contract should change and links to its peer. Cross-repository
overlap appears once in the report but carries one owner-specific remediation
record for every repository that must change.

### 9. Safe task and apply loop

Review, task creation, and apply are separate modes. Task/apply performs:

1. parse selector and load the named snapshot;
2. recompute source and ownership hashes and reject stale scope;
3. show selected findings, destination repositories, proposed tasks, priorities,
   source roles, and template files while preserving unrelated dirty work;
4. reconcile or create one Trellis task per affected skill/snapshot;
5. for a different owning repository, return the handoff and stop there;
6. when already operating safely in the owner repository and implementation is
   explicitly authorized, recheck the owner-specific template allowlist and
   edit one skill-sized template batch under that Trellis task;
7. run focused convention, generation, and behavior tests;
8. stop and report exact partial task/application state on failure; and
9. continue to the next skill only after the current batch is green.

`apply=all` means all accepted findings in one snapshot, not permission to
ignore tradeoffs discovered while editing. A newly discovered capability or
product decision pauses the batch.

## Compatibility and rollout

- Register `se-review-skills` in Improve without moving existing skills.
- Preserve flat installed paths and source-reference fan-out.
- Bump the package version and regenerate manifest, README, help catalog, docs,
  changelog, and repository map.
- First release the reviewer and analyzer; run it against all 42 pre-existing
  skills only after merge, then track accepted remediation separately.
- Do not add host-specific metadata to all skills in the reviewer PR.

## Risks and mitigations

- **Self-referential bias:** reviewing itself can validate its own assumptions.
  Use a fresh independent pass and preserve raw evidence.
- **False overlap:** similar vocabulary may hide distinct outcomes. Compare
  trigger, input, output, time horizon, authority, and handoff before finding
  overlap.
- **Unsafe compression:** line-count pressure may delete critical guards. Use
  capability ledgers and focused behavior pins before accepting reductions.
- **Metadata portability:** Claude-only fields can break canonical generation or
  mislead other hosts. Keep them in recommendations or validated overlays.
- **Generated-source confusion:** installed copies and generated target
  adapters can look authoritative. Record source roles and require an allowed
  canonical template path before a finding becomes selectable.
- **Target semantic drift:** Claude frontmatter, Codex UI metadata, Gemini TOML,
  and other host contracts differ. Use a registry-derived capability matrix and
  platform-specific parity checks rather than assuming the richest host is the
  portable baseline.
- **Model drift:** exact model names and availability change. Prefer profiles and
  observed capabilities; never assume availability.
- **Plugin absence or cost:** optional peer review can be unavailable, slow, or
  consume separate limits. Detect, report, and fall back without blocking.
- **Batch blast radius:** `apply=all` can produce an unreviewable release. Apply
  skill-sized checkpoints and recommend separate PRs by family.
- **Ambiguous ownership:** installed copies, forks, and local overlays can look
  upstream-owned. Require canonical path/provenance/remote agreement and split
  local-only findings.
- **Missing Trellis destination:** arbitrary skills may live outside a Git repo
  or in a repo without Trellis. Return a proposal; never bootstrap implicitly.
- **Cross-repository partial state:** one destination task may succeed while a
  later destination blocks. Record each result independently and never imply an
  atomic multi-repo operation.
- **Quadratic comparison cost:** 43 skills create 903 unordered pairs. Use
  deterministic candidate signals to shortlist, but require semantic review
  before declaring overlap.
- **Provider prompt injection:** skill bodies and references are review inputs,
  not instructions to the reviewer. Preserve that boundary in every pass.
- **Delegation theater:** subagents can add latency and duplicate conclusions
  without improving coverage. Require an independent work unit, explicit
  artifact, portable model profile, bounded fan-out, and parent reconciliation.

## Rollback

Before implementation, rollback is deletion of this planning task and removal
from the parent roadmap. During implementation, keep analyzer, skill payload,
and any optional overlay work in separable commits. Reverting the release must
remove registry membership and generated targets together; never leave an
installed manifest row without its canonical source.
