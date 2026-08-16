# Disposition: SD pack registry-snapshot producer parity

This task's deliverable is external. The specification, the design decision it
turns on, and the verification that the external result actually satisfies the
consumer live here; the producer itself lands in `sd-ai-command-pack`.

## Route taken

Upstream pull request, under the explicit per-PR approval recorded in `prd.md`
("Route: upstream pull request (approved)"). That approval covered **one** pull
request against `platypeeps/sd-ai-command-pack` and created no standing
authority.

| | |
| --- | --- |
| Pull request | `platypeeps/sd-ai-command-pack#483` |
| Branch | `feat/registry-snapshot-producer` |
| Base | `eade46ccd116beb086d400b3fd17623fd7bd4382` |
| Head | `40c53aa930f4d7ff68c92a18f394e68e7bd4e98d` |
| Commits | `6e03412f` producer + snapshot, `40c53aa9` release bookkeeping (0.71.25) |
| Merged | squash, `232138a8e98fb5d033e641dd1701cb816fe89ef4`, 2026-08-16T21:27:54Z |

Copilot reviewed 14 of 15 changed files and generated no comments. All nine
required checks passed, including `Release payload gate`.

Confirmed on `main` after the merge by asking the remote rather than trusting the
merge result: `generated/registry-snapshot.json`, 2876 bytes.

Work happened in an isolated `git worktree`, never in the shared clone at
`~/repos/platypeeps/sd-ai-command-pack`, which other sessions hold. The shared
clone was neither checked out, reset, nor branched.

Following the `08-10-review-scope-late-arrival` precedent, `design.md` and
`implement.md` were kept in this repository rather than opening a Trellis task
upstream. The deviation is recorded in `prd.md` under "Planning depth" rather
than left silent.

## The fix

`generate-command-surfaces.py` gains `REGISTRY_SNAPSHOT_PATH`,
`REGISTRY_SNAPSHOT_SCHEMA_VERSION = 1`, and `generate_registry_snapshot_text()`,
registered as **one entry** in the existing `generate_surfaces()` outputs dict.
`prepare-release.py` gains `generated/registry-snapshot.json` in
`PAYLOAD_SINGLETONS`.

The seam matters more than the payload. Because `generate_surfaces()` already
returns `dict[relative_path, content]` and is consumed by both `write_surfaces`
and `run_check`, drift detection and byte-determinism come from machinery
already in place, and `write_surfaces`'s existing `mkdir(parents=True)` creates
the previously absent `generated/` directory with no special handling. No second
code path exists to disagree with the first.

The payload derives from the **imported** registry objects. Re-parsing
`installer/registry.py` with `ast` would have made the producer agree with the
consumer's parser by construction while both drift from the real objects — which
is the failure the parity criterion exists to catch.

`PAYLOAD_SINGLETONS` rather than a `generated/` prefix: a prefix would silently
enrol every future file under `generated/` into the release gate, a decision that
belongs to whoever adds such a file.

## The design decision this task turned on

`_parse_registry` derives `family_order = ()` and `shared_references = {}` for
SD. The first draft of `design.md` read those as real absences and specified
`"familyOrder": []` / `"sharedReferences": {}` for strict parity with the AST.

That was wrong on the facts. SD has `COMMAND_FAMILIES` (5 entries) and
`SHARED_SKILL_REFERENCES` (4 entries); the parser reads the SE names
`FAMILY_LABELS` and `SHARED_REFERENCES` and simply cannot see them. The empties
were parser blind spots, not absences.

Shipping them would have encoded a parser limitation into the file that becomes
the *only* registry source once `08-04-audit-registry-snapshot-ast-removal`
deletes the AST path — discarding real data permanently to satisfy a
transitional comparison, and making SD inconsistent with SE, whose snapshot
ships the real family list.

Acceptance criterion 4 was therefore **split** into criteria 4 and 5: exact AST
agreement on the three fields the AST can derive, and assertion against the
imported objects for the two it cannot. That is stricter than the original
single criterion, not weaker — strict AST parity would have accepted empty for
both fields and passed.

## Acceptance criteria

Every quotation below is output from a run at head `40c53aa9` unless stated.

- [x] **Approval obtained and recorded before any change was proposed.** Granted
      2026-08-16, recorded in `prd.md` under "Route" before the first SD file was
      written.

