# Design: SE capabilities as cross-platform sub-agents

Status: ACCEPTED (user, 2026-07-25). Section 1 is binding for all child tasks. Section 2's
open work is distributed to the child tasks listed in `prd.md` (Task map); each child
completes its own detailed design before its `task.py start`.

## 1. Settled design inputs (cross-platform strategy - binding)

Source: `research/cross-platform-agent-support.md` (do not re-litigate without new evidence).

1. One canonical agent source format: neutral Markdown + YAML frontmatter
   (`name`, `description`, portable tool/model hints), body = system prompt. Same shape as
   Trellis `.trellis/agents/*.md`, which already fans out to five platforms in this checkout.
2. Per-platform renderers inside the existing generator, not a new install layer:
   - claude: MD near-passthrough into the existing generated-overlay tree
     (`generated/skills/claude/...` gains a sibling agents tree).
   - codex: TOML transform (`name`, `description`, `developer_instructions`, optional
     `model`, `sandbox_mode`).
   - agents/Amp anchor: EXCLUDED - Amp has no agent files (plugin API only, experimental);
     Amp consumers rely on the inline fallback prose. Skills remain the only Amp artifact.
3. Manifest/installer delta: add kind `agent` to `KNOWN_MANIFEST_KINDS`; agent rows are
   `scope: user`, `install: if-anchor-exists` like all SE rows - absence of a platform
   anchor naturally skips them.
4. Generator delta: replace the hardcoded `if platform == "claude" and relative ==
   "SKILL.md"` branch in `build_rows()` with a per-platform overlay/renderer hook so
   codex agent rendering (and any future platform) is additive.
5. Dispatch protocol in skill bodies stays capability-first (neutrality lint forbids host
   names): "on sub-agent dispatch platforms, run these in parallel; on inline platforms,
   work sequentially in one context." Precedent: `sd-audit-repo` in the sibling pack.
6. Known runtime constraints to encode in agent bodies / docs:
   - Class-2 platforms do not hook-inject context; dispatch prompts must open with the
     active-task/context line (Trellis `Active task:` convention).
   - Codex project-scoped agents load only in trusted projects; SE targets user scope.
   - `fresh-session` (se-red-team) needs an explicit encoding decision (R6).
   - Governance rules from `se-review-skills/references/runtime-routing.md` apply verbatim.

## 2. Open design work (distributed to child tasks - see prd.md Task map)

- Worker-role catalog: which named agents ship in wave 1 and their exact frontmatter
  (candidates: se-source-reader read-only researcher; se-claim-verifier refuter).
- RuntimeProfile extension: how `RUNTIME_PROFILE_ASSIGNMENTS` maps skills to worker roles
  (`delegation: none|optional|required` per runtime-routing.md schema).
- Renderer details: TOML escaping, frontmatter dialect table, drift-gate coverage.
- Test plan: which suites pin the new behavior (test_generate, test_install, test_skills).
- Rollout/rollback: version bump, changelog, retired-targets handling if agents are pulled.
