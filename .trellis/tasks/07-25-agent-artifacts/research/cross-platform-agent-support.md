# Cross-platform custom-agent support (settled research input)

Date: 2026-07-25. Method: verified against official platform docs via web research; local
evidence from this repo and the sibling `sd-ai-command-pack`. This document is a settled
input to the agent-artifacts design: the final design MUST honor the findings and the
recommendation recorded here.

## Verdict

1. Custom agent definition files (a user-droppable file defining a named agent with its own
   prompt/tools/model that the main agent can delegate to) are now supported by most major
   AI coding platforms. The Claude subagent format (Markdown + YAML frontmatter `name`,
   `description`, `tools`, `model`; body = system prompt) is the de facto standard dialect.
2. No new install layer is needed. The existing SE registry -> generator -> manifest ->
   anchor-gated installer machinery is the cross-platform layer; agents are a new artifact
   kind flowing through it, plus per-platform renderers.

## Platform support matrix (SE targets first)

SE installs to 3 platform anchors: `claude` (`~/.claude`), `codex` (`~/.codex`), and
`agents` (`~/.config/agents`, Amp and compatible).

| Platform | Custom agent files | Location & format | Status (2026-07) |
|---|---|---|---|
| Claude Code | Yes | `.claude/agents/*.md` (and `~/.claude/agents/`), MD + YAML | Stable |
| Codex CLI | Yes | `.codex/agents/*.toml` / `~/.codex/agents/*.toml`, TOML (`name`, `description`, `developer_instructions`, optional `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`) | GA since 2026-03; project-scoped agents load only in trusted projects; open issue openai/codex#15250 (project agents not visible from SDK/exec sessions) |
| Amp (`agents` anchor) | No agent files | Plugin API only (`amp.experimental.createAgent`, experimental). `~/.config/agents/skills/` entries are Amp Skills, not agents | Not installable as files |

Non-SE-target platforms for reference (relevant because the canonical format choice should
transpile widely; full matrix lives in the SD twin task): Gemini CLI (`.gemini/agents/*.md`,
stable), GitHub Copilot (`.github/agents/*.agent.md`, GA core), OpenCode
(`.opencode/agents/*.md`, plural dir, `mode: subagent` + permission maps), Cursor
(`.cursor/agents/*.md`, stable since 2.4, also auto-loads `.claude/agents/` and
`.codex/agents/`), Kiro (JSON), Factory droids (MD), CodeBuddy (MD), Antigravity (MD).
Not supported: Devin, Trae (UI only), Qoder (SDK only), Zed (profiles only).

## De facto standard

- Markdown + YAML frontmatter with body-as-system-prompt is used in near-identical dialects
  by Claude, Gemini CLI, Copilot, OpenCode, Cursor, Factory, CodeBuddy, Antigravity.
- Format outliers: Codex (TOML), Kiro (JSON). Both are mechanical transforms from the MD form.
- There is no formal cross-vendor spec for agent definitions (AGENTS.md covers instructions
  only; Agent Skills / SKILL.md covers skills). A nascent `.agents/` root convention exists
  (Amp `.agents/skills/`, Antigravity `.agents/agents/`) but is not a standard.

## Implications for SE (the recommendation)

1. Author canonical agents once, as neutral MD + frontmatter (same shape as Trellis
   `.trellis/agents/*.md`, which already fans to five platforms in this checkout).
2. Extend the existing layer, do not build a new one:
   - Add `agent` to `KNOWN_MANIFEST_KINDS` in `installer/manifest.py` (currently rejects it).
   - Generalize the generator's single hardcoded `if platform == "claude"` overlay branch
     (`.github/scripts/generate-skill-surfaces.py`, `build_rows()`) into a per-platform
     overlay/renderer hook.
   - Renderers: Claude MD (near-passthrough) and Codex TOML. The `agents`/Amp anchor gets
     NO agent artifacts - Amp keeps skills-only.
3. Graceful degradation is mandatory: every skill that dispatches sub-agents must carry
   capability-first fallback prose ("on sub-agent dispatch platforms, run in parallel; on
   inline platforms, work sequentially in one context") - the `sd-audit-repo` pattern.
   This is also what the canonical-body neutrality lint (`BANNED_PHRASE_PATTERN`) forces:
   canonical text may never name a host product.
4. Runtime wrinkles the design must handle:
   - Codex project agents load only in trusted projects; SE installs user-scoped
     (`~/.codex/agents/`) which avoids the trust gate but should be verified.
   - Class-2 platforms (no hook context injection) require the dispatch prompt to carry
     context explicitly; Trellis's `Active task:` first-line convention is the working model.
   - The portable `fresh-session` runtime context (used by `se-red-team`) has no Claude
     frontmatter encoding today and silently degrades at generation time - the design must
     decide its encoding (in-body instruction, doc note, or host field).
   - Governance policy already exists and applies: `templates/skills/se-review-skills/`
     `references/runtime-routing.md` (smallest complete source set, concurrency caps, no
     recursive spawning, parent verifies and owns the final report).

## Sources

- Codex subagents: https://learn.chatgpt.com/docs/agent-configuration/subagents (GA 2026-03-16); openai/codex issue #15250
- Gemini CLI subagents: https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md
- Copilot custom agents: https://docs.github.com/en/copilot/reference/custom-agents-configuration
- OpenCode agents: https://opencode.ai/docs/agents/
- Cursor subagents: https://cursor.com/docs/subagents.md (2.4 changelog; reads `.claude/agents/`, `.codex/agents/`)
- Amp manual (skills vs agents, plugin API): https://ampcode.com/manual
- Kiro: https://kiro.dev/docs/cli/custom-agents/ ; Factory: https://docs.factory.ai/cli/configuration/custom-droids ; CodeBuddy: https://www.codebuddy.ai/docs/cli/sub-agents ; Antigravity: https://antigravity.google/docs/subagents ; Zed: https://zed.dev/docs/ai/agent-profiles
