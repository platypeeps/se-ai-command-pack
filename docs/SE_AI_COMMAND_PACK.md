# SE AI Command Pack — Operator Guide

The maintainer-facing reference for the pack's internals: manifest schema,
receipts, checklists for adding skills and platforms, and the release
process. User-facing install/update/remove instructions live in the
[README](../README.md). This document is repo-only; it is not installed.

## Layout

| Path | Role |
|---|---|
| `templates/skills/<name>/` | Canonical skill definitions (`SKILL.md` + optional flat `references/*.md` and `scripts/*.py`). The only place skills are edited. |
| `templates/skills/_shared/references/` | Shared references fanned into consuming skills' `references/` dirs by the generator. |
| `templates/skills/_shared/references/skill-catalog.md` | Generated bundled family/skill catalog fanned into `se-help`; never hand-edit. |
| `templates/skills/_shared/references/personal-profile-contract.md` | Portable `se-personal-profile/v1` schema and privacy/consumer contract fanned into profile workflows. |
| `templates/skills/_shared/references/state-schema.md` | Portable `se-monitor-state/v1` schema fanned into compatible bounded-delta workflows. |
| `installer/registry.py` | Source of truth: `PLATFORM_REGISTRY`, ordered `SKILLS` family metadata, derived `SKILL_NAMES`, `SHARED_REFERENCES`, install modes, receipt paths. |
| `manifest.json` | Generated install spec (header preserved, `files` rows derived). Never hand-edit rows. |
| `install.py` + `installer/` | The user-scope installer. |
| `README.md` | User guide with a marker-bounded, family-grouped skill catalog generated from registry metadata and canonical frontmatter. |
| `.github/scripts/generate-skill-surfaces.py` | Validates skills and atomically coordinates the manifest, README catalog, and bundled help catalog; `--check` gates drift in all three. |
| `.github/scripts/check-release-payload.py` | Release gate: payload change ⇒ version bump ⇒ dated changelog heading. |
| `scripts/` | Repository wrappers and maintenance helpers (`se-ai-command-pack-*` prefix); skill-bundled runtime helpers live with their canonical skill template. |

## Product and development surfaces

- **Shipped skills** are the `se-*` entries under `templates/skills/`. They are
  grouped by primary outcome family in the README but retain flat canonical and
  installed paths. The current bundle includes report-first technical editing
  with `se-technical-editor` and audience-calibrated explanation with
  `se-explain`, traceable feedback synthesis with `se-feedback`, and compact
  evidence-backed continuity packets with `se-handoff`, plus preview-first
  Obsidian/Notion publishing with `se-knowledge-capture` and bounded
  knowledge-system auditing with `se-knowledge-gap`, plus adaptive
  mastery-oriented paths with `se-learn` and source-traceable field mapping
  with `se-literature-map`, plus evidence-linked post-meeting reconciliation
  with `se-meeting-follow-through`, plus private cross-stream weekly reflection
  with `se-weekly-review`.
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

### Handoff workflow boundary

`se-handoff` owns compact transfer of a defined objective to another person,
team, tool, or AI session. It reconstructs dated current state from the smallest
sufficient authoritative sources; separates verified facts, recorded decisions,
assumptions, and unresolved questions; preserves only continuation-critical
locators; and makes the first proposed next action independently executable.
Arbitrary corpus synthesis stays with `se-digest`, while stakeholder progress
reporting stays with `se-status`. The workflow omits secret values and unrelated
private material, remains read-only, and never sends the packet or authorizes its
next actions.

### Knowledge-capture workflow boundary

`se-knowledge-capture` is the explicit write-capable bridge from one normalized
`se-capture` artifact to an authorized Obsidian vault or Notion data source. It
searches canonical URL, external ID, title/aliases, and fingerprint before
classifying create, managed append/update, skip, or conflict; previews exact
mapping and preservation effects; requires approval; then writes once and
verifies by semantic read-back. User-owned and unsupported content is preserved,
ambiguous or destructive paths stop for specific confirmation, and unavailable
connectors yield a portable preview. Full-content mirroring and bidirectional
sync remain out of scope; a separately approved cross-link keeps one canonical
full record.

