# SE AI Command Pack

User-level knowledge-work skills for AI agent frameworks: personal profile
maintenance and consultation, interview-driven technical authoring,
destination-neutral capture, bookmark and action-inbox triage,
critical operational checklists, neutral alternative comparisons,
evidence-traceable diagrams, auditable extreme distillation,
rubric-driven evaluations, evidence-backed editorial opportunity ranking,
report-first technical editing,
decision-oriented agendas, pack discovery,
deep research, claim fact-checking, decision support, project-status reporting,
daily briefs, meeting prep, landscape scans, and document digests — installed
once per machine, centrally managed from this repository.

The pack borrows the installer architecture of its sibling
`sd-ai-command-pack` (manifest-driven payload, provenance receipts, vouched
removal, generated surfaces) but targets general knowledge work instead of
the software-delivery lifecycle, installs into **user-level** agent scopes
instead of per-repo adapters, and has no Trellis dependency.

## Skills

The catalog is grouped by each skill's primary outcome family. Descriptions
come directly from canonical skill frontmatter.

<!-- SE_SKILL_CATALOG:START -->
### Understand

| Skill | Use when |
|---|---|
| `se-research` | Use when the user asks for deep, multi-source research on a question or topic and wants a verified, source-graded written brief rather than a quick answer. |
| `se-scan` | Use when the user wants a competitive, market, or landscape scan that inventories the players in a space and compares them on consistent criteria. |
| `se-digest` | Use when the user provides multiple documents, threads, or links and wants them synthesized into one decision-ready brief with disagreements surfaced. |
| `se-fact-check` | Use when the user supplies claims or a draft and wants a claim-by-claim evidence audit with supported, partially supported, unverified, contradicted, or outdated verdicts. |
| `se-ask-me` | Use when the user wants a profile-grounded prediction, aligned recommendation, reflection, or outward-safe draft without treating prior behavior as identity or authority. |
| `se-compare` | Use when the user wants a neutral, evidence-aware comparison of known alternatives on one fair frame without ranking them or recommending a winner. |
| `se-distill` | Use when the user wants supplied material compressed to an explicit information budget while preserving decision-critical meaning, attribution, exceptions, and an auditable loss ledger. |
| `se-explain` | Use when the user wants one complex topic explained accurately for a stated audience, purpose, prior-knowledge level, and depth, with explicit analogy and limitation boundaries. |
| `se-knowledge-gap` | Use when the user wants a bounded, cross-source audit of missing, inaccessible, stale, conflicting, unsupported, duplicated, or unresolved knowledge. |
| `se-learn` | Use when the user wants an adaptive, mastery-oriented learning path from a stated capability goal, diagnosed baseline, constraints, and observable evidence. |
| `se-literature-map` | Use when the user wants a source-traceable map of a field's schools, methods, works, relationships, disputes, gaps, and reading paths without a flattened narrative review. |

### Decide

| Skill | Use when |
|---|---|
| `se-decide` | Use when the user wants a defensible recommendation between known options using explicit criteria, constraints, evidence, tradeoffs, and uncertainty. |

### Create

| Skill | Use when |
|---|---|
| `se-author` | Use when the user wants to develop an original evidence-backed technical article through a one-question interview, approved editorial brief, staged drafting, review, and publication handoff. |
| `se-diagram` | Use when the user wants a precise, evidence-traceable diagram specification or conservative Mermaid diagram for a system, process, concept, hierarchy, comparison, state model, or event sequence. |
| `se-topic-radar` | Use when the user wants ten ranked technical writing opportunities grounded in authorized personal activity, current developments, prior coverage, evidence readiness, novelty, and effort. |

### Coordinate

