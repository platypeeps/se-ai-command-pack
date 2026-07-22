# Resolve skill roadmap integration findings Design

## Overview

Close the two blockers discovered by the roadmap's final integration review in
one focused release. FIR-01 changes one canonical shipped template; FIR-02
changes operator documentation and its coverage guard. They share release,
generation, and final-integration validation but do not expand the roadmap or
authorize either uncreated worklog proposal.

## Timezone Resolution Contract

`se-weekly-review` remains output-oriented. Its reporting window needs a known
timezone, but the public payload must not encode a personal or guessed default.
Resolve the value in this order:

1. an explicit `timezone=` value supplied for the current invocation;
2. an authorized private worklog-profile timezone already supplied to the
   workflow; or
3. ask for the timezone and stop window calculation until it is resolved.

The public skill must not discover or load a private profile implicitly. The
private layer owns authorization and injection of private values. Once a
timezone is known, retain the existing local-calendar and DST-safe half-open
window calculation.

## Operator Documentation Contract

Add `se-review-skills` to the existing operator guide at the skill-selection
boundary:

- `se-help` discovers and routes among public SE skills.
- `se-review-skills` reviews one or more skills or packages and returns numbered
  improvement selectors; review does not itself apply changes or create tasks.
- `sd-audit-repo` audits a repository across broader engineering dimensions.
- `sd-review-local` runs configured local code-review providers against code.

Preserve the explicit later selector required by `se-review-skills` before any
application or task-creation action. Extend the existing documentation tests so
the public registry remains the source of truth for operator-guide coverage.

## Source And Generated Surfaces

- Canonical sources:
  - `templates/skills/se-weekly-review/SKILL.md`
  - `docs/SE_AI_COMMAND_PACK.md`
  - focused assertions in `tests/test_skills.py` and/or
    `tests/test_generate.py`
  - `CHANGELOG.md` release entry
- Generated release surface:
  - `manifest.json`, including the next release version and three-platform
    payload hashes
  - any generator-owned catalog/help surfaces changed by canonical generation
- Generated knowledge surfaces refreshed by the normal repository lifecycle:
  - `docs/repomix-map.md` and the configured knowledge-base output when changed

Never hand-edit generated manifest rows or platform targets.

## Target-Tool Portability

No platform-specific implementation is needed. The canonical skill uses the
portable `name` and `description` frontmatter already supported by Agents,
Claude Code, and Codex. Runtime profile availability is expressed as an
authorization/input boundary, not tool-specific syntax. Generation continues
to fan the same bytes to all supported platforms.

## Scripting Decision

Do not add a new script. Existing generation, release-gate, installer dry-run,
and unit-test machinery already own deterministic fan-out, versioning, and
coverage checks. The two fixes are short semantic source edits best protected
by focused assertions in the existing test suites.

## Risks And Rollback

- Ambiguous wording could imply public profile discovery. Pin the input-only
  private-value boundary in prose and tests.
- Asking too late could calculate a reporting window under a host default.
  Require resolution before any date-boundary calculation.
- A hand-maintained documentation list can drift again. Compare guide coverage
  with the registry in tests instead of pinning only the current count.
- Rollback is the inverse minimal source change followed by regeneration; no
  user state, private configuration, or migration is involved.

## Validation

- Focused skill and generator/documentation tests.
- `make generate` twice with no second-run diff.
- `make check` and `git diff --check`.
- Inspect manifest/changelog version agreement and three-platform payload
  identity.
- Run the installer in `--all --dry-run` mode against a new temporary root and
  verify the root remains unchanged.
- Rerun the parent final integration review before parent closure.