### Claim-audit workflow boundary

`se-fact-check` starts from supplied claims or an artifact and returns a
claim-by-claim ledger using exactly five verdicts: supported, partially
supported, unverified, contradicted, or outdated. Open-ended evidence questions
stay with `se-research`, while multi-document synthesis stays with `se-digest`
unless the request explicitly asks to audit claims. Both `se-research` and
`se-fact-check` consume the shared `verification-protocol.md`; the canonical
source lives under `_shared/references/` while installed paths remain local to
each skill. The audit is read-only and offers only minimal corrected wording.

### Knowledge-gap workflow boundary

`se-knowledge-gap` audits a bounded existing knowledge system against a stated
decision or audience. It records search coverage and access limits, normalizes
terminology, then builds a provenance-preserving claim and decision map before
classifying missing, inaccessible, stale, conflicting, unsupported, duplicated,
or unresolved knowledge. “Not found” never becomes “does not exist” without
sufficient authoritative coverage, and conflicting positions retain their
dates and authority signals. Individual claim verdicts stay with
`se-fact-check`, new external evidence with `se-research`, source consolidation
with an explicit documentation task, and continuous freshness checking with
`se-monitor` when that separate capability is available. The audit remains
read-only and reports every proposed follow-up as not run.

### Adaptive-learning workflow boundary

`se-learn` owns the path from a stated capability goal and diagnosed baseline
to ordered prerequisite stages, observable outcomes, practice, transfer,
checkpoints, and spaced review. It distinguishes self-report from demonstrated
ability, adapts from explicit evidence states, and exposes workload, horizon,
scope, and material-access tradeoffs without guaranteeing mastery or silently
lowering the goal. One-concept clarification stays with `se-explain`, durable
source-derived review artifacts with `se-study-guide`, and adaptive mastery
probing with `se-socratic-review`; unavailable siblings remain honest proposed
handoffs. The workflow is read-only and never enrolls, purchases, schedules,
grades, or credentials.

### Study-guide workflow boundary

`se-study-guide` owns durable transformation of a bounded source set into a
concept and prerequisite map, essential definitions and notation, worked
examples, traps, retrieval prompts, flashcards, varied practice, traceable
solutions, and review order. It reads every accessible source fully, discloses
unreadable regions, preserves conflicting definitions in context, and labels
source content, source-derived transformation, generated scaffolding,
generated inference, and unsupported gaps separately.

Every answer, solution, rubric, and distractor maps to concept IDs and source
locators or remains visibly generated or unsupported. Prompt audits catch
ambiguity, answer leakage, notation drift, and omitted-context dependencies.
Compression stays with `se-distill`, curricula with `se-learn`, one-concept
teaching with `se-explain`, live assessment with `se-socratic-review`, and
stepwise teaching with `se-tutorial` when available. The workflow is read-only
and never adds external research, creates decks, schedules sessions, grades,
certifies, or claims mastery.

### Tutorial workflow boundary

`se-tutorial` owns checkpoint-driven technical teaching from a declared reader,
objective, starting state, environment, prerequisites, and version scope to an
observable final result. Every step carries an exact command or code sample,
execution state, expected output or stable assertion, checkpoint, failure
signals, recovery, and rollback when state changes. Verified, partially
verified, and unverified examples remain distinct, and mutable APIs or versions
are dated and checked against authoritative sources.

Platform differences produce explicit branches instead of universalized
commands. Secrets remain placeholders; destructive, costly, and production
steps require scoped targets, safer alternatives, authorization, backup, and
rollback, and cleanup receives the same safeguards. Durable review material
stays with `se-study-guide`, curricula with `se-learn`, one-concept teaching
with `se-explain`, and operational execution with `se-runbook`. The workflow
does not run commands on the reader's system, deploy, publish, enroll, submit,
or certify.

### Video-notes workflow boundary