| Skill | Use when |
|---|---|
| `se-brief` | Use when the user asks for a morning, daily, or on-demand brief that assembles their stated topics and sources into one short, scannable update. |
| `se-meeting-prep` | Use when the user has an upcoming meeting or call and wants a dossier on the people, company, and context, plus talking points and questions. |
| `se-status` | Use when the user wants an objective-oriented project status update from supplied or connected work sources, with outcomes, current state, blockers, risks, decisions, asks, and next actions. |
| `se-action-inbox` | Use when the user wants a reviewable, cross-source inbox of explicit commitments and opt-in possible actions without creating tasks or sending replies. |
| `se-agenda` | Use when the user wants a decision-oriented, timeboxed meeting agenda with explicit outcomes, roles, evidence, preparation, and parking-lot rules. |
| `se-handoff` | Use when the user wants a compact, evidence-backed continuity packet that lets another person, team, or AI session safely resume a defined objective. |

### Operate

| Skill | Use when |
|---|---|
| `se-help` | Use when the user wants to discover, compare, or choose SE skills and receive a justified recommendation with a copy-ready prompt without executing another workflow. |
| `se-profile` | Use when the user wants to create, inspect, correct, review, import, export, or forget a consent-driven personal operating profile with traceable assertions. |
| `se-bookmark-triage` | Use when the user wants to deduplicate and triage a bounded collection of saved links, videos, pages, or notes into a small evidence-labeled attention queue without mutating the source collection. |
| `se-capture` | Use when the user wants one URL, file, pasted passage, connected record, or bounded thread normalized into a destination-neutral knowledge artifact with provenance and no implicit external write. |
| `se-checklist` | Use when the user wants a short read-do or do-confirm checklist derived from bounded authoritative sources, with observable pass conditions, failure responses, and no execution or certification. |
| `se-knowledge-capture` | Use when the user wants a normalized capture safely published to Obsidian or Notion through duplicate-aware preview, preservation, approval, and verified write-back. |

### Improve

| Skill | Use when |
|---|---|
| `se-evaluate` | Use when the user wants one defined subject assessed against an explicit rubric with criterion-level evidence, uncertainty, sensitivity, deficiencies, and prioritized improvements. |
| `se-technical-editor` | Use when the user wants an existing technical draft reviewed through evidence-located correctness, citation, code, structure, comprehension, confidentiality, and voice passes before approved revisions are applied. |
| `se-feedback` | Use when the user wants supplied reviews, comments, interviews, or conversations synthesized into traceable themes, tensions, and evidence-backed response dispositions. |
<!-- SE_SKILL_CATALOG:END -->

Skills that use external evidence share one quality bar: a
`source-standards.md` reference (source tiers, independence, dating,
confidence vocabulary) is installed into each consumer's `references/`
directory.

`se-profile` maintains a private, portable `se-personal-profile/v1` Markdown
artifact from explicit input and bounded user-authorized sources. The public
pack contains the schema and workflow only: profile content, locators,
credentials, and destination configuration remain private. Obsidian is the
preferred user-selected destination, with an explicit user-selected Notion
fallback; the skill implements no connector and never silently mirrors both.
Every mutation previews the change, preserves user-owned content, writes, reads
back, and verifies stable IDs. Any other skill that adopts the contract is a
read-only consumer and must never write back merely because it used the profile.

`se-ask-me` is the first read-only profile consumer. It keeps profile facts,
prediction, aligned advice, reflection, and outward-facing drafts distinct;
current context outranks historical patterns, uncertain or conflicting evidence
stays visible, and outward drafts use only eligible `outward-safe` assertions.
It never treats the profile as identity, consent, authority, or permission to act.

`se-author` develops original technical articles through topic qualification, a
one-question-at-a-time interview, an explicitly approved editorial brief,
claim-specific evidence work, ordered drafting passes, and resumable workspace
checkpoints. It preserves user testimony separately from assistant framing and
returns a publication package without publishing or writing to a destination.

`se-topic-radar` ranks technical writing opportunities from explicitly
authorized personal activity, dated external developments, and prior-content
coverage. It traces every component score, keeps private evidence out of
outward-facing rationales, penalizes duplicate angles, and returns exactly ten
only when the evidence supports ten materially distinct candidates. Selection
hands off to `se-author` or `se-paper`; it does not draft or publish.

