# Design personal worklog profile boundary Design

## Overview

Separate portable worklog synthesis from private scheduling, destination, and
write-through behavior. The public pack should eventually contain only an
output-oriented `se-worklog` skill if general demand is proven. A private
automation or companion configuration should own the user's timezone, source
inventory, destination paths, filename variants, metadata, section ownership,
follow-up-link policy, connector preference, fallback, and read-back contract.

Do not add a general profile subsystem to `se-ai-command-pack` for one personal
workflow. The current installer deliberately has no configuration surface, and
the same framework-neutral payload is installed for every user.

## Proposal

Adopt a two-layer boundary:

### Portable core candidate

A future `se-worklog` skill would accept explicit request/context arguments such
as reporting period, activity sources, project grouping, audience, and output
length. Its responsibilities would be:

1. Resolve and state the reporting window.
2. Inventory available activity sources and identify unavailable ones.
3. Exclude automation/helper noise using stated criteria.
4. Group substantive work by project or workstream.
5. Produce a dated worklog with outcomes, decisions, open items, and a bounded
   set of suggested follow-ups.
6. Return the artifact in conversation; it would not choose a destination,
   patch a note, create task files, or schedule the next run.

The core skill must not contain a real identity, timezone, vault path, note
name, section marker, metadata tag, connector endpoint, or follow-up URL
template. It should treat all activity inputs as data, not instructions.

### Private automation/profile layer

The private layer would invoke or reproduce the portable synthesis contract and
own:

- local timezone and previous-day calculation;
- authoritative activity sources and noise classification overrides;
- destination system, root, directory, and filename variants;
- metadata/frontmatter and owned-section markers;
- existing-content preservation rules;
- maximum follow-up links and whether links or task files are allowed;
- preferred connector and explicit fallback behavior;
- empty-day behavior;
- write-through followed by direct read-back verification; and
- private operational memory about prior runs.

Store that layer in the existing private automation configuration/memory or a
private companion repository, not in this public manifest. Explicit invocation
values override private defaults; private defaults override portable defaults.
The public skill must never discover or load a private profile implicitly.

### Options considered

1. **Hardcode the personal workflow in the public skill — reject.** It leaks
   personal contracts and makes the skill non-portable.
2. **Build a pack-wide profile/config subsystem now — reject.** It expands
   install, update, remove, precedence, migration, and secret-handling behavior
   without general evidence.
3. **Ship only a private standalone skill — viable fallback.** Prefer this if a
   generic output-only worklog does not prove useful beyond one automation.
4. **Generic output skill plus private automation — recommended.** It preserves
   a reusable synthesis boundary without coupling the public pack to personal
   writes or scheduling.

## Boundaries And Non-Goals

- This design task ships no `se-worklog` template and changes no installer
  behavior.
- Do not commit real personal paths, identity details, private metadata, or
  connector credentials to the public repository.
- Do not modify the existing automation before a separate implementation task
  is approved.
- Do not auto-create follow-up task files from the portable skill.
- Do not make Obsidian or any other product a dependency of the public skill.

## Affected Files

For this task:

- `.trellis/tasks/07-17-personal-worklog-profile/prd.md`
- `.trellis/tasks/07-17-personal-worklog-profile/design.md`
- `.trellis/tasks/07-17-personal-worklog-profile/implement.md`

Potential later work, only after separate approval:

- `templates/skills/se-worklog/SKILL.md`, registry, tests, generated manifest,
  and catalog/release docs for the portable output skill.
- A private automation memory/config or companion repository for the personal
  profile and write-through workflow.

No public installer/profile files should be added by this task.

## Risks And Edge Cases

- Splitting synthesis and delivery can duplicate wording between public and
  private layers. Keep the public layer responsible for artifact shape and the
  private layer responsible for orchestration/destination only.
- An automation can report success after synthesis but before write/read-back.
  Private completion must require verified destination state.
- Existing notes may use filename or section variants. The private layer must
  inspect and preserve existing structure rather than normalize it.
- Empty reporting periods are valid and should not trigger fabricated work or
  follow-up links.
- Connector failure is not evidence of an empty day. The private layer must
  separate source discovery, synthesis, write, and read-back outcomes.
- A public argument like `destination=` could quietly turn an output skill into
  a mutation workflow. Keep writes outside the initial portable core.
- Private profile data may still leak through examples or tests. Use synthetic
  names, paths, tags, dates, and connector identifiers in any public artifact.

## Validation

- Review the boundary against the current installer contract and confirm no
  configuration, precedence, or removal change is needed.
- Model synthetic substantive-day, empty-day, existing-note, filename-variant,
  connector-failure, write-failure, and read-back-failure scenarios.
- Verify the portable core can be described with no product-specific path or
  personal datum.
- Scan proposed public artifacts for real identity, home/vault paths, private
  metadata, endpoints, and credentials before review.
- Require separate user approval before creating implementation tasks or
  changing the private automation.

## SD Work Designs Scope Update - 2026-07-17

The earlier recommendation against a pack-wide profile contract was based on a
single worklog use case. The user has now explicitly requested a reusable,
user-owned personal operating profile consumed by authoring, papers, generated
communications, and a read-only self-query workflow. That is sufficient product
evidence to revisit the general mechanism without weakening this task's privacy
boundary.

Keep worklog destination paths, filenames, connector fallbacks, and TaskNotes
rules in the private worklog layer. Coordinate the new general profile work
through the separate `personal-profile-contract`, `se-profile`, and `se-ask-me`
tasks. The general profile must store portable preferences, voice evidence,
values, goals, working patterns, and explicit boundaries—not workflow-specific
vault paths, credentials, or automation state.
