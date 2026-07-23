# Quality Guidelines

> Code quality standards for backend development.

---

## Overview

Changes must preserve safe, deterministic installation across supported Python
and operating-system versions. Prefer small modules, explicit data flow,
immutable result records, plan-before-apply operations, and tests at the same
boundary users exercise.

---

## Forbidden Patterns

- Hand-editing generated `manifest.json` rows instead of changing the registry
  or canonical templates and running `make generate`.
- Hand-editing the marker-bounded README skill catalog instead of changing
  `SKILLS` or canonical skill frontmatter and running `make generate`.
- Writing outside the validated install root or following untrusted symlinked
  receipt/destination paths.
- Destructive overwrite/removal without hash or template provenance, except
  when the user explicitly requests `--force`.
- Network/Git mutation during a dry-run.
- Broad exception catches that hide actionable filesystem or subprocess errors.
- Adding a shipped payload change without a manifest version bump and matching
  `CHANGELOG.md` entry.

---

## Required Patterns

- Validate manifest, registry, source, and destination paths before mutation.
- Preview a multi-file lifecycle operation before applying it.
- Use atomic writes for installed files and receipts.
- Keep canonical skill content under `templates/skills/` and pack declarations
  in `installer/registry.py`.
- Keep family membership singular and canonical in `SKILLS`; derive
  `SKILL_NAMES`, preserve flat skill paths, and generate grouped catalog prose
  from validated frontmatter.
- When sibling skills intentionally share a request noun, route by the user's
  intended outcome instead of deleting accepted capability from either skill.
  For tutorials, original thesis, argument, firsthand experience, or publication
  contribution belongs to `se-author`; ordered teaching that completes and
  verifies an observable result belongs to `se-tutorial`.
- If the intended outcome leaves those workflows materially ambiguous, ask one
  focused routing question before selecting a skill.
- For portable comparison state, define staleness from an explicit caller
  freshness policy or an unrecoverable source-specific continuity gap. Never
  select a stale-state recovery branch from age alone when no freshness
  horizon is part of the accepted contract; preserve source boundaries and use
  qualified comparison when continuity fails.
- Preserve compatibility with Python 3.10; use postponed annotations where
  modern typing syntax appears.
- Format for Ruff's 88-character line length and selected `E4`, `E7`, `E9`,
  `F`, `I`, and `B` rules; keep mypy clean for `installer` and `install.py`.

---

## Testing Requirements

- Add focused unittest coverage for every observable behavior change, including
  failure and preservation paths when filesystem state is involved.
- Pin both positive sides of any overlapping-skill routing boundary plus its
  materially ambiguous clarification path.
- Pin fresh, explicit-policy stale, continuity-gap stale, and no-policy paths
  whenever a shared state contract selects normal versus qualified comparison.
- Use temporary install roots; never target the developer's real home directory
  from tests.
- Mock Git/subprocess boundaries when asserting lifecycle sequencing, while
  retaining end-to-end CLI tests for parsing, exit codes, and installed files.
- Run `make check`: generation parity, Ruff, mypy, the unittest suite, and the
  release payload/version gate must all pass.

---

## Code Review Checklist

- Is the change made in the canonical registry/template/module rather than a
  generated or duplicated surface?
- Are all paths constrained to the intended source/install roots?
- Does dry-run avoid mutation, and does apply reuse or revalidate its plan?
- Are user-modified files preserved by default?
- Do errors include actionable context without leaking sensitive contents?
- Do tests cover success, invalid input, conflicts, and compatibility state?
- If payload changed, are `manifest.json`, version, and `CHANGELOG.md` aligned?

---

## Scenario: Skill Family Registry And Generated Catalog

### 1. Scope / Trigger

- Trigger: adding, retiring, reordering, or reclassifying a shipped skill, or
  changing either generated skill catalog.
- Why: family metadata crosses the registry, canonical frontmatter, generator,
  README, tests, and manifest-order compatibility even though it does not alter
  installed paths or the manifest schema.

### 2. Signatures

```text
FAMILY_LABELS: dict[str, str]
FAMILY_DESCRIPTIONS: dict[str, str]
SKILLS: tuple[SkillInfo, ...]
SKILL_NAMES = tuple(skill.name for skill in SKILLS)
make generate
python .github/scripts/generate-skill-surfaces.py --check
<!-- SE_SKILL_CATALOG:START --> ... <!-- SE_SKILL_CATALOG:END -->
templates/skills/_shared/references/skill-catalog.md
```

`FAMILY_LABELS` order is public catalog order. `FAMILY_DESCRIPTIONS` must have
the same keys in the same order. `SKILLS` order remains canonical
manifest/install order, and grouping must not reorder generated manifest rows.

### 3. Contracts

- Every `SkillInfo.name` is non-empty, unique, `se-` prefixed, and backed by a
  flat `templates/skills/<name>/SKILL.md` directory.
- Every skill has exactly one family from Understand, Decide, Create,
  Coordinate, Operate, or Improve. Empty families remain valid: the compact
  README catalog omits them, while the bundled help catalog renders every
  family with its canonical outcome description.
- `SKILL_NAMES` is derived for compatibility; no consumer owns a second skill
  list.
- The catalog description comes from the already validated frontmatter parse.
  Markdown table pipes are escaped deterministically; descriptions are not
  duplicated in registry code.
- Generation computes and validates manifest, README, and bundled help-catalog
  results before writing any of them. A later write failure rolls earlier
  surfaces back to their committed state. README content outside one ordered
  marker pair is preserved.
- Family-only metadata and catalog changes do not require a release bump when
  `manifest.json` and shipped payload bytes remain unchanged.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Empty skill name, family, or family description | Raise a registry `RuntimeError` before generation. |