`se-video-notes` owns destination-neutral notes for one supplied video or a
bounded comparison set. It inventories video identity, metadata, version,
caption source and quality, language, transcript access, timestamp basis, and
coverage before separating metadata, transcript-grounded creator content,
description or comment material, and assistant analysis. Complete, partial,
metadata-only, and unavailable transcripts remain explicit states; unavailable
captions produce verified metadata plus a manual-viewing aid, never guessed
video content.

Every chapter, timestamp, short quotation, claim, demonstration, and referenced
resource maps to its video and evidence basis. Edited cuts, ads, automatic-
caption errors, translations, and unequal comparison coverage remain visible.
Independent claim verification stays with `se-fact-check`, general source
normalization with `se-capture`, and persistence with `se-knowledge-capture`.
Downloading, transcription implementation, access bypass, channel mutation,
publication, and external writes remain `not run`.

### Socratic-review workflow boundary

`se-socratic-review` owns a bounded formative dialogue that asks exactly one
assessable question per turn, requires commitment before explanation, and
adapts difficulty, representation, prerequisites, or transfer checks from the
learner's demonstrated reasoning. It distinguishes correct reasoning from a
correct guess, partial models, procedural success without understanding,
misconceptions, and unassessed turns. Hints and reveals remain contaminated
evidence; invalid prompts are retired rather than counted against the learner.
The workflow is read-only, learner-controlled, non-grading, and never infers
intelligence, personality, or general ability.

### Literature-map workflow boundary

`se-literature-map` owns a source-traceable map of a bounded field or research
question: search protocol, work inventory, schools, methods, cluster bases,
direct relationships, disputes, gaps, and a purpose-specific reading sequence.
It discloses missing databases and abstract-only access, treats cluster
boundaries as interpretive, and keeps prominence, methodological strength,
recency, and current evidentiary support distinct. Deeper answer synthesis stays
with `se-research`, while paper development stays with `se-paper` when that
separate capability is available. The map is read-only, makes no bibliometric
completeness claim, and never infers full-text conclusions from metadata.

### Meeting-follow-through workflow boundary

`se-meeting-follow-through` owns post-meeting reconciliation between supplied
intent and the available meeting record. It inventories notes and transcript
coverage, classifies expected outcomes as achieved, changed, deferred,
unaddressed, or unclear, and preserves decisions, proposals, commitments,
candidate actions, disputes, owners, dates, and source locators as distinct
evidence states. Missing prep disables expected-versus-actual conclusions;
conflicting or sensitive records stay visible without widening disclosure.
Preparation remains with `se-meeting-prep`, agenda design with `se-agenda`,
bounded thread outcome reconstruction with `se-thread-digest`, generic
multi-document synthesis with `se-digest`, and durable publishing with
`se-knowledge-capture`. Recaps and handoffs are drafts only: task creation,
calendar changes, messages, and system updates require separate authorization.

### Monitor workflow boundary

`se-monitor` owns read-only, baseline-to-current comparison for one bounded
subject and watch set. A first run creates an explicit baseline without claiming
a delta; later runs validate `se-monitor-state/v1`, match stable semantic keys,
apply materiality rules, and classify facts as new, changed, resolved,
unchanged, or unverifiable. Source-only wording, layout, locator, and coverage
changes remain separate from changes in the watched subject, and unavailable
sources never become evidence of resolution.

The versioned state block is an output/input interchange artifact, not an
implicit file or connected record. Broad current-topic catch-up stays with
`se-brief`, objective-oriented project reporting with `se-status`, and one-time
deep investigation with `se-research`. Persistence, recurring schedules,
subscriptions, notifications, webhooks, and external writes require separate
requests and authorized capabilities; all remain `not run` in the monitor
report.

### Watchlist workflow boundary

`se-watchlist` owns read-only attention triage for a bounded set of channels,
feeds, authors, searches, playlists, podcasts, or collections since an explicit
checkpoint. It reuses `se-monitor-state/v1`, separates baseline creation,
ranked change, no material change, and insufficient coverage, and never treats
an unavailable or stale source as evidence that nothing changed.

