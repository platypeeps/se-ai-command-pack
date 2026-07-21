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
- Preserve compatibility with Python 3.10; use postponed annotations where
  modern typing syntax appears.
- Format for Ruff's 88-character line length and selected `E4`, `E7`, `E9`,
  `F`, `I`, and `B` rules; keep mypy clean for `installer` and `install.py`.

---

## Testing Requirements

- Add focused unittest coverage for every observable behavior change, including
  failure and preservation paths when filesystem state is involved.
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
- Apply the shared source standards and verification protocol. Prefer primary
  evidence, trace to origin, corroborate load-bearing claims, preserve credible
  conflicts, and date every mutable claim against the explicit as-of date.
- Absence of evidence is not contradiction without an authoritative
  completeness boundary. Inaccessible content is never inferred from snippets.
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
| Available evidence cannot establish the claim | Use unverified; do not upgrade uncertainty through tone. |
| Item is opinion, rhetoric, or prediction | Classify it outside factual verdict totals. |
| User asks to rewrite or publish | Require a separate request and relevant action authority. |

### 5. Good/Base/Bad Cases

- Good: preserve each original claim and locator, inspect primary and contrary
  evidence, assign one calibrated verdict, cite dated sources, and offer only a
  minimal correction where required.
- Base: evidence is incomplete, so the ledger records unverified with the
  inaccessible source and the evidence that would resolve it.
- Bad: label an opinion false, infer a paywalled source, call missing evidence a
  contradiction, silently rewrite the draft, or break an existing installed
  reference path during a canonical-source move.

### 6. Tests Required

- Pin all five verdicts, exactly-one-verdict wording, claim inventory before
  search, atomic locators, non-fact-checkable categories, minimal correction,
  prompt-injection resistance, and read-only authority.
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
