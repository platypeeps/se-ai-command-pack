# Research: Agent rendering to Claude MD and Codex TOML

- **Query**: How do agents render to generated/agents/claude/*.md and generated/agents/codex/*.toml? What drives output, structure validation, discovery?
- **Scope**: internal
- **Date**: 2026-08-05

## Findings

### Discovery (glob over templates/agents/)

`agent_names()` — `.github/scripts/generate-skill-surfaces.py:613-622`:

```python
def agent_names() -> list[str]:
    if not AGENTS_ROOT.is_dir():
        return []
    return sorted(
        path.stem
        for path in AGENTS_ROOT.glob("*.md")
        if path.is_file() and not path.is_symlink()
    )
```

`AGENTS_ROOT = ROOT / "templates/agents"` (`:74-75`). Adding `se-source-reader.md` and `se-claim-verifier.md` there is all that is needed for them to be discovered — no registry list of agent names exists.

### Claude MD renderer

`render_claude_agent()` — `:770-788`. Near-passthrough overlay:

- Parses/allowlists frontmatter via `_agent_frontmatter()` (`:625-636`).
- Emits `name` and `description` always; copies `tools` and `model` **if present**; **drops** `sandbox_mode` (Codex-only hint).
- Re-dumps frontmatter with `yaml.safe_dump(..., sort_keys=False, width=10000)`.
- Body is passed through **verbatim**: `return f"---\n{dumped}---\n{body}"`.

Output determined by: canonical frontmatter (minus `sandbox_mode`) + verbatim body.

### Codex TOML renderer

`render_codex_agent()` — `:791-806`:

```python
lines = [
    f"name = {_toml_basic_string(frontmatter['name'])}",
    f"description = {_toml_basic_string(frontmatter['description'])}",
]
for key in ("model", "sandbox_mode"):
    if key in frontmatter:
        lines.append(f"{key} = {_toml_basic_string(frontmatter[key])}")
lines.append(f"developer_instructions = {_toml_multiline_string(body)}")
return "\n".join(lines) + "\n"
```

- Scalar fields first: `name`, `description`, then `model`/`sandbox_mode` **if present**. Note Codex **drops `tools`** (only Claude keeps it) — asymmetric with Claude which drops `sandbox_mode`.
- Body becomes `developer_instructions` as a TOML multiline basic string. `_toml_multiline_string` (`:744-767`) escapes every `"` (so no accidental `"""` terminates early), doubles backslashes, keeps `\n`/`\t` literal, and emits a newline right after the opening `"""` (TOML trims exactly one, so the body round-trips byte-for-byte). This is why `generated/agents/codex/se-smoke.toml` shows a blank line then `# Smoke Agent`.
- `_toml_basic_string` (`:722-741`) full-escapes scalar strings.

### What determines the output

For each `agent_names()` name, `regenerated_agent_texts()` (`:819-839`) iterates `PLATFORM_REGISTRY.items()` and renders **only** platforms whose `info.agents_dir is not None` (`:831-833`). Codex → `render_codex_agent`, everything else → `render_claude_agent`. The `agents` (Amp) platform has `agents_dir=None` and is skipped. Generated path chosen by `_agent_generated_path()` (`:809-816`): codex → `generated/agents/codex/<name>.toml`, else `generated/agents/claude/<name>.md`.

### Structure / section-order validation for agent bodies (vs skills)

There is **none** for agents beyond the H1-open + trailing-newline + brand-lint checks in `validate_agent()` (`:682-693`). Skills enforce the 5-section ordered list `REQUIRED_SECTIONS` (`:90-96`, checked `:270-277`); agents have no equivalent. The renderers do **not** validate body structure at all — they only re-parse frontmatter through `_agent_frontmatter`.

### Drift gate + manifest rows

- `read_committed_agents()` (`:842-887`): reads expected overlays, rejects symlinks, and inventories stale/unexpected files under `generated/agents/` for removal.
- `build_agent_rows()` (`:890-911`): one manifest row per (agent, agent-capable platform) with `kind: "agent"`, `scope: user`, `install: if-anchor-exists`, `source` = generated path, `target` = `{info.agents_dir}/{name}.{ext}`, `anchor` = `info.anchor`.
- Wired into the run in `main()` (`:1217`, `:1222-1225`, `:1301-1315` for `--check` drift, `:1340-1344` for write). `validate_agents()` runs before rendering (`:1217`).

## Caveats / Not Found

- Rendering is content-agnostic: two new agents render with zero generator changes; adding `delegation` semantics does not touch these renderers (delegation lives in registry/skill-overlay, not agent overlays).
- Asymmetry to remember for authoring: Claude keeps `tools`+`model`, drops `sandbox_mode`; Codex keeps `model`+`sandbox_mode`, drops `tools`. Any hint that must reach both platforms must be within that intersection (`model` only).
</content>
