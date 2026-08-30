# Design: Shared-reference citation-closure gate

## Overview

`validate_skills()` in `.github/scripts/generate-skill-surfaces.py` today checks
the **forward** direction of the shared-reference contract: every file under
`templates/skills/_shared/references/` must be registered in
`installer/registry.py` `SHARED_REFERENCES`, every registered source must exist
(unless generated), and no consumer may carry an own copy that collides with a
fan-out basename.

It does **not** check the **reverse** direction. A skill body (`SKILL.md`) can
cite `references/<file>.md` that will never ship to that skill — neither an own
`references/<file>.md` resource nor a registered `SHARED_REFERENCES` fan-out
delivering it. Such a skill installs fleet-wide with a dangling citation. An
existing unit test (`test_shared_reference_consumers_cite_registered_reference`)
proves registration -> citation; nothing proves citation -> delivery.

This task adds the reverse gate to the generate `--check` path so a dangling
citation fails generation instead of shipping.

## Proposal (primary path)

Implement requirement bullet 1 (extend `validate_skills`). The optional
"invert the opt-in consumer list to opt-out" alternative (bullet 2) is **not**
taken: it is a larger registry refactor with its own risk and is out of scope
for this closure gate. Recorded as a deferred consideration in Follow-Ups.

### Delivered-reference map

Inside `validate_skills()`, after the existing forward/collision checks, build a
per-skill set of reference basenames that will actually ship to that skill:

```
delivered[skill] =
    { own references/*.md basenames present under templates/skills/<skill>/ }
  ∪ { basename(source) for source, consumers in SHARED_REFERENCES
                       if skill in consumers }
```

- The fan-out arm keys on `SHARED_REFERENCES` **membership**, not source-file
  presence, so `GENERATED_SHARED_REFERENCES` (e.g. `skill-catalog.md`) count as
  delivered even though their source file does not exist at scan time.
- The own-copy arm and the fan-out arm are mutually exclusive per basename: the
  existing collision check already forbids a consumer from carrying an own copy
  of a fan-out basename, so no basename is double-counted or ambiguous.

### Citation scan

For each registered skill with a present directory, read `SKILL.md` and find
citations with a strict basename pattern:

```
CITATION = re.compile(r"references/([A-Za-z0-9][A-Za-z0-9._-]*\.md)")
```

The leading-alnum class means literal placeholders such as `references/<file>.md`
(angle-bracketed) do not match, avoiding false positives from documentation-style
prose. For every captured basename `b`: if `b not in delivered[skill]`, append an
error.

### Error contract

```
templates/skills/<skill>/SKILL.md cites references/<b> but it will not ship to
this skill (no own references/<b> and no registered SHARED_REFERENCES fan-out);
add the skill as a consumer of the source in installer/registry.py
SHARED_REFERENCES, or provide templates/skills/<skill>/references/<b>.
```

Errors accumulate into the existing `errors` list and are raised together via
the existing `GenerationError` path — the reverse check adds messages, it does
not change control flow or introduce a new exception type.

## Boundaries

- Scan **only** `SKILL.md` bodies. Citations inside reference files or scripts
  are out of scope (a reference citing another reference is not a skill-install
  contract).
- No behavior change to generation output, manifests, installers, or the
  release-payload gate. This is a validation-only addition on the `--check` and
  build paths (both call `validate_skills`).
- No registry data change unless the current tree is found to contain a real
  dangling citation (see Risks / AC3).

## Affected files

- `.github/scripts/generate-skill-surfaces.py` — add the reverse closure check
  inside `validate_skills()` (and a small module-level `CITATION` pattern).
- `tests/test_generate.py` (or `tests/test_skills.py`) — add a reverse-direction
  test: a seeded citation without registration/own-copy fails; the collision and
  forward tests remain unchanged.
- Possibly `installer/registry.py` `SHARED_REFERENCES` — only if the current
  tree already has a dangling citation that closure should fix by registration.

## Contracts

- Input: `templates/skills/<name>/SKILL.md` bodies; `SHARED_REFERENCES`
  (source -> consumers); own `references/*.md` files at source.
- Output: `validate_skills()` returns metadata unchanged on success; raises
  `GenerationError` listing each dangling citation on failure. `make generate
  --check` exits nonzero on any dangling citation.
- No new env keys, CLI flags, or signatures. `validate_skills()` keeps its
  current signature and return type.

## Validation & error matrix

| Condition | Result |
|-----------|--------|
| Skill cites a basename delivered by registered fan-out | pass |
| Skill cites a basename it owns as `references/<b>.md` | pass |
| Skill cites `references/<b>.md`, neither owned nor fanned-out | error (fail generate) |
| Body contains placeholder `references/<file>.md` (angle brackets) | ignored (no match) |
| Generated shared reference (`skill-catalog.md`) cited by a registered consumer | pass (membership, not file presence) |

## Risks

- **R-1 (AC3 — current tree must pass):** The new gate may surface a real
  existing dangling citation. Mitigation: run the gate against the current tree
  during implementation; if it flags, resolve in scope by registering the
  missing consumer (if the reference is genuinely intended) or removing the dead
  citation (if the reference is not intended). If it surfaces a broad latent
  problem beyond a couple of citations, stop and reassess scope rather than
  mass-editing.
- **R-2 (false positives):** A code-block or example line could cite a
  `references/*.md` name that is intentionally illustrative. The strict pattern
  ignores angle-bracket placeholders; any real-basename example that is not
  delivered is, by definition, the dangling-citation case the gate targets. If a
  legitimate illustrative citation exists, the fix is to make it a placeholder or
  register it — both correct outcomes.
- **R-3 (coordination):** PRD notes `07-25-agent-artifact-kind` will later
  refactor the generator build/validate paths. That task is not active or
  in-progress, so there is no concurrent-edit conflict now; this gate lands
  first, as the PRD recommends.

## Rollback

Single-file revert of the `validate_skills()` addition plus the new test. No
data migration, no generated-artifact change, so rollback is a pure code revert
with no residual state.
