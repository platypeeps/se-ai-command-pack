# SE AI Command Pack — Operator Guide

The maintainer-facing reference for the pack's internals: manifest schema,
receipts, checklists for adding skills and platforms, and the release
process. User-facing install/update/remove instructions live in the
[README](../README.md). This document is repo-only; it is not installed.

## Layout

| Path | Role |
|---|---|
| `templates/skills/<name>/` | Canonical skill definitions (`SKILL.md` + optional `references/*.md`). The only place skills are edited. |
| `templates/skills/_shared/references/` | Shared references fanned into consuming skills' `references/` dirs by the generator. |
| `templates/skills/_shared/references/skill-catalog.md` | Generated bundled family/skill catalog fanned into `se-help`; never hand-edit. |
| `templates/skills/_shared/references/personal-profile-contract.md` | Portable `se-personal-profile/v1` schema and privacy/consumer contract fanned into profile workflows. |
| `installer/registry.py` | Source of truth: `PLATFORM_REGISTRY`, ordered `SKILLS` family metadata, derived `SKILL_NAMES`, `SHARED_REFERENCES`, install modes, receipt paths. |
| `manifest.json` | Generated install spec (header preserved, `files` rows derived). Never hand-edit rows. |
| `install.py` + `installer/` | The user-scope installer. |
| `README.md` | User guide with a marker-bounded, family-grouped skill catalog generated from registry metadata and canonical frontmatter. |
| `.github/scripts/generate-skill-surfaces.py` | Validates skills and atomically coordinates the manifest, README catalog, and bundled help catalog; `--check` gates drift in all three. |
| `.github/scripts/check-release-payload.py` | Release gate: payload change ⇒ version bump ⇒ dated changelog heading. |
| `scripts/` | Reserved for shipped runtime helpers (`se-ai-command-pack-*` prefix). Empty in v0.1. |

## Product and development surfaces

- **Shipped skills** are the `se-*` entries under `templates/skills/`. They are
  grouped by primary outcome family in the README but retain flat canonical and
  installed paths. The current bundle includes report-first technical editing
  with `se-technical-editor` and audience-calibrated explanation with
  `se-explain`, plus traceable feedback synthesis with `se-feedback`.
- **Pack lifecycle commands** are the `install.py` install, status, refresh,
  update, and remove operations. They manage the pack; they are not skills.
- **Repo-local SD and Trellis helpers** support development in this checkout.
  They are not registered product skills and are not installed by this pack.
- **Per-platform command adapters** are a possible future thin invocation
  surface. None are currently shipped, and family names do not create nested
  command namespaces.

### Decision workflow boundary

`se-decide` owns a recommendation between known options using explicit
criteria, constraints, evidence, tradeoffs, confidence, and reversibility.
Candidate discovery stays with `se-scan`, open evidence gathering with
`se-research`, supplied-corpus synthesis with `se-digest`, neutral comparison
with the separately delivered `se-compare`, extreme purpose-bound compression
with `se-distill`, single-subject rubric assessment with `se-evaluate`, and
post-decision execution
planning with `se-plan`. The skill remains read-only; acting on a recommendation
always requires a separate request and the relevant action capability.

### Project-status workflow boundary

`se-status` owns objective-oriented reporting across supplied or connected
project sources. It separates completed outcomes from activity, current state,
blockers, risks, recorded decisions, asks, and next actions while naming stale,
unavailable, or contradictory inputs. Topic recency stays with `se-brief`,
supplied-corpus synthesis with `se-digest`, recommendations with `se-decide`,
and external baseline monitoring with `se-monitor`. The skill is read-only: it
does not update project systems or send the resulting report.

### Claim-audit workflow boundary

`se-fact-check` starts from supplied claims or an artifact and returns a
claim-by-claim ledger using exactly five verdicts: supported, partially
supported, unverified, contradicted, or outdated. Open-ended evidence questions
stay with `se-research`, while multi-document synthesis stays with `se-digest`
unless the request explicitly asks to audit claims. Both `se-research` and
`se-fact-check` consume the shared `verification-protocol.md`; the canonical
source lives under `_shared/references/` while installed paths remain local to
each skill. The audit is read-only and offers only minimal corrected wording.

### Pack-help workflow boundary

