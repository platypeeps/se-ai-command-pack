# Review the Gemini and Codex Retirements Implementation Plan

## Execution Order

1. **Inventory artifact** — already written:
   `research/inventory-2026-08-26.md`. No further edit.
2. **PRD decisions** — already appended (D1-D5 plus superseding acceptance
   criteria). No further edit.
3. **`CONTRIBUTING.md` note.** Add a short paragraph immediately after the
   vendored-ownership table (the table ending at line 45). Content:
   - `.gemini/**` is Trellis-vendored; edits are reverted by `trellis update`.
   - This pack ships no gemini platform — point at `installer/registry.py`'s
     `PLATFORM_REGISTRY` as the source of truth rather than restating the
     platform names.
   - The gemini command adapters a developer may see on their machine come
     from `sd-ai-command-pack` and install at user level.
   Keep it to one short paragraph. Do not restate the platform list.
4. **Follow-up Trellis task** relaying the gemini decision upstream:
   ```
   python3 ./.trellis/scripts/task.py create \
     "Relay the gemini-CLI retirement decision to sd-ai-command-pack" \
     --description "sd-ai-command-pack ships gemini command adapters; gemini-cli is disabled 2026-12-18. Decide retarget to agy / sunset / drop and what happens to already-installed users." \
     --slug relay-gemini-retirement-sd-pack \
     --priority P2 \
     --no-start
   ```
   `--no-start` is required, not optional: without it `task.py create` makes
   the new task active in this session (`--no-start` is documented as "create
   the task without making it active in this session"), which would hijack the
   current task mid-iteration and desynchronize the work-loop ledger.
   Its PRD must carry: the 2026-12-18 disable date, the three strategy
   options, the user-level install path, and a pointer back to
   `research/inventory-2026-08-26.md` here.
5. **Commit** on a feature branch off `main`.

Dependency order matters only between 3 and 5. Step 4 is independent of 3.

## Validation Plan

Focused, run first:

```bash
python3 .github/scripts/check-trellis-provenance.py
git diff --stat
```

Expect: provenance reports no `uncovered:`/`drifted:`; diff touches only
`.trellis/tasks/**` and `CONTRIBUTING.md`.

Broad gate, run before shipping:

```bash
make check
```

Expect green. This change touches no code path, so a red result means
something unrelated drifted — investigate rather than adapting the change.

## Documentation And Spec Updates

`CONTRIBUTING.md` is the only documentation change. No `.trellis/spec/**`
update is warranted: the finding is about which platforms this pack targets,
which `installer/registry.py` already states executably. Recording it in a
spec would duplicate a fact that has a single authoritative home.

No CHANGELOG entry — this ships no user-visible behavior change.

## Review Notes

Reviewer-sensitive points, stated up front because each looks like an omission:

- **Nothing under `.gemini/**` changed, deliberately.** It is vendored; see
  design Boundaries.
- **The two workflow files and `test_skill_review.py` are untouched
  deliberately.** Their gemini references are the Gemini API and a synthetic
  fixture respectively (PRD D5), not touchpoints.
- **`.codex/config.toml:24` is untouched deliberately.** Its desktop-app
  mention is a warning that protects the bundled CLI (PRD D3).
- **R2 is closed as not-applicable, not as done.** The genuine decision is
  relayed upstream, mirroring how task `08-10` handles work this repo cannot
  land locally.

## Rollback Points

Every step is a documentation or task-record change; rollback is
`git revert` of the single commit. No migration, no generated artifact, no
receipt regeneration. The follow-up task created in step 4 would be archived
separately if the whole change were abandoned.

## Follow-Ups

Explicitly outside this PR:

- The `sd-ai-command-pack` gemini decision itself (relayed as the step-4 task).
- Any `.gemini/**` change, which must originate in `mindfold-ai/Trellis` and
  arrive through a vendored refresh.
- Re-checking after 2026-12-18 that no fleet consumer still installs a gemini
  adapter — belongs to the relayed task, not here.
