# Implement — Repomix map policy decision (A-025)

Policy (a): gitignore `docs/repomix-map.md`, generate on demand. See design.md.

## Preconditions

- [ ] On a fresh feature branch off `main` (via `task.py start` / sd flow).
- [ ] `trellis-before-dev` guidance loaded for the touched packages.

## Ordered steps

1. **Verify not a payload/manifest target.**
   - `grep -rn "repomix-map" installer/ manifest.json .sd-ai-command-pack/manifest.json`
     (the payload manifest is lowercase `manifest.json`, not `MANIFEST*`) and
     confirm the map is not an installed pack target. install-audit already
     excludes it; confirm no manifest entry would break `pack.install-audit`.
   - Validation: `bash scripts/sd-ai-command-pack-toolchain.sh run-python -- scripts/sd-ai-command-pack-check.py --repo . --json` still passes `pack.install-audit` after later steps.

2. **Gitignore + untrack.**
   - Add `docs/repomix-map.md` to `.gitignore` (near other generated-artifact
     entries).
   - `git rm --cached docs/repomix-map.md` (keep working-tree copy).
   - Validation: `git status` shows the path staged as deleted-from-index and
     now ignored; `git check-ignore docs/repomix-map.md` prints the path.

3. **Update `tests/test_repomix.py`.**
   - Rename `test_checked_in_map_matches_scope_contract` →
     `test_generated_map_matches_scope_contract_when_present` and guard with
     `@unittest.skipUnless(MAP_PATH.exists(), "map is generated on demand and gitignored")`.
   - Keep the config-contract test unchanged.
   - Validation: `make test` — the repomix tests pass locally (map present);
     confirm the renamed test SKIPS when `MAP_PATH` is temporarily absent
     (reason: proves CI-safety) — verify by reasoning/one-off, then restore.

4. **Update spec `quality-guidelines.md`.**
   - §3 Contracts: note the map is gitignored and generated on demand, never
     committed.
   - §4 Validation matrix: replace the "Configuration changes → Regenerate and
     commit" row with "Regenerate on demand; the map is gitignored and never
     committed."
   - §5 Good case: "replaces the tracked map" → "replaces the local generated
     map."
   - Validation: `knowledge.obsidian-kb` / spec consistency checks in
     `sd-check` still pass.

5. **Update `README.md` (~line 467).**
   - Reword so the map is described as an on-demand, gitignored artifact; keep
     `make repomix`. Do not present the linked file as checked in.
   - Validation: `pack.review-preflight` doc-path check passes (no broken
     required references introduced).

6. **Confirm every consumer is absence-safe.**
   - `grep -rn "repomix-map" scripts/ tests/ .trellis/spec/ README.md` and
     confirm each hit is: excluded, present-or-absent safe, skip-guarded, or an
     inert diff-scope classifier. Record the list in the check pass.

## Validation gate (before ship)

- [ ] `make repomix` exits 0 and regenerates the map after untracking (proves
      the primary on-demand workflow still works, and the regenerated file stays
      gitignored). Security scan reports no suspicious files.
- [ ] `make test` green (repomix tests included; suite hermetic).
- [ ] `bash scripts/sd-ai-command-pack-toolchain.sh run-python -- scripts/sd-ai-command-pack-check.py --repo . --json` → all checks pass.
- [ ] `git check-ignore docs/repomix-map.md` prints the path; `git ls-files docs/repomix-map.md` prints nothing.
- [ ] Acceptance criteria in prd.md all satisfiable and re-checked.

## Ship

- sd-ship `until=merge`. PR body MUST include the "Tooling/generated scope:"
  section (the diff removes the 1.1 MB tracked file → tooling/generated scope).

## Rollback point

- Revert the single feature commit; the map returns to tracked state with no
  data loss (generation is deterministic).