- [x] **SD ships `generated/registry-snapshot.json` at `schemaVersion` 1 with all
      five keys, produced by its surface generator.**

      ```
      ['familyOrder', 'platforms', 'schemaVersion', 'sharedReferences', 'skills']
      1 20 18 5 4
      ```

      Produced by the generator, not hand-written: with the generator restored
      from BASE the file is not recreated (see the falsifiability criterion).

- [x] **In an SD checkout, `skill_review.py` resolves the snapshot and does not
      call `_parse_registry`.** `_parse_registry` was monkeypatched to raise and
      the inventory still succeeded, `rc=0`, `selectedSkills: 20`. "It still
      works" would not have shown this; a patched-to-raise parser does.

      Control arm, so the probe is not vacuous: with the snapshot moved aside and
      the same patch applied, the run engages the fallback instead. Both arms
      were established, not only the one being shipped.

- [x] **The three AST-derivable fields agree exactly.**

      ```
      PASS  G2a families
      PASS  G2a skill_order
      PASS  G2a platforms
      ```

      Compared on the same checkout by loading the real consumer and calling
      `_load_registry_snapshot` and `_parse_registry` directly.

- [x] **The two AST-blind fields match the imported registry objects.**

      ```
      PASS  G2b family_order
      PASS  G2b shared_references
      AST-derived counts: families=20 skills=20 platforms=18 family_order=0 shared_references=0
      ```

      The trailing line is the point: the AST yields 0 and 0 for exactly these
      two fields, which is why they are asserted against `COMMAND_FAMILIES` and
      `SHARED_SKILL_REFERENCES` rather than against the parser.

- [x] **`--check` fails on an induced drift.** Two `CommandInfo` entries
      reordered in `installer/registry.py`:

      ```
      drift: generated/registry-snapshot.json
      exit=1
      ```

      After a full restore: `check: 87 generated surfaces match the committed
      tree`, `exit=0`.

      A first attempt at this gate substituted a `family=` keyword and failed
      because the entries are positional; a second tripped
      `validate_command_registry` instead of the byte-compare, so it never
      exercised the snapshot at all. Only the third attempt — a valid reorder —
      actually tested the criterion. Recorded because two of the three attempts
      would have been reportable as passes by a less specific check.

- [x] **Re-running the generator on an unchanged registry produces byte-identical
      output.** Two consecutive runs:

      ```
      surfaces: 87 generated, 0 written, 87 unchanged
      porcelain-after-1: []
      porcelain-after-2: []
      ```

- [x] **The release gate treats the snapshot as shipped payload.** Induced, not
      read. Unbumped:

      ```
      release prep: failed: shipped payload changed without a manifest version bump relative to eade46ccd116beb086d400b3fd17623fd7bd4382: generated/registry-snapshot.json
      exit=1
      ```

      The snapshot is the *only* path named, which is also the evidence that the
      `PAYLOAD_SINGLETONS` entry is what enrolled it — before that entry,
      `generated/` matched neither `PAYLOAD_SINGLETONS` nor
      `PAYLOAD_PREFIXES = ("templates/", "plugins/")`.

      After bumping `manifest.json` to 0.71.25, restamping
      `plugins/sd/.claude-plugin/plugin.json`, and adding
      `## 0.71.25 - 2026-08-16`:

      ```
      release prep: exact candidate evidence and shipped-surface closure are current
      exit=0
      ```

- [x] **Only `.trellis/` task artifacts change in this repository.**

      ```
      $ git status --porcelain | grep -v '^.. \.trellis/' || echo "boundary clean"
      boundary clean
      ```

      Run in `/Users/sven/repos/platypeeps/se-ai-command-pack`, confirmed by
      `pwd`, after a first invocation had run in the worktree instead and would
      have reported a vacuous pass.

### Additional gates beyond the criteria

- **`make check` exits 0** in the worktree, 0 `FAIL` lines.

  A prior invocation reported three failures — `test_full_check_script_runs_pack_source_drift_gates`,
  `test_pack_source_drift_gate_accepts_payload_with_version_bump`,
  `test_pack_source_drift_gate_runs_for_sd_manifest_identity` — all with
  `error: release version gate cannot compare committed payload changes because
  base ref 'eade46cc…' does not resolve`. Cause was mine, not the branch's: I had
  exported `SD_AI_COMMAND_PACK_FULL_CHECK_RELEASE_BASE_REF` for the release-gate
  proof and it leaked into tests that build throwaway repositories where that SHA
  does not exist. Re-run without the export: `exit=0`. Recorded rather than
  quietly re-run.

