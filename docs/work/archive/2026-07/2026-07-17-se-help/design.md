# Implement se-help Design

## Overview

Add `se-help` as the pack's read-only discovery, explanation, and routing
surface. It belongs to Operate because it helps users operate the pack itself,
but it may recommend skills from every family.

The design separates stable routing behavior from catalog data. The canonical
`SKILL.md` defines how to list, explain, compare, recommend, and onboard. A
generated bundled reference supplies the exact released families and skills,
while a small authored examples reference demonstrates common prompts and
workflow handoffs. This avoids copying the growing catalog into the skill body
or relying on roadmap documentation that may describe unshipped work.

## Proposal

Create `templates/skills/se-help/SKILL.md` with a natural-language-first
interface and optional arguments:

- `mode=list|explain|compare|recommend|examples|tour` — infer from an
  unambiguous request; otherwise default to `recommend` when a goal is given
  and `tour` when no goal is given.
- `family=` — optional canonical family name for list/examples filtering.
- `skill=` — one skill for explain mode.
- `skills=` — two or more comma-separated names for compare mode.
- `goal=` — natural-language outcome for recommendation mode; use the user's
  request directly when already present.
- `detail=compact|standard` — concise answer or expanded boundaries/examples.

The skill should accept ordinary questions without requiring these keys. When
explicit key/value arguments are used, retain the pack-wide unknown-argument
stop rule.

## Shared SD/SE Help Experience

The two packs should expose comparable help behavior even though SD ships
project-local commands and SE ships user-scoped skills. Use one stable response
envelope:

1. pack identity plus bundled catalog version and availability basis;
2. direct answer or recommendation;
3. fit rationale or comparison rule;
4. required context and prerequisites;
5. expected output or handoff artifact;
6. meaningful side effects, mutation boundary, and important non-goals;
7. related skills, closest alternatives, or lifecycle neighbors; and
8. a copy-ready platform-native invocation for a separate next request.

Apply the envelope by mode:

- **list/tour** - identity and version, canonical families, outcome-oriented
  "I want to..." routes, availability labels, then representative examples;
- **explain** - availability, purpose and trigger, required context and
  prerequisites, expected artifact, boundaries and side effects, adjacent
  skills, then two copy-ready SE-native invocations;
- **compare** - availability plus a compact matrix for outcome, input, output,
  time horizon, prerequisites, and mutation boundary; finish with a selection
  rule and one next invocation;
- **recommend** - smallest-fit choice, why it fits, one assumption or at most
  one decisive question, required context, expected output, closest material
  alternative, and one next invocation;
- **examples** - task-oriented examples grouped by family or outcome, using the
  same invocation conventions.

`detail=compact` may collapse low-value or inapplicable fields but must not
change their meaning. `detail=standard` retains the full applicable shape.
SE invocations use the current host's skill form, such as `$se-digest` when
supported, or a natural-language request naming the skill. Never emit SD slash
commands or imply that SE has project-local command adapters.

Use this workflow:

1. Resolve the requested mode and normalize family/skill names. Accept a missing
   `se-` prefix and an obvious minor misspelling only when exactly one catalog
   match exists; otherwise show the closest valid choices.
2. Read `references/skill-catalog.md` for canonical family order, bundled
   catalog version, skill names, family membership, and frontmatter
   descriptions. Read `references/examples.md` only for examples, onboarding,
   or workflow routing. When the installed manifest or status information is
   readable, compare its version with the catalog. On mismatch, report both
   versions and point to `python3 install.py status --user` plus the documented
   update flow. When metadata is unavailable, identify only the catalog version
   and continue.
3. Reconcile the bundled catalog with the host's current skill/capability list
   when that list is available:
   - **available now** — exposed in the current session;
   - **included in the installed pack but not discoverable now** - present in
     the installed/bundled catalog but not exposed by the current host,
     possibly requiring installation, refresh, or session reload;
   - **source/package-local only** - use only if canonical registry metadata
     explicitly marks a capability that is intentionally not installed;
   - **external** — exposed by the host but not owned by this pack;
   - **unknown** — present in neither source.
   Never use Trellis roadmap tasks to claim availability.
4. For `list`, show the six families in canonical order and only the requested
   level of skill detail. Clearly label availability instead of dumping host
   skills into the SE catalog.
5. For `explain`, report the skill's trigger/outcome, required context,
   prerequisites, expected artifact, meaningful side effects and mutation
   boundary, important non-goals, adjacent/delegated skills, and two copy-ready
   platform-native invocations. Inspect the available canonical `SKILL.md`
   when the runtime exposes it; otherwise state that the explanation is limited
   to catalog metadata and curated examples.
6. For `compare`, use a compact matrix covering intended outcome, input,
   output, depth/time horizon, mutation boundary, and distinguishing signal.
   End with a concrete selection rule.
7. For `recommend`, extract the user's desired outcome, supplied material,
   desired artifact, recency/depth, and requested mutation. Select the one
   smallest-fit available skill. Ask one question only when the answer changes
   the route; otherwise state an assumption.
8. Recommend a workflow chain only when stages produce distinct artifacts.
   Name each stage and its handoff, cap the default chain at three skills, and
   explain why one skill is insufficient.
