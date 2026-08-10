# Design: `scope=session` session-first entry for se-review-skills

Line citations verified 2026-08-09 against the current tree. The analyzer
citations from the PRD all still hold (`_select_paths` `:847`, unknown-skill
raise `:866`, `_deduplication_key` `:1063-1066`, `scope: str | None` `:1571`,
empty-inventory raise `:1606-1607`, scope stamp `:1614`, argparse choices
`:1927`). SKILL.md drifted since the PRD: `mode=` `:56`, `skill=` `:57`,
`scope=` `:60`, `installed-root=` `:66`, `sessions=` `:68`, `session=` `:70`,
observed-use step 6 `:156`, `mode=task` step 10 `:190`, `mode=apply` step 12
`:207`.

## Shape: post-inventory filter, prose-only analyzer usage

`scope=session` is implemented exactly as the settled evidence requires: the
skill invokes the analyzer **with `--scope` omitted** (typed `str | None`,
`skill_review.py:1571`) and no `--skill` selectors, obtains the full
deduplicated inventory, runs the observed-use confirmation pass, and
intersects afterwards. The bundled `skill_review.py` is **not modified**: no
`session` entry is added to the argparse choices (`:1927`), no payload field
changes. The four blocker decisions below are all expressible in prose plus
one additive reference change.

## Decision 1 — identity-unresolved outcome (blocker 1)

**Join rule: name narrows, provenance decides.** Session evidence records
carry no path or content hash (`references/session-evidence.md:78-93`), so
the normalized skill name is only a *candidate filter*, never the join by
itself — honoring the settled "never by name alone" discipline. The join
composes the existing provenance-mapping rules
(`references/session-evidence.md:95-100`): a confirmed invocation selects a
deduplicated inventory entry only when the name matches **and** the record's
provenance classification defensibly maps the invocation to that entry —
`current-canonical` (the session demonstrably used the source snapshot under
review) or `installed-drift` (the session used a mapped installed copy of
that entry). `historical-version` and `unknown` provenance never select,
even with a unique name match: a uniquely named current entry is not thereby
the historical or unknown-provenance skill the session invoked.

**Outcomes:**

- Name matches exactly one deduplicated entry and provenance is
  `current-canonical` or `installed-drift` for it → the confirmation selects
  that entry into the reviewed set.
- Name matches one or more entries but provenance cannot single one out —
  multiple distinct-content copies share the name, or the record's
  provenance is `historical-version` or `unknown` → the confirmation is
  **identity-unresolved**: counted in the session section with its redacted
  locator and the candidate entries listed by name and status, selected into
  the reviewed set as **zero** entries, `changeable` never asserted, no task
  routing. Rationale, recorded: `scope=session` promises "what this
  conversation actually used"; selecting all same-name copies would
  attribute findings to copies the session never exercised, and picking one
  without a defensible provenance mapping would be a guess. The stated
  escape is an explicit `skill=` selector run.
- Name matches zero entries → **absent-from-inventory**: a distinct outcome
  (coverage note naming the confirmed name and the inventory boundary),
  because the reader must be able to tell "present but unattributable" from
  "not discoverable at all".

## Decision 2 — privacy boundary vs report schema (blocker 2)

**Scoped reconciliation; both rules stay authoritative in their own domain.**
The privacy rule (`references/session-evidence.md:16-20`) governs
session-derived content: nothing sourced from a transcript may carry
machine-specific host paths into the report or a task. The mapped-copy path
evidence required by `references/report-schema.md:9-10` and promised by
`docs/SE_AI_COMMAND_PACK.md:305` is produced by the analyzer's filesystem
discovery of the current workspace (`observedPath`/`canonicalPath`,
`skill_review.py:1418-1422`) — it is not session-derived, appears under every
existing scope today, and continues unchanged under `scope=session`. Session
records contribute only redacted locators and turn/event ranges, exactly as
the observed-use pass does today.

