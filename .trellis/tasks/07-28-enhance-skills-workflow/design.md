# Design: a Gotchas mandate for tasks se-review-skills creates

Prose-only change: no new skill, no new argument, no registry change, no Python
change.

| File | Kind | Why |
|---|---|---|
| `templates/skills/se-review-skills/SKILL.md` | authored | D1, D2, D3 |
| `.../references/session-evidence.md` | authored | D1 in the guide itself |
| `docs/SE_AI_COMMAND_PACK.md` | authored | `### Skill-review workflow boundary` describes this skill |
| `tests/test_skills.py` | authored | the contract pins in D5 |
| `manifest.json`, `CHANGELOG.md` | authored | release payload gate, D4 |
| `generated/**`, `templates/skills/_shared/references/skill-catalog.md` | generated | `make generate` output |

## D1 — The mandate is an acceptance requirement on created tasks

`mode=task` already creates at most one planning task per affected skill and
snapshot (`SKILL.md` step 10). The change: when a task carries at least one
**gotcha-qualifying** observed-use finding, its body states as an acceptance
requirement that the touched SKILL.md gains or extends a `## Gotchas` section.

**"Gotcha-qualifying" is the existing gate, not a new one.**
`references/session-evidence.md`, *Gotchas and regression records*, already
restricts a gotcha to a recurring or high-consequence edge case whose evidence
can state all five parts — trigger, failure, prevention, recovery, regression
method. An earlier draft mandated the section for *every* observed-use task,
which would have forced a gotcha for evidence the governing reference says does
not qualify, and the two rules would have contradicted each other in the same
skill.

The mandate therefore reads: when the finding qualifies under that gate, the
task must carry the requirement; when it does not, the task is created without
it and says so. This adds the *obligation to carry a qualifying record into the
target*, not a new schema and not a broader eligibility rule.

Rejected alternative: broadening gotcha eligibility so every observed-use
finding qualifies. That would dilute the section into a changelog of one-off
transcript errors, which the reference explicitly guards against — "a transcript
error alone is never a finding".

Scope limit: source-only findings with no session evidence create tasks
unchanged. The mandate follows the evidence class, not the skill.

**The rule goes in the reference too.** `references/session-evidence.md` is the
required reading for the observed-use pass; `SKILL.md` step 6 sends the reader
there. A rule stated only in the skill body does not reach a reader who follows
the citation, and the two files would drift.

## D2 — Section placement in a touched SKILL.md

`## Gotchas` is not in `REQUIRED_SECTIONS` (`tests/test_skills.py`), and the
order test only asserts the five required headings appear in relative order, so
an extra heading is legal anywhere.

The mandate specifies **last in the skill body** so a required-section sequence
is never split by it. In this pack that resolves to "after `## Final report`",
but the target may live in another repository with a different section set, so
the rule is stated positionally rather than relative to a heading that may not
exist. A target whose canonical source has no recognizable section structure is
a routing gap the existing step 11 already handles — not a reason to guess a
location.

## D3 — Neighbor boundary, stated once and accurately

The `## When to use` handoff paragraph currently names `se-help`,
`sd-audit-repo`, and `sd-review-local`. Extend it with the two neighbors this
task's original PRD called out:

- `sd-retro` — incident and debugging retrospectives, and journal capture;
- `sd-review-learnings` — recurring PR-review feedback patterns; and
- `se-review-skills` — skill-instruction defects from source and observed use.

Both exist as installed skills and the descriptions match their frontmatter.
This is the paragraph that would have prevented the duplicate-skill proposal, so
it is part of the deliverable rather than a nicety.

## D4 — Release surface

`templates/**` and `generated/**` change, so the release payload gate applies:
bump `manifest.json` **before** `make generate`, because `rendered_help_catalog`
embeds the manifest version in the bundled catalog
(`.trellis/spec/backend/quality-guidelines.md`, section 6a).

That section is titled *Adding One Skill*, so read its two halves separately.
The bump-before-generate ordering is a property of the generator, not of adding
a skill: it applies to any change that bumps the version and regenerates, which
this one does. The four golden test literals in the same section really are
add-a-skill-only, and none of them changes here.

**Patch bump: `0.67.0` to `0.67.1`**, with a dated `## 0.67.1 - <date>`
CHANGELOG heading. The repository reserves minor bumps for adding a skill —
`0.67.0` added `se-brand-voice`, `0.65.0` added `se-propose-skills`, `0.40.0`
added `se-review-skills`. Capability additions to *existing* skills took patch
bumps even when substantial: `0.66.12` rolled the sub-agent dispatch protocol
across five skills and `0.66.13` shipped two new worker agents and a new
`RuntimeProfile` axis. This task adds no skill, so it is a patch.

No `installer/registry.py` change: `se-review-skills` is already registered in
the `improve` family with its runtime profile and shared-reference consumers.

## D5 — Test-side changes

New pins in `tests/test_skills.py` only, asserting the contract this task
introduces rather than restating prose. Each pins the shortest substring that
carries the contract, so ordinary rewording does not break the test but deleting
the contract does.

| Test | Substrings pinned (lowercased) | Guards | File |
|---|---|---|---|
| `test_created_tasks_require_a_gotchas_section_in_the_target` | ``` `## gotchas` section ```; `placed last in the target skill body`; `rather than after a named heading the target may not have` | D1 mandate, D2 placement | `SKILL.md` |
| `test_nonqualifying_evidence_creates_a_task_without_the_requirement` | `does not qualify`; `create the task without the requirement and say so`; `never widen the gate to manufacture a gotcha` | D1 negative case | `SKILL.md` |
| `test_session_evidence_guide_states_the_same_mandate` | `placed last in the skill body`; `never relax the five parts above to make a record qualify` | D1 in the guide | `references/session-evidence.md` |
| `test_neighbor_boundary_names_the_two_session_reading_skills` | ``` `sd-retro` owns incident and debugging retrospectives ```; ``` `sd-review-learnings` owns recurring pull-request review feedback ``` | D3 | `SKILL.md` |

The ``` `## gotchas` section ``` pin is satisfied by the backticked mention
inside the step 10 mandate. It is not an instruction to add a literal
`## Gotchas` heading to `se-review-skills` itself — the mandate applies to the
skills this one reviews. Pinning the backticked token plus the word `section`
is deliberate: the bare heading text `## Gotchas` is a prefix of the guide's own
`## Gotchas and regression records` heading, which is how the vacuous first
draft passed.

The reference pin uses the existing `normalized_resource(name, relative)` helper
(`tests/test_skills.py:107-110`), which whitespace-normalizes a skill-owned
reference, so a pin survives rewrapping but not deletion.

**Every pinned token was checked against the current unedited files and is
absent from all of them.** That check is not optional bookkeeping: an earlier
draft pinned `## Gotchas` against the *reference*, whose existing heading
`## Gotchas and regression records` (line 141) already contains that substring —
the assertion would have passed before any edit and could never have failed.

The check is a runnable procedure, not a promise. The subsection
*Prose contracts: prove the pin can fail* in
`.trellis/spec/backend/quality-guidelines.md` owns it: grep each token against the unedited file, then restore the source files from
`HEAD`, confirm the new tests report `FAILED`, restore the edits, and confirm
`OK`. Re-run it for any token substituted later.

No change to `tests/test_generate.py`: `EXPECTED_SHARED_SOURCES` tracks
shared-reference consumers, and this task adds none.