Stable external IDs, conservative canonical URLs, exact supplied fingerprints,
and original locators form the identity order; uncertain cross-posts and
repeated topics remain unresolved until semantic evidence establishes
continuity. Exclusions apply only when their conditions are sourced, and any
private interest/profile signal stays out of outward-facing explanations.
Broad catch-up remains `se-brief`, saved-backlog triage remains
`se-bookmark-triage`, and persistence or recurrence remains `se-monitor` or
host-owned. Capture, video-note, brief, and fact-check routes are proposed only
and marked not run.

### Planning workflow boundary

`se-plan` begins only after an outcome or strategic direction is accepted. It
works backward into milestones with observable changed states and completion
signals, then maps dependencies, sequencing, risks, contingencies, decision
points, assumptions, and immediate actions. Supplied commitments remain
separate from proposed owners, dates, estimates, and actions; unsupported
critical paths, dependency cycles, missing prerequisites, and unknown authority
stay explicit.

Choosing among unresolved alternatives remains `se-decide`. When implementation
work occurs in a repository with a local requirements, design, task, or delivery
workflow, `se-plan` returns a `not run` handoff to that workflow instead of
writing competing technical artifacts. Task creation, calendar changes,
messages, purchases, approvals, and every external write require separate
authorization.

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

### Skill-review workflow boundary

`se-review-skills` owns bounded review of one or more skills or skill packages.
It inventories capabilities, identifies evidence-backed issues, overlap, and
improvement opportunities, and returns numbered selectors at skill, family,
and all-skills scope. The default is review-only: applying an improvement or
creating a task requires a later explicit `apply=` or `task=` selector.

By default it also inspects bounded user skill roots derived from the verified
pack manifest. Installed copies are matched to canonical repository sources;
the repository source remains the review and task target even when an installed
copy has drifted. Multiple installations of the same canonical skill collapse
into one finding set while retaining per-path drift evidence. Unverified copies
are never merged by name alone. Every report ends with advisory suggested next
steps, including exact selectors and installation-refresh guidance where useful.

Pack discovery and intent routing remain with `se-help`. Broader engineering
repository audits remain with `sd-audit-repo`, while configured local
code-review providers remain with `sd-review-local`. A skill review does
not silently broaden into either workflow, edit installed copies, or treat a
recommendation as authorization to mutate a repository.

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

### Research-paper workflow boundary

`se-paper` owns gated development of a research paper from question refinement
through a venue-aware, submission-ready draft. It requires a one-question
interview, feasibility and ethics review, and explicit approval of a research
brief before full literature work, analysis, outlining, or drafting. Literature
coverage is bounded by dated databases/sources, queries, selection rules,
screening, deduplication, access gaps, and a stopping condition.

Every literature work, dataset, experiment, code artifact, quotation, citation,
exclusion, transformation, analytical decision, and unavailable component keeps
stable provenance. Method, results, interpretation, discussion, and conclusions
remain separate; contradictory, negative, null, and inconclusive findings cannot
be rewritten to fit a preferred narrative. Profile use is framing-only, and
venue requirements are dated rather than inferred as timeless. General
technical articles stay with `se-author`, field maps with `se-literature-map`,
open evidence work with `se-research`, and claim audits with `se-fact-check`.
Submission, publication, data collection, experiment execution, ethics approval,
and peer review remain separate actions marked `not run`.

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

### Runbook workflow boundary

`se-runbook` owns detailed operational procedure design for a bounded event,
maintenance activity, migration, recovery, or recurring technical
intervention. It inventories source authority and validation coverage, defines
preflight and abort gates, and writes dependency-ordered steps. Every mutation
retains explicit authority, exact target, execution state, expected result,
read-back verification, failure signal, stop/escalation response, decision
rule, rollback or recovery state, and evidence.

Validated, partially validated, and proposed steps remain distinct and are
bound to environment, version, date, target, and observed result. Partial
failure requires live-state reconciliation before retry, rollback, or
recovery. Rollback and recovery are separate contracts; unavailable or
untested paths stay explicit, with containment and escalation instead of false
guarantees. Secrets use placeholders, destructive targets must be resolved and
bounded, and stale or unsupported context produces a prominent warning.

