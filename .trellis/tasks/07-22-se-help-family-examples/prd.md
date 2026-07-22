# Align se-help family examples with the catalog

## Goal

Make the extended `se-help` examples agree with the generated skill catalog so
family discovery never reports bundled Create or Improve capabilities as absent.

Review snapshot:
`4e4619ac8aab4220a5390e039393b8f58a5af36f34e44efe30be85ac498cd968`.
Finding: `1.6.1.1`.

## Requirements

- Change only the canonical example template
  `templates/skills/se-help/references/examples.md` for the behavioral fix.
- Replace the stale Create-family example with a realistic request routed to a
  currently registered Create skill.
- Replace the stale Improve-family example with a realistic request routed to a
  currently registered Improve skill.
- Preserve honest handling for unknown, external, bundled-but-unavailable, and
  unavailable skills without using a declared nonempty family as the negative
  example.
- Keep the generated catalog authoritative; do not introduce a second manual
  inventory of family membership.
- Add a regression check that family examples cannot claim a registered,
  nonempty family has no bundled capability.

## Acceptance Criteria

- [ ] Create and Improve examples route to registered skills present in the
      current generated catalog.
- [ ] No example says either family is empty or merely planned.
- [ ] Unknown, external, and unavailable capability examples remain honest and
      do not execute another workflow.
- [ ] The example resource contains only registered skill names except where an
      item is explicitly labeled unknown or external.
- [ ] Focused `se-help` tests and generated-surface checks pass.

## Notes

- This is expected to remain a lightweight PRD-only implementation task.
- The regression check may live in the package test suite; the behavioral
  remediation itself must remain under `templates/skills/**`.
