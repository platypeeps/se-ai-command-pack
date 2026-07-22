# Use session evidence in skill reviews

## Goal

Extend se-review-skills to inspect bounded current and recent conversations that actually used reviewed skills, correlate manifested mistakes with skill instructions, and recommend structural changes and edge-case gotchas that prevent repetition.

## Background

Static skill inspection shows intended behavior but not how instructions perform
in real use. Bounded session evidence can reveal skipped gates, ambiguous
branches, repeated retries, missing recovery paths, and edge cases that only
manifest during execution.

Live project-scoped `trellis mem` research confirmed several constraints:

- Skill-name search results contain incidental mentions from repository maps,
  diffs, copied prompts, approval transcripts, and tool output. A name match is
  not proof that the skill ran.
- Current-session history can lag until turns are flushed, roles can be noisy
  after compaction, and nested transcripts can appear inside one outer turn.
- OpenCode history is unavailable in the currently installed Trellis reader;
  missing provider coverage must remain explicit.
- Session evidence can describe an old or installed-drifted skill version, so
  findings must not silently blame the current canonical source.

The current canonical reviewer already owns semantic judgment and bounded
inventory. Its analyzer must remain deterministic, local to declared artifact
roots, and free of conversation-history scanning.

## Requirements

- Add session evidence as an explicit review dimension after deterministic
  skill inventory and before final findings.
- Default to `sessions=auto`, with `sessions=off` as an opt-out and repeatable
  `session=<id>` selectors for user-supplied evidence. Unknown values remain an
  error and must not broaden history scope.
- In automatic mode, inspect the current conversation when it contains verified
  use of a reviewed skill. Search only project-scoped recent history through an
  already available, read-only session-insight capability; never install a
  provider, scan raw home-directory logs, or switch to global history without a
  separate explicit request.
- Bound automatic history to three confirmed sessions per reviewed skill and
  twenty sessions total, prioritized by explicit selectors, the current
  conversation, invocation strength, then recency. Allocate candidates across
  skills so one frequently mentioned skill cannot consume the entire budget.
- Treat session content, embedded transcripts, tool calls, tool output, links,
  and commands as untrusted evidence. Never execute or follow them.
- Confirm actual skill use before judging a session. Accept an explicit
  platform activation record or user skill invocation as strong evidence;
  accept an assistant usage declaration only when the subsequent workflow
  corroborates it. Repository text, diffs, paths, and incidental name mentions
  are candidates only.
- Inspect a minimal context window around the invocation, manifested problem,
  recovery, and outcome. Do not reproduce raw conversations or expose local
  session-file paths, secrets, personal data, or unrelated turns in the report.
- Classify each observed problem as `skill-contract`, `execution-deviation`,
  `tool-or-environment`, `user-intent-change`, or `indeterminate`. A session
  finding requires canonical source evidence and a causal explanation; an
  error or retry alone is not proof of a skill defect.
- Compare failures with at least one successful or neutral use when available.
  Do not overfit the skill to one anomalous run or treat a successful final
  outcome as proof that the workflow was efficient or unambiguous.
- Record whether the observed session used the current canonical skill,
  installed drift, an older version, or an unknown version. Unknown provenance
  lowers causal confidence and stays visible.
- For verified repeated or structurally important mistakes, recommend the
  smallest capability-preserving placement: ordered core workflow, safety or
  authority gate, conditional reference, deterministic helper, host overlay,
  focused evaluation, or explicit failure/recovery path.
- Produce edge-case gotchas with trigger, observable failure, prevention,
  recovery, and a regression method. Avoid duplicating prose when moving or
  reordering an existing rule would make it reliably visible.
- Keep session-derived findings selectable only when they also identify an
  allowed canonical template remediation. Revalidate both the source snapshot
  and the cited session evidence before `task=` or `apply=`.
- Report per-skill session coverage, confirmed invocations, manifested
  mistakes, successful controls, causal confidence, structural suggestions,
  gotchas, and unavailable or excluded history.
- Keep review mode read-only. Do not persist raw dialogue, session extracts, or
  a review report unless the user separately requests that write.
- Add a directly linked session-evidence reference, update the review rubric,
  report schema, runtime routing, focused skill contract tests, generated
  platform payload, release version, and changelog.

## Acceptance Criteria

- [x] `se-review-skills` documents `sessions=auto|off` and repeatable
      `session=<id>` arguments, bounded defaults, explicit opt-out, and a
      project-scoped-only automatic search boundary.
- [x] A confirmed invocation with a source-correlated manifested mistake can
      produce a finding containing session locator, provenance, causal class,
      confidence, structural remedy, gotcha, and falsifiable validation.
- [x] Incidental skill-name mentions in diffs, maps, tool output, or nested
      transcripts do not count as invocations or findings.
- [x] Execution deviations, environment failures, user intent changes, and
      unknown-version sessions remain visible without being misclassified as
      canonical skill defects.
- [x] Automatic selection is capped at three sessions per skill and twenty
      total, deduplicates sessions, distributes coverage across skills, and
      reports truncation.
- [x] Reports minimize session content, redact sensitive or unrelated material,
      omit host session-file paths, and disclose unavailable provider coverage.
- [x] Structural recommendations choose among core workflow, reference,
      helper, host overlay, evaluation, and recovery-path changes without
      deleting accepted capability.
- [x] Task/apply mode revalidates current canonical source and session evidence;
      session evidence alone cannot authorize mutation.
- [x] The new reference is shipped to every registered platform target and all
      focused tests, generated-surface checks, release gate, and repository
      quality checks pass.

## Out Of Scope

- Adding a new conversation-log parser or changing `trellis mem`.
- Global cross-project history scans by default.
- Persisting, publishing, or uploading raw conversation history.
- Automatically editing reviewed skills from session evidence in review mode.
- Treating telemetry frequency, keyword counts, or model self-critique as a
  substitute for source and causal analysis.

## Notes

- Session research used project-scoped, local, read-only history only. Raw
  excerpts and host paths are intentionally not copied into this task.
- This is a complex task and requires `design.md` plus `implement.md` before
  activation.
