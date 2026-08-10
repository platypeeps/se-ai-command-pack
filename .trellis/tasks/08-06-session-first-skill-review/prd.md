# Add `scope=session` session-first entry to se-review-skills

## Goal

Let `se-review-skills` derive its reviewed set from the skills a conversation
actually invoked, instead of only supplementing an already-selected set with
observed-use evidence. Today the reviewed set comes from a skill selector or
from repository plus installed roots; there is no way to say "review whatever
this conversation actually used."

## Status: design recorded

The four open blockers below each have a recorded decision in this task's
`design.md` (Decisions 1–4, with source evidence and current line numbers —
the SKILL.md citations below drifted; `design.md` carries the verified 
current map). The file scope is stated there: SKILL.md and
`references/report-schema.md` (additive) change; the bundled
`skill_review.py` and `references/session-evidence.md` do not. `implement.md`
carries the ordered checklist including the pre-edit pin verification.

## History

This was split out of `07-28-enhance-skills-workflow` after **four rounds** of
the planning adversarial-review contract. Every round found blocking defects,
all of them in this half; the Gotchas half of that task was stable from round 2
and shipped separately. Three of the round-4 blockers were defects introduced by
round-3 remediations, which is why this needs a fresh planning pass rather than
one more remediation round.

Do not start implementation from the notes below. They are **the starting
evidence for re-planning**, not a design. The core finding is that
`scope=session` is not a prose tweak: it reaches into the report schema, the
bundled analyzer's payload contract, the session privacy boundary, snapshot
replay, and `mode=apply`.

## What was settled

Verified against source across rounds 1-4. Carry these forward rather than
rediscovering them:

- **The selector cannot be expressed through the analyzer's interface.**
  `_select_paths` (`templates/skills/se-review-skills/scripts/skill_review.py:847`)
  matches every `--skill` against *repository* discovery and raises
  `unknown skill in bounded scope` (`:866`) for a name it does not find;
  installed discovery is never consulted for a selector. With no selector, the
  analyzer selects everything. So neither "name the session's skills" nor "name
  none of them" works.
- **Therefore `scope=session` must be a post-inventory filter**: invoke the
  analyzer with `--scope` omitted (typed `str | None`, `:1571`), run observed-use
  confirmation separately, intersect. `--scope`'s argparse choices are
  `("skill","family","repo","package","all")` (`:1927`); adding `session` to them
  is a Python change the split-off planning tried to avoid.
- **`scope=session` with `sessions=off` is an argument error** — one demands
  session-derived discovery, the other forbids session inspection.
- **The join must not be by bare name.** `SKILL.md` step 3 requires deduplicating
  unowned copies by "normalized skill name and content hash match, never by name
  alone", and `_deduplication_key` (`:1063-1066`) keys owned entries by canonical
  root plus path and unowned entries by `(name, sha256)`.
- **`installed-root=` replaces the manifest-derived roots** (`SKILL.md:57-58`,
  `:84`), so it can *widen* what is resolvable. Any composition model asserting
  "every selector only narrows" is wrong.
- **`skill=` accepts a name or a path** (`SKILL.md:49`), and the analyzer honors
  path candidates (`skill_review.py:860`).
- **Version convention**: a capability addition to an existing skill is a patch
  bump. Minor is reserved for adding a skill.

## The four open blockers

Each verified against source; none has an accepted resolution.

1. **Identity-unresolved has no defined outcome.** Confirmation requires only
   strong activation or corroborated use (`references/session-evidence.md:64`),
   neither of which guarantees a path, hash, or canonical root, and the retained
   minimal evidence record (`:78-93`) has none of those fields. A confirmed
   invocation that *is* in the inventory but cannot be joined to a specific entry
   needs its own outcome — counted, unreviewed, `changeable=false`, no routing —
   distinct from "absent from the inventory".