The workflow authors but never executes, schedules, publishes, approves, or
operationally validates a runbook. Compact point-of-work checks stay with
`se-checklist`, routine policy-oriented procedures with `se-sop`, planning with
`se-plan`, and live incident coordination with the applicable incident-command
process.

### SOP workflow boundary

`se-sop` owns controlled procedure design for routine, repeatable work. It
inventories observed and approved practice, preserves conflicts and unknowns,
and keeps proposed improvements in a separate future-state register. Every
operative step carries an observable trigger, responsible function, bounded
action, output, verification, record, failure response, and source basis.
Mandatory controls retain their authority and applicability; helpful guidance
remains visibly non-mandatory.

The workflow defines supported exceptions, escalation and safe-stop behavior,
document ownership, version, effective date, review cadence, staleness triggers,
and source-backed compliance scope. It never executes, enforces, assigns,
approves, publishes, trains, creates operational records, or certifies the
procedure. Event-driven intervention, failure, rollback, and recovery stay with
`se-runbook`; compact point-of-work checks stay with `se-checklist`; and project
planning stays with `se-plan`.

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

### Presentation workflow boundary

`se-presentation` owns read-only narrative and slide-specification planning
from an approved source artifact. It inventories load-bearing claims and assets
before building an outcome-led story arc, then gives every slide one primary
claim, source IDs, visual intent and status, speaker notes, transition,
anticipated question, timing budget, and accessible linear alternative.

Short and standard variants reprioritize the same argument through an explicit
omission ledger; they never shrink text or silently drop evidence. Existing,
data-derived, and proposed visuals remain distinct, and sparse evidence can
support a discussion deck without being upgraded into a decision deck. Profile
data is optional, read-only, and limited to presentation preferences. Deck-file
creation, rendering, rehearsal, delivery, and publication belong to separate
presentation or publishing capabilities.

### Proposal workflow boundary

`se-proposal` owns interview-led development of a decision-ready case for a
bounded intervention. It identifies the actual decision authority and required
evidence, classifies material claims as observed evidence, estimate, assumption,
or advocacy, and requires explicit approval of a proposal brief before full
drafting. Estimates retain methods, ranges, time bases, and sensitivity rather
than acquiring certainty from persuasive prose.

The proposal applies common criteria to the preferred intervention, credible
alternatives, and a do-nothing baseline. Conflicting stakeholder criteria,
weak evidence, rejected framing, authority gaps, and rescoping conditions stay
visible. Profile data can shape voice only; it cannot establish relationships,
motives, facts, authority, or commitments. An accepted proposal may hand its
approved outcome and constraints to `se-plan`, but approval, negotiation, task
creation, implementation planning, and execution remain separate workflows.

### Publish workflow boundary

`se-publish` owns read-only adaptation of an already approved artifact into a
destination-specific draft and exact preview. It supports Slack messages and
canvases, Notion pages, internal memos, announcements, briefings, and YouTube
outlines through capability-neutral destination contracts. It inventories
load-bearing claims, citations, required nuance, audience scope, and sensitive
material before drafting, then exposes every compression, reordering,
terminology change, omission, or proposed addition in an adaptation ledger.

Source fidelity, accessibility, and confidentiality outrank channel style or
tight length limits. `se-digest` owns synthesis of unsettled inputs,
`se-author` owns original argument development, `se-presentation` owns slide
story specifications, and `se-knowledge-capture` owns approved durable writes
to supported knowledge systems. `se-publish` never sends, schedules, posts, or
creates a destination artifact; a write-capable connector workflow requires a
separate explicit request, fresh preview, and target/audience revalidation.

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

### Red-team workflow boundary

`se-red-team` owns constructive adversarial review of a settled proposal,
decision, article, conclusion, plan, or similar artifact. It confirms the
authorized frame, steelmans the artifact, inventories evidence and value
premises, then tests only relevant lanes across assumptions, contrary evidence,
incentives, misuse/abuse, failures, security/privacy, strongest counterarguments,
and reversal conditions.