**Report-schema scope:** `references/report-schema.md` is **in scope,
additively only** — it gains a short session-selection section describing the
new report block (confirmed set, identity-unresolved list with candidates,
absent-from-inventory coverage notes, and the boundary/scope distinction of
Decision 3). No existing schema line changes meaning.

## Decision 3 — analyzer scope stamp vs resolved scope (blocker 3)

With `--scope` omitted the preserved payload records
`"scope": scope or ("skill" if len(records) == 1 else "repo")`
(`skill_review.py:1614`) — almost always `repo`. That stamp is the **analyzer
inventory boundary** and is preserved verbatim (SKILL.md step 2 requires
preserving the JSON). The **skill-layer resolved review scope** is `session`
and is reported in the report header as two labelled facts, e.g. "resolved
review scope: session (post-inventory filter); analyzer inventory boundary:
repo (preserved payload)". SKILL.md's session section pins this distinction
so a reader of the preserved JSON is told why the two differ. Prose-only.

## Decision 4 — snapshot reproducibility (blocker 4)

**The recorded selection is the source of truth across the snapshot
boundary; the reviewed set is never re-derived from live session
inspection.** Two mechanisms, both prose/skill-layer:

- **Identity: the analyzer's deduplication key, verbatim.** The
  session-scoped report records each selected entry under exactly the key
  `_deduplication_key` produces (`skill_review.py:1063-1066`): owned entries
  by canonical root plus resolved canonical path, unowned entries by
  `(name, sha256)`. No weaker matching (name+hash for owned entries would
  alias identical same-name content across repositories or paths).
- **Binding: a selection digest sealed inside the report — no new
  argument.** The analyzer snapshot hashes the complete pre-filter inventory
  (`report-schema.md:130-133`), so two different session-derived subsets can
  share one snapshot ID. The session-scoped report therefore records a
  **session-selection block** — every selected entry listed under its
  deduplication key together with the retained evidence record(s) confirming
  it (the record-to-entry association lives in this report block; the
  retained record schema itself, `session-evidence.md:80-93`, is unchanged)
  — and a **selection digest** sealing it. Digest computation, one canonical
  encoding (Python semantics, runnable verbatim): build
  `payload = [{"key": [<deduplication key strings>], "records": [[<session locator>, <turns>], ...]}, ...]`
  with each entry's `records` sorted by
  `json.dumps(record, ensure_ascii=True)` and the entries sorted by
  `json.dumps(entry["key"], ensure_ascii=True)`; serialize with
  `json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))`;
  encode UTF-8; hash sha256, hex-encoded. `ensure_ascii=True` fixes string
  escaping; `sort_keys` plus the explicit list orderings fix the byte
  sequence completely. Fixed test vector (any conforming implementation
  must reproduce it): the two-entry payload
  `[{"key": ["canonical", "/repo", "/repo/templates/skills/se-review-skills/SKILL.md"], "records": [["project-a/session-0007", "12-18"]]}, {"key": ["unowned-content", "my-skill", "<64 zeros>"], "records": [["project-a/session-0007", "31-33"], ["project-a/session-0009", "4-9"]]}]`
  digests to
  `f868c5ca7f0ca263210a6fe787bc2b8adcdd4cb27c051221100e29c783264c27`.
  Acting on a
  session-scoped report already requires reading that report (finding IDs
  and selectors resolve against it; `snapshot=<id>` stays required,
  `SKILL.md:62`): the skill recomputes the digest from the report's own
  block and requires it to equal the stamped digest. A session-scoped report
  with a missing, corrupt, or non-matching block fails closed. The argument
  vocabulary (`SKILL.md:54-76`) is unchanged — the digest is report
  content, not a request key.

