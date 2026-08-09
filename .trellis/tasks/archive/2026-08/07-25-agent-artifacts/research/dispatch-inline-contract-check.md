# Dispatch-vs-inline se-research contract check (final open AC)

Evidence for the last open acceptance criterion: one se-research run on a
sub-agent-dispatch platform and one on an inline platform, same question,
same arguments, compared on the `## Final report` contract.

- Date: 2026-08-09
- Question (both runs): What is the LTS status of Node.js 22 as of August
  2026 (Active LTS or Maintenance), and when is its scheduled end-of-life?
- Arguments (both runs): `depth=brief min_sources=3 format=brief`
- Skill content (both platforms): se-ai-command-pack 0.67.1 rendering of
  `templates/skills/se-research/SKILL.md`, including the
  `## Sub-agent dispatch` section, freshly installed via `install.py
  refresh` before the runs.

## Run A — sub-agent-dispatch platform (Claude Code)

Execution strategy: the skill's dispatch section. Three parallel
search-lane workers in step 3 (`se-source-reader` role: primary documents,
structured-data aggregators, news/practitioner), then three parallel
claim-verification workers in step 4 (`se-claim-verifier` role, one per
load-bearing claim, refutation-default). One documented deviation from the
letter of the dispatch section: step 5's disconfirmation queries were not a
third fan-out wave — each step-4 verifier, being refutation-default by
role, executed and recorded the contrary-evidence search for its own
conclusion (schedule revisions, transition delays, EOL changes), after the
lane results were in. Phase ordering was preserved (no verification before
all lanes returned, no disconfirmation before verification input existed);
the consolidation changed which worker ran the queries, not whether or when
they ran. Phases never overlapped otherwise; the orchestrator assigned unit
IDs, reconciled worker output, owned the disconfirmation judgment, and
wrote the report below. Workers
honored the worker input contract (smallest complete input, exclusions,
read-only authority boundary, expected artifact, stop condition); the
`min_sources` gate was enforced globally by the orchestrator.

### Final report (Run A)

**Question and scope.** As of 2026-08-09, is Node.js 22 in Active LTS or
Maintenance LTS, and when is its scheduled end-of-life? Scope: upstream
Node.js community support; paid/extended support out of scope. Assumption:
"end-of-life" means the upstream project's scheduled EOL.

**Findings.**

