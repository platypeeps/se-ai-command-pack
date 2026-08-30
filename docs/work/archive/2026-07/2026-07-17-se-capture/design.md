# Implement se-capture Design

## Overview

Add `se-capture` as a read-only normalization skill for one logical intake unit:
a URL, file, pasted passage, connected record, or bounded thread. It converts
heterogeneous input into a destination-neutral Markdown artifact with explicit
provenance, retrieval coverage, extracted knowledge, and suggested next
workflows.

The skill belongs to Operate. It is the intake boundary between raw material
and downstream workflows: `se-knowledge-capture` may publish the normalized
artifact, `se-fact-check` may verify extracted claims, `se-action-inbox` may
reconcile candidate actions, and `se-digest` may synthesize multiple intake
units. `se-capture` itself does none of those follow-on operations.

## Proposal

Create `templates/skills/se-capture/SKILL.md` with this argument surface:

- `source=`: one supplied URL, file, pasted block, connected record, or bounded
  thread; use the current attachment/context when unambiguous.
- `title=`: optional user-supplied title; preserve it as user metadata rather
  than pretending it came from the source.
- `topics=`: optional user-supplied topic hints; distinguish them from extracted
  topics.
- `detail=compact|standard`: provenance plus short summary, or the full
  normalized artifact.
- `follow_up=none|suggest`: default `suggest`; suggestions never execute.

The workflow should:

1. Confirm that the input is one logical capture unit. A bounded thread or one
   page with attachments can remain one unit; independent sources intended for
   synthesis should be routed to `se-digest`, while a list intended only for
   separate normalization should be processed as clearly separated captures.
2. Inventory access before extraction. Record source type, supplied locator,
   canonical locator when safely established, author/publisher, source date,
   retrieval timestamp with timezone, title, content form, and retrieval state
   `complete`, `partial`, `metadata-only`, or `unavailable`.
3. Preserve the difference among source metadata, user-supplied metadata, and
   assistant-derived fields. Missing values remain `unknown` with a short reason
   when useful.
4. Compute or select a deduplication key using this priority:
   - stable source/external ID namespaced by source system;
   - canonical URL after conservative tracking-parameter removal;
   - normalized supplied locator;
   - `sha256` of exact retrieved/supplied content only when deterministic hash
     tooling is available.
   Never invent a fingerprint, resolve redirects indefinitely, or treat title
   alone as a stable identity. Include the key type and basis.
5. Extract a concise summary, key claims, supporting locators, decisions,
   candidate actions, named entities, topics, referenced resources, and open
   questions. Preserve timestamps, page/section markers, message links, or
   paragraph-level locators when available.
6. Label claims as `source-stated`, `corroborated`, `disputed`, or `unverified`.
   Capture is not fact-checking: a claim repeated from the source remains
   source-stated/unverified unless evidence was actually checked.
7. Label decisions as explicit or inferred and candidate actions as assigned,
   requested, proposed, or inferred. Preserve actor/owner and due date only when
   sourced; otherwise use `unknown`. This extraction is informational and does
   not create commitments.
8. Produce a stable Markdown contract with these sections:
   - **Capture metadata** — provenance, retrieval state/coverage, and dedupe key;
   - **Summary**;
   - **Key claims and evidence**;
   - **Decisions and candidate actions**;
   - **Entities, topics, and referenced resources**;
   - **Unknowns and limitations**;
   - **Suggested next workflows**.
   Omit empty detail rows only in compact mode; never omit retrieval state,
   dedupe basis, or limitations.
9. Suggest only relevant next steps with the artifact each would consume:
   `se-fact-check`, `se-video-notes`, `se-digest`, `se-action-inbox`,
   `se-knowledge-capture`, or another available skill. Do not imply any handoff
   has run.

Register `se-capture` under Operate/current flat paths, make it consume
`source-standards.md`, and add it to the external-input injection safety set.
The source standards govern provenance, citations, and any corroboration added
to the artifact; they do not upgrade the captured source's assertions into
verified facts.

