# SE AI Command Pack

A pack of user-level knowledge-work skills for AI agent frameworks (Claude
Code / Cowork, OpenAI Codex, Amp-compatible tools): research, fact-checking,
authoring, review, planning, meeting support, monitoring, and dozens of other
evidence-disciplined workflows — installed once per machine, centrally managed
from this repository.

## Quick start

Requires Python 3.10 or newer (the oldest version CI tests).

```sh
git clone https://github.com/platypeeps/se-ai-command-pack.git
cd se-ai-command-pack
python3 install.py --user
```

After installing, ask your agent for **`se-help`** — it is the pack's entry
point: it recommends the right skill for the job at hand and returns a
copy-ready prompt. All skills are natural-language-triggered; there are no
slash commands to memorize.

See [Install](#install) for variants, conflict handling, and the refresh
contract.

## Contents

- [Skills](#skills)
- [What gets installed where](#what-gets-installed-where)
- [Install](#install) · [Update](#update) · [Remove](#remove)
- [How it works](#how-it-works)
- [Maintaining the pack](#maintaining-the-pack)
- [Repository map](#repository-map)
- [Non-goals in v0.1](#non-goals-in-v01-designed-for-not-built)
- [License](#license)

The pack borrows the installer architecture of its sibling
`sd-ai-command-pack` (manifest-driven payload, provenance receipts, vouched
removal, generated surfaces) but targets general knowledge work instead of
the software-delivery lifecycle, installs into **user-level** agent scopes
instead of per-repo adapters, and has no Trellis dependency.

## Skills

The catalog is grouped by each skill's primary outcome family. Descriptions
come directly from canonical skill frontmatter: the table below is generated
by `make generate` and CI fails if it drifts from the skill sources, so it
never goes stale by hand-editing.

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
| `se-monitor` | Use when the user wants a dated, source-traceable comparison of a watched subject against an explicit baseline, with meaningful deltas and a portable next-state artifact. |
| `se-socratic-review` | Use when the user wants a bounded, adaptive Socratic review that asks one question at a time, tests demonstrated understanding, repairs misconceptions, and reports evidence without grading. |
| `se-study-guide` | Use when the user wants a bounded source set transformed into a durable study guide with traceable concepts, definitions, examples, retrieval prompts, practice, solutions, traps, and review order. |
| `se-video-notes` | Use when the user wants one or more supplied videos converted into source-faithful, timestamped notes with explicit transcript coverage, claim extraction, comparison, and read-only downstream handoffs. |

### Decide

| Skill | Use when |
|---|---|
| `se-decide` | Use when the user wants a defensible recommendation between known options using explicit criteria, constraints, evidence, tradeoffs, and uncertainty. |
| `se-plan` | Use when the user has accepted a goal or decision and wants a bounded, evidence-aware plan with observable milestones, dependencies, risks, decision points, and immediate next actions. |

### Create

| Skill | Use when |
|---|---|
| `se-author` | Use when the user wants to develop an original evidence-backed technical article through a one-question interview, approved editorial brief, staged drafting, review, and publication handoff. |
| `se-diagram` | Use when the user wants a precise, evidence-traceable diagram specification or conservative Mermaid diagram for a system, process, concept, hierarchy, comparison, state model, or event sequence. |
| `se-topic-radar` | Use when the user wants ten ranked technical writing opportunities grounded in authorized personal activity, current developments, prior coverage, evidence readiness, novelty, and effort. |
| `se-paper` | Use when the user wants to develop a credible research paper through question refinement, an approved research brief, explicit literature and methodology protocols, traceable evidence, reproducibility, and venue-aware review. |
| `se-presentation` | Use when the user wants to turn an approved source artifact into an audience-specific story arc and source-traceable slide specification before using presentation tooling. |
| `se-proposal` | Use when the user wants to develop an evidence-backed, decision-ready proposal with transparent alternatives, investment, risks, success criteria, and an explicit ask. |
| `se-publish` | Use when the user wants an approved source artifact adapted into a source-faithful, destination-specific draft and preview without sending or publishing it. |
| `se-tutorial` | Use when the user wants a checkpoint-driven technical tutorial that moves a defined audience from a known starting state to an observable result with honest execution status, verification, recovery, and cleanup. |

### Coordinate

| Skill | Use when |
|---|---|
| `se-brief` | Use when the user asks for a morning, daily, or on-demand brief that assembles their stated topics and sources into one short, scannable update. |
| `se-meeting-prep` | Use when the user has an upcoming meeting or call and wants a dossier on the people, company, and context, plus talking points and questions. |
| `se-status` | Use when the user wants an objective-oriented project status update from supplied or connected work sources, with outcomes, current state, blockers, risks, decisions, asks, and next actions. |
| `se-action-inbox` | Use when the user wants a reviewable, cross-source inbox of explicit commitments and opt-in possible actions without creating tasks or sending replies. |
| `se-agenda` | Use when the user wants a decision-oriented, timeboxed meeting agenda with explicit outcomes, roles, evidence, preparation, and parking-lot rules. |
| `se-handoff` | Use when the user wants a compact, evidence-backed continuity packet that lets another person, team, or AI session safely resume a defined objective. |
| `se-meeting-follow-through` | Use when the user wants a source-traceable post-meeting package that reconciles intended and actual outcomes, decisions, commitments, unresolved items, and consent-gated follow-through. |
| `se-stakeholder-map` | Use when the user wants an evidence-aware map of the people and groups relevant to a defined initiative or decision, with authority, influence, interests, tensions, engagement order, and validation gaps kept distinct. |
| `se-thread-digest` | Use when the user wants a bounded Slack thread, channel window, or equivalent conversation converted into an evidence-linked digest of decisions, commitments, unresolved work, disagreement, risks, and message history. |

### Operate

| Skill | Use when |
|---|---|
| `se-help` | Use when the user wants to discover, compare, or choose SE skills and receive a justified recommendation with a copy-ready prompt without executing another workflow. |
| `se-profile` | Use when the user wants to create, inspect, correct, review, import, export, or forget a consent-driven personal operating profile with traceable assertions. |
| `se-bookmark-triage` | Use when the user wants to deduplicate and triage a bounded collection of saved links, videos, pages, or notes into a small evidence-labeled attention queue without mutating the source collection. |
| `se-capture` | Use when the user wants one URL, file, pasted passage, connected record, or bounded thread normalized into a destination-neutral knowledge artifact with provenance and no implicit external write. |
| `se-checklist` | Use when the user wants a short read-do or do-confirm checklist derived from bounded authoritative sources, with observable pass conditions, failure responses, and no execution or certification. |
| `se-knowledge-capture` | Use when the user wants a normalized capture safely published to Obsidian or Notion through duplicate-aware preview, preservation, approval, and verified write-back. |
| `se-runbook` | Use when the user wants a source-traceable operational runbook with bounded authority, ordered steps, verification, failure handling, escalation, rollback, recovery, and maintenance metadata. |
| `se-sop` | Use when the user wants a source-traceable standard operating procedure for routine repeatable work, with controlled current practice, testable controls, exceptions, records, and maintenance metadata. |
| `se-watchlist` | Use when the user wants a read-only review of configured channels, feeds, authors, searches, playlists, podcasts, or collections that reports only material new items since an explicit checkpoint. |

### Improve

| Skill | Use when |
|---|---|
| `se-evaluate` | Use when the user wants one defined subject assessed against an explicit rubric with criterion-level evidence, uncertainty, sensitivity, deficiencies, and prioritized improvements. |
| `se-technical-editor` | Use when the user wants an existing technical draft reviewed through evidence-located correctness, citation, code, structure, comprehension, confidentiality, and voice passes before approved revisions are applied. |
| `se-feedback` | Use when the user wants supplied reviews, comments, interviews, or conversations synthesized into traceable themes, tensions, and evidence-backed response dispositions. |
| `se-postmortem` | Use when the user wants a formal, evidence-linked, blameless analysis of an incident or failed outcome with defensible causes, safeguard findings, and verifiable corrective actions. |
| `se-premortem` | Use when the user wants to stress-test an accepted plan before execution by assuming failure, ranking plausible failure modes, and defining indicators, prevention, contingencies, and stop conditions. |
| `se-propose-skills` | Use when the user wants the current session reviewed for recurring friction, repeated steps, and hard-won gotchas, and high-bar skill proposals drafted into a configurable Obsidian Skill Proposals destination for later accept or decline. |
| `se-red-team` | Use when the user wants a constructive adversarial review of an artifact's assumptions, contrary evidence, incentives, failure modes, misuse, security, privacy, counterarguments, and reversal conditions. |
| `se-retro` | Use when the user wants an evidence-led, non-blaming retrospective of a project, research effort, meeting, launch, or operational period with lessons and proposed follow-ups. |
| `se-weekly-review` | Use when the user wants an evidence-backed personal weekly review across configured work and knowledge sources, with outcomes, activity, carryover, lessons, patterns, and next-week focus kept distinct. |
| `se-review-skills` | Use when the user wants AI skills reviewed for defects, harmful instructions, observed session mistakes, interaction design, overlap, missing capabilities, capability-preserving brevity, metadata, portability, context, delegation, model routing, and selectable improvements or Trellis tasks. |
| `se-brand-voice` | Use when the user wants written content validated against a defined brand voice - tone, terminology, style, and audience fit - with located findings and suggested rewrites, or wants starter voice guidelines drafted from representative samples when none exist. |
| `se-coherence-audit` | Use when a knowledge corpus — a note vault, agent-instruction files, or a docs tree — must be audited against itself for contradictions, vagueness, bandaid guidance, and redundancy, returning a read-only findings ledger with both sides quoted. |

### Engineer

| Skill | Use when |
|---|---|
| `se-rust-design` | Use when designing, writing, or restructuring Rust types and domain models — a new struct or enum, a state machine, typestate transitions, newtype wrappers, or a public API's type surface — and the goal is a design whose illegal states are unrepresentable. |
| `se-rust-quality` | Use when writing, editing, or planning Rust code — .rs files, Cargo.toml, lint configuration, or clippy fixes — to hold the idiomatic bar covering error type design, clippy posture, Rust API guidelines conformance, naming, and recurring anti-patterns. |
| `se-rust-modules` | Use when planning, creating, splitting, or reorganizing Rust modules and crates — mod declarations, file layout, visibility, re-export facades, crate boundaries — or when a module is growing into a god module. |
| `se-rust-async` | Use when writing, designing, or debugging async or multithreaded Rust — spawned tasks, channels, select loops, Send or 'static bound errors, suspected blocking inside async code, lock-across-await questions, or cancellation-safety concerns. |
| `se-rust-review` | Use when a diff, branch, or pull request touches Rust — .rs files, Cargo.toml, lint configuration — to run the pack's Rust-specific probe checklist as a local lens whose findings feed the review of record. |
| `se-typed-holes` | Use when starting a Rust feature, module, or rewrite skeleton-first — design the types and signatures, land a compiling skeleton whose bodies are todo!() as its own commit, then fill the holes in a separate later pass; never mix the two. |
| `se-gate-probes` | Use when a change or plan is about to be offered for review — at a commit boundary, before a pull request is opened, or when asked to run pre-merge quality probes over a diff or an implementation plan. Probes report findings; the sd-review lane holds the review verdict. |
| `se-docs-bustest` | Use when documentation must survive a cold read — checking that a newcomer with no prior context can execute a README, runbook, setup guide, or handoff doc exactly as written, when docs are created or changed, or when asked to bus-test docs. |
| `se-rebase-hygiene` | Use when the user explicitly asks to rebase a long-lived branch or worktree — user-invoked only, never triggered automatically. Fetch before trusting local state, dry-run the merge before touching the working tree, pre-plan every conflict resolution, and verify the remote ref after a user-approved force-with-lease push. |
| `se-skill-retro` | Use when the user explicitly asks for a skill retro after a working session — which skills fired, which should have fired and did not, which fired wrongly, and which gaps have no skill at all — with each vetted finding routed to the surface that owns the fix. This is a deliberate, user-invoked post-session action; it reviews the skills, not the work. |
| `se-prose-lint` | Use when prose written on the user's behalf — skill bodies, docs, README text, commit or PR text, release notes, outbound drafts — needs a prose lint, style lint, or AI-tell check before it is committed or sent; runs the deterministic Vale gate where it exists and assigns every finding a disposition, degrading gracefully where Vale is absent. |
| `se-humanizer` | Use when text should read as if a person wrote it — the user says humanize, de-AI, naturalize, sounds robotic, or reads like AI, or prose written on the user's behalf is about to be committed or sent — removing hedging, filler, throat-clearing, formulaic transitions, and generated-text vocabulary while restoring specificity and a human cadence. |
| `se-adr-review` | Use when a PR or diff touches docs/adr/, DECISIONS.md, or *.adr.md files, when an ADR moves between proposed, accepted, rejected, or superseded status, or when the user asks to review an architecture decision record; checks MADR-style completeness, RFC-2119 driver force, honest consequences, forward links, lifecycle validity, and premise freshness, and reports P1/P2/P3 findings with one verdict line. |
<!-- SE_SKILL_CATALOG:END -->

Skills that use external evidence share one quality bar: a
`source-standards.md` reference (source tiers, independence, dating,
confidence vocabulary) is installed into each consumer's `references/`
directory.

Each skill's full contract lives in its own `SKILL.md` under
`templates/skills/<name>/` — the table above is the complete catalog.

## What gets installed where

Skills are self-contained `SKILL.md` directories with optional references and
scripts, installed into every platform whose anchor directory exists in your
home directory:

| Platform | Skills directory | Gating anchor | Used by |
|---|---|---|---|
| `claude` | `~/.claude/skills/` | `~/.claude` | Claude Code / Cowork |
| `codex` | `~/.codex/skills/` | `~/.codex` | OpenAI Codex |
| `agents` | `~/.config/agents/skills/` | `~/.config/agents` | Amp and compatible tools |

A platform whose anchor is missing is skipped with a hint; pass
`--platform <id>` or `--all` to install it anyway. Adding a platform is one
row in `installer/registry.py`.

The installer reads no environment variables (see the operator guide): every
platform's directories are fixed relative to your home directory, and Codex
always reads `~/.codex` regardless of `$CODEX_HOME`. To make Codex load skills
from another location, symlink `~/.codex` to it (or relocate your home
directory). `install.py --root <dir>` changes only where the installer *writes*
(`<dir>/.codex/skills`), not where Codex looks — on its own it does not
redirect Codex's lookup.

## Install

Requires Python 3.10 or newer (the oldest version CI tests).

```sh
git clone https://github.com/platypeeps/se-ai-command-pack.git
cd se-ai-command-pack
python3 install.py --user
```

The install ends with an aggregate per-platform summary; pass `--verbose`
for one status line per file.

Useful variants:

- `python3 install.py --user --dry-run` — show the plan without writing.
- `python3 install.py --user --platform codex` — one platform only.
- `python3 install.py --user --all` — install every platform, creating
  missing directories.

The installer is plan-before-apply. Targets governed by preservation semantics
remain `preserved`. Otherwise, when a target differs from the current payload
but its sha256 still matches the prior provenance hash, a normal refresh safely
reports and applies it as `updated`. If any target instead has unvouched
changes, the installer reports the conflicts and exits with code 2 without
writing anything. Re-run with `--force` to overwrite those conflicts (add
`--backup` to keep `.bak` copies).

## Update

```sh
cd se-ai-command-pack
python3 install.py update --user --dry-run
python3 install.py update --user
```

The update command locates the checkout through the install receipt, refuses
a dirty worktree, pulls fast-forward only, previews the refreshed install,
then reapplies it from a fresh Python process.

Because the recorded source path drives `git` and re-executes `install.py`, the
update refuses an unverified source: the recorded checkout must be a git
repository (owned by the current user on POSIX platforms), and it must be the
checkout you are running `install.py` from. To update from a **relocated**
checkout — one you moved or renamed since installing — confirm it explicitly:

```sh
python3 install.py update --user --confirm-source
```

Without `--confirm-source`, a recorded source that differs from the running
checkout is refused (or, when run interactively, prompts for confirmation)
before any `git` or install runs.

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
  only place skills are edited. Nothing generated lives there; every
  `make generate` output is written under `generated/`.
- `installer/registry.py` declares platforms, ordered skill-family metadata,
  outcome descriptions, and shared-reference fan-out; `make generate`
  regenerates `manifest.json`, this README's grouped catalog, and the versioned
  `se-help` catalog (`generated/references/skill-catalog.md`) from one
  frontmatter parse.
- `install.py` owns the pack lifecycle and applies the manifest to your home directory (or `--root`
  elsewhere) and writes receipts under `~/.se-ai-command-pack/`:
  - `manifest.json` — copy of the installed manifest (version lookup);
  - `provenance.json` — sha256 per installed file plus `sourceRoot`, the
    checkout path updates run from;
  - `installed-targets.txt` — every installed path, the removal record.
- CI gates: the manifest must match the generated surfaces, and any payload
  change must bump the version with a dated `CHANGELOG.md` heading.

## Maintaining the pack

0. `make setup` once per fresh clone to create the virtualenv and install the
   dev dependencies (PyYAML, ruff, mypy, coverage); `make generate` and
   `make check` import PyYAML and fail without it.
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

The Repomix repository map (`docs/repomix-map.md`) provides a compact,
AI-friendly view of the repository. It is **gitignored and generated on
demand** — never committed — so the repository carries no large, drift-prone
snapshot. Generate or refresh it locally whenever you need it:

```sh
make repomix
```

The refresh script runs the pinned Repomix version through `npx`; Node.js and
`npx` are required, but no Node dependencies are installed into this Python
project. It exports `NPM_CONFIG_IGNORE_SCRIPTS=true` so the unattended
`npx --yes` fetch cannot run package lifecycle scripts.

**Accepted risk — unlocked npm transitives.** The Repomix version itself is
pinned, but `npx` resolves its transitive tree fresh on every run, so two
refreshes on different days can install different sub-dependencies. That is
accepted rather than fixed: locking it would mean vendoring an npm lockfile
and an `npm ci` step for a tool that produces one
gitignored artifact and is never part of a build, a test, or a release. The
exposure is bounded by lifecycle scripts being off and by the map being
regenerated on demand, never committed. Revisit if Repomix output ever gates
CI or ships in the pack payload.

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

## License

MIT — see [LICENSE](LICENSE).