| Finding | Confidence | Sources (with dates) |
|---|---|---|
| Node.js 22 "Jod" is in **Maintenance LTS**, not Active LTS, as of 2026-08-09; Node 24 is the Active LTS line. | high | nodejs/Release schedule.json + README (Tier 1, read 2026-08-09 at commit e4bf922d, byte-identical to main); Heroku changelog 3502 (Tier 2, 2025-12-03); HeroDevs (Tier 3, 2026-06-23); endoflife.date (Tier 3, updated 2026-08-06) |
| It transitioned Active→Maintenance on **2025-10-21** — a governed calendar event ("No release" per nodejs/Release issue #1001), scheduled unchanged since 2023-09-22. | high | nodejs/Release schedule.json `maintenance` field (Tier 1); nodejs/Release issue #1001 release plan (Tier 1, updated 2026-07-14); Heroku changelog 3502 (Tier 2, 2025-12-03) |
| Its scheduled upstream end-of-life is **2027-04-30** — "scheduled," not immutable (WG has amended EOL dates before, e.g. Node 16). | high | nodejs/Release schedule.json `end` field (Tier 1, stable since 2023-09-22 across all 36 lifetime edits of the file); AWS Lambda runtime schedule (Tier 3 vendor-derived, retrieved 2026-08-09: nodejs22.x deprecation 2027-04-30); Google Cloud Run functions runtime support (Tier 3 vendor-derived, retrieved 2026-08-09: nodejs22 deprecation 2027-04-30); HeroDevs (Tier 3, 2026-06-23) |

**Open questions.** None material to the question. Watch item: the
schedule is subject to WG revision (precedents: Node 10/12 maintenance
delays, Node 16 EOL shortened); only a later nodejs/Release commit could
move the 2027-04-30 date. Side observation: the nodejs/Release README
status column lagged the actual transition by 7 days (flipped 2025-10-28),
so consumers keying on README wording rather than schedule.json see a
reporting window — relevant to `08-07-status-collector-pack-drift`, not to
this question.

**Methodology.** Lanes searched: primary/official records, structured-data
aggregators, news/practitioner commentary (three dispatched lane workers).
Publishers consulted: 9 (Node.js project, nodejs.org, endoflife.date,
Heroku, HeroDevs, NodeSource, Red Hat, AWS, Google), of which 4 are
independently *maintained* records (the Node.js WG schedule, AWS's runtime
schedule, Google's runtime schedule, Heroku's operational changelog).
Stated limitation, per the source standard's shared-upstream-origin rule:
for the upstream-schedule facts themselves these are not independent
origins — every secondary derives informationally from the WG record, and
the endoflife.date surfaces collapse to one source — so origin-independent
corroboration of the schedule claims is effectively unavailable by the
nature of the subject (a single authority owns the record). The
`min_sources` gate is met on sources consulted (9 publishers, 4
independently maintained); the load-bearing verdicts do not rest on
corroboration arithmetic at all but on the verification protocol's
dispositive-record path (the Release WG's own schedule for its own release
lines, identity and applicability verified, disconfirmation run), with the
secondaries as consistency checks — vendor dates being independent facts
only about those vendors' own policies.
Disconfirmation (recorded per conclusion by the refutation-default
verifiers): searched for "still Active LTS in 2026-08", schedule revisions
after the pinned commit (full commit history of schedule.json enumerated),
transition delays/postponements, and EOL extensions/shortenings; no
credible contradiction surfaced. Limits: one fetch-layer summarization
artifact was detected and discarded in the primary lane; the nodejs.org
previous-releases page was found unusable for EOL claims (no EOL column)
and excluded from that finding.

## Run B — inline platform (Codex CLI, single context)

Execution strategy: `codex exec` (read-only sandbox) instructed to follow
the identical installed skill file at `~/.codex/skills/se-research/SKILL.md`
per its inline-platform instruction — units run sequentially in one
context, no dispatch. Verbatim output (question restated with the same
as-of date; 102,879 tokens):

> **Question:** As of August 9, 2026, is Node.js 22 in Active LTS or
> Maintenance LTS, and when is its scheduled end-of-life?
> **Scope:** Upstream Node.js community support, excluding paid extended
> support and cloud-provider-specific retirement periods.
> **Assumption:** "End-of-life" means the upstream Node.js project's
> scheduled EOL date.
>
> | Finding | Confidence | Sources (with dates) |
> |---|---|---|
> | Node.js 22 is in Maintenance LTS, not Active LTS. It entered Maintenance on October 21, 2025. | high | Node.js Release Working Group schedule (Tier 1, accessed August 9, 2026); endoflife.date Node.js lifecycle (Tier 3, updated August 6, 2026). |
> | Its scheduled upstream end-of-life is April 30, 2027. | high | Node.js Release Working Group schedule (Tier 1, accessed August 9, 2026); Node.js 22.20.0 release notes (Tier 1, September 24, 2025); AWS Lambda Node.js runtime schedule (Tier 1 for AWS policy, accessed August 9, 2026); Google Cloud runtime schedule (Tier 1 for Google policy, updated July 29, 2026). |
> | During Maintenance, Node.js 22 remains supported primarily for critical bug fixes and security updates, with new features added only selectively. | high | Node.js Release Working Group phase definitions (Tier 1, accessed August 9, 2026). |
>
> **Open questions:** None material. The official schedule states that
> dates are subject to change, so only a later Node.js Release Working
> Group update could revise the April 30, 2027 EOL date.
>
> **Methodology:** Searched official release records, lifecycle trackers,
> cloud-runtime schedules, and contrary or supersession evidence. Five
> pages from four independently maintained publishers were consulted; the
> load-bearing verdict rests on the dispositive Node.js Release Working
> Group record. Disconfirmation searches covered claims that Node.js 22
> remained Active LTS in August 2026, that its Maintenance transition
> changed, and that its EOL had been extended, shortened, or postponed; no
> credible contradiction surfaced. One current NodeSource page could not be
> reopened and was excluded.

## Contract comparison — verdict: contract-identical

| Contract element | Run A (dispatch) | Run B (inline) | Identical? |
|---|---|---|---|
| Section 1: Question and scope (one sentence each, stated assumptions) | present | present | yes |
| Section 2: Findings table — finding / confidence (high, medium, low) / sources with dates | present, leads with the answer | present, leads with the answer | yes |
| Section 3: Open questions | present | present | yes |
| Section 4: Methodology — lanes, sources-consulted count with independence limits stated, disconfirmation queries | present | present | yes |
| Confidence vocabulary (exactly high/medium/low) | yes | yes | yes |
| Source tiering per source-standards | yes | yes | yes |
| Substantive verdicts | Maintenance LTS; transition 2025-10-21; EOL 2027-04-30; all high | identical, all high | yes |
| Disconfirmation pass recorded | yes (per-conclusion refutation searches) | yes (three queries named) | yes |

Differences observed are execution-strategy differences, not outcome
differences: Run A parallelized inside phases (3 lane workers, then 3
refutation-default verifier workers that also carried the disconfirmation
queries — the documented consolidation above) while Run B ran sequentially
in one context; Run A's evidence set is deeper on the transition-date
provenance (issue #1001, field history) because dedicated refutation
workers dug further; publisher counts differ (9 vs 4). The scope, the
verification bar, and the `## Final report` shape did not vary. The AC's
requirement — "execution strategy differs, outcome does not" — is met.
