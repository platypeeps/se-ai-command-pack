# Implement se-author Design

## Overview

Add `se-author` as the primary interactive authoring workflow for technical
articles. It should preserve the user's authorship by eliciting and recording
their thesis, experience, examples, and judgments before generating polished
prose. The workflow is checkpointed and resumable rather than a single prompt
that jumps from topic to finished article.

The skill belongs to Create. It orchestrates narrower read-only workflows for
topic discovery, research, fact checking, distillation, editing, and publication
adaptation, but it must remain useful when some of those planned skills have not
landed. Dependencies are therefore capability contracts, not hard runtime calls.

## Proposal

Create `templates/skills/se-author/SKILL.md` with these arguments:

- `theme=`: optional starting topic, observation, or tentative thesis.
- `type=technical-blog|tutorial|argument|case-study`: default inferred from the
  approved brief; route research-paper intent to `se-paper` when available.
- `audience=`: intended reader and their existing knowledge/decision need.
- `objective=`: what the reader should understand, believe, or do differently.
- `length=`: target words or `short|standard|long`, recorded as a target rather
  than a reason to omit required evidence.
- `tone=`: user-supplied voice guidance; do not invent a personal brand.
- `workspace=`: optional supplied artifact location or resume pointer.
- `stage=discover|interview|brief|outline|draft|review|package|resume`: optional
  explicit entry point, validated against available checkpoints.

Use an artifact contract that can be represented as files or equivalent host
state:

- `brief.md`: approved audience, thesis, reader outcome, original contribution,
  evidence needs, format, length, tone, and confidentiality constraints.
- `interview.md`: dated questions and user answers, clearly separated from
  assistant hypotheses and prose suggestions.
- `evidence.md`: claim/evidence ledger with source, strength, citation, state,
  contrary evidence, and unresolved gaps.
- `outline.md`: approved section sequence with claim, evidence, example, and
  reader purpose for each section.
- `draft.md`: current prose plus declared draft stage.
- `review.md`: findings, decisions, unresolved issues, and approved edits.

The workflow should:

1. Discover: when `theme=` is absent, offer the `se-topic-radar` top-ten shape;
   when unavailable, generate explicitly provisional ideas from authorized
   context and disclose source coverage.
2. Qualify: test audience value, timeliness, thesis strength, firsthand
   contribution, novelty, evidence readiness, and confidentiality. Recommend
   reframing or stopping when the result would be generic or unsupported.
3. Interview: ask exactly one highest-value unresolved question per turn. Build
   a decision tree across problem, audience, thesis, experience, mechanisms,
   examples, objections, limitations, reader outcome, and voice. Challenge vague
   answers with concrete follow-ups rather than filling them in.
4. Brief: synthesize the interview into an editorial brief and require approval
   before broad research or drafting.
5. Evidence: plan claim-specific research lanes; use source standards, separate
   internal experience from external fact, and prevent new research from
   silently changing the approved thesis. Material thesis changes return to brief approval.
6. Outline: present two or three useful structures only when materially distinct,
   recommend one, then approve a claim/evidence/example skeleton.
7. Draft: produce passes in order—skeleton, substance, voice, compression,
   reader comprehension, integrity. Do not call early prose “final.”
8. Review: run separated technical, evidence, novelty, skeptical-reader,
   structure, confidentiality, title/opening, and voice passes. Report findings
   before changing load-bearing claims.
9. Package: return final article, title/deck options, summary, evidence status,
   visual/adaptation suggestions, and follow-up topics. Publication is a separate action.
10. Resume: inventory artifacts, locate the latest approved checkpoint, disclose
    gaps or conflicts, and continue from the first incomplete safe stage.

Register under Create/current registry and fan in `source-standards.md` because
the workflow consumes external research and internal records.

## Boundaries And Non-Goals

- Do not fabricate personal experience, opinions, measurements, quotes, code
  execution, or publication history.
- Do not present assistant-generated framing as the user's original insight.
- Do not start broad research before the brief is approved unless the user asks
  only for exploratory topic research.
- Do not publish, post, message, or modify a knowledge system.
- Do not replace `se-research`, `se-fact-check`, `se-distill`,
  `se-technical-editor`, or `se-publish`; define explicit handoffs.
- Do not force a fixed article structure when another structure better supports
  the approved reader outcome.
- Do not use research-paper language or rigor claims for work that belongs in `se-paper`.

## Affected Files

- `templates/skills/se-author/SKILL.md` — canonical authoring workflow.
- Optional `templates/skills/se-author/references/authoring-workspace.md` only if
  the artifact and checkpoint schemas make `SKILL.md` too large.
- `installer/registry.py` — Create/current registration and shared-reference fan-out.
- `manifest.json` — generated platform payload.
- `tests/test_skills.py` — interview, approval, authorship, evidence, resume,
  injection, and read-only pins.
- `tests/test_generate.py` — registry/reference/resource validation where needed.
- `README.md`, `docs/SE_AI_COMMAND_PACK.md`, `CHANGELOG.md`, and manifest version.

## Risks And Edge Cases

- A user may want fast drafting rather than a long interview. Permit explicit
  stage/brief shortcuts, but state which authorship and evidence inputs remain missing.
- Topic discovery can expose private recent activity. Inventory only authorized
  sources and summarize sensitive signals without reproducing unnecessary content.
- Research can produce a more fashionable but less original angle. Treat thesis
  changes as editorial decisions requiring approval.
- The user's voice cannot be inferred reliably from one sentence. Use supplied
  samples or interview language and label low-confidence voice assumptions.
- Artifact state may be partial, stale, or contradictory across sessions. Never
  overwrite silently; surface conflicts and choose the latest explicit approval.
- A technically correct draft can still disclose employers, clients, secrets, or
  security details. Include a dedicated confidentiality pass.
- Planned dependent skills may not yet exist. Use their contracts inline at a
  minimal level and never claim a handoff occurred when unavailable.
- Long interviews can lose momentum. After each meaningful branch, summarize
  what is settled, what remains, and why the next question matters.

## Validation

- Pin both theme and no-theme entry routes, one-question interview behavior,
  editorial-brief approval, and the ordered checkpoint sequence.
- Pin separation of user answers, assistant hypotheses, sourced claims, and draft prose.
- Pin no fabricated experience, no silent thesis drift, evidence-gap disclosure,
  publication boundary, and external-input injection protection.
- Test resume with complete, partial, conflicting, and missing artifacts.
- Exercise manual examples for a strong theme, vague theme, no activity sources,
  insufficient originality, sensitive firsthand example, unsupported technical
  claim, fast-draft request, and abandoned/reframed topic.
- Run `make generate`, focused tests, `make check`, and `git diff --check`.