Every finding has exactly one class: demonstrated defect, plausible risk,
speculative case, or value disagreement. Severity cannot outrun evidence and
consequence; adversaries, vulnerabilities, motives, and exploitability are not
invented. Sensitive defensive detail is minimized, strong artifacts may return
an honest no-material-findings result, and closure evidence stays explicit.
Claim verification remains with `se-fact-check`, rubric assessment with
`se-evaluate`, plan failure discovery with `se-premortem`, and after-action
causal analysis with `se-postmortem`. Probing, approval, remediation, disclosure,
task creation, and other external action require separate authority.

### Retrospective workflow boundary

`se-retro` owns general evidence-led reflection after a project, research
effort, meeting, launch, or operational period. It inventories source coverage
and builds a factual timeline before comparing intended with actual outcomes.
Verified facts, attributed participant perspectives, and assistant inference
remain distinct; disagreements and evidence gaps stay visible rather than
being collapsed into a convenient consensus.

The workflow examines multiple contributing conditions across decisions,
process, information, environment, dependencies, incentives, and chance.
Root-cause language requires evidence for a causal mechanism; otherwise the
result names contributing factors and explicit uncertainty. Lessons retain
their transfer limits, and follow-ups remain proposed, unassigned, and
unscheduled unless an owner or date was supplied or approved.

Software-delivery debugging streams, incidents, CI or review gate misses, and
pull-request workflow retros route to `sd-retro` when that specialized skill is
available. Formal incident causal and safeguard analysis remains with
`se-postmortem`. `se-retro` never records a journal entry, creates or assigns a
task, contacts participants, publishes a report, changes systems, or executes a
follow-up.

### Weekly-review workflow boundary

`se-weekly-review` owns personal cross-stream synthesis for one explicit local
week. It inventories configured work and knowledge sources, normalizes aware
timestamps into a half-open local reporting window based on local calendar
midnights rather than a fixed 168-hour duration, and conservatively groups
duplicate records without erasing provenance. For a current or future-ending
range, the evidence cutoff is invocation time, so scheduled future records do
not become completed activity. Observable outcomes, meaningful activity,
recorded decisions, cutoff carryover, supported lessons, directly self-reported
energy, documented friction, and at most three next-week focus items remain
separate. Missing connectors are coverage gaps rather than empty-week evidence,
and sparse weeks produce short truthful reviews.

Timezone resolution precedes calendar-boundary calculation: use an explicit
invocation value, then an authorized private worklog-profile timezone already
supplied to the workflow. If neither is available, ask and stop rather than
guessing a named locale, host default, or system setting.

The private worklog boundary is explicit: `worklog_profile=off|<locator>` must
resolve before source reads, never searches private stores, and has no public
schema, path, identity, tag, source list, or destination data. The separate
`profile=auto|off|<locator>` surface consumes `se-personal-profile/v1` under its
existing read-only rules; weekly evidence never writes back. Objective project
progress remains `se-status`, deeper bounded-event analysis remains `se-retro`,
`se-capture` does not own weekly synthesis, and persistence through
`se-knowledge-capture` requires a separate explicit request. The weekly review
itself never publishes notes, mutates tasks or profiles, schedules work,
contacts people, or scores employee performance.

### Premortem workflow boundary

`se-premortem` owns prospective stress-testing after an objective and plan are
accepted but before execution or an irreversible commitment. It defines the
failed state, inventories plan sufficiency and evidence, develops distinct
technical, operational, people, dependency, incentive, security, market, and
external failure modes, and labels each scenario as evidence-supported,
analogical, or speculative. Scenarios remain hypotheses rather than forecasts.

Likelihood, impact, detectability, and evidence confidence use explained
ordinal bands without composite arithmetic. Common-cause, correlated, and
cascading failures remain linked, while low-likelihood catastrophic tails stay
visible separately. Every prevention and contingency must map to a named mode
and observable indicator; no-mitigation cases, residual risk, decision points,
and stop conditions remain explicit. Planning stays with `se-plan`, adversarial
artifact review with `se-red-team`, and after-outcome analysis with
`se-postmortem`. Approval, assignments, go/no-go decisions, and execution
require separate authority.