`se-technical-editor` reviews an existing technical draft through separate
technical correctness, evidence and citations, hidden assumptions, code and
examples, novelty and originality, skeptical-reader objections, structure,
reader comprehension, confidentiality, title and opening, and voice consistency
passes. It reports located
findings before substantive rewriting, preserves representative author language
and evidence states, and applies only explicitly approved edits without publishing.

`se-bookmark-triage` turns a bounded saved-item collection into a small,
evidence-labeled attention queue. It preserves original locators, keeps
uncertain duplicates separate, distinguishes full-content review from snippets
or metadata, and fits selected work to a disclosed time budget. It never
mutates the source collection; deep viewing, durable capture, knowledge
capture, and action extraction remain separate handoffs.

`se-capture` normalizes one URL, file, pasted passage, connected record, or
bounded thread into a destination-neutral Markdown artifact. It records actual
retrieval coverage, separates source/user/derived metadata, uses a reproducible
deduplication basis, and preserves source-stated claims without upgrading them
to verified facts. Publication and every suggested downstream workflow remain
separate, not-yet-run operations.

`se-checklist` distills bounded authoritative procedures, policies, plans, or
failure history into the smallest dependency-ordered set of checks that prevent
a named failure or prove completion. Every item has an observable pass state,
evidence rule, failure response, and source basis. It never executes the work,
replaces a full procedure, or claims certification.

`se-compare` applies one fair, source-aware frame to a known set of
alternatives. It preserves version and evidence asymmetry, explicit unknown and
conflicting cells, conditional tradeoffs, eligibility, and qualitative
sensitivity without ranking or recommending a winner. Choice remains a separate
handoff to `se-decide`.

`se-diagram` builds a traceable element-and-relationship ledger before choosing
the smallest useful visual form. It emits conservative Mermaid when faithful or
a tool-neutral brief when rendering constraints would distort the model, while
preserving cycles, boundaries, conflicts, uncertainty, and an accessible description.

`se-distill` compresses a supplied corpus to an explicit information budget
using a traceable importance map and invariant audit. It reports measured input
and output size, preserves load-bearing attribution and disagreement, and
returns a smallest-safe result plus an auditable loss ledger when 10% would be
unsafe. The 80/10 goal remains a disclosed prioritization heuristic, not a
semantic-retention guarantee.

`se-evaluate` audits a rubric before assessing one defined subject. It maps
every judgment to criterion-level evidence, keeps failure separate from missing
or non-evaluable evidence, uses numbers only when scales and aggregation are
meaningful, and exposes weight or threshold sensitivity plus the highest-value
subject, rubric, and evidence improvements. It does not certify, score people,
or make the final decision.

`se-action-inbox` reconciles explicit assignments and commitments across a
bounded source set while keeping requests, proposals, and opt-in inferred
possibilities separate. It preserves every locator and conflicting value,
suppresses resolved items visibly, and ranks active work with evidence-backed
reasons. The workflow is read-only: task creation, reminders, replies, and
handoff to `se-plan` require a separate request.

`se-agenda` designs a meeting around an observable outcome, known authority,
required evidence, and a verified time budget. It moves broadcast status and
preparation out of synchronous time when practical, keeps missing decision
roles visible, and can recommend an asynchronous alternative, split, cancel,
or reschedule. Scheduling, invitations, delivery, notes, and follow-through
remain separate operations.

## What gets installed where

Skills are plain `SKILL.md` directories, installed into every platform
whose anchor directory exists in your home directory:

| Platform | Skills directory | Gating anchor | Used by |
|---|---|---|---|
| `claude` | `~/.claude/skills/` | `~/.claude` | Claude Code / Cowork |
| `codex` | `~/.codex/skills/` | `~/.codex` | OpenAI Codex (honors `$CODEX_HOME`) |
| `agents` | `~/.config/agents/skills/` | `~/.config/agents` | Amp and compatible tools |