| Family-description keys or order differ from family labels | Raise a registry `RuntimeError` before generation. |
| Unknown family | Raise a registry `RuntimeError` naming the skill and family. |
| Duplicate skill name, including cross-family membership | Raise a registry `RuntimeError`; never choose one row implicitly. |
| Missing, duplicate, or reversed README markers | Fail generation before either surface is written. |
| Frontmatter description contains a table pipe | Escape it as `\|` in the README cell. |
| Manifest, README, or bundled help catalog drifts | `--check` reports each drifted surface and exits nonzero. |
| Family metadata changes but payload does not | Manifest and changelog stay unchanged; release gate passes without a bump. |

### 5. Good/Base/Bad Cases

- Good: add one `SkillInfo` row with one valid family, run `make generate`, and
  receive a grouped README entry while flat installed targets remain stable.
- Base: rerun `make generate` with unchanged inputs and receive no file diff.
- Bad: hand-edit a catalog row, duplicate the description in the registry,
  move a skill under a family subdirectory, or add family fields to manifest
  rows.

### 6. Tests Required

- Registry tests pin family and description order, all valid identifiers,
  derived name order, prefix rules, and rejection of empty, unknown, or
  duplicate membership.
- Generator tests pin README grouping, all-family bundled-help output,
  frontmatter sourcing, version identity, pipe escaping, marker validation,
  independent drift reporting, coordinated rollback, and patched temporary
  output paths.
- `make generate` twice, `make check`, `git diff --check`, and explicit empty
  diffs for `manifest.json` and `CHANGELOG.md` complete the change gate.

### 7. Wrong vs Correct

#### Wrong

```python
SKILL_NAMES = ("se-research", "se-new")
README_DESCRIPTIONS = {"se-new": "A second description source."}
```

#### Correct

```python
SKILLS = (
    SkillInfo(name="se-research", family="understand"),
    SkillInfo(name="se-new", family="decide"),
)
SKILL_NAMES = tuple(skill.name for skill in SKILLS)
```

Run `make generate`; canonical `SKILL.md` frontmatter supplies the catalog
description.

---

## Scenario: Skill-Owned References And Deterministic Scripts

### 1. Scope / Trigger

- Trigger: adding or changing a file below a canonical skill directory other
  than `SKILL.md`, or changing generator resource validation and fan-out.
- Why: optional resources cross canonical-source validation, manifest rows,
  every supported platform target, install behavior, and release payload
  identity.

### 2. Signatures

```text
templates/skills/<skill>/SKILL.md
templates/skills/<skill>/references/<name>.md
templates/skills/<skill>/scripts/<name>.py
skill_payload_files(name) -> list[str]
make generate
python .github/scripts/generate-skill-surfaces.py --check
```

### 3. Contracts

- Resource directories are optional and flat. The only accepted resource
  shapes are `references/*.md` and `scripts/*.py`; nested directories and other
  suffixes fail validation before any generated surface is written.
- Every accepted resource is fanned out byte-for-byte beside `SKILL.md` for
  each platform in `PLATFORM_REGISTRY`, with deterministic ordering and a
  manifest row using the skill's normal scope and anchor.
- References hold conditional detail that is directly reachable from the skill.
  Scripts hold bounded deterministic work such as parsing, normalization,
  validation, hashing, inventory, or stable transformation. Judgment, dialogue,
  approvals, and mutation authority remain explicit in `SKILL.md`.
- Bundled scripts should be Python 3.10-compatible and standard-library-first.
  Their user-facing contract defines inputs, outputs, failure behavior, side
  effects, portability, idempotence or dry-run behavior, and tests.
- Adding or changing a resource changes shipped payload bytes and therefore
  requires a manifest version bump and matching changelog entry.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Flat `references/*.md` or `scripts/*.py` file | Validate and fan out to every declared platform. |
| Nested resource directory or unsupported suffix | Fail generation with the unexpected path; write no partial surfaces. |
| Resource exists but is absent from a platform manifest target | `--check` reports drift and exits nonzero. |
| Script requires an undeclared runtime dependency | Reject the design or document and validate the dependency before shipping. |
| Script performs semantic judgment or exceeds caller authority | Keep that operation in the skill; do not extract it. |
| Resource payload changes without version/changelog alignment | Release gate fails. |

### 5. Good/Base/Bad Cases

- Good: move repeated JSON inventory logic into a read-only, standard-library
  script with stable JSON output, focused failure tests, and direct invocation
  from the skill.
- Base: keep a short one-off judgment instruction in `SKILL.md`; no helper is
  created because scripting adds more maintenance than reliability.
- Bad: add a nested helper directory below the skill's scripts resource, ship
  an executable that silently edits files, or move user approval logic into
  code to reduce prompt length.

### 6. Tests Required

- Generator tests accept and fan out each allowed resource type to every
  platform and reject nested directories, wrong suffixes, and unregistered
  files without partial writes.
- Skill-specific tests pin the helper's deterministic output, invalid-input
  behavior, boundary protections, and read-only or dry-run guarantees.
- Run the helper in an isolated install and assert that every declared platform
  receives the same payload bytes and no unsupported frontmatter is introduced.
- Run `make generate` twice, `make check`, the release payload/version gate, and
  `git diff --check`.

### 7. Wrong vs Correct

#### Wrong

```text
templates/skills/se-example/scripts/lib/decide.py
# The script chooses whether the user-approved action is safe and performs it.
```

#### Correct

```text
templates/skills/se-example/scripts/inventory.py
# The script validates bounded inputs and emits stable, read-only JSON facts.
# SKILL.md interprets the facts and retains approval and mutation decisions.
```