2. **The privacy boundary and the report schema conflict.**
   `references/session-evidence.md:16-20` forbids persisting machine-specific
   host paths in the report or a Trellis task. But `references/report-schema.md:9-10`
   requires "For every mapped copy, show its path and `canonical-match` or
   `installed-drift` status", the analyzer emits absolute `observedPath`,
   `observedHash`, `canonicalPath`, and `canonicalHash`
   (`skill_review.py:1418-1422`), and `docs/SE_AI_COMMAND_PACK.md:305` promises
   per-path evidence. Resolving this means deciding the authoritative rule and
   reconciling every consumer — which puts `references/report-schema.md` in
   scope, a file the split-off task deliberately did not touch.

3. **The analyzer stamps a conflicting scope.** With `--scope` omitted the
   payload records `"scope": scope or ("skill" if len(records) == 1 else "repo")`
   (`skill_review.py:1614`), so the preserved JSON says `repo` while the skill
   would report `scope=session` — and `SKILL.md` step 2 requires preserving that
   JSON. The plan must separate "analyzer inventory boundary" from "skill-layer
   resolved review scope", and pin the distinction.

4. **A session-derived set is not reproducible across a snapshot boundary.**
   `mode=task` (step 10) and `mode=apply` (step 12) both "revalidate selected
   session evidence", but a later run executes in a *different* conversation, so
   it would silently re-derive a different reviewed set under the same snapshot
   ID — the worst failure mode, because report and tasks would disagree while
   both look valid. Replaying the recorded locator does not work either: the
   evidence record stores a "redacted stable locator" (`session-evidence.md:80`)
   while `session=` takes an ID (`SKILL.md:63`), with no reversible mapping.
   Either define a privacy-safe locator the session reader demonstrably accepts
   as `session=<id>`, or require the acting request to resupply the original IDs.

## Requirements

- Resolve all four open blockers with an explicit recorded decision each, before
  any implementation step is written.
- Decide and record whether the feature stays prose-only. If resolving blockers
  2 or 3 requires touching `references/report-schema.md` or the bundled
  `skill_review.py`, that is a legitimate outcome — but it changes the release
  surface and the test surface, and must be stated rather than absorbed.
- Preserve the existing invocation-confirmation standard, session budgets,
  privacy boundary, and causal-classification table. Mention-only matches stay
  rejected; nothing is relaxed to make the selector produce results.
- Zero confirmed invocations is an honest empty result with a stated coverage
  limit, never a silent fallback to repository-plus-installed discovery. Note the
  one boundary: an empty *combined* inventory makes the analyzer raise
  `no skills found under bounded root or installed roots` (`:1606-1607`), which
  under `scope=session` is reachable only with `installed=off` in a repository
  with no discoverable skills.
- A skill confirmed in-session but outside the resolvable canonical source
  boundary stays reviewable evidence with `changeable=false` and no task routing,
  exactly as an unresolved installed copy does today.
- An empty result names the stage that produced it, and names a selector only
  when a selector caused it.

## Acceptance Criteria

- [ ] Each of the four open blockers has a recorded decision with the source
      evidence it rests on.
- [ ] The design states which files change, including whether
      `references/report-schema.md` and the bundled `skill_review.py` are in
      scope.
- [ ] The planning adversarial review completes with no unresolved blocking
      concern.
- [ ] `make check` passes, with focused coverage for each observable behavior
      change, and every pinned token verified absent from the unedited file so
      each assertion can fail.
- [ ] The release payload gate passes with the appropriate patch bump and a
      dated CHANGELOG heading.

## Out of scope

- The Gotchas mandate — shipped by `07-28-enhance-skills-workflow`.
- A separate `se-enhance-skills` skill.
- Automated or scheduled invocation.

## Notes

- Planning depth: **Complex — needs `design.md` and `implement.md` before `task.py start`.** A new `scope=session` mode introduces a new evidence source for the reviewed set, so it needs its selector precedence, its behaviour when no session evidence exists, and its interaction with the existing repository/installed-roots selection all specified before implementation.
