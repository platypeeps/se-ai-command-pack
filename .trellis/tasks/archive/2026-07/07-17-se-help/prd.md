# Implement se-help

## Goal

Make the pack self-discovering by helping a user understand its families and
skills, choose the smallest suitable workflow, and start it with a useful,
copy-ready prompt.

## Background

As the pack grows, a grouped README improves browsing but does not solve
in-session discovery. Users need to ask outcome-oriented questions such as
“what should I use for this?”, compare overlapping skills, see realistic
examples, and understand what is actually available in their current install.
A static hand-maintained help prompt would drift from the registry and make
that problem worse.

## Requirements

- Add `se-help` as an Operate-family skill covering pack discovery, onboarding,
  skill explanation, comparison, and intent-to-skill routing.
- Support these modes without requiring exact argument syntax:
  - list families with concise outcome-oriented descriptions;
  - list available skills, optionally filtered by family or user goal;
  - explain one skill's purpose, prerequisites, inputs, output, meaningful side
    effects, boundaries, adjacent skills, and useful examples;
  - compare two or more skills and recommend when to use each;
  - recommend a single skill or short workflow chain from a natural-language goal;
  - provide copy-ready starter prompts that use the user's supplied context;
  - offer a short onboarding tour for a new user.
- Generate the authoritative help catalog from registry family metadata and
  canonical skill frontmatter. Do not maintain a second manual list of skills
  or descriptions inside `se-help`.
- Distinguish skills available in the current pack/session from planned,
  unknown, unavailable, or externally provided skills. Never claim a skill is
  installed merely because it is mentioned in documentation.
- Report the bundled catalog version and, when installed receipt metadata is
  readable, the installed pack version. Disclose a mismatch and point to the
  pack's native status/update path instead of guessing whether installation,
  refresh, or session reload caused it. Missing optional metadata must not make
  help fail.
- For recommendations, state why the selected skill fits, identify the closest
  alternative when ambiguity is material, and ask at most one clarifying
  question only when the answer would change the route.
- Prefer one smallest-fit skill. Recommend a workflow chain only when the
  outcome genuinely crosses stages, and show the handoff between each stage.
- Keep examples task-oriented and realistic, including short prompts for every
  family and representative multi-skill workflows.
- Remain strictly read-only: explaining or recommending another skill must not
  invoke it, mutate external systems, or broaden authority in the same help
  request. End with an exact platform-native invocation and require a separate
  explicit request before execution.
- Handle aliases, common terminology, and minor misspellings when the intended
  skill is unambiguous; surface ambiguity rather than inventing a match.
- Keep the canonical `SKILL.md` concise through progressive disclosure. Put the
  generated catalog and extended examples in directly referenced resources.

## Shared Help Experience Contract

`se-help` and `sd-help` should feel like members of the same product family
without erasing their different delivery models. Every non-error response should
use the applicable parts of this stable envelope:

1. pack identity, bundled catalog version, and installed/current availability
   basis;
2. the direct answer, recommendation, or comparison;
3. why it fits and the selection rule used;
4. required context and prerequisites;
5. expected output or handoff artifact;
6. meaningful side effects, mutation boundary, and important non-goals;
7. related skills, closest alternatives, or lifecycle neighbors; and
8. a copy-ready platform-native invocation for the next separate request.

Progressive disclosure controls how many fields are shown, not what the fields
mean. Compact answers may collapse empty or low-value fields, while standard
explanations and comparisons keep the ordering stable. SE examples must use its
user-scoped skill surface, such as `$se-digest` where supported or an ordinary
natural-language skill request; they must not copy SD's project-local slash
commands or command adapters.

## Acceptance Criteria

- [ ] A user can list all six families in canonical order and get a concise,
      outcome-oriented explanation of each.
- [ ] The listed skills, family assignments, names, and descriptions are derived
      from canonical pack sources and drift checks fail when help is stale.
- [ ] A user can ask “which skill should I use?” in natural language and receive
      a justified smallest-fit recommendation plus a copy-ready prompt.
- [ ] Explain and compare modes expose triggers, required context, outputs,
      prerequisites, meaningful side effects, important non-goals, and
      adjacent-skill boundaries in the shared response shape.
- [ ] Help distinguishes installed/available skills from documented plans and
      does not fabricate unavailable capabilities.
- [ ] Help reports bundled and installed versions when available, handles
      missing metadata gracefully, and directs mismatches to
      `python3 install.py status --user` and the documented update flow.
- [ ] Workflow recommendations name each stage, explain the handoff artifact,
      and avoid chains when one skill is sufficient.
- [ ] Examples cover every family, new-user onboarding, ambiguous intent,
      unknown skills, aliases/misspellings, and common overlap pairs.
- [ ] The skill never executes a recommended workflow or external mutation
      in the help request; every executable next step requires a separate
      explicit request.
- [ ] List, explain, compare, recommend, examples, and tour responses follow the
      shared SD/SE envelope and end with SE-native rather than SD command syntax.
- [ ] Skill validation, generated catalog/reference surfaces, README/operator
      documentation, release metadata, and full pack checks pass.

## Out of Scope

- A command shell, interactive TUI, fuzzy-search application, telemetry system,
  or persistent user-profile implementation.
- Installing, updating, enabling, or executing skills on the user's behalf.
- Listing unrelated host-platform or third-party skills as if they belong to
  the SE pack.