---

## Scenario: Decision Skill Evidence And Authority Boundary

### 1. Scope / Trigger

- Trigger: adding or changing a skill that recommends one option, scores a
  choice, or turns evidence into user-specific judgment.
- Why: recommendation language can hide assumptions, upgrade weak evidence,
  blur neutral comparison with decision authority, or imply permission to act.

### 2. Signatures

```text
question=<bounded choice>
options=<two or more known alternatives>
criteria=<comparison axes>
constraints=<hard limits>
evidence=<authorized sources>
format=brief|memo
```

The final report exposes the decision, option comparison, tradeoffs,
confidence, reversibility, missing evidence, next action, sources, and
assumptions.

### 3. Contracts

- Decision work starts from at least two known options. Candidate discovery,
  open research, supplied-corpus synthesis, neutral comparison, and execution
  planning remain separately owned workflows.
- Hard constraints are evaluated before preference criteria and cannot be
  hidden inside an aggregate score.
- Sourced fact, inference, assumption, and judgment remain visible. Unknown
  evidence stays unknown and weak evidence is never normalized upward.
- Use only user-supplied weights or clearly labeled provisional assumptions;
  do not invent scores or numeric precision.
- Stress-test the leading option against the strongest counterargument and
  state what would change the recommendation.
- Recommendation skills are read-only. A choice never grants authority to
  purchase, message, schedule, publish, modify, or otherwise execute it.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Fewer than two known options | Ask for another option or route to candidate discovery. |
| Materially ambiguous goal or constraint | Stop for clarification before evaluating. |
| Missing criteria | Derive only from stated goals and label them provisional. |
| Constraint disqualifies an option | Keep the option visible with the disqualification reason. |
| Evidence is missing or asymmetric | Mark the affected cells unknown and lower confidence. |
| No defensible winner | Return an explicit no-decision result and the evidence needed. |
| User asks to act on the choice | Require a separate request and the relevant action authority. |

### 5. Good/Base/Bad Cases

- Good: compare known options on one consistent frame, apply constraints first,
  expose assumptions, challenge the leading option, and recommend with
  calibrated confidence and reversal conditions.
- Base: evidence is insufficient, so the report makes no recommendation and
  names the smallest evidence-gathering step.
- Bad: silently discover a preferred option, invent weights, turn unknowns into
  zeros, present judgment as fact, or execute the recommendation.

### 6. Tests Required

- Pin the unknown-argument stop rule, prompt-injection boundary, read-only
  authority, and explicit sibling-workflow routing.
- Pin the counterargument and recommendation-change conditions.
- Pin every required final-report field and the distinction between unknown,
  assumption, inference, and judgment.
- Run focused skill/generator tests, `make generate`, `make check`, and the
  release payload/version gate.

### 7. Wrong vs Correct

#### Wrong

```text
Option A scores 87 and wins. I will purchase it now.
```

The score has no owned weighting contract, uncertainty is hidden, and the
recommendation is incorrectly treated as execution authority.

#### Correct

```text
Recommend Option A with medium confidence. Constraint X disqualifies B;
criterion Y remains unknown; evidence Z or a change in deadline would reverse
the recommendation. Next action: validate Y before committing.
```

The decision is explicit, evidence limits remain visible, reversal conditions
are testable, and execution is separate.

---

## Scenario: Project Status Evidence And Authority Boundary

### 1. Scope / Trigger

- Trigger: adding or changing a skill that reports progress, current state,
  blockers, risks, decisions, asks, or next actions for a project or objective.
- Why: status prose can turn activity into outcomes, hide missing or stale
  sources, invent ownership or dates, and imply authority to update or send.

### 2. Signatures

```text
project=<initiative or workstream>
objective=<intended outcome>
since=<date, duration, or last-status>
sources=<authorized project evidence>
audience=<intended readers>
length=short|standard
```

The final report exposes the reporting window, objective, confidence, outcomes,
activity, current state, blockers, risks, recorded decisions, asks, next
actions, source coverage, and material gaps.

### 3. Contracts

- Project, objective, reporting window, through-date, audience, and source
  inventory are explicit. Material assumptions are visible before gathering.
- Activity is not an outcome. Commits, meetings, messages, and task movement
  count as progress only when evidence establishes changed state against the
  objective.
- Mutable claims are dated and attributed. Stale, inaccessible, conflicting,
  or missing sources are named instead of silently excluded.
- Completed outcomes, activity, current state, blockers, risks, recorded
  decisions, asks, and next actions remain distinct report categories.
- Unknown owners, dates, deadlines, percentages, and causal claims stay unknown;
  concise no-material-change periods are valid.
- Project status is distinct from topical recency, corpus synthesis,
  recommendation, and external baseline monitoring.
- Status skills are read-only. Reporting never grants authority to update tasks
  or repositories, assign work, publish, message, or send the report.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Project or objective is materially ambiguous | Ask before classifying progress. |
| Reporting window is absent | Use only a context-established cadence; otherwise ask. |
| `last-status` baseline is unavailable | Name the missing baseline and require an explicit replacement window. |
| A requested source is stale or inaccessible | Name it in source coverage and lower confidence. |
| Sources disagree | Show each dated position and source; do not silently pick one. |
| Evidence shows effort but no changed state | Report activity, not an outcome. |
| No material change occurred | Return a short no-material-change report without filler. |
| User asks to update or send | Require a separate request and the relevant action authority. |

### 5. Good/Base/Bad Cases

- Good: report dated outcomes against an explicit objective, keep activity and
  current state separate, surface blockers and source gaps, and identify only
  evidenced decisions, asks, and next actions.
