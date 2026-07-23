# Detect missing AskUserQuestion guidance in skill reviews

## Goal

Extend se-review-skills to identify workflows that should use AskUserQuestion or a verified platform-equivalent for necessary user decisions, then produce bounded evidence-backed enhancement suggestions for those skills.

## Requirements

- Add an explicit interaction-design dimension to `se-review-skills` that
  assesses whether a reviewed workflow has a decision point where structured
  user input is necessary or materially safer than inference.
- Treat `AskUserQuestion` as the named Claude capability and define a portable
  contract for verified platform equivalents, such as Codex structured user
  input. Do not add unsupported tool names or host-only fields to shared
  canonical frontmatter.
- Recommend structured questioning when at least one of these conditions is
  evidenced in the reviewed skill:
  - required input is missing and cannot be discovered safely from available
    context or tools;
  - two or more materially different choices would change scope, authority,
    output, cost, or downstream side effects;
  - user approval is required before an external, destructive, irreversible,
    privacy-sensitive, or otherwise consequential action; or
  - a stated preference is part of the skill's accepted outcome and no safe
    default is established.
- Do not recommend a question when the answer is discoverable, the skill
  already defines a safe and transparent default, the prompt would merely
  restate available context, or the workflow can continue safely while
  accepting an optional later correction.
- Distinguish blocking questions from useful but non-blocking questions.
  Recommend a blocking interaction only when proceeding by assumption would
  materially change the result or exceed the user's authority.
- Require semantic inspection of the decision point. Keywords such as `ask`,
  `confirm`, `choose`, `approve`, or `clarify` may identify candidates but are
  not findings by themselves.
- For every verified finding, identify the owning skill, exact source locator,
  missing decision or approval, why structured input is appropriate, whether
  it blocks progress, the smallest capability-preserving instruction change,
  platform fallback behavior, and a validation method.
- Make enhancement suggestions concrete enough to apply: recommend placement,
  prompt intent, two or three mutually exclusive choices when choices are
  appropriate, the recommended option and tradeoff, and behavior when the user
  does not answer. Do not prescribe choices when free-form input is required.
- Preserve review mode as read-only. Findings and suggestions must not edit the
  affected skills until the user supplies a valid `task=` or `apply=` selector.
- Keep deterministic analysis bounded to candidate discovery and inventory;
  semantic judgment about whether a question is warranted remains in the skill
  review workflow.
- Update the report schema, rubric, and focused contract/behavior tests for the
  new review dimension and output fields. Keep generated or installed skill
  copies synchronized through the repository's normal generation flow.

## Acceptance Criteria

- [ ] The review rubric defines when `AskUserQuestion` or a verified
      platform-equivalent is required, useful-but-optional, or inappropriate.
- [ ] A reviewed fixture with an unresolved consequential choice produces one
      evidence-backed enhancement finding with locator, rationale, blocking
      state, suggested interaction, fallback, and validation.
- [ ] A reviewed fixture with a discoverable answer or explicit safe default
      does not produce a missing-question finding.
- [ ] A fixture containing question-related keywords without an actual user
      decision remains a candidate signal and is not promoted to a finding.
- [ ] Suggestions distinguish mutually exclusive option selection from
      necessary free-form input and do not force an artificial option list.
- [ ] Cross-platform guidance names `AskUserQuestion` where supported and uses
      only verified equivalents or a concise direct-question fallback on other
      targets.
- [ ] Review mode remains read-only, and task/application selectors continue
      to gate every repository mutation.
- [ ] Focused `se-review-skills` tests, repository skill contract tests,
      generated-target checks, and the repository quality gate pass.

## Notes

- Keep `prd.md` focused on requirements, constraints, and acceptance criteria.
- This is a medium, skill-sized task. Keep it in `planning` and add an
  implementation plan before `task.py start` if the report schema requires a
  public-version migration.
- Coordinate with `07-22-se-review-skills-analyzer-hardening` only if candidate
  discovery needs analyzer changes; do not merge its unrelated runtime,
  ownership, or snapshot fixes into this task.
