---
title: Fix flaky TemporaryDirectory teardown in install test support
status: done
created: 2026-08-14
branch: fix/tempdir-cleanup-flake
---
# Fix flaky TemporaryDirectory teardown in install test support

## Goal

Stop teardown races in the shared temp-directory test base from reporting as
test errors, so a green suite means the code under test is green.

## Background

`tests/install_test_support.py:129`:

```python
tmp = tempfile.TemporaryDirectory()
self.addCleanup(tmp.cleanup)
```

`TempDirTestCase` is the base class for 36 usages across 10 test modules
(`test_update_e2e`, `test_install`, `test_provenance`, `test_generate`,
`test_management`, `test_remove`, `test_release_gate`, `test_skill_review`,
`test_install_core`, `test_frontmatter_conformance`), so anything that races
its cleanup can surface anywhere in the suite, not just in one module.

Several of those tests run `git` inside the temp tree. Git can leave a
short-lived background process (auto-gc after a clone) writing under the tree
while `shutil.rmtree` walks it, and the directory becomes non-empty between
`rmtree`'s scan and its `os.rmdir`.

Observed on PR #223, `unittest (ubuntu-latest, 3.10)`:

```
ERROR: test_update_pulls_and_refreshes_the_installed_tree (test_update_e2e.UpdateEndToEndTest)
  ...
  File ".../tempfile.py", line 882, in cleanup
  File ".../shutil.py", line 662, in _rmtree_safe_fd
    os.rmdir(entry.name, dir_fd=topfd)
OSError: [Errno 39] Directory not empty: 'src'
```

`Ran 739 tests`, `FAILED (errors=1, skipped=6)`. The identical commit passed on
rerun (1m32s), and `ubuntu-3.13` and `macos-3.13` passed on that same head.

The whole traceback is inside `tempfile`/`shutil` cleanup — no assertion is
involved. The test's subject passed; only the teardown failed.

## Requirements

- A teardown race in `TempDirTestCase` must not fail a test whose assertions
  all passed.
- Real test failures must still fail. Suppressing cleanup errors must not
  suppress anything raised by test bodies or by other `addCleanup` callbacks.
- The fix belongs in the shared base class, not in `test_update_e2e` alone —
  every module listed above inherits the same race.
- Python floor is 3.10 (`uv pip compile --python-version 3.10`), so
  `ignore_cleanup_errors=True` is available; confirm it is not gated behind a
  later version before relying on it.

## Acceptance criteria

- [ ] `TempDirTestCase` no longer errors when its temp tree cannot be fully
      removed.
- [ ] Demonstrated against the actual failure mode, not just asserted: hold a
      file open (or leave a stray entry) under the temp tree and show the test
      passes after the change and errors before it.
- [ ] Full suite green on the 3.10/3.13 × ubuntu/macOS matrix.
- [ ] A test body that genuinely fails still fails, and an exception raised by
      a non-temp-dir `addCleanup` still surfaces.

## Notes on approach

`tempfile.TemporaryDirectory(ignore_cleanup_errors=True)` is the one-line
candidate and is almost certainly right. Before taking it, confirm it does not
mask a real leak the suite should care about — a test that leaves processes
alive under its temp tree may be worth fixing at the source instead. If any
module depends on cleanup being strict, say so in the task rather than
silently loosening it everywhere.

Leaked temp trees are a side effect of ignoring cleanup errors. On CI runners
this is irrelevant (ephemeral), but on a developer machine it accumulates under
`/tmp`; note it if it turns out to matter.

## Non-goals

- Rewriting how the install tests set up their fixtures.
- Changing what any test asserts.
- Chasing git's auto-gc behaviour itself.

---

## COMPLETION (2026-08-14)

Shipped in PR #225, fix commit `7bbba64`, merged as `026a06b`.

`tests/install_test_support.py` now builds the temp directory with
`ignore_cleanup_errors=True`, and `tests/test_install_test_support.py` guards
it. Suite on `main`: `Ran 745 tests ... OK`, up from 739, coverage 89.2%.

Criteria against what was actually done:

- **[met]** `TempDirTestCase` no longer errors when its temp tree cannot be
  fully removed.
- **[NOT met as written — substituted]** "hold a file open (or leave a stray
  entry) under the temp tree and show the test passes after the change and
  errors before it."

  This is not achievable, and the criterion was written without knowing that.
  Two attempts failed for reasons worth keeping:

  1. Clearing a directory's write bit does not reproduce the failure, because
     `tempfile`'s cleanup installs an error handler that chmods and retries
     exactly that case. Written and run; observed `AssertionError: OSError not
     raised`.
  2. Raising straight out of a patched `shutil.rmtree` does not either, because
     `ignore_cleanup_errors` acts *through* that handler — a direct raise
     escapes regardless of the flag, so both settings look identical and the
     test cannot discriminate.

  Holding a file open does not work at all on POSIX: an open file does not
  block `unlink`. The production failure is a race against a separate process
  (git auto-gc) and cannot be staged deterministically in-process.

  Substituted: the tests drive `tempfile`'s real error path — the handler it
  passes to `rmtree`, invoked with the exact `ENOTEMPTY`, through `onexc` on
  3.12+ and `onerror` on 3.10/3.11 — and pin that the flag decides whether the
  error escapes. Discrimination is proven by mutation rather than by staging:
  reverting the one-line fix fails
  `test_temp_dir_is_built_to_ignore_cleanup_errors` with `AssertionError: None
  is not True`.

  **What remains unproven:** that the real git-auto-gc race is fixed. The
  mechanism is understood and the flag demonstrably suppresses removal errors,
  but no test reproduces the original race. Confidence rests on the mechanism,
  not on a reproduction.

- **[met]** Full suite green on 3.10/3.13 × ubuntu/macOS — all four matrix legs
  passed on #225.
- **[met]** A failing assertion still fails, and an exception from a
  non-temp-dir `addCleanup` still surfaces. Both pinned by tests.

Residual: leaked temp trees when removal genuinely fails. Accepted and
documented at the call site.