- Base: sources are available but show no changed state, so the result is a
  concise no-material-change report with current blockers and coverage.
- Bad: summarize commit counts as outcomes, invent a completion percentage or
  owner, hide an unavailable task system, make a new decision, or send the
  report automatically.

### 6. Tests Required

- Pin the unknown-argument stop rule, prompt-injection boundary, read-only
  authority, and explicit sibling-workflow routing.
- Pin objective and reporting-window handling, outcome-versus-activity wording,
  unavailable-source disclosure, no-material-change behavior, and the ban on
  invented owners or dates.
- Pin every required final-report field and shared source-standard fan-out.
- Run focused skill/generator tests, `make generate`, `make check`, and the
  release payload/version gate.

### 7. Wrong vs Correct

#### Wrong

```text
We merged 14 commits, so the project is 80% complete. I assigned the remaining
work and sent this update to stakeholders.
```

Activity was promoted to an outcome, the percentage and authority were
invented, and reporting was incorrectly treated as permission to act.

#### Correct

```text
Outcome: the dated acceptance evidence shows the stated objective now supports
workflow X. Activity: 14 commits landed, but source Y is unavailable and no
completion percentage is supported. Next action has no recorded owner.
```

The outcome is tied to changed state, activity stays separate, source limits
remain visible, and unknown ownership is preserved.

---

## Scenario: Claim Audit Evidence And Verdict Boundary

### 1. Scope / Trigger

- Trigger: adding or changing a skill that audits supplied claims, drafts,
  transcripts, or artifacts and assigns evidence-based verdicts.
- Why: claim auditing can lose original locators, force opinion into binary
  truth labels, inflate weak evidence, rewrite beyond the evidence, or break
  installed reference paths when verification rules become shared.

### 2. Signatures

```text
input=<artifact or link>
claims=<explicit claim subset>
scope=material|all
as_of=<audit date>
format=ledger|memo
```

Each audited claim retains an ID, original wording, original locator, exactly
one verdict, rationale, evidence links or locators, source dates, and confidence.

### 3. Contracts

- Inventory requested inputs before searching. Split compound statements into
  atomic claims without losing exact wording or the original locator.
- Use exactly five mutually exclusive verdicts: supported, partially supported,
  unverified, contradicted, and outdated.
- Opinion, rhetoric, value judgment, and prediction remain visible outside the
  factual verdict totals; audit their checkable premises separately when useful.
- Apply the shared source standards and verification protocol. Determine
  freshness from claim volatility, applicable version or period, supersession,
  and any explicit domain horizon; age alone does not make immutable or stable
  historical evidence stale. Date and scope every mutable claim against the explicit
  as-of date, jurisdiction, version, environment, or period.
- One authoritative primary record may support an exact load-bearing claim only
  when the record is dispositive and its identity and applicability are
  verified. Empirical, interpretive, disputed, surprising, and interested-party
  claims still require independent corroboration or remain low-confidence or
  unverified. A first-party vendor assertion is not dispositive by origin alone.
- Trace evidence to origin, preserve credible conflicts, and perform a real
  disconfirmation pass even for a dispositive-record claim.
- Absence of evidence is not contradiction without an authoritative
  completeness boundary. Inaccessible content is never inferred from snippets.
- Preserve every audited factual claim through exactly one verdict. An
  unsupported load-bearing claim remains `unverified` in the claim and
  evidence-gap ledgers but cannot support conclusions, recommendations, or
  corrected wording.
- Corrected wording is limited to the smallest evidence-matched change for a
  partially supported, contradicted, or outdated claim.
- Claim audits are read-only. A verdict never grants authority to edit,
  replace, publish, contact, or enforce.
- Moving a skill-owned reference to shared canonical ownership must preserve
  every existing installed target and add a regression for its new consumers.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Neither input nor explicit claims are supplied | Ask before reading or searching. |
| One sentence contains several assertions | Split into atomic claims and retain one original locator. |
| Material evidence is inaccessible | Name the gap; never infer its contents. |
| Evidence supports only a narrower statement | Use partially supported and offer minimal qualified wording. |
| Stronger current evidence conflicts | Use contradicted and show the decisive dated evidence. |
| Earlier evidence held but current evidence changed | Use outdated against the explicit as-of date. |
| Stable historical or immutable primary evidence is old | Keep it applicable unless version, period, supersession, or a domain horizon says otherwise. |
| One authoritative record establishes its exact bounded fact | Verify identity and applicability; it may support that claim without a redundant echo. |
| A vendor makes an empirical or self-interested assertion | Require independent corroboration or keep it low-confidence or unverified. |
| Available evidence cannot establish the claim | Use unverified; do not upgrade uncertainty through tone. |
| An unverified claim is load-bearing | Keep its claim ID, verdict, and missing evidence in the ledgers; exclude it from conclusions and recommendations. |
| Item is opinion, rhetoric, or prediction | Classify it outside factual verdict totals. |
| User asks to rewrite or publish | Require a separate request and relevant action authority. |

### 5. Good/Base/Bad Cases

- Good: preserve each original claim and locator, inspect primary and contrary
  evidence, assign one calibrated verdict, cite dated sources, and offer only a
  minimal correction where required.
- Base: evidence is incomplete, so the ledger records unverified with the
  inaccessible source and the evidence that would resolve it; if the claim is
  load-bearing, the summary cannot rely on it.
- Bad: label an opinion false, infer a paywalled source, call missing evidence a
  contradiction, delete an unsupported load-bearing claim from the ledger,
  silently rewrite the draft, or break an existing installed reference path
  during a canonical-source move.

