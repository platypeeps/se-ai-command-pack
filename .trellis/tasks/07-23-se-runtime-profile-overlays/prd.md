# Add per-target runtime profile overlays

## Goal

Turn the runtime recommendations produced by the SE skill review into validated,
host-specific behavior where the host supports it, without weakening the
portable canonical skill contract or creating hand-maintained platform copies.

The first supported runtime overlay is Claude Code. Its installed `SKILL.md`
files should expose the reviewed invocation, fork, model, and effort choices.
Codex and the shared Agent Skills target must continue to receive portable
`name`/`description` frontmatter because their verified skill contracts do not
support the same selectors.

## Requirements

- Keep `templates/skills/<name>/SKILL.md` as the only authored skill body and
  keep its frontmatter limited to `name` and `description`.
- Add a registry-owned runtime profile model that records each skill's:
  invocation mode, context mode, model profile, and effort.
- Cover every registered skill exactly once. Reject missing, duplicate, unknown,
  or unregistered assignments before generation writes any files.
- Resolve the review report's duplicate `se-evaluate` classification in favor
  of the more specific independent recommendation: forked, deep, high effort.
- Translate portable profiles to Claude Code only through an explicit,
  allowlisted adapter:
  - `user-only` -> `disable-model-invocation: true`;
  - `both` -> no invocation override;
  - `forked` -> `context: fork`;
  - `inline` -> no context override;
  - `fast` -> `model: haiku`;
  - `balanced` -> `model: sonnet`;
  - `deep` -> `model: opus`;
  - `inherit` -> `model: inherit`; and
  - effort -> the matching validated Claude effort value.
- Do not translate `fresh-session` to `context: fork`: a new independent
  session and a forked subagent are different isolation contracts. Apply the
  supported invocation/model/effort fields for that profile and leave context
  unset.
- Fail closed on an unsupported platform field, unknown portable profile value,
  unknown Claude model alias, or invalid effort value.
- Generate committed Claude-specific `SKILL.md` payloads from canonical
  frontmatter/body plus the registry overlay. Do not allow manual platform body
  edits or platform-specific resources.
- Point only Claude `SKILL.md` manifest rows at the generated payloads. Continue
  to point shared-agent and Codex rows, plus every resource row, at canonical
  templates.
- Include all derived Claude files in `--check` drift detection and in the
  generator's coordinated write/rollback behavior so a failure cannot leave a
  partially updated payload or manifest.
- Preserve deterministic ordering, source/target path safety, installer
  provenance, dry-run behavior, user-file conflict protection, and Python 3.10
  compatibility.
- Treat this as a shipped payload change: bump the pack version and add a
  matching changelog entry.
- Update the backend specification to document the new registry and generated
  platform-overlay contract.

## Acceptance Criteria

- [x] Every value in `SKILL_NAMES` has exactly one validated runtime profile.
- [x] Generated Claude skills preserve each canonical body byte-for-byte and
      merge only allowlisted frontmatter keys in deterministic order.
- [x] At least one forked skill contains `context: fork`, a reviewed model
      alias, and its reviewed effort in the installed Claude payload.
- [x] User-only Claude skills contain `disable-model-invocation: true`; skills
      available to both callers do not.
- [x] `se-red-team` receives its user-only/deep/xhigh selectors but does not
      receive `context: fork` for the `fresh-session` recommendation.
- [x] Codex and shared-agent `SKILL.md` payloads remain byte-identical to the
      canonical templates and contain no Claude-only keys.
- [x] Generator tests reject incomplete/duplicate assignments, unsupported
      fields, unknown model aliases, and unknown effort values without partial
      writes.
- [x] Manifest tests prove that only Claude `SKILL.md` source rows use generated
      paths and all other payload fan-out remains unchanged.
- [x] Installer tests verify the platform-specific installed bytes, refresh
      idempotence, conflict preservation, and backup behavior.
- [x] `make generate` is idempotent; `make check` and `git diff --check` pass.
- [x] Manifest version, `CHANGELOG.md`, generated payloads, and release checks
      agree.

## Notes

- Codex `agents/openai.yaml` is UI metadata, not a model/fork execution control,
  so it is outside this task unless a separate requirement is approved.
- A Claude alias is intentionally preferable to a pinned model version: the
  alias expresses the reviewed capability tier while allowing the host and
  account provider to resolve an available current model.
