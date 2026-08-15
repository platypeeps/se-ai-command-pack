#!/usr/bin/env python3
"""Re-run the inverted-evidence assertion for every ledger finding marked `fixed`.

Acceptance evidence for task 08-15-audit-ledger-reconcile. Not repo tooling and
deliberately not wired into `make check`: it pins the tree as it stood when the
ledger was reconciled, so it is expected to rot as the repository moves on.

The script reads the ledger to discover which findings claim `fixed`, rather
than taking that list as an argument. A `fixed` finding with no registered
assertion is a failure, not a skip -- that is what stops the check from being a
restatement of whatever was just written into the ledger.

Exit codes: 0 all assertions hold; 1 a contradiction or an unregistered
`fixed` finding; 2 the ledger could not be read.
"""

from __future__ import annotations

import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
LEDGER = REPO / ".trellis" / "audit" / "ledger.md"


@lru_cache(maxsize=None)
def read(relative: str) -> str:
    """Read a repo-relative file once. Several findings cite the same file --
    Makefile, tests.yml, and CONTRIBUTING.md are each read by three
    assertions -- so the cache keeps one pass over the tree per file."""
    path = REPO / relative
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def exists(relative: str) -> bool:
    return (REPO / relative).exists()


@lru_cache(maxsize=None)
def tracked(relative: str) -> int:
    """Count of paths git tracks under `relative`.

    Cached for the same reason `read` is: an assertion that both tests a count
    and reports it names the same path twice, which would otherwise spawn git
    twice for one answer."""
    result = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "--", relative],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    return len([line for line in result.stdout.splitlines() if line.strip()])