### 6. Tests Required

- Pin all five verdicts, exactly-one-verdict wording, claim inventory before
  search, atomic locators, unsupported load-bearing claim retention and
  conclusion exclusion, non-fact-checkable categories, minimal correction,
  prompt-injection resistance, and read-only authority.
- Pin claim-sensitive freshness, the narrowly dispositive authoritative-record
  exception, and conservative corroboration for empirical, disputed,
  interpretive, surprising, and interested-party claims.
- Pin explicit sibling boundaries from open research and corpus synthesis.
- Pin every required final-report field and both shared reference citations.
- When a reference source moves, assert the canonical shared source plus every
  old and new installed target across supported platforms.
- Run focused skill/generator tests, `make generate`, `make check`, and the
  release payload/version gate.

### 7. Wrong vs Correct

#### Wrong

```text
The paragraph is false. I rewrote it and published the correction; the
paywalled source probably agrees.
```

The claims were not split, no evidence or locator is traceable, inaccessible
content was invented, and auditing was treated as action authority.

#### Correct

```text
C-03 at paragraph 4 is partially supported: the primary source supports the
narrower dated statement, while the broader quantity is unverified. Suggested
minimal correction: replace only that quantity; no source file was changed.
```

The original claim remains traceable, evidence strength controls the verdict,
the correction is bounded, and execution stays separate.

---

## Scenario: Installed Skill Review Inventory

### 1. Scope / Trigger

- Trigger: changing `se-review-skills` discovery, installed-copy ownership,
  deduplication, snapshot inputs, or task-routing evidence.
- Why: this shipped analyzer crosses repository manifests, user installation
  roots, Git identity, shared resources, and mutation-routing boundaries.

### 2. Signatures

```text
skill_review.py inventory [--root PATH] [--skill NAME_OR_PATH]...
  [--family FAMILY] [--scope skill|family|repo|package|all]
  [--installed auto|off] [--installed-root PATH]... [--pretty]
```

The CLI defaults to `--installed auto`. The Python `build_inventory()` API
defaults installed discovery to `off` so callers and tests must opt in.

### 3. Contracts

- Automatic discovery derives bounded user skill roots only from verified
  manifest `target` rows and inspects direct child `*/SKILL.md` files. It never
  recursively searches a home directory or plugin cache.
- A copy maps to the current repository only through verified manifest target,
  provenance, package identity, and Git ownership evidence. The canonical
  repository file remains `reviewPath` for both matching and drifted installs.
- Verified copies deduplicate by canonical repository identity. Unowned copies
  deduplicate only when normalized skill name and content hash both match.
- Every collapsed copy retains path, root, platform, observed hash, drift, and
  mapping evidence. Installed copies are evidence, never mutation targets.
- Parse `SHARED_REFERENCES` statically from the registry AST. Hash each selected
  canonical shared source into `relatedTemplates` and snapshot identity without
  importing or executing reviewed repository code.
- Inventory schema version 3 exposes `installationRoots`, per-skill
  `installations`, `installedCopies`, `reviewPath`, `testTextReferences`, and
  deduplication coverage. Test-text references are bounded substring locators,
  not verified behavioral pins; callers must inspect the cited assertion before
  claiming behavioral coverage.
- The analyzer supports Python 3.9 and newer. When that runtime is unavailable,
  the skill reports the prerequisite and uses the documented bounded manual
  ownership, path, hash, and selector checks without executing reviewed files.
- Snapshot inputs exclude ignored directories, `__pycache__`, and `*.pyc` so
  interpreter side effects cannot change inventory identity.
- A safely resolved unowned installed copy remains reviewable evidence, but it
  is not changeable and cannot route task creation. Changeability requires a
  verified repository owner and a canonical source within its allowed template
  root.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Automatic install root is absent | Record `missing`; continue with bounded coverage. |
| Automatic root or skill is symlinked | Skip it and report the coverage limit. |
| Explicit root is missing, unbounded, non-directory, or symlinked | Reject before scanning. |
| Same name lacks verified ownership | Keep it unowned and disable task creation. |
| Unowned copy resolves safely | Keep it reviewable, but set `changeable=false`. |
| Installed hash differs from canonical | Report `installed-drift`; still review the verified canonical source. |
| Shared reference is missing, escaped, or symlinked | Fail closed before snapshot creation. |
| Test source contains the skill name | Emit a `substring-reference` locator with `behavioralPinVerified=false`. |
| Bytecode appears below a reviewed skill | Exclude it from related resources and snapshot identity. |
| Python is older than 3.9 | Exit with an actionable prerequisite and bounded manual-fallback instruction. |
| Installed discovery is `off` with explicit roots | Reject the contradictory arguments. |

### 5. Good/Base/Bad Cases

- Good: matching Claude and Codex copies collapse into one repository record
  with two installation entries; a drifted copy changes aggregate drift but
  not task ownership.
- Base: `--installed off` inventories only the selected repository skills.
- Bad: walking `$HOME`, mapping by a skill-name prefix, editing an installed
  copy, or merging different same-named unowned skills.

### 6. Tests Required

- Assert manifest-derived roots without a home walk, explicit opt-out and root
  overrides, multi-platform deduplication, drift routing, and unowned-name
  separation.
- Assert shared-reference content and membership change snapshot identity and
  that missing or symlinked sources fail closed.
- Assert the Python 3.9 floor, controlled fallback, honest test-text reference
  classification, unowned reviewability without changeability, and stable
  snapshots when generated bytecode appears.
- Preserve tests proving reviewed content is never executed, symlinks are not
  followed, pair comparison remains bounded, and SE/SD canonical roles remain
  stable.
