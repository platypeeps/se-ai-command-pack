# Refresh sd-ai-command-pack to 0.71.38

## Goal

Fleet refresh: install sd-ai-command-pack v0.71.38 (tag v0.71.38 @ 6881aaa3f34fbcc46fddb72ea21476ededc52e58, payload sha256:4046b21a45352cc96aca01dc8578a3be5c2f045c0f878930d0bd2bd9fe8de5e3) into se-ai-command-pack. Managed scope: installer-managed platform files (claude, gemini, github, opencode), receipts, provenance, and the deterministic repomix map only; no product-code edits. Prepare: none declared (this repo owns neither the repomix generator nor docs/repomix-map.md). Check: bash "$HOME/.agents/bin/sd-ai-command-pack-housekeeping.sh" --self-test. Bound to refresh branch chore/pack-refresh-0.71.38 off base 800483dd7606f6fd1e640a9e06b7a96a2cfe8fdc. Completion: PR opened, remote review converged, CI green, merged via housekeeping, post-merge audit confirms 0.71.38.

## Requirements

- Install sd-ai-command-pack v0.71.38 (tag `v0.71.38` @ `6881aaa3f34fbcc46fddb72ea21476ededc52e58`, payload `sha256:4046b21a45352cc96aca01dc8578a3be5c2f045c0f878930d0bd2bd9fe8de5e3`) for exactly the claude, gemini, github, and opencode platforms recorded in the fleet manifest.
- Repair the executable bit on `.sd-ai-command-pack/bin/sd-ai-command-pack-review-layout.py`, tracked here as `100644`. This is the payload this release exists to deliver: 0.71.36 corrected the bit in the pack, but the installer returned `unchanged` as soon as a destination's bytes matched, before considering its mode, so no reinstall at any version could have applied it. 0.71.38 fixes that, and the mode change is expected to appear in this diff.
- Limit the diff to installer-managed platform files, `.sd-ai-command-pack/` manifest and provenance receipts, and this task's own `.trellis/` bookkeeping. No product-code edits.
- Run the manifest-ordered check command for this consumer (`bash "$HOME/.agents/bin/sd-ai-command-pack-housekeeping.sh" --self-test`) before the local gate. This consumer declares no preparation step.
- Keep the refresh on branch `chore/pack-refresh-0.71.38` off base `800483dd7606f6fd1e640a9e06b7a96a2cfe8fdc`, published as a single PR.
- Carry no `trellis update` diff. Trellis version drift is owned separately; a mixed PR stops the lane instead of merging.

## Acceptance Criteria

- [ ] The sd-ai-command-pack install audit passes for all four expected platforms and reports installed payload provenance 0.71.38. It runs from the sd-ai-command-pack source checkout, not from this repository: `python3 scripts/sd-ai-command-pack-install-audit.py --repo <this repository> --expected-platform ...`.
- [ ] `git ls-files -s .sd-ai-command-pack/bin/sd-ai-command-pack-review-layout.py` reports mode `100755`, not `100644`. A refresh that leaves it `100644` has not delivered this release and must not merge.
- [ ] `bash "$HOME/.agents/bin/sd-ai-command-pack-housekeeping.sh" --self-test` passes.
- [ ] The repository's documented deterministic gate passes, or its only findings are dispositioned through the fleet finding severity gate with zero blockers.
- [ ] The refresh is published as one PR whose head carries the work commit plus this task's archive and journal bookkeeping.

## Post-archive handoff

Owned by the fleet campaign after this task is archived, not by its acceptance
criteria: remote review convergence, CI settle, merge through the consumer
housekeeping gate, refresh-branch deletion, default-branch sync, and the
post-merge audit that confirms the installed pack version is 0.71.38.