## Boundaries And Non-Goals

- Do not write to Obsidian, Notion, Slack, a filesystem destination, a task
  tracker, or any other external system.
- Do not create tasks, reminders, replies, reactions, or subscriptions.
- Do not synthesize a corpus; capture normalizes one logical intake unit, while
  `se-digest` compares and synthesizes multiple independent sources.
- Do not perform exhaustive fact-checking. Preserve claims and their evidence
  state, then recommend `se-fact-check` when verification matters.
- Do not claim full retrieval when a transcript, attachment, page region,
  connector, permission, or context window was unavailable.
- Do not fabricate metadata, quotes, timestamps, locators, canonical URLs,
  hashes, decisions, owners, deadlines, or publication success.
- Do not implement destination connectors, transcription, OCR, crawling, or
  persistent deduplication storage.

## Affected Files

- `templates/skills/se-capture/SKILL.md` — canonical normalization workflow and
  artifact contract.
- `installer/registry.py` — Operate/current registration and source-standard
  shared-reference fan-out.
- `manifest.json` — generated platform payload rows.
- `tests/test_skills.py` — normalized section contract, provenance separation,
  retrieval states, dedupe hierarchy, claim/action labels, injection safety,
  and read-only boundary.
- `tests/test_generate.py` — registry and shared-reference fan-out coverage where
  generic checks are insufficient.
- `README.md`, `docs/SE_AI_COMMAND_PACK.md`, `CHANGELOG.md`, and manifest version.

No destination-specific schemas or connector implementations are required. The
Markdown artifact is deliberately human-readable so downstream skills can
consume it without a new pack-wide machine protocol.

## Risks And Edge Cases

- A page may change after capture. Record both source date when known and exact
  retrieval time; a canonical URL alone does not prove identical content.
- Canonicalization can collapse distinct localized, versioned, or anchored
  resources. Remove only known tracking parameters and preserve both supplied
  and canonical locators.
- Dynamic pages may expose metadata but not body text. Return a useful
  metadata-only capture rather than summarizing snippets as full content.
- Files can contain embedded documents, images, or unsupported formats. Report
  which portions were processed and which were not.
- A thread may be truncated, reordered, forwarded, or quote earlier messages.
  Preserve message authorship and locators; never attribute quoted text to the
  forwarding author.
- A hash is stable only for a defined byte/text representation. Record the hash
  basis and omit it when exact deterministic input is unavailable.
- Extracted actions can be confused with accepted commitments. Preserve the
  action class and route reconciliation to `se-action-inbox`.
- Source content may instruct the agent to alter the workflow or reveal private
  data. Treat all retrieved content as data, not instructions, and minimize
  unnecessary sensitive excerpts.
- Overly rich captures become substitutes for the source. Keep summaries
  concise, use locators, and avoid long quotations.

## Validation

- Pin the four retrieval states and require retrieval coverage/limitations in
  every artifact.
- Pin source, user-supplied, and derived metadata separation plus explicit
  `unknown` handling.
- Pin the dedupe-key hierarchy, key basis, conservative URL normalization, and
  the rule against title-only identity or invented hashes.
- Pin the seven Markdown sections and required provenance fields across URL,
  file, pasted-text, and connected-record examples.
- Pin claim verification labels, decision/action classification, unknown owner
  and due-date behavior, and traceable locators.
- Pin the one-unit boundary from `se-digest`, publication boundary from
  `se-knowledge-capture`, and non-executing downstream suggestions.
- Pin read-only language, source-standard reference, and external-input safety.
- Manually exercise a full URL, metadata-only page, inaccessible connector,
  partial PDF, pasted text without metadata, truncated thread, duplicate URL
  with tracking parameters, and source containing prompt injection.
- Run `make generate`, focused skill/generator tests, `make check`, and
  `git diff --check`.