- Run the focused analyzer suite, skill contract tests, `make generate`, and
  `make check` with a temporary bytecode cache outside the shipped skill tree.

### 7. Wrong vs Correct

#### Wrong

```text
~/.codex/skills/se-example/SKILL.md differs, so edit that installed file and
open one task for every host copy named se-example.
```

#### Correct

```text
Map each bounded installed copy through verified package evidence, review the
canonical repository source once, retain per-copy drift, and route one task to
the verified owner repository.
```

---

## Scenario: Observed Session Evidence In Skill Reviews

### 1. Scope / Trigger

- Trigger: changing how `se-review-skills` discovers, classifies, reports, or
  acts on conversations that used a reviewed skill.
- Why: session indexes contain incidental mentions, private data, nested
  transcripts, incomplete outcomes, and old skill versions. Without a separate
  evidence gate, an execution error can be misreported as a current source
  defect or leak raw conversation content into a task.

### 2. Signatures

```text
sessions=auto|off       default auto
session=<id>            repeatable, inside the verified project boundary
```

Automatic review inspects the available current conversation, then bounded
project-scoped history. It stops at three distinct confirmed sessions per skill
and twenty distinct sessions total, allocated round-robin across skills. One
session consumes one total slot and one slot for each reviewed skill it
demonstrably invoked; repeated invocations of the same skill stay in one
minimized skill/session evidence record.

### 3. Contracts

- Confirm invocation through explicit user or platform activation, or an
  assistant declaration corroborated by distinctive workflow behavior. Paths,
  diffs, maps, copied prompts, test output, and nested transcripts are
  mention-only candidates.
- Keep session discovery and causal judgment inline with the parent. Use only
  an already available project-aware reader and never scan global history, raw
  home directories, provider caches, or unrelated projects.
- Minimize evidence to a redacted session locator and relevant turn range,
  invocation evidence, skill provenance, request, expected contract, behavior,
  outcome, causal class, and confidence. Never persist raw dialogue, secrets,
  personal data, host paths, or full tool output.
- Record provenance as `current-canonical`, `installed-drift`,
  `historical-version`, or `unknown`. Historical or unknown evidence can show
  recurrence risk but cannot alone prove a current source defect.
- Classify mistakes as `skill-contract`, `execution-deviation`,
  `tool-or-environment`, `user-intent-change`, or `indeterminate`. A selectable
  finding also requires an observed consequence, causal explanation, current
  canonical locator, allowed template remedy, and falsifiable validation.
- Compare a successful or neutral invocation when available. Structure a remedy
  as core workflow, safety gate, conditional reference, deterministic helper,
  host overlay, evaluation, or recovery path. Every gotcha names trigger,
  failure, prevention, recovery, and regression method.
- Session evidence is read-only and never grants task or edit authority. Before
  `task=` or `apply=`, recompute the source snapshot and revalidate the project
  boundary, invocation, provenance, causality, locator, and redaction.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Session reader is unavailable or incompletely indexed | Continue static review and report the coverage limit. |
| Search result only mentions the skill | Reject it as an invocation and do not spend the confirmed-session budget. |
| Explicit session is outside the verified project | Reject it without global fallback. |
| Activation, outcome, or version was lost to compaction | Classify as `indeterminate`; do not create a finding. |
| Clear skill contract was ignored | Classify `execution-deviation`; prefer evaluation unless recurrence implicates structure. |
| Tool or permission failure caused the outcome | Change the skill only when its fallback or recovery contract is deficient. |
| User changed intent after invocation | Preserve chronology as `user-intent-change`; do not blame the skill. |
| Selected session evidence is stale before mutation | Reject the selector and require a fresh review. |

### 5. Good/Base/Bad Cases

- Good: verify a user activation, compare the relevant current skill rule to a
  redacted mistake and a successful control, classify the cause, point to the
  current template, and propose a testable recovery gotcha.
- Base: no safe history reader exists, so complete the static skill review and
  disclose zero historical-session coverage.
- Bad: count every skill-name search hit, quote a private transcript, assume an
  old session used current source, delegate raw conversations, or create a task
  because one run failed.

### 6. Tests Required

- Pin `sessions=auto|off`, repeatable `session=`, the three-per-skill and
  twenty-total budgets, round-robin allocation, and project-only discovery.
- Pin invocation confirmation, mention-only and nested-transcript rejection,
  all provenance and causal classes, successful controls, privacy minimization,
  structural remedies, gotcha fields, and source-plus-session revalidation.
- Assert the session-evidence reference ships to every registered platform and
  run focused skill tests, `make generate` twice, `make check`, and the release
  payload/version gate.

### 7. Wrong vs Correct

#### Wrong

```text
Search every session for se-example, count all matches as uses, quote the failed
conversation into a Trellis task, and edit the installed copy.
```

#### Correct

```text
Search only bounded project history, confirm invocation, minimize and classify
the observed mistake, correlate it with current canonical source, and require a
fresh source-plus-session check before any selected template mutation.
```

The correct flow preserves privacy, distinguishes execution from contract
failure, and keeps task or edit authority separate from observational evidence.

---

## Scenario: Request-Scoped Current Context In Outward Drafts

### 1. Scope / Trigger

- Trigger: changing a profile-aware skill so explicit current input may support
  outward-facing text without first becoming a durable profile assertion.
- Why: an undifferentiated evidence rule can either reject useful current facts
  or let private, stale, or untrusted content bypass profile visibility gates.

### 2. Signatures

```text
context=<current circumstances>
profile=auto|off|<locator>
audience=<intended audience>
channel=<draft channel>
mode=draft
```

