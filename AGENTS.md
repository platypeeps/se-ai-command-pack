<!-- TRELLIS:START -->
# Trellis Instructions

These instructions are for AI assistants working in this project.

This project is managed by Trellis. The working knowledge you need lives under `.trellis/`:

- `.trellis/workflow.md` — development phases, when to create tasks, skill routing
- `.trellis/spec/` — package- and layer-scoped coding guidelines (read before writing code in a given layer)
- `.trellis/workspace/` — per-developer journals and session traces
- `.trellis/tasks/` — active and archived tasks (PRDs, research, jsonl context)

If a Trellis command is available on your platform (e.g. `/trellis:finish-work`, `/trellis:continue`), prefer it over manual steps. Not every platform exposes every command.

If you're using Codex or another agent-capable tool, additional project-scoped helpers may live in:
- `.agents/skills/` — reusable Trellis skills
- `.codex/agents/` — optional custom subagents

Managed by Trellis. Edits outside this block are preserved; edits inside may be overwritten by a future `trellis update`.

<!-- TRELLIS:END -->

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

<!-- SD-AI-COMMAND-PACK:ROUTING:START -->
## Canonical Entry Points

The SD AI Command Pack wraps several Trellis workflows. Where a wrapper
exists, it is the canonical entry point: it carries the pack's own gates,
review loop, and completion bookkeeping, and the underlying Trellis command
does not. Reaching past a wrapper to the command it wraps skips those.

Route by intent:

- **Publishing a branch, working its review, and merging it** — use the pack's
  ship workflow rather than invoking the create-PR, review, and merge steps
  separately. It sequences them and owns the stop-points between them.
- **Finishing a task** — use the pack's finish-work workflow. It produces the
  bookkeeping receipt the merge gate independently revalidates.
- **Merging** — go through the pack's housekeeping gate. It is the only merge
  authority; nothing else in the chain merges.
- **Reviewing changes locally before publishing** — use the pack's review
  workflow, which runs the deterministic checks the remote review assumes.
- **Anything with no pack wrapper** — use the Trellis command directly. The
  pack adds surfaces; it does not replace Trellis.

To see which wrappers this repository actually has, list the installed skills
rather than relying on a list written down somewhere: they are the pack's
`sd-*` skills, and the pack's own help surface enumerates them at runtime.

The pack verifies that this block matches the version it shipped — `install.py
<repo> --check` reports `refresh-required` if the text between the markers
drifts. It does **not** verify the routing against this repository's installed
skills, and deliberately names none: the block routes by intent so that there
is nothing in it that a later release or a thin conversion could make false.

Managed by the SD AI Command Pack. Edits outside this block are preserved;
edits inside it are replaced on the next install.
<!-- SD-AI-COMMAND-PACK:ROUTING:END -->