`se-help` owns pack discovery, onboarding, explanation, comparison, and
intent-to-skill routing. Its installed `references/skill-catalog.md` is generated
from registry family metadata, the manifest version, and canonical skill
frontmatter; roadmap tasks and third-party host capabilities are never catalog
inputs. Bundled ownership and current-session availability remain separate
observations. Help reports observed version mismatches through
`python3 install.py status --user` and the documented update flow without
guessing their cause. It remains read-only and ends with a copy-ready
user-scoped invocation that requires a separate request before execution.

### Personal-profile workflow boundary

`se-profile` is the sole mutation owner for a user-owned
`se-personal-profile/v1` Markdown artifact. It uses explicit current input and
bounded user-authorized sources, preserves stable assertion/evidence IDs and
unknown user content, previews every mutation, and verifies destination writes
by semantic read-back. Inferred assertions always begin proposed, observed
assertions remain approval-gated, and sensitive or protected traits are never
inferred. Corrections preserve superseded evidence; forgetting reports the
verified deletion boundary without claiming erasure from connector history or
backups.

The public pack stores no profile, locator, source inventory, identity,
credential, vault/workspace/channel name, or destination configuration.
Obsidian is the preferred user-selected destination, with an explicit
user-selected Notion fallback; no connector implementation or silent dual-copy
sync is included. Audience overlays store sparse differences and cannot weaken
boundaries or visibility. Review cadence is a preference only, not a scheduler
or authorization for recurring ingestion. Other skills are read-only consumers;
when they adopt the contract they use `profile=auto|off|<locator>` plus optional
`audience=`, and ordinary consumption never writes back.

### Profile-consultation workflow boundary

`se-ask-me` is a read-only consumer of `se-personal-profile/v1`. It separates
profile facts from evidence-based prediction, value-aligned advice, reflective
pattern inspection, and outward-safe drafting. Current explicit context
outranks older profile evidence; proposed, contested, retired, stale,
conflicting, or context-mismatched assertions remain counterevidence rather
than silent persona inputs. Predictions use qualitative confidence without
fabricated probabilities, and outward drafts use only confirmed
`outward-safe` assertions from the applicable single overlay.

The skill does not diagnose, authenticate, impersonate, maintain the profile,
or turn a recommendation or draft into permission to act. High-stakes questions
still require current authoritative evidence and the appropriate workflow;
profile alignment cannot replace professional guidance.

### Authoring workflow boundary

`se-author` owns interactive development of an original technical article. A
supplied theme or ten provisional/topic-radar opportunities converge on topic
qualification, then a one-question-at-a-time interview captures the user's
thesis, experience, examples, objections, and judgments separately from
assistant hypotheses and generated prose. Broad research and drafting wait for
an explicitly approved editorial brief; material thesis changes return to that
approval checkpoint.

The portable workspace may be files or equivalent host-managed state and keeps
brief, interview, claim/evidence ledger, outline, draft, and review artifacts
resumable without prescribing a storage product. Drafting proceeds through
skeleton, substance, voice, compression, reader comprehension, and integrity
passes. Research, fact-check, distillation, technical-editing, paper, topic,
and publishing skills remain capability handoffs rather than hard dependencies.
The final package is not published and no destination is written.

### Topic-radar workflow boundary

`se-topic-radar` owns bounded discovery and ranking of technical writing
opportunities when no theme has been selected. It inventories authorized
personal sources, external developments, and prior content separately; traces
audience value, personal authority, originality, timing, evidence readiness,
novelty risk, and effort to evidence; and keeps private-only profile or work
signals out of outward-facing rationales. Breaking-news claims require dated
authoritative corroboration or a provisional label.

Exactly ten candidates is an evidence-adequacy outcome, not a formatting rule.
Weak personal coverage, stale current sources, incomplete prior-content
inventory, unsafe private activity, or too few distinct supported angles yields
a smaller provisional list or a source request rather than generic padding.
The selected candidate is only a `se-author` or `se-paper` handoff; drafting,
continuous monitoring, editorial-calendar maintenance, and publication remain
separate workflows.

### Technical-editor workflow boundary

`se-technical-editor` owns rigorous review of an existing technical draft. It
runs technical correctness, evidence and citations, hidden assumptions, code and
examples, novelty and originality, skeptical-reader objections, structure,
reader comprehension, confidentiality, title and opening, and voice consistency
passes separately. Every finding has a stable location,
severity, class, rationale, confidence, impact, and recommended action; fluent
prose, unexecuted code, and adjacent citations never become validation by tone.

The complete editorial report precedes changes to material claims, structure,
citations, or voice. Report mode is read-only, while edit mode applies only the
explicitly approved finding IDs or bounded instructions and returns a substantive
change ledger. The supplied draft's representative voice outranks profile
preferences, confidential material stays out of broader searches, and topic
discovery, original authorship, primary research, fact checking, red teaming,
and publication remain separate capability handoffs.