9. End recommendations with a copy-ready platform-native invocation using the
   user's real context. Do not offer or execute the target skill in the same
   help request; the user must issue a separate explicit request.

Generate `templates/skills/_shared/references/skill-catalog.md` from the same
family metadata, `SKILL_NAMES`, canonical frontmatter, and manifest version used
by the grouped README catalog. Register it as a shared reference consumed only
by `se-help`. The generated file should include a clear generated-file marker
and deterministic ordering. It must not include planned tasks or third-party
skills.

Create `templates/skills/se-help/references/examples.md` as a concise authored
resource with one representative prompt per family, common comparison pairs,
new-user tour examples, and a few cross-stage workflows. Validate every named
SE skill against the registry so examples cannot retain removed or renamed
skills.

## Boundaries And Non-Goals

- Do not execute, install, update, enable, or remove a skill.
- Do not combine help and execution merely because the initial request included
  enough context to run the recommended skill.
- Do not treat a bundled skill as currently callable when the host does not
  expose it; explain likely refresh/reload needs without claiming their cause.
- Do not present roadmap tasks, repository development commands, installer
  lifecycle actions, or third-party host skills as shipped SE skills.
- Do not recommend multiple skills merely to showcase the pack. One
  smallest-fit skill is the default.
- Do not maintain a second manual family/skill catalog in `SKILL.md`, README
  prose, or the examples file.
- Do not build a shell, TUI, fuzzy-search engine, telemetry system, or persistent
  preference store.
- Do not expose hidden reasoning. A brief user-facing fit explanation is enough.

## Affected Files

- `templates/skills/se-help/SKILL.md` — canonical help workflow.
- `templates/skills/se-help/references/examples.md` — curated examples and
  workflow patterns.
- `templates/skills/_shared/references/skill-catalog.md` — generated released
  catalog consumed by `se-help`.
- `installer/registry.py` — Operate family registration and shared-reference
  fan-out.
- `.github/scripts/generate-skill-surfaces.py` — deterministic catalog-reference
  rendering and drift/write handling alongside manifest and README generation.
- `manifest.json` — generated skill/reference platform rows and release version.
- `tests/test_skills.py` — help modes, availability labels, routing boundaries,
  examples, and no-execution pins.
- `tests/test_generate.py` — generated help-catalog content, ordering, drift,
  escaping, and test-sandbox isolation.
- `README.md`, `docs/SE_AI_COMMAND_PACK.md`, and `CHANGELOG.md`.

No platform-specific UI metadata or connector is required. The canonical
skill remains framework-neutral and uses whatever session capability inventory
the host makes available.

## Risks And Edge Cases

- The bundled catalog and current host inventory can disagree after an install
  or update. Report both observations rather than guessing whether a reload,
  failed install, or host limitation caused the mismatch.
- Bundled catalog, installed receipt, and source-checkout versions can disagree.
  Report only values actually observed, keep help usable when any optional
  source is absent, and route remediation through the native status/update
  commands.
- Frontmatter descriptions explain triggers but may not contain detailed input
  and boundary information. Load the target skill when possible and disclose a
  metadata-only explanation when it is not.
- A user may name an external skill beginning with `se-`. Ownership comes from
  the bundled catalog, not the prefix alone.
- Aliases and misspellings can route to the wrong workflow. Auto-correct only a
  unique match and keep ambiguous suggestions non-executing.
- Generated Markdown must escape table delimiters and normalize frontmatter
  whitespace without changing its meaning.
- Adding help-catalog generation to the existing generator increases the risk
  of partial writes. Compute and validate manifest, README, and help catalog
  before replacing any committed surface.
- Sandbox generator tests must patch the help-catalog destination just as they
  patch manifest and README paths; tests must never modify the real repository.
- Examples can become stale even when the catalog is generated. Pin all named
  SE skills and family headings in tests.
- Overlong lists reduce usefulness. Default to compact grouped output and
  provide detail only for a selected family or skill.

## Validation

- Pin all six families in canonical order and exact registry-derived skill
  membership in the generated reference.
- Pin the bundled pack version and generated-file marker.
- Pin catalog/installed-version matches, mismatches, and missing optional
  metadata. Mismatches must name the native status/update path without guessing
  the cause.
- Pin list, explain, compare, recommend, examples, and tour modes; natural
  language must work without exact argument syntax.
- Pin the four core availability labels, the conditional
  `source/package-local only` label, and ensure planned/external skills are
  not represented as bundled skills.
- Pin smallest-fit routing, one-question maximum, three-stage default chain cap,
  explicit handoff artifacts, and no silent execution.
- Pin the stable response field order for every mode, compact-field elision,
  standard detail, and SE-native invocation examples. No example may use an SD
  slash command.
- Pin unique alias/misspelling handling plus an ambiguous and unknown case.
- Pin every SE skill named by `examples.md` against `SKILL_NAMES`.
- Test generator check/write behavior in a temporary destination, including
  frontmatter containing Markdown-sensitive characters.
- Manually exercise “what can this pack do?”, family filtering, explaining an
  unavailable bundled skill, comparing `se-brief` with `se-digest`, choosing a
  skill from a vague goal, recommending a capture-to-author workflow, and a
  bundled-versus-installed version mismatch.
- Run `make generate`, focused generator/skill tests, `make check`, and
  `git diff --check`.
