#!/usr/bin/env python3
"""Rewrite `status:` and add a dated `notes:` bullet for every ledger finding.

One-shot transform for task 08-15-audit-ledger-reconcile. Kept alongside the
re-check script so the edit is reproducible and reviewable as code rather than
as 44 hand edits.

Touches exactly two things per entry:
  * the `- status:` value;
  * one new `- notes:` bullet appended after the entry's existing bullets.

Every other line, including any pre-existing `- notes:` bullet, is left byte
identical -- the owning skill requires unknown lines within an entry to be
preserved, and 13 entries already carry human-authored notes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
LEDGER = REPO / ".trellis" / "audit" / "ledger.md"
STAMP = "2026-08-15 reconciled at 564d4a2"

# finding -> (status, observation appended after the stamp)
RECONCILIATION = {
    "A-001": ("fixed", "`git ls-files .claude` returns 107; the re-includes work."),
    "A-002": (
        "open",
        "`_parse_registry` is still live in skill_review.py. Removal is owned by "
        "blocked task 08-04-audit-registry-snapshot-ast-removal, which waits on "
        "the SD pack shipping a snapshot producer.",
    ),
    "A-003": (
        "fixed",
        "HELP_CATALOG_SOURCE now resolves under the generated references dir.",
    ),
    "A-004": (
        "fixed",
        "CONTRIBUTING.md:17 documents the repo-own vs vendored split; its "
        "\"all 26 files\" count matches `ls scripts/`.",
    ),
    "A-005": (
        "open",
        "partially addressed: AGENTS.md:30-36 adds a canonical /sd:* block, but "
        ":13 still names only /trellis:*. The two upstream halves are owned by "
        "blocked task 08-10-upstream-entrypoint-routing-mechanisms.",
    ),
    "A-006": (
        "fixed",
        "`sources=` is now `min_sources=`; tests/test_skills.py:190 enforces "
        "argument-vocabulary conformance.",
    ),
    "A-007": (
        "fixed",
        "generate-skill-surfaces.py:454-456 validates reverse citation closure.",
    ),
    "A-008": (
        "open",
        "installer/fileops.py:145 still selects ALWAYS_INSTALL/IF_NOT_EXISTS rows "
        "and continues before the platform check at :152. Unchanged.",
    ),
    "A-009": (
        "fixed",
        "the duplicate _is_within is gone; only _is_relative_to remains.",
    ),
    "A-010": (
        "fixed",
        "two parsers remain by design, but tests/test_frontmatter_conformance.py "
        "now binds them (skill_review.py:522).",
    ),
    "A-011": (
        "fixed",
        "installer/fileops.py:67-77 captures _PROCESS_UMASK once at import.",
    ),
    "A-012": (
        "fixed",
        "work-loop.py:1071 verifies identity before unlinking a stale lock.",
    ),
    "A-013": (
        "fixed",
        "installer/management.py:397 passes timeout=GIT_TIMEOUT_SECONDS.",
    ),
    "A-014": (
        "fixed",
        "create-release-tag.py:34,36 catch FileNotFoundError and TimeoutExpired.",
    ),
    "A-015": (
        "fixed",
        "the shell `while hasNextPage` loop is gone from housekeeping.sh; paging "
        "moved to review.py, which delegates to `gh --paginate` and caps "
        "accumulation at :1322.",
    ),
    "A-016": (
        "open",
        "work-loop.py:717 still closes a descriptor os.fdopen owned at :705. The "
        "wrapping `except OSError` hides EBADF but does not prevent closing a "
        "reused descriptor; masking is not fixing.",
    ),
    "A-017": (
        "fixed",
        "installer/management.py:294 gates the recorded source path before any "
        "git or exec, labelled \"audit A-017, hardened by A-017/1\".",
    ),
    "A-018": (
        "fixed",
        "the variables moved to ~/.agents/bin/sd_ai_command_pack_lib.py:118-124 "
        "and the cache root is UID-qualified at :333.",
    ),
    "A-019": (
        "fixed",
        "installer/fileops.py:406 opens the backup exclusively and streams via "
        "copyfileobj instead of shutil.copyfile.",
    ),
    "A-020": ("fixed", "Makefile:106 runs `coverage report --fail-under=80`."),
    "A-021": (
        "fixed",
        "tests/test_release_gate.py passes env=git_env() at every git call site.",
    ),
    "A-022": (
        "fixed",
        "tests/test_update_e2e.py provides the missing end-to-end coverage.",
    ),
    "A-023": (
        "fixed",
        "CONTRIBUTING.md and README.md both document the generated/ surface.",
    ),
    "A-024": ("fixed", "`make setup` is documented in README.md and CONTRIBUTING.md."),
    "A-025": (
        "fixed",
        "docs/repomix-map.md is no longer tracked; .gitignore cites this policy "
        "and the map is produced on demand.",
    ),
    "A-026": ("fixed", "scripts/se-ai-command-pack-skill-review.py is deleted."),
    "A-027": (
        "fixed",
        "status.py:3284 collects the fleet through a ThreadPoolExecutor.",
    ),
    "A-028": (
        "fixed",
        "review-learnings.py:1951 uses an aliased-batch query, batching 20 PRs "
        "per request.",
    ),
    "A-029": (
        "open",
        "no memoization of changed-path or base-ref discovery in "
        "review-preflight.mjs; readTextCache at :21 is a different cache. The "
        "file was restructured, so the original line numbers no longer resolve.",
    ),
    "A-030": (
        "open",
        "review-scope.sh:127 still runs `grep -Fxq` per path, called per changed "
        "file from :373.",
    ),
    "A-031": ("fixed", ".github/dependabot.yml exists and drives the update path."),
    "A-032": (
        "open",
        ".opencode/package.json:3 still declares the floating dependency; "
        "`git log` on that path shows only the original add. The local "
        "disposition recorded in task 08-10-upstream-relay-opencode-plugin-dep "
        "was the decision to relay upstream, not an edit to the package file.",
    ),
    "A-033": (
        "fixed",
        "requirements-dev.lock is committed fully pinned, hashed and wheel-only; "
        "`make lock-check` guards drift.",
    ),
    "A-034": (
        "open",
        "half addressed. The script moved to .github/scripts/update-repomix, "
        "which sets NPM_CONFIG_IGNORE_SCRIPTS=true at :26, closing the "
        "lifecycle-script half. `npx --yes repomix@1.16.1` at :27 still "
        "resolves transitives fresh with no lockfile, so the unlocked-transitive "
        "half stands.",
    ),
    "A-035": (
        "fixed",
        "Makefile:163 passes `--base auto`, so the local gate is no longer vacuous.",
    ),
    "A-036": (
        "fixed",
        "Makefile:7-8 list skill_review.py in both LINT_PATHS and MYPY_PATHS.",
    ),
    "A-037": (
        "fixed",
        "tests.yml:89 runs the gate on pull_request and on push to refs/heads/main.",
    ),
    "A-038": ("fixed", "tests.yml:37,62,77 set `cache: pip`."),
    "A-039": (
        "fixed",
        "tests.yml:13 declares a concurrency group cancelling superseded PR runs.",
    ),
    "A-040": (
        "fixed",
        "check-release-payload.py:42,48 include installer/ and install.py as payload.",
    ),
    "A-041": (
        "open",
        "89 tags against 90 changelog headings; 0.53.0 is still untagged.",
    ),
    "A-042": (
        "fixed",
        "docs/SE_AI_COMMAND_PACK.md:1088 points at the CONTRIBUTING.md "
        "patch-versus-minor policy.",
    ),
    "A-043": (
        "fixed",
        "tests/test_generate.py:445,630 iterate gen.SHARED_REFERENCES instead of "
        "hand-copied per-skill methods.",
    ),
    "A-044": (
        "fixed",
        "README.md:164 states ~/.codex is read regardless of $CODEX_HOME.",
    ),
}


def wrap_note(text: str) -> list[str]:
    """Render the note as `- notes:` plus indented continuations at 80 columns.

    A continuation must never begin with `-`: in a unified diff such a line
    reads as `+  --flag`, which is indistinguishable from a changed bullet and
    defeats the "only status/notes changed" review check. When a break would
    put a `-`-leading token first, the break moves one word earlier instead.
    """
    words = text.split()
    lines: list[str] = []
    current = "- notes:"
    for index, word in enumerate(words):
        candidate = f"{current} {word}"
        must_break = len(candidate) > 79 and current != "- notes:"
        # Look ahead: breaking here would strand a `-`-leading token at the
        # start of the next line, so break before this word instead.
        next_word = words[index + 1] if index + 1 < len(words) else ""
        strands_dash = (
            not must_break
            and next_word.startswith("-")
            and len(f"{candidate} {next_word}") > 79
            and current != "- notes:"
        )
        if must_break or strands_dash:
            lines.append(current)
            current = f"  {word}"
        else:
            current = candidate
    lines.append(current)
    return lines


def main() -> int:
    text = LEDGER.read_text(encoding="utf-8")
    blocks = re.split(r"(?=^## A-)", text, flags=re.M)
    seen: set[str] = set()
    out: list[str] = []

    for block in blocks:
        heading = re.match(r"## (A-\d+)", block)
        if not heading:
            out.append(block)
            continue
        finding = heading.group(1)
        if finding not in RECONCILIATION:
            print(f"error: {finding} has no reconciliation entry", file=sys.stderr)
            return 1
        seen.add(finding)
        status, observation = RECONCILIATION[finding]

        updated, count = re.subn(
            r"^- status: .*$", f"- status: {status}", block, count=1, flags=re.M
        )
        if count != 1:
            print(f"error: {finding} has no status line", file=sys.stderr)
            return 1

        note = "\n".join(wrap_note(f"{STAMP} — {observation}"))
        # Append after the entry's final bullet, before its trailing blank line.
        body = updated.rstrip("\n")
        trailing = updated[len(body):]
        out.append(f"{body}\n{note}{trailing}")

    missing = set(RECONCILIATION) - seen
    if missing:
        print(f"error: entries not found in ledger: {sorted(missing)}", file=sys.stderr)
        return 1

    LEDGER.write_text("".join(out), encoding="utf-8")
    fixed = sum(1 for s, _ in RECONCILIATION.values() if s == "fixed")
    print(f"reconciled {len(seen)} entries: {fixed} fixed, {len(seen) - fixed} open")
    return 0


if __name__ == "__main__":
    sys.exit(main())
