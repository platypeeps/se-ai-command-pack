## Summary

<!-- 1-3 bullets: what changed and why. Name every behavior change in the diff. -->

## Test plan

<!-- Focused checks first, then the local gate. -->

- [ ] Focused local checks:
- [ ] Local gate: `make check`

## Pre-PR checklist

<!-- Tick each item once confirmed, or replace the box with "N/A -- reason". -->

- [ ] Docs, help text, and env-var references match the changed behavior
- [ ] Failure paths keep state consistent (no mutate-before-success)
- [ ] Helper errors are caught at entrypoints and reported, not raw tracebacks
- [ ] Portability checked (macOS/BSD vs GNU tools, CRLF, Windows paths)
- [ ] A payload change under `templates/` bumps `manifest.json` and adds a
      dated `CHANGELOG.md` heading
- [ ] Review fixes are batched: address all comments, re-run the gate, push once