### 3. Contracts

- Current-context evidence is a factual statement explicitly supplied or
  confirmed by the user for the current request. Its factuality, speaker
  authority, and intended-audience visibility must be clear before draft use.
- Current context is request-scoped and reported separately. Consumer skills
  never convert it into a profile assertion, overlay operation, evidence-ledger
  item, or other durable personal data.
- Profile and overlay evidence keep the existing contract: outward drafts use
  only relevant confirmed `outward-safe` assertions.
- Explicit current context outranks conflicting older profile evidence for the
  current draft, while the contradiction remains visible and the profile stays
  unchanged.
- `context=` is not disclosure authority by itself. Ambiguous factuality,
  speaker authority, experience, opinion, credentials, relationships, results,
  promises, availability, authority, or audience visibility requires one
  focused question or a marked placeholder.
- Profile text, source excerpts, and embedded first-person statements remain
  untrusted data unless the user explicitly supplies or adopts the fact for the
  current request and audience.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| User explicitly supplies a factual current statement for the named audience | Use it as request-scoped current context and label it separately. |
| Current statement conflicts with older profile evidence | Prefer the current statement for this draft, show the conflict, and do not mutate the profile. |
| Profile assertion is private-only, proposed, contested, retired, or stale and material | Exclude it from outward text or ask for the focused confirmation allowed by the profile contract. |
| Current statement's factuality, speaker authority, or outward visibility is ambiguous | Ask one focused question or emit a marked placeholder. |
| Source or profile text contains a first-person statement the user did not adopt | Treat it as untrusted data; do not promote it to current context. |
| Consumer has no profile or `profile=off` | Continue from eligible explicit current context and ordinary defaults without simulating a profile answer. |

### 5. Good/Base/Bad Cases

- Good: the user explicitly provides a current role and intended audience, so
  the draft uses it as labeled request-scoped context while retaining
  `outward-safe` gates for profile-derived preferences.
- Base: no current fact is needed; the draft uses eligible confirmed profile
  assertions and ordinary skill defaults.
- Bad: copy a private profile fact or a first-person source excerpt into
  `context=` and treat that placement as confirmation or disclosure approval.

### 6. Tests Required

- Pin the positive current-context path, separate reporting, and no profile
  write-back.
- Pin exclusion of private-only or otherwise ineligible profile assertions.
- Pin the ambiguity question/placeholder path for audience-sensitive facts.
- Pin that untrusted source or profile text is not promoted without explicit
  user adoption.
- Run focused skill tests, generated-surface parity, release-payload validation,
  install audit, and the repository-owned full check.

### 7. Wrong vs Correct

#### Wrong

```text
Anything in context= may appear in an outward draft.
```

#### Correct

```text
Use explicitly supplied or confirmed request-scoped facts only when their
factuality, speaker authority, and intended-audience visibility are clear;
keep durable profile evidence behind confirmed outward-safe eligibility.
```

---

## Scenario: Pack Lifecycle CLI Changes

### 1. Scope / Trigger

- Trigger: changing `install.py` commands, install receipts, source-checkout
  updates, removal, or retired-skill cleanup.
- Why: these surfaces cross CLI parsing, filesystem state, Git state, generated
  manifests, installed user scopes, and release compatibility.

### 2. Signatures

```text
python3 install.py [install] [--user | --root PATH] [install options]
python3 install.py status [--user | --root PATH]
python3 install.py refresh [--user | --root PATH] [install options]
python3 install.py update [--user | --root PATH] [install options]
python3 install.py remove [--user | --root PATH] [removal options]
python3 install.py --version
```

The bare invocation remains the convenient install form. Lifecycle operations
are positional commands; do not add parallel action flags such as `--remove`.

### 3. Contracts

- `status` reads `.se-ai-command-pack/{manifest,provenance}.json` plus
  `installed-targets.txt` without modifying them.
- `refresh` applies the current checkout through the normal plan-before-apply
  installer path.
- `update` trusts only the provenance-recorded `sourceRoot`, requires the
  expected pack manifest, refuses a dirty checkout, and fast-forwards with
  `git pull --ff-only`.
- After pulling, `update` launches a fresh Python process, runs a dry-run, and
  applies only when that plan succeeds. This prevents old imported modules
  from being mixed with newly pulled files.
- `remove` and retired-target cleanup delete only hash-vouched or
  template-identical files unless the user explicitly passes `--force`.
- Retiring a skill requires removing it from `SKILLS`, deleting its
  canonical template, regenerating `manifest.json`, and registering every
  previously shipped target in `RETIRED_TARGETS`.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Install root is missing | Exit nonzero with `install root not found`. |
| Status receipts are absent or invalid | Report not installed and return 1. |
| Recorded source checkout is missing or is the wrong pack | Exit before Git or filesystem writes. |
| Source checkout is dirty | Exit before fetch, pull, or refresh. |
| Fast-forward pull fails | Exit with the Git failure; never merge or rebase. |
| Refreshed dry-run fails | Do not run the applying refresh. |
| Retired target is hash-vouched | Remove it during normal refresh. |
| Retired target drifted | Preserve and report it unless `--force` is explicit. |

### 5. Good/Base/Bad Cases

- Good: `python3 install.py update --user` fast-forwards a clean recorded
  checkout, previews the new payload, and reapplies from a fresh process.
- Base: `python3 install.py --user` remains an idempotent install/refresh.
- Bad: implementing lifecycle behavior in a skill prompt, accepting both a
  positional command and an action flag, continuing in the pre-pull Python
  process, or deleting retired files without provenance vouching.

### 6. Tests Required

- CLI tests assert each positional command dispatches correctly and obsolete
  action flags are rejected.