- **Falsifiability from BASE.** With `generate-command-surfaces.py` restored from
  `eade46cc` and the snapshot deleted:

  ```
  surfaces: 86 generated, 0 written, 86 unchanged
  snapshot present: False  loaded: False
  FAIL  snapshot resolved (returned None -> consumer falls back to AST)
  parity-exit=1
  ```

  86, not 87: the generator without this change does not produce the file, and
  the consumer falls back exactly as before. Restored afterwards; parity returns
  to `parity-exit=0`. `git checkout <base> -- <file>` throughout, never
  `git stash`, and only after the branch was committed.

## The verification hazard that cost the most time

The `--check` restore arm failed for a while in a way that looked like generator
nondeterminism and was not.

`git status --porcelain` reported a clean tree, `git diff $BASE HEAD --
installer/registry.py` was empty, `md5` of the file matched the HEAD blob — and
`--check` still reported `drift: generated/registry-snapshot.json` plus
`manifest.json` and the sd-help command catalog. Importing the module from that
clean tree returned `['sd-help', 'sd-continue', 'sd-status', ...]` while the
source read `sd-help`, `sd-status`, `sd-continue`.

Two independent causes, both worth carrying forward:

1. **Stale bytecode survived a byte-identical-size restore.** The induced drift
   was a *reorder* of two `CommandInfo` lines, which leaves the file size
   unchanged, and the restore landed in the same wall-clock second as the
   tampered compile. Python validates a `.pyc` on source mtime (seconds) and
   size, so `installer/__pycache__/registry.cpython-314.pyc` was accepted and the
   tampered registry kept being served from a clean tree. An earlier attempt to
   clear `__pycache__` did not settle it because the very next generator run
   recreated the cache before the state was re-measured.
2. **The tampered run had written other generated files.** A write-mode run under
   the tampered registry rewrote `manifest.json` and the catalog too;
   `git checkout -- installer/registry.py` restored one file out of four.

The general lesson, which `implement.md` now carries: an induced-drift gate must
restore *everything the tampered run touched* and clear the bytecode cache, or
the restore arm reports a defect in the code under test that belongs to the test
harness.

## Planning adversarial review

The blocking-concern ledger was not maintained as a separate document for this
task. What the contract exists to catch was nevertheless caught and is recorded
in the artifacts themselves rather than claimed here:

- **C-1 (blocking, resolved before implementation).** `design.md` specified
  `"familyOrder": []` / `"sharedReferences": {}`. Refuted by measuring the
  imported objects: 5 families, 4 shared references. Corrected across `prd.md`,
  `design.md` and `implement.md`; criterion 4 split into 4 and 5. This is the
  single largest planning error in the task and the correction made the criteria
  stricter.
- **C-2 (blocking, resolved before implementation).** An earlier hypothesis held
  that SD's AST registry might be near-empty and replaceable with an empty
  `RegistryData`, removing the need for a snapshot at all. Refuted by
  measurement — 20 families, 20 skills, 18 platforms — and discarded. Recorded in
  `prd.md` under "Verification of this PRD's premise".
- **C-3 (non-blocking, resolved).** The payload gate was assumed to cover
  `generated/`. Verified instead: `PAYLOAD_PREFIXES = ("templates/", "plugins/")`
  matches neither, so criterion 7 would have failed. Fixed by the
  `PAYLOAD_SINGLETONS` entry.
- **C-4 (non-blocking, resolved 2026-08-16).** `implement.md` Step 1 claimed two
  of the four registry symbols still needed importing; all four were already
  imported at `generate-command-surfaces.py:66-87`. It also named the constant
  and function differently from the shipped code. Corrected in place.

No approval is claimed from a review lane that did not run. The host lane is the
only lane; the pack ships no second one.

## What this repository is left holding

No shipped file here changed — no source, no template, no generated payload.
This repository holds the specification, the design decision, the verification
record, and this disposition. `skill_review.py` is untouched, including
`_load_registry_snapshot`, the fallback branch, and
`SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS`.

Two couplings outlive this task:

- **Schema-version skew.** SD hardcodes `schemaVersion` 1. If this pack ever
  widens `SUPPORTED_REGISTRY_SNAPSHOT_SCHEMA_VERSIONS`, SD's snapshot must move
  in the same release or SD checkouts fail closed — a malformed or
  unrecognized-version snapshot raises rather than falling back.
- **`08-04-audit-registry-snapshot-ast-removal` is unblocked by the merge**, not
  by the PR existing. Its precondition is that SD actually ships the snapshot.
