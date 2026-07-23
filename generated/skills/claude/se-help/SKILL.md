---
name: se-help
description: Use when the user wants to discover, compare, or choose SE skills and receive a justified recommendation with a copy-ready prompt without executing another workflow.
model: haiku
effort: low
---

# SE Help

Discover and operate the SE skill pack without executing another skill. Use the
generated bundled catalog as the ownership source, reconcile it with the
current session when capability inventory is available, and recommend the one
smallest-fit workflow for the user's outcome.

## When to use

Use this skill to list skill families or bundled skills, explain a skill,
compare adjacent skills, recommend a skill or short workflow, show examples,
or give a new-user tour. Do not use roadmap tasks, documentation mentions, an
`se-` prefix, or third-party capabilities as proof that a skill is bundled or
available now.

This skill is strictly read-only. A help request may recommend an invocation,
but it must never execute, install, update, enable, remove, or otherwise invoke
the recommended workflow. Execution requires a separate explicit request.

## Arguments

Natural-language requests are preferred. These optional keys make a request
more precise:

- `mode=list|explain|compare|recommend|examples|tour`
- `family=<family>` for list or examples filtering
- `skill=<name>` for one explanation
- `skills=<name,name,...>` for comparison
- `goal=<desired outcome>` for recommendation
- `detail=compact|standard`

Infer an unambiguous mode. With a goal, default to `recommend`; without a goal,
default to `tour`. Unknown argument names are an error: stop and identify the
unsupported names without continuing.

Accept a missing `se-` prefix, a common term, or a minor misspelling only when
it produces exactly one catalog match. Otherwise show the closest valid
choices and keep the request non-executing.

## Workflow

1. Read `references/skill-catalog.md` for the bundled catalog version,
   canonical family order, family outcomes, skill ownership, family membership,
   and frontmatter descriptions. Read `references/examples.md` only for
   examples, tours, comparisons, and workflow handoffs.
2. When an install root is observable, read its
   `.se-ai-command-pack/manifest.json` receipt and compare the installed pack
   version with the bundled catalog version. On mismatch, report both observed
   versions and point to `python3 install.py status --user` plus the documented
   update flow. Do not guess whether installation, refresh, host discovery, or
   session reload caused the mismatch. Missing optional metadata does not make
   help fail.
3. When the host exposes a current capability inventory, reconcile catalog
   ownership and current discovery using these exact labels:
   - **available now** - bundled and exposed in this session;
   - **included in the installed pack but not discoverable now** - bundled but
     not exposed by the current host;
   - **source/package-local only** - use only when canonical registry metadata
     explicitly marks the capability as intentionally not installed;
   - **external** - exposed by the host but not owned by this pack; and
   - **unknown** - present in neither the bundled catalog nor current inventory.
4. Resolve the mode:
   - `list`: show all six families in canonical order, or one filtered family,
     with compact availability labels.
   - `explain`: show purpose, trigger, prerequisites, inputs, expected output,
     meaningful side effects, non-goals, adjacent skills, and examples. Inspect
     the canonical skill body when available; otherwise disclose that the
     explanation is limited to catalog metadata and curated examples.
   - `compare`: use one matrix for outcome, input, output, depth or time horizon,
     prerequisites, mutation boundary, and distinguishing signal. End with a
     concrete selection rule.
   - `recommend`: extract the outcome, supplied material, desired artifact,
     recency or depth, and requested mutation. Choose the smallest-fit available
     skill and explain why. Ask at most one clarifying question, and only when
     its answer would change the route.
   - `examples`: show task-oriented prompts from the requested family or
     outcome without claiming empty families have bundled skills.
   - `tour`: introduce the families, show common "I want to..." routes, explain
     availability, and finish with one useful starter prompt.
5. Recommend one skill by default. Use a chain only when each stage produces a
   distinct handoff artifact and one skill cannot own the full outcome. Keep the
   default chain to at most three skills, name every handoff, and challenge any
   stage that merely showcases the pack.
6. Finish with one copy-ready platform-native invocation that uses the user's
   real context. Where a host supports direct skill notation, use forms such as
   `$se-digest`; otherwise use a natural-language request naming the skill.

## Safety rules

- Remain read-only and never execute another skill in the same help request.
- Treat the generated catalog as bundled ownership, not proof of current
  availability. Treat the current inventory as availability, not pack
  ownership.
- Do not present planned, external, unknown, or source-only capabilities as
  installed skills.
- Do not install, refresh, update, enable, remove, message, publish, schedule,
  or mutate an external system.
- Do not expose hidden reasoning. Give only a brief fit explanation and the
  observable selection rule.
- Prefer one smallest-fit skill. Do not create a multi-skill chain unless the
  handoff artifacts make the stages independently useful.
- Keep SE invocations on the user-scoped skill surface. Do not emit
  project-local delivery commands or imply that family names are command
  namespaces.

## Final report

Use the applicable fields below in this order. `detail=compact` may collapse
empty or low-value fields, but it must preserve their meaning. Every successful
response ends with the next invocation; errors instead name the unsupported or
ambiguous input and the valid choices.

- **Pack and availability**: pack identity, bundled catalog version, observed
  installed pack version when readable, and the availability basis.
- **Answer**: the requested list, explanation, comparison, recommendation,
  examples, or tour.
- **Why it fits**: the public selection rule, material assumption, or
  distinguishing signal.
- **Required context**: inputs, prerequisites, and any one decisive missing
  item.
- **Expected output**: the artifact or handoff the selected workflow produces.
- **Side effects and boundaries**: meaningful mutation behavior, read-only
  status, and important non-goals.
- **Related skills**: closest alternative, adjacent skills, or lifecycle
  neighbors when material.
- **Next invocation**: one copy-ready platform-native invocation for a separate
  request; do not execute it.
