# Refresh sd-ai-command-pack to 0.54.0

## Goal

Install and verify the immutable sd-ai-command-pack 0.54.0 release for SE AI Command Pack.

## Requirements

- Install only the immutable `sd-ai-command-pack` `v0.54.0` release at commit
  `163c104b95871dc315a8e643ffa664b00a723bf5d`.
- Refresh the managed Claude, Gemini, GitHub, and OpenCode payloads using the
  release checkout; do not hand-edit generated payload files.
- Preserve repository-owned files and unrelated work. The refresh must remain
  isolated on `codex/refresh-sd-ai-command-pack-0-54-0` targeting `main`.
- Run `bash scripts/sd-ai-command-pack-housekeeping.sh --self-test` as the
  configured focused candidate check, followed by the repository's complete
  `make check` gate.
- Publish the refresh through the normal PR, routed-review, CI, and
  housekeeping gates. Complete and archive this task through `sd-finish-work`
  before merge.

## Acceptance Criteria

- [ ] Installation provenance reports version `0.54.0`, and the install audit
      passes for Claude, Gemini, GitHub, and OpenCode.
- [ ] The housekeeping self-test passes for the installed candidate.
- [ ] `make check` passes for the exact candidate.
- [ ] Review findings and required CI checks converge on the published PR head.
- [ ] Finish-work validates the completion bundle, archives this task, records
      the session journal, and leaves the merged repository clean and synced.

## Notes

- This is a lightweight fleet-maintenance task; the immutable release and the
  fleet manifest define the implementation boundary.