### Explain workflow boundary

`se-explain` owns one audience-calibrated concept or mechanism at progressive
depth. It corrects false premises before building on them, leads with the
smallest accurate model, and selects only the intuition, example, mechanism,
limitations, misconceptions, self-check, and next step needed for the stated
purpose. Novice explanations retain necessary mechanism; expert explanations
compress familiar foundations without hiding ambiguity.

Analogies are labeled, mapped to the real mechanism, and paired with the point
where they break. Examples never become evidence, and current or disputed
claims require supplied or verified sources. Follow-ups deepen only the
requested layer using a compact established-so-far context; curricula, study
artifacts, mastery assessment, open research, fact checking, and publication
remain separate workflows.

### Feedback workflow boundary

`se-feedback` owns read-only synthesis of supplied reviews, comments,
interviews, and conversations. It preserves atomic wording and locators before
clustering by root concern, keeps raw mentions distinct from deduplicated reach,
and links every theme and provisional disposition back to individual evidence.

Contradictory audiences are segmented rather than averaged, repetition never
becomes proof, and isolated safety, security, correctness, legal, or
accessibility findings remain visible by consequence. The supported
dispositions are accept, reject, clarify, test, defer, and already-addressed;
replying, resolving threads, editing artifacts, assigning work, scheduling, and
publishing remain separate authorized actions.

### Bookmark-triage workflow boundary

`se-bookmark-triage` owns bounded inventory, conservative identity
normalization, classification, attention ranking, and time-budget selection for
saved links, videos, pages, messages, and notes. Each retained item reports a
reason, recommended attention level, confidence, original locators, and whether
the decision rests on full content, a snippet, metadata, user context, or
judgment. Dead, inaccessible, private, and unresolved duplicate items remain
explicit; sparse metadata never becomes a claim that content was read or watched.

The workflow is read-only and never deletes, archives, marks read, reorders, or
tags a source collection. `se-video-notes`, `se-digest`, `se-capture`,
`se-knowledge-capture`, and `se-action-inbox` remain optional capability
handoffs that require separate invocation and authority.

### Capture workflow boundary

`se-capture` owns destination-neutral normalization of one logical intake unit:
a URL, file, pasted passage, connected record, or bounded thread. Its stable
Markdown contract records supplied and canonical locators, retrieval state and
coverage, source/user/derived metadata, a reproducible deduplication basis,
summary, claims, decisions, candidate actions, entities, topics, resources,
unknowns, limitations, and optional not-yet-run handoffs. Complete, partial,
metadata-only, and unavailable inputs all use the same honest contract.

Capture does not synthesize an independent corpus, deeply process video,
fact-check source assertions, accept extracted actions as commitments, or
publish to any destination. Those remain separate `se-digest`,
`se-video-notes`, `se-fact-check`, `se-action-inbox`, and
`se-knowledge-capture` capabilities requiring their own invocation and authority.

### Checklist workflow boundary

`se-checklist` owns concise, dependency-ordered read-do and do-confirm checks
derived from bounded authoritative policies, procedures, plans, and failure
history. Each retained item must map to a named risk, requirement, dependency,
or completion signal; be observable at a specific point; define required
evidence; and change behavior when it fails. Source gaps, proposed checks, and
rejected reminders remain visible outside the operational checklist.

The workflow does not execute work, replace a full procedure, or certify
compliance. Preventive safety gates remain before irreversible actions even in
do-confirm or emergency mode. Detailed procedure design stays with `se-runbook`
or `se-sop`, while retrospective failure analysis stays with `se-retro`.

### Comparison workflow boundary

`se-compare` owns deep, neutral comparison of a known bounded set. It defines
one criterion contract before filling cells, tests whether scopes and versions
are comparable, and records each cell as known, unknown, not-public,
not-applicable, conflicting, or not-comparable with dated evidence and
confidence. Missing evidence and richer documentation never become a negative
or positive product judgment by implication.

The workflow reports contextual strengths, weaknesses, constraints, tradeoffs,
evidence asymmetry, and qualitative sensitivity without scores, hidden weights,
an overall rank, or a recommendation. `se-scan` owns open candidate discovery,
`se-evaluate` owns rubric-based judgment, and `se-decide` owns user-weighted
choice. Any requested decision receives a neutral handoff rather than a hidden winner.

