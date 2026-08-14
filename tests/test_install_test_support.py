"""Guards on the shared test base class itself.

`TempDirTestCase` backs 36 usages across 10 modules, so a teardown race in it
surfaces as an error in whichever module happened to lose the race — most
recently `test_update_e2e` on the ubuntu-3.10 lane, with the whole traceback
inside `tempfile`/`shutil` and no assertion involved.

**On reproducing the real failure.** The production failure is
`OSError: [Errno 39] Directory not empty`, raised because a git background
process wrote into the tree between `rmtree`'s scan and its `rmdir`. That is a
genuine race against another process and cannot be staged deterministically
in-process. Two cheaper fakes were tried and rejected: clearing a directory's
write bit does not reproduce it, because `tempfile`'s cleanup installs an error
handler that chmods and retries precisely that case; and raising straight out of
a patched `shutil.rmtree` does not either, because `ignore_cleanup_errors` acts
through that handler, so a direct raise escapes whatever the flag is set to and
both settings would look identical.

So `RemovalErrorHandlingTest` drives `tempfile`'s real error path — the handler
it passes to `rmtree`, invoked with the exact errno seen in CI — and pins that
the flag is what decides whether the error escapes. The remaining tests pin that
nothing else about failure reporting changed to buy that tolerance.
"""

from __future__ import annotations

import errno
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from install_test_support import TempDirTestCase


def notempty_error(path: str) -> OSError:
    """The exact failure observed on CI."""
    return OSError(errno.ENOTEMPTY, "Directory not empty", path)


def rmtree_reporting_error(path: str, **kwargs: object) -> None:
    """Stand-in for `shutil.rmtree` that reports a failure the way rmtree does.

    `tempfile` passes `onexc` on 3.12+ and `onerror` on 3.10/3.11, and the two
    take different payloads. Reporting through whichever was supplied is what
    makes this exercise the same branch on every supported interpreter.
    """
    error = notempty_error(str(path))
    # Raised and caught so the handler runs with an active exception, as it does
    # inside the real rmtree: tempfile's handler re-raises bare when the flag is
    # off, and a bare raise outside an except block is a RuntimeError instead.
    try:
        raise error
    except OSError:
        if "onexc" in kwargs:
            handler = kwargs["onexc"]
            handler(os.rmdir, str(path), error)  # type: ignore[operator]
            return
        if "onerror" in kwargs:
            handler = kwargs["onerror"]
            handler(os.rmdir, str(path), (type(error), error, None))  # type: ignore[operator]
            return
        raise


def run_case(case: type[unittest.TestCase]) -> unittest.TestResult:
    suite = unittest.TestLoader().loadTestsFromTestCase(case)
    result = unittest.TestResult()
    suite.run(result)
    return result


class RemovalErrorHandlingTest(unittest.TestCase):
    """The flag, not luck, is what decides whether a removal error escapes."""

    def drive_cleanup(self, *, ignore_cleanup_errors: bool) -> None:
        tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=ignore_cleanup_errors)
        try:
            with mock.patch.object(shutil, "rmtree", rmtree_reporting_error):
                tmp.cleanup()
        finally:
            shutil.rmtree(tmp.name, ignore_errors=True)

    def test_default_propagates_a_removal_error(self) -> None:
        """Control: without the flag this failure reaches the test result."""
        with self.assertRaises(OSError) as caught:
            self.drive_cleanup(ignore_cleanup_errors=False)
        self.assertEqual(caught.exception.errno, errno.ENOTEMPTY)

    def test_ignore_cleanup_errors_swallows_a_removal_error(self) -> None:
        self.drive_cleanup(ignore_cleanup_errors=True)


class TempDirTestCaseTest(unittest.TestCase):
    def test_temp_dir_is_built_to_ignore_cleanup_errors(self) -> None:
        """Pins the fix at its source, so a future edit cannot quietly drop it."""
        seen: dict[str, object] = {}
        real = tempfile.TemporaryDirectory

        def record(*args: object, **kwargs: object) -> tempfile.TemporaryDirectory:
            seen.update(kwargs)
            return real(*args, **kwargs)  # type: ignore[arg-type]

        class Inner(TempDirTestCase):
            def test_passes(self) -> None:
                self.assertTrue(self.base.is_dir())

        with mock.patch.object(tempfile, "TemporaryDirectory", record):
            result = run_case(Inner)

        self.assertTrue(result.wasSuccessful())
        self.assertIs(seen.get("ignore_cleanup_errors"), True)

    def test_base_is_a_resolved_existing_directory(self) -> None:
        captured: list[Path] = []

        class Inner(TempDirTestCase):
            def test_passes(self) -> None:
                captured.append(self.base)
                self.assertTrue(self.base.is_dir())

        result = run_case(Inner)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(captured[0], captured[0].resolve())

    def test_a_failing_assertion_still_fails(self) -> None:
        """Tolerating cleanup errors must not soften real failures."""

        class Inner(TempDirTestCase):
            def test_fails(self) -> None:
                self.fail("deliberate")

        result = run_case(Inner)
        self.assertEqual(len(result.failures), 1)
        self.assertFalse(result.wasSuccessful())

    def test_an_error_from_another_cleanup_still_surfaces(self) -> None:
        """Only the temp-dir removal is forgiven, not every addCleanup."""

        class Inner(TempDirTestCase):
            def test_passes(self) -> None:
                self.addCleanup(self.boom)

            def boom(self) -> None:
                raise RuntimeError("cleanup blew up")

        result = run_case(Inner)
        self.assertEqual(len(result.errors), 1)
        self.assertIn("cleanup blew up", result.errors[0][1])


if __name__ == "__main__":
    unittest.main()