A platform whose anchor is missing is skipped with a hint; pass
`--platform <id>` or `--all` to install it anyway. Adding a platform is one
row in `installer/registry.py`.

## Install

```sh
git clone https://github.com/platypeeps/se-ai-command-pack.git
cd se-ai-command-pack
python3 install.py --user
```

Useful variants:

- `python3 install.py --user --dry-run` — show the plan without writing.
- `python3 install.py --user --platform codex` — one platform only.
- `python3 install.py --user --all` — install every platform, creating
  missing directories.

The installer is plan-before-apply: if any target file exists with
different content, it reports the conflicts and exits with code 2 without
writing anything. Re-run with `--force` to overwrite (add `--backup` to
keep `.bak` copies).

## Update

```sh
cd se-ai-command-pack
python3 install.py update --user --dry-run
python3 install.py update --user
```

The update command locates the checkout through the install receipt, refuses
a dirty worktree, pulls fast-forward only, previews the refreshed install,
then reapplies it from a fresh Python process.

Other lifecycle commands:

```sh
python3 install.py status --user
python3 install.py refresh --user --dry-run
python3 install.py refresh --user
```

## Remove

```sh
python3 install.py remove --user --dry-run
python3 install.py remove --user
```

Removal is vouched: a file is deleted only when its content matches the
recorded install hash or the current template. Files you have edited are
preserved and reported; `python3 install.py remove --user --force` deletes
them too. Empty parent
directories are pruned.

## How it works

- `templates/skills/<name>/` holds the canonical skill definitions — the
  only place skills are edited.
- `installer/registry.py` declares platforms, ordered skill-family metadata,
  outcome descriptions, and shared-reference fan-out; `make generate`
  regenerates `manifest.json`, this README's grouped catalog, and the versioned
  `se-help` catalog from one frontmatter parse.
- `install.py` owns the pack lifecycle and applies the manifest to your home directory (or `--root`
  elsewhere) and writes receipts under `~/.se-ai-command-pack/`:
  - `manifest.json` — copy of the installed manifest (version lookup);
  - `provenance.json` — sha256 per installed file plus `sourceRoot`, the
    checkout path updates run from;
  - `installed-targets.txt` — every installed path, the removal record.
- CI gates: the manifest must match the generated surfaces, and any payload
  change must bump the version with a dated `CHANGELOG.md` heading.

## Maintaining the pack

1. Edit or add skills under `templates/skills/` (see
   [docs/SE_AI_COMMAND_PACK.md](docs/SE_AI_COMMAND_PACK.md) for the
   add-a-skill checklist).
2. `make generate` to refresh the manifest, README catalog, and bundled
   `se-help` catalog reference.
3. For shipped payload changes, bump `version` in `manifest.json` and add the
   matching `CHANGELOG.md` heading. Metadata-only catalog changes do not need a
   release bump when generated payload bytes stay unchanged.
4. `make check` (tests, lint, release gates), then PR.
5. `make sync` to dogfood the result into your own home directory.

## Repository map

The generated [Repomix repository map](docs/repomix-map.md) provides a compact,
AI-friendly view of the repository. Refresh it after structural or substantial
documentation changes:

```sh
make repomix
```

The refresh script runs the pinned Repomix version through `npx`; Node.js and
`npx` are required, but no Node dependencies are installed into this Python
project.

## Non-goals in v0.1 (designed-for, not built)

- **Per-folder installs** — the manifest already carries a `scope` field
  and the installer a `--root`; a future `project` scope slots in without a
  schema break.
- **Plugin/marketplace packaging** — a build step can emit a plugin layout
  from the same `templates/skills/` source; that is the path to cloud
  sessions whose home directory is not this machine's.
- **Command surfaces** (per-platform command/prompt adapters) — the
  generator keeps the sd-pack fan-out pattern available if skills alone
  stop being enough.
- **A workflow backbone** — `preflight_checks()` in `install.py` is the
  single seam where a future backend prerequisite would land.

## License

MIT — see [LICENSE](LICENSE).