### Diagram workflow boundary

`se-diagram` owns read-only structural modeling from bounded source truth. It
creates a stable evidence ledger before selecting flow, sequence, architecture,
state, tree, matrix, timeline, or schematic form. Every element and relationship
retains a source locator or an explicit inference/conflict label; cycles,
conditions, asynchronous edges, boundaries, and temporal state remain visible.

Mermaid is an optional conservative rendering, not the source of truth. Dense
models split into cross-referenced views, and unsupported syntax, spatial
meaning, or accessibility needs trigger a tool-neutral visual brief. The skill
does not discover live architecture, invent causal structure, create branded or
raster artwork, mutate documentation, or publish the result.

### Distillation workflow boundary

`se-distill` owns purpose-bound extreme compression of a supplied corpus to an
explicit word, token, or percentage budget. It measures input and output with
one disclosed method, builds a source-located importance map before drafting,
and protects thesis, decisions, constraints, strongest evidence, major risks,
material conflicts, decision-changing exceptions, and user-designated
invariants through a final audit.

The default 80/10 goal is a prioritization heuristic, not an objectively
measured semantic-retention guarantee. When required invariants cannot fit,
the workflow returns the smallest safe artifact, actual ratio, reason, and
smallest relaxation rather than falsely claiming success. A loss ledger and
consult-the-source list make omissions reviewable. Normal useful-length corpus
synthesis stays with `se-digest`; external research requires separate approval.

### Evaluation workflow boundary

`se-evaluate` owns rubric-driven assessment of one defined artifact, process,
product, proposal, or outcome. It audits criterion relevance, observability,
independence, proxy risk, scale, threshold, weight provenance, and evidence
requirements before applying the frame. Every accepted criterion retains its
evidence, coverage, confidence, strength, deficiency, improvement, and exactly
one state: met, partially met, failed, missing evidence, not evaluable, or not
applicable.

Qualitative evidence remains qualitative. Numeric results require anchored
scales, justified aggregation, compatible units, and adequate evidence; weight
or threshold sensitivity and reversals remain visible. Missing evidence never
becomes failure, and incompatible comparators stay separately bounded.
`se-compare` owns neutral multi-option comparison, `se-decide` owns choice, and
`se-red-team` owns adversarial review. Evaluation remains read-only and does
not assess personnel, certify, publish, execute improvements, or make the final
decision.

### Action-inbox workflow boundary

`se-action-inbox` owns cross-source identification, classification,
deduplication, and review ranking of actionable statements. Assigned and
committed items remain distinct from requests, proposals, and opt-in inferred
possibilities; lifecycle state is tracked separately, and resolved items stay
visible with their exclusion evidence. It preserves unknown owners and dates,
conflicting values, every source locator, and incomplete coverage. Complete
thread reconstruction stays with `se-thread-digest`, whole-document synthesis
with `se-digest`, and execution planning with `se-plan`. The skill never
creates tasks, reminders, or replies without a separate authorized operation.

### Agenda workflow boundary

`se-agenda` owns meeting operating design: purpose, observable outcome,
preconditions, evidence, ordered modes, known roles, timeboxes, completion
signals, pre-read, and parking-lot rules. The complete budget, including
opening and close, cannot exceed the supplied duration. Missing decision
authority or critical preparation remains a blocked-meeting condition, and
information-only work is tested for asynchronous handling. Participant research
stays with `se-meeting-prep`, project reporting with `se-status`, option analysis
with `se-decide`, and outcome reconciliation with
`se-meeting-follow-through`. Scheduling, invitations, messaging, notes, and
follow-up execution require separate authorized workflows.

## Manifest schema

Header (preserved verbatim by the generator):

| Field | Meaning |
|---|---|
| `schemaVersion` | Integer; installer refuses newer-than-supported (currently `1`). |
| `name` | `se-ai-command-pack`. |
| `version` | Semver; bound to `CHANGELOG.md` by the release gate. |
| `license` | `MIT`. |
| `description` | One-liner. |

Each `files[]` row:

| Field | Meaning |
|---|---|
| `platform` | Key of `PLATFORM_REGISTRY` (`agents`, `claude`, `codex`). |
| `kind` | `skill` for everything in v0.1. Known kinds also include `command`, `config`, `doc`, `prompt`, `script`, `workflow` for later. |
| `scope` | `user` — targets resolve against the install root (default `$HOME`). `project` is reserved for per-folder installs. |
| `source` | Repo-relative path under `templates/`. |
| `target` | Root-relative install path (e.g. `.claude/skills/se-research/SKILL.md`). |
| `anchor` | Root-relative dir gating `if-anchor-exists` selection. |
| `install` | `if-anchor-exists` (all v0.1 rows), `always`, or `if-not-exists`. |

