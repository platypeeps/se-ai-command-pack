

<!-- SD-ROUTING:START -->
## Canonical command entry points

Repo-own section, deliberately outside the Trellis block above so a
`trellis update` preserves it.

The SD command pack wraps four Trellis workflows. For each, the `sd:*` wrapper
is the canonical entry point in this repository. The wrapped Trellis skill runs
the same workflow **without** the wrapper's added recording and gating steps, so
reaching it directly is a bypass, not an alternative:

- `continue` — canonical `/sd:continue`; bypassed by resolving `trellis-continue` directly
- `finish-work` — canonical `/sd:finish-work`; bypassed by resolving `trellis-finish-work` directly
- `start` — canonical `/sd:start`; bypassed by resolving `trellis-start` directly
- `update-spec` — canonical `/sd:update-spec`; bypassed by resolving `trellis-update-spec` directly

What the bypass costs, measured for `finish-work`: the journal keeps
`(see git log)` instead of commit subjects resolved from Git, Main Changes and
Testing fall back to generic sentences, and the exact-head final-bundle gate
never runs at all.

Trellis emits `/trellis:` next actions of its own — from the session hooks, the
`.trellis/workflow.md` phase flows, and the Trellis CLI itself. Those files are
vendored and cannot be corrected from this repository. When one of them names a
wrapped workflow, take the canonical route listed above instead of the route it
printed.

`tests/test_agent_routing.py` derives the four workflows from
`.agents/skills/` at run time and fails when this section drifts from them.
<!-- SD-ROUTING:END -->
