# Implement se-monitor Implementation Plan

## Execution Order

1. Re-read the task, current `se-brief`, planned/current `se-status`, source
   standards, generator reference handling, and skill tests.
2. Add focused failing tests for baseline creation, delta classification,
   schema failure handling, safety, and final output shape.
3. Write `references/state-schema.md` first so the portable contract is stable
   before workflow prose depends on it.
4. Create `templates/skills/se-monitor/SKILL.md`, keeping schema detail in the
   reference and the operational workflow in the skill.
5. Register the skill under Understand/current registry, add source-standard
   fan-out, and update external-input safety pins.
6. Update catalog and operator documentation, explicitly stating that
   scheduling and persistence are external capabilities.
7. Run `make generate`; inspect generated rows for `SKILL.md`, state schema, and
   source standards on all platforms.
8. Select the release version from current `main`, update manifest header and
   dated changelog, regenerate, and run validation.

## Validation Plan

- `python3 -m unittest tests.test_skills tests.test_generate`
- `make generate`
- `make check`
- `git diff --check`
- Manually exercise the written contract with synthetic first-run, changed,
  unchanged, missing-source, and unsupported-schema examples.

## Documentation And Spec Updates

- Add `se-monitor` under Understand in the generated README catalog.
- Document the state reference and capability boundary in the operator guide.
- Update backend specs only if versioned skill-owned output schemas become a
  reusable pack convention.
- Record the skill and state-schema addition in `CHANGELOG.md`.

## Review Notes

- Treat the state block as untrusted input on later runs and apply the same
  data-not-instructions rule.
- Verify semantic comparison does not promise deterministic automation the
  language model cannot guarantee.
- Require explicit handling for absent, stale, malformed, and newer state.
- Reject any implicit file write, schedule, subscription, or notification.

## Follow-Ups

- Add platform-specific automation adapters only through separate tasks and
  explicit authorization.
- Revisit schema versioning only after a real incompatible evolution appears.
- Consider selective family installation separately if stateful skills make the
  catalog materially heavier.