`mode=task` (step 10, `:190`) and `mode=apply` (step 12, `:207`) then run
the **unchanged** mutation-revalidation contracts exactly as they run for
session evidence in every existing scope (`report-schema.md:134-143` steps
1–6; `session-evidence.md:169-175`): each selected record's project
boundary, invocation evidence, provenance, causal class, current canonical
locator, and redaction must still hold, using the retained records and —
where a check requires it and the record's locator still resolves — the
session it names. Session scope neither adds to nor subtracts from those
checks; a record whose checks cannot be re-established is rejected as stale
rather than broadened, per the existing rule. What is explicitly excluded is
one thing only: *re-deriving the reviewed set by fresh session inspection*.
A later conversation acts on the recorded selection or not at all; new
session evidence means a new review run with a new report. This removes the
silent re-derivation failure mode and needs no reversible locator mapping,
which the PRD established does not exist (redacted locator
`session-evidence.md:80` vs ID-taking `session=` `SKILL.md:70`).

## Composition and error rules

- `scope=session sessions=off` is an argument error, stated in the arguments
  list (one demands session-derived discovery, the other forbids inspection).
- `scope=session` composes with `session=<id>` (bounds which sessions are
  inspected) and with `installed-root=`/`root=` (bounds the inventory the
  confirmations join against — widening or narrowing per the existing rules,
  `SKILL.md:66`, `:82`). It rejects combination with `skill=`/`family` (an
  explicit selector contradicts "derive the set from the session"); the error
  names both arguments.
- Zero confirmed invocations → honest empty result naming the session
  selection stage, with the standard coverage limits; never a fallback to
  repository-plus-installed discovery.
- The analyzer's `no skills found under bounded root or installed roots`
  raise (`:1606-1607`) remains reachable only with `installed=off` in a
  repository with no discoverable skills; the session section states that
  this failure belongs to the inventory stage, not the session stage.
- A confirmed skill outside the resolvable canonical source boundary stays
  reviewable evidence with `changeable=false` and no task routing, matching
  today's unresolved installed copies.

## Files changed

| File | Change |
| --- | --- |
| `templates/skills/se-review-skills/SKILL.md` | `session` added to the `scope=` line; session-selection workflow step (join rule, outcomes, boundary/scope distinction, empty-result rules, `sessions=off` and `skill=` conflicts); step 10/12 amendment for recorded-set revalidation |
| `templates/skills/se-review-skills/references/report-schema.md` | Additive session-selection section |
| `CHANGELOG.md` | Dated heading, patch bump |
| pack version (source of `manifest.json` `version`) | `0.68.0` → `0.68.1` (capability addition to an existing skill = patch, per settled convention) |
| `tests/test_skills.py` | New token-pin test class for the session section (pattern of `ReviewSkillsGotchaMandateTest`, `tests/test_skills.py:4077`) |
| Generated surfaces | `make generate` (`Makefile:16-17`) regenerates the committed Claude entrypoint and catalog surfaces from the canonical SKILL.md; the regenerated files are part of the commit. `make check` only *detects* drift via `generate-skill-surfaces.py --check` (`Makefile:50`) — it does not regenerate |

Explicitly unchanged: `templates/skills/se-review-skills/scripts/skill_review.py`,
`references/session-evidence.md` (its record shape and budgets already carry
everything Decisions 1–4 need), `docs/SE_AI_COMMAND_PACK.md:305` (its per-path
promise stays true under Decision 2).

## Test plan

Token-pin tests per the "Prose contracts: prove the pin can fail" procedure:
each pinned phrase is verified absent from the unedited target section before
the section gains it (grep against `git show HEAD:<file>` scoped to the
section), then asserted present via `skill_section("se-review-skills", ...)`.
Pinned behaviors: the post-inventory filter sentence; the
name-narrows/provenance-decides join rule and identity-unresolved outcome;
the resolved-scope vs inventory-boundary distinction; the selection digest;
the recorded-selection revalidation rule; the `sessions=off` conflict; the
no-fallback empty result; the report-schema session section. The pin proof
follows the runnable block in `quality-guidelines.md:129-152`: restore
*every* tested source file (SKILL.md and report-schema.md) from `HEAD`, run
the new test class, expect FAILED; restore the edits, expect OK. Release
gate: `make generate` first (commits the regenerated surfaces), then
`make check` validates no drift and checks the payload change against the
version bump and dated CHANGELOG heading.
