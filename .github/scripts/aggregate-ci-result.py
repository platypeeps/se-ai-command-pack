#!/usr/bin/env python3
"""Aggregate CI lane results from the workflow's `toJSON(needs)` payload.

Policy lives here, not in the workflow: required lanes must be exactly
`success` (a skipped required lane is a failure), conditional lanes may be
`success` or `skipped`. Any lane in the payload but not declared below, any
declared lane missing from the payload, and any unparseable payload all fail
closed — a renamed job turns the aggregate red instead of silently passing.

Exit codes: 0 all declared lanes acceptable; 1 unacceptable lane result;
2 malformed input or lane-set mismatch.
"""

from __future__ import annotations

import json
import os
import sys

REQUIRED_LANES = {
    "unittest",
    "test-hermetic",
    "lint",
    "prose-lint",
    "release-payload-gate",
}
CONDITIONAL_LANES = {"auto-tag-release"}


def evaluate(needs: dict[str, dict[str, object]]) -> tuple[int, list[str]]:
    """Return (exit_code, messages) for a parsed `needs` payload."""
    messages: list[str] = []
    declared = REQUIRED_LANES | CONDITIONAL_LANES

    undeclared = sorted(set(needs) - declared)
    missing = sorted(declared - set(needs))
    if undeclared or missing:
        for lane in undeclared:
            messages.append(f"lane-set mismatch: undeclared lane in needs: {lane}")
        for lane in missing:
            messages.append(f"lane-set mismatch: declared lane missing from needs: {lane}")
        return 2, messages

    failed: list[str] = []
    malformed: list[str] = []
    for lane in sorted(needs):
        entry = needs[lane]
        result = entry.get("result") if isinstance(entry, dict) else None
        if not isinstance(result, str):
            messages.append(f"{lane}: malformed entry (no string result)")
            malformed.append(lane)
            continue
        acceptable = ("success",) if lane in REQUIRED_LANES else ("success", "skipped")
        verdict = "ok" if result in acceptable else "FAIL"
        messages.append(f"{lane}: {result} [{verdict}]")
        if verdict == "FAIL":
            failed.append(lane)

    if malformed:
        messages.append("malformed lane entries: " + ", ".join(malformed))
        return 2, messages
    if failed:
        messages.append("failed lanes: " + ", ".join(failed))
        return 1, messages
    messages.append("all lanes green")
    return 0, messages


def main() -> int:
    raw = os.environ.get("NEEDS_JSON")
    if raw is None:
        print("NEEDS_JSON is not set", file=sys.stderr)
        return 2
    try:
        needs = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"NEEDS_JSON is not valid JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(needs, dict):
        print("NEEDS_JSON must be a JSON object of lane results", file=sys.stderr)
        return 2

    code, messages = evaluate(needs)
    for line in messages:
        print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