- Status tests assert installed version, source checkout, platform grouping,
  and the not-installed return code.
- Update tests assert dirty-checkout refusal, `--ff-only`, dry-run-before-apply,
  and two fresh-process invocations for planning and application.
- Retirement tests inject a prior provenance hash and assert normal refresh
  removes the vouched old target while existing drift-preservation tests stay
  green.
- Run `make check` to cover unit tests, Ruff, mypy, generated manifest parity,
  and the release payload/version gate.

### 7. Wrong vs Correct

#### Wrong

```text
python3 install.py --remove
```

This duplicates the positional command model and creates a second parser path.

#### Correct

```text
python3 install.py remove --user --dry-run
python3 install.py remove --user
```

One command surface owns removal, with an explicit preview before application.

## Scenario: Repomix Repository Map Refresh

### 1. Scope / Trigger

- Trigger: adding or changing the checked-in repository map, its Repomix
  configuration, or its refresh command.

### 2. Signatures

```text
make repomix
bash scripts/update_repomix
```

### 3. Contracts

- `repomix.config.json` owns the input exclusions and writes compressed,
  parsable Markdown to `docs/repomix-map.md`.
- Git change-count sorting is disabled so identical repository contents
  generate byte-stable file ordering before and after commits.
- `scripts/update_repomix` runs the pinned Repomix version through `npx`
  without adding Node dependencies to this Python project.
- The generated map excludes itself, local knowledge copies and receipts,
  Trellis task/session state, and copied agent-platform surfaces.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| `npx` is unavailable | Exit nonzero with an actionable requirement message. |
| Repomix installation or generation fails | Propagate the nonzero exit; do not report a refreshed map. |
| Repomix detects suspicious content | Treat the generation as failed and inspect before committing. |
| Configuration changes | Regenerate and commit `docs/repomix-map.md` in the same change. |
| Identical inputs generate a different map | Treat the map as nondeterministic; do not commit ordering-only churn. |

### 5. Good/Base/Bad Cases

- Good: `make repomix` uses the pinned version and replaces the tracked map.
- Base: rerunning the command without source changes produces no map diff.
- Bad: running an unpinned global or latest Repomix version and committing an
  output whose behavior cannot be reproduced from the repository.

### 6. Tests Required

- `tests/test_repomix.py` asserts the required copied/runtime exclusion set and
  verifies the checked-in map omits those files while retaining representative
  repo-owned source, tests, templates, and specs.
- Run `make repomix` and require a successful Repomix security scan.
- Run `git diff --check` and verify `docs/repomix-map.md` is the configured
  output and does not include itself.
- Run `make check` so repository-map tooling changes do not regress the Python
  pack, generated surfaces, or release gate.

### 7. Wrong vs Correct

#### Wrong

```text
npx repomix@latest
```

#### Correct

```text
make repomix
```

The repository-owned command pins the tool and applies the curated exclusions.

## Scenario: Repository-Owned PR Full Check

### 1. Scope / Trigger

- Trigger: configuring or changing the repository-owned project check selected
  by the deterministic `sd-review-pr` local gate.

### 2. Signatures

```text
package.json scripts.check = "make check"
package.json scripts.check:full =
  "npm run check && bash scripts/sd-ai-command-pack-full-check.sh"
bash scripts/sd-ai-command-pack-review-full-check.sh
bash scripts/sd-ai-command-pack-toolchain.sh doctor
```

### 3. Contracts

- The package `check` script is the sole package-level owner of `make check`.
- `check:full` runs the project check first and the shared pack full-check
  second, joined by `&&` so either failure remains blocking.
- The review selector invokes `check:full` with Prism and Gito disabled; the
  shared gate continues to own all other pack-wide checks.
- Root package metadata stays private and dependency-free. It exists only to
  expose scripts and must not produce a package lockfile.
- `check:full` must not call the review selector, `sd-review-pr`, or a platform
  adapter because those paths recurse into selection.
- Toolchain doctor reports `package:check` as a candidate but does not execute
  it; execution belongs to the review selector.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| `check:full` is missing or invalid | The review selector uses its documented fallback. |
| The configured package runner is unavailable | Exit `127` with an actionable error. |
| `make check` fails | Stop before the shared pack full-check. |
| The shared pack full-check fails | Propagate its nonzero exit. |
| The wrapper contains a forbidden recursive command | Reject it with exit `2`. |
| The Repomix map is stale | `make check` exits nonzero before remote review. |

### 5. Good/Base/Bad Cases

- Good: `check:full` composes the canonical project check and shared pack gate.
- Base: contributors continue to run `make check` directly.
- Bad: `check:full` calls the review helper, skips the shared gate, declares
  dependencies, or duplicates the Make target in multiple package scripts.

### 6. Tests Required

- Parse `package.json` and assert the exact private, dependency-free script
  contract and absence of supported package lockfiles.
- Run the review selector with a stub package runner and assert it requests
  `run check:full` with Prism and Gito disabled.
- Run the focused configuration test, `npm run check`, toolchain doctor,
  `make repomix`, the Obsidian KB refresh, `npm run check:full`, and
  `git diff --check`.

### 7. Wrong vs Correct

#### Wrong

```json
{
  "scripts": {
    "check:full": "bash scripts/sd-ai-command-pack-review-full-check.sh"
  }
}
```

#### Correct

```json
{
  "private": true,
  "scripts": {
    "check": "make check",
    "check:full": "npm run check && bash scripts/sd-ai-command-pack-full-check.sh"
  }
}
```

The correct wrapper preserves the repository's canonical check and the shared
pack gate without creating a recursive review path.