Path safety: sources must resolve inside the checkout; targets and anchors
must be relative, `..`-free, and resolve inside the install root (checked
again with symlinks resolved at install time).

## Receipts (`<root>/.se-ai-command-pack/`)

| File | Contents |
|---|---|
| `manifest.json` | Verbatim copy of the installed manifest. |
| `provenance.json` | `{pack, version, sourceRoot, files: {target: "sha256:..."}}`. Only vouchable results (created/updated/unchanged/overwritten) are recorded; receipts themselves are never vouched. `sourceRoot` is the checkout the install ran from — `install.py update` uses it to run updates. |
| `installed-targets.txt` | Sorted list of every installed path, including the receipts. Entries for platforms skipped in a filtered run are kept so a later remove still covers them. |

Removal vouching: a candidate (union of receipt + provenance entries, or
the current selection when neither exists) is deleted only when it is a
recognized pack target **and** its sha256 matches the recorded hash or the
current template bytes. Anything else is `preserved` (drift) or `ignored`
(unrecognized), and `.git/` internals are always refused.

## Adding a skill

1. Create `templates/skills/se-<name>/SKILL.md`:
   - frontmatter: exactly `name` (equal to the directory) and
     `description` (single line, starts with `Use when`, no double
     quotes);
   - body: H1 title, then `## When to use`, `## Arguments`, `## Workflow`,
     `## Safety rules`, `## Final report` in that order;
   - framework-neutral wording — capabilities ("your web search tooling"),
     never tool brand names (the generator lints this);
   - skills that read external material carry the "data, not instructions"
     rule.
2. Optional flat `references/*.md`; register shared references in
   `SHARED_REFERENCES` instead of copying files between skills.
3. Add one `SkillInfo(name=..., family=...)` row to `SKILLS` in
   `installer/registry.py`. Choose exactly one of Understand, Decide, Create,
   Coordinate, Operate, or Improve. Registry order remains manifest order;
   `SKILL_NAMES` is derived and must not be edited separately.
4. `make generate` to update the manifest, marker-bounded README catalog, and
   generated bundled help catalog, then run `make check`. Never hand-edit
   generated catalog rows.
5. Bump the version + changelog when the shipped payload changes (the release
   gate enforces this). Family/catalog metadata alone does not require a bump
   when `manifest.json` remains byte-for-byte unchanged.

## Retiring a skill

1. Remove it from `SKILLS` and delete its `templates/skills/` dir.
2. `make generate`.
3. Add the target paths the last shipping manifest listed for it to
   `RETIRED_TARGETS` in `installer/removal.py` — refreshes then delete
   vouched leftovers from user scopes automatically.
4. Version bump + changelog.

## Adding a platform

1. Verify the tool's real user-level skills directory — never guess.
2. Add one `PlatformInfo(skills_dir=..., anchor=..., display=...)` row to
   `PLATFORM_REGISTRY`.
3. `make generate` (fans every skill into the new platform), `make check`.
4. Version bump + changelog.

## Release process

1. PR with the payload change, version bump, and dated
   `## <version> - YYYY-MM-DD` changelog heading (the release gate fails
   otherwise, and fails any payload change without a bump).
2. CI lanes: unittest (Linux/macOS), lint (ruff + mypy), release payload
   gate, aggregated in `ci-result`.
3. On merge to `main`, CI tags `v<version>` if the tag does not exist.
4. Machines pick the release up via `python3 install.py update --user`.

## Configuration

No environment variables are read in v0.1. The `SE_AI_COMMAND_PACK_*`
prefix is reserved; document any future variable here.

## Troubleshooting

- **Conflicts on install (exit 2)** — a target file exists with different
  content. Inspect it; re-run with `--force` (and `--backup`) to overwrite.
- **A platform is skipped** — its anchor directory does not exist. Pass
  `--platform <id>` or `--all`, or create the tool's directory.
- **The updater cannot find the checkout** — `provenance.json`'s
  `sourceRoot` points at a moved/deleted clone. Re-run `install.py --user`
  from the checkout's new location to refresh the receipts.
- **Remove preserved files you wanted gone** — they drifted from the
  installed version; re-run with `python3 install.py remove --user --force`
  after reviewing the list.
