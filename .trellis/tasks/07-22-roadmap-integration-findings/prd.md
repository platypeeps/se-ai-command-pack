# Resolve skill roadmap integration findings

## Goal

Close FIR-01 and FIR-02 from the parent final integration review: remove the public se-weekly-review America/Denver fallback in favor of explicit/private timezone resolution, add se-review-skills operator-guide coverage, pin both with focused tests, regenerate shipped surfaces, and make the required release decision without implementing the unapproved worklog proposals.

## Requirements

- Change only the canonical `se-weekly-review` template. Resolve timezone from
  an explicit invocation value first, then an authorized private worklog-profile
  value. If neither exists, ask for the timezone or stop; never guess a named
  locale or silently use a host default.
- Preserve the existing local-date, daylight-saving-time, and half-open
  reporting-window semantics after timezone resolution.
- Document `se-review-skills` in the operator guide as bounded skill or package
  review. Distinguish it from `se-help`, `sd-audit-repo`, and
  `sd-review-local`, and preserve its review-only default plus explicit later
  selector for applying improvements or creating tasks.
- Add focused regression coverage for the timezone-resolution contract and for
  complete registry coverage in the operator guide.
- Regenerate all derived surfaces from canonical sources. Because the weekly
  review template is shipped payload, bump the manifest version, add a matching
  dated changelog entry, and keep all three platform payloads byte-identical.
- Keep examples and tests synthetic and path-neutral. Do not introduce a
  public profile loader, platform-specific skill variant, or new installer
  configuration mechanism.

## Acceptance Criteria

- [ ] The canonical `se-weekly-review` template contains no `America/Denver`
      fallback and defines precedence as explicit timezone, then an authorized
      private worklog-profile timezone, then ask or stop.
- [ ] Focused tests fail for any named/default locale fallback and pin the
      required unresolved-timezone behavior without weakening reporting-window
      or DST semantics.
- [ ] `docs/SE_AI_COMMAND_PACK.md` covers every registered skill, including a
      clear `se-review-skills` boundary against `se-help`, `sd-audit-repo`, and
      `sd-review-local`.
- [ ] Tests fail when a registered public skill is omitted from the operator
      guide.
- [ ] Generated payloads remain flat and identical across Agents, Claude Code,
      and Codex, with a manifest version bump and matching changelog entry.
- [ ] `make generate`, focused tests, `make check`, an all-platform temporary
      installer dry-run, and `git diff --check` pass.
- [ ] No `se-worklog` payload, private automation, private destination value,
      schedule, path, or write-back behavior is created or changed.

## Out of Scope

- Implementing the approved-but-unplanned public `se-worklog` concept.
- Creating or modifying private worklog automation, destinations, schedules,
  write-back, or private operational values.
- Adding platform-specific copies, target-tool frontmatter, or a public profile
  subsystem.

## Notes

- Source findings: FIR-01 and FIR-02 in
  `../07-17-se-skill-roadmap/final-integration-review.md`.
- This concrete closure task is intentionally not added to the parent child
  list; that list remains the exact 50-child roadmap delivery record.