def revision() -> str:
    """The HEAD this run's assertions were actually evaluated against.

    Printed before the results because the assertions pin a specific tree. A
    bare pass read months later says nothing without the revision it passed
    at, and this script is expected to rot."""
    result = subprocess.run(
        ["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    return result.stdout.strip() or "unknown"


SKILL_REVIEW = "templates/skills/se-review-skills/scripts/skill_review.py"
GENERATOR = ".github/scripts/generate-skill-surfaces.py"
WORKFLOW = ".github/workflows/tests.yml"

# One assertion per finding marked `fixed`. Each returns (holds, observation).
# The assertion must test the *defect being gone*, never merely that a file
# moved: A-018 is the cautionary case, where the variables relocated but the
# finding was about UID qualification.
CHECKS = {
    "A-001": lambda: (
        tracked(".claude") > 0,
        f"{tracked('.claude')} tracked .claude files",
    ),
    "A-003": lambda: (
        "GENERATED_REFERENCES_DIR}/skill-catalog.md" in read(GENERATOR),
        "HELP_CATALOG_SOURCE resolves under the generated references dir",
    ),
    "A-004": lambda: (
        "Repo-own source vs vendored installs" in read("CONTRIBUTING.md"),
        "CONTRIBUTING documents the ownership split",
    ),
    "A-006": lambda: (
        "def test_argument_vocabulary_conformance" in read("tests/test_skills.py"),
        "argument-vocabulary conformance test present",
    ),
    "A-007": lambda: (
        "Reverse citation-closure" in read(GENERATOR),
        "generator validates reverse citation closure",
    ),
    "A-009": lambda: (
        read(SKILL_REVIEW).count("def _is_within(") == 0,
        "the duplicate _is_within predicate is gone",
    ),
    "A-010": lambda: (
        exists("tests/test_frontmatter_conformance.py"),
        "a conformance test binds the two grammars",
    ),
    "A-011": lambda: (
        "_PROCESS_UMASK" in read("installer/fileops.py"),
        "umask captured once at import, not per installed file",
    ),
    "A-012": lambda: (
        "verifying identity" in read("scripts/sd-ai-command-pack-work-loop.py"),
        "stale-lock unlink re-checks identity",
    ),
    "A-013": lambda: (
        "timeout=GIT_TIMEOUT_SECONDS" in read("installer/management.py"),
        "_run_git is bounded",
    ),
    "A-014": lambda: (
        "TimeoutExpired" in read(".github/scripts/create-release-tag.py"),
        "git timeout and missing-git are caught",
    ),
    # Absence alone would be the "it moved" fallacy, so this also asserts the
    # replacement is bounded.
    "A-015": lambda: (
        "hasNextPage" not in read("scripts/sd-ai-command-pack-housekeeping.sh")
        and "exceeds 1000 rows" in read("scripts/sd-ai-command-pack-review.py"),
        "the shell loop is gone and the replacement caps accumulation",
    ),
    "A-017": lambda: (
        "Source-trust gate" in read("installer/management.py"),
        "update gates the recorded source path before git or exec",
    ),
    "A-018": lambda: (
        "os.getuid()" in read("scripts/sd_ai_command_pack_lib.py"),
        "cache root is UID-qualified",
    ),
    "A-019": lambda: (
        "_open_exclusive_backup" in read("installer/fileops.py"),
        "backup opens exclusively instead of shutil.copyfile",
    ),
    "A-020": lambda: (
        "--fail-under" in read("Makefile"),
        "coverage floor enforced in the Makefile",
    ),
    "A-021": lambda: (
        "env=git_env()" in read("tests/test_release_gate.py"),
        "subprocess git tests scrub the environment",
    ),
    "A-022": lambda: (
        exists("tests/test_update_e2e.py"),
        "update has an end-to-end test",
    ),
    "A-023": lambda: (
        "generated/" in read("CONTRIBUTING.md"),
        "CONTRIBUTING documents the generated payload surface",
    ),
    "A-024": lambda: (
        "make setup" in read("README.md") and "make setup" in read("CONTRIBUTING.md"),
        "make setup documented in both contributor docs",
    ),
    "A-025": lambda: (
        tracked("docs/repomix-map.md") == 0,
        "the generated map is no longer committed",
    ),
    "A-026": lambda: (
        not exists("scripts/se-ai-command-pack-skill-review.py"),
        "the dead wrapper is deleted",
    ),
    "A-027": lambda: (
        "ThreadPoolExecutor" in read("scripts/sd-ai-command-pack-status.py"),
        "fleet collection is concurrent",
    ),
    "A-028": lambda: (
        "aliased-batch" in read("scripts/sd-ai-command-pack-review-learnings.py"),
        "Copilot comments are fetched in aliased batches",
    ),
    "A-031": lambda: (
        exists(".github/dependabot.yml"),
        "a dependency-update path exists",
    ),
    "A-033": lambda: (
        exists("requirements-dev.lock"),
        "transitives are pinned in a committed lock",
    ),
    "A-035": lambda: (
        "--base auto" in read("Makefile"),
        "local release-check compares against a real base",
    ),
    "A-036": lambda: (
        SKILL_REVIEW in read("Makefile"),
        "the shipped payload is inside the lint and type gates",
    ),
    "A-037": lambda: (
        "refs/heads/main" in read(WORKFLOW),
        "the release gate also runs on push to main",
    ),
    "A-038": lambda: (
        "cache: pip" in read(WORKFLOW),
        "CI caches pip",
    ),
    "A-039": lambda: (
        re.search(r"^concurrency:", read(WORKFLOW), re.M) is not None,
        "the workflow declares a concurrency group",
    ),
    "A-040": lambda: (
        '"installer/"' in read(".github/scripts/check-release-payload.py"),
        "installer/ counts as release payload",
    ),
    "A-042": lambda: (
        "patch-versus-minor policy" in read("docs/SE_AI_COMMAND_PACK.md"),
        "a bump policy is documented",
    ),
    "A-043": lambda: (
        "for source, consumers in gen.SHARED_REFERENCES.items()"
        in read("tests/test_generate.py"),
        "shared-reference tests are registry-driven",
    ),
    "A-044": lambda: (
        "regardless of `$CODEX_HOME`" in read("README.md"),
        "the README states the real behavior",
    ),
}


def fixed_findings(ledger_text: str) -> tuple[list[str], list[str]]:
    """Return (ids claiming `fixed`, structural problems).

    An entry whose status line does not parse would otherwise drop out of the
    `fixed` set silently and be reported as nothing at all, which reads as a
    pass. Duplicate ids would run one assertion twice and hide the fact that
    the ledger violates the monotonic-unique-id rule. Both are surfaced as
    failures rather than skipped.
    """
    found: list[str] = []
    problems: list[str] = []
    seen: set[str] = set()

    for block in re.split(r"\n(?=## A-)", ledger_text):
        heading = re.match(r"## (A-\d+)", block)
        if not heading:
            continue
        finding = heading.group(1)
        if finding in seen:
            problems.append(f"{finding}: duplicate entry in the ledger")
            continue
        seen.add(finding)

        status = re.search(r"^- status: (\S+)$", block, re.M)
        if status is None:
            problems.append(f"{finding}: status line is missing or malformed")
            continue
        if status.group(1) not in {"open", "fixed", "regressed"}:
            problems.append(
                f"{finding}: status {status.group(1)!r} is outside the vocabulary"
            )
            continue
        if status.group(1) == "fixed":
            found.append(finding)

    return found, problems


def main() -> int:
    if not LEDGER.is_file():
        print(f"error: ledger not found at {LEDGER}", file=sys.stderr)
        return 2

    print(f"assertions evaluated against {REPO.name} at {revision()}\n")

    claimed, problems = fixed_findings(LEDGER.read_text(encoding="utf-8"))
    if problems:
        for problem in problems:
            print(f"FAIL {problem}", file=sys.stderr)
        return 1
    if not claimed:
        # Distinct wording on purpose: a vacuous pass must not read like a real
        # one, or a run before the ledger is written would certify nothing.
        print("0 findings marked fixed; nothing to verify")
        return 0

    failures = []
    for finding in claimed:
        check = CHECKS.get(finding)
        if check is None:
            failures.append(f"{finding}: marked fixed but has no registered assertion")
            continue
        holds, observation = check()
        if holds:
            print(f"ok   {finding}  {observation}")
        else:
            failures.append(f"{finding}: assertion failed -- expected {observation}")

    print(f"\n{len(claimed) - len(failures)}/{len(claimed)} fixed findings verified")
    for failure in failures:
        print(f"FAIL {failure}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