### Postmortem workflow boundary

`se-postmortem` owns formal corrective analysis after an incident or failed
outcome is stable enough to review. It inventories source coverage and
conflicts, reconstructs an evidence-linked timeline, separates impact from
mechanism, and examines detection, response, recovery, decision context, and
safeguards. Observation, interpretation, contributing factor, root cause, and
counterfactual remain distinct; a root-cause claim requires a defensible causal
mechanism, and inadequate evidence yields an explicit no-root-cause result.

Blameless analysis focuses on system conditions and controls without erasing
impact, accountable decisions, or control ownership. Human error is never a
terminal cause. Corrective actions must map to findings or control gaps and
name observable verification, approved or proposed commitment state, expected
risk reduction, and residual risk. Active incident response, discipline,
legal conclusions, task assignment, publication, and action execution remain
separate workflows. Lighter cross-domain reflection stays with `se-retro`.

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

### Stakeholder-map workflow boundary

`se-stakeholder-map` owns an evidence-aware map of the people and groups
relevant to one initiative or decision. It records role-specific entries,
keeps formal authority separate from behavior- or process-evidenced informal
influence, and distinguishes observed positions, user judgments, assistant
inferences, conflicts, and unknowns. Every inference carries a validation
question and action; missing stakeholders remain access or coverage gaps, not
evidence that a perspective is irrelevant.

Groups retain internal disagreement, people with multiple roles retain
role-specific interests and dependencies, and organizational change triggers
revalidation. The workflow minimizes personal data and prohibits protected-
trait inference, personality or vulnerability profiling, and manipulative
engagement. Meeting design stays with `se-agenda`, accepted-outcome planning
with `se-plan`, continuity transfer with `se-handoff`, feedback synthesis with
`se-feedback`, and personal-profile maintenance with `se-profile`. Contact,
scheduling, assignments, approvals, and external writes remain `not run`.

### Thread-digest workflow boundary

`se-thread-digest` owns outcome reconstruction for one bounded Slack thread,
channel window, chat export, issue discussion, or equivalent conversation. It
retains message locators, parent/reply relationships, timestamps, revisions,
corrections, conflicts, coverage gaps, and a conservative state for every
proposal, decision, explicit commitment, candidate action, question,
disagreement, and risk. Silence, repetition, attendance, reactions, and third-
party assignments never prove acceptance by themselves.

Generic multi-document synthesis stays with `se-digest`; meeting-intent
reconciliation stays with `se-meeting-follow-through`. The workflow may draft
portable `se-status`, `se-handoff`, and `se-knowledge-capture` payloads but does
not invoke them. Private-channel information remains within the authorized
source and stated audience, and posting, reacting, canvases, lists, monitoring,
messages, tasks, persistence, and other external mutations remain `not run`.

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
| `provenance.json` | `{pack, version, sourceRoot, files: {target: "sha256:..."}}`. Only vouchable results (created/updated/unchanged/overwritten) are recorded; receipts themselves are never vouched. A normal refresh may replace differing regular-file bytes only when they still match this prior hash. `sourceRoot` is the checkout the install ran from — `install.py update` uses it to run updates. |
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
2. Optional flat `references/*.md` and standard-library `scripts/*.py`;
   register shared references in `SHARED_REFERENCES` instead of copying files
   between skills. Scripts must have stable input/output/error contracts and
   focused tests; keep judgment and approval logic in `SKILL.md`.
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

- **Conflicts on install (exit 2)** — a target differs from both the current
  payload and its prior recorded install hash, or no trusted prior hash is
  available. Inspect it; re-run with `--force` (and `--backup`) to overwrite.
- **A platform is skipped** — its anchor directory does not exist. Pass
  `--platform <id>` or `--all`, or create the tool's directory.
- **The updater cannot find the checkout** — `provenance.json`'s
  `sourceRoot` points at a moved/deleted clone. Re-run `install.py --user`
  from the checkout's new location to refresh the receipts.
- **Remove preserved files you wanted gone** — they drifted from the
  installed version; re-run with `python3 install.py remove --user --force`
  after reviewing the list.
