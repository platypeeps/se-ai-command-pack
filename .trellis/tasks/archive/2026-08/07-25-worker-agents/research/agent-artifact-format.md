# Research: Canonical agent artifact format

- **Query**: How is a canonical agent MD authored? Frontmatter allowlist, body rules, neutrality lint, vs skill SKILL.md.
- **Scope**: internal
- **Date**: 2026-08-05

## Findings

### The canonical se-smoke agent (verbatim)

`templates/agents/se-smoke.md` (whole file):

```markdown
---
name: se-smoke
description: Throwaway smoke agent that proves the agent artifact pipeline end to end.
---

# Smoke Agent

Minimal system prompt used only to exercise the agent render, manifest, install,
status, and remove pipeline. It carries no real role.

Remove this agent when the first real worker role ships; it exists solely to
prove the plumbing.
```

So the canonical shape is: YAML frontmatter (`---` fenced), then a Markdown body that opens with an H1 title (`# Smoke Agent`), then free-form neutral system-prompt prose. That is the entire contract — there is **no** required section list for agent bodies (unlike skills).

### Frontmatter allowlist (required vs optional)

`.github/scripts/generate-skill-surfaces.py:82-88`:

```python
ALLOWED_AGENT_FRONTMATTER_KEYS = (
    "name",
    "description",
    "tools",
    "model",
    "sandbox_mode",
)
```

Validation in `validate_agent()` (`.github/scripts/generate-skill-surfaces.py:639-694`):

- **Required**: `name` — must equal the file stem (`:655-659`); `description` — must be a non-empty single-line string, no double quotes, ≤ `DESCRIPTION_MAX_LENGTH` (1024) chars (`:660-671`). Note: unlike skills, an agent description does **not** need the `"Use when"` prefix (`DESCRIPTION_PREFIX` is only enforced in `validate_skill`, `:252-255`).
- **Optional hints**: `tools` must be a list of strings (`:672-676`); `model` and `sandbox_mode` must be strings (`:677-680`). These are the source of per-platform overlay fields.
- Any key outside the allowlist is a hard error (`:649-654`), duplicated once in `_agent_frontmatter` (`:630-635`).
- Body rules: file must end with a newline (`:682-683`); body must open with an H1 (`# `) after stripping leading newlines (`:684-685`).

### Neutrality lint (BANNED_PHRASE_PATTERN)

Defined once at `.github/scripts/generate-skill-surfaces.py:140-142`:

```python
BANNED_PHRASE_PATTERN = re.compile(
    r"\b(Claude|Cowork|Codex|Copilot|Gemini|ChatGPT|OpenAI|Anthropic|Amp)\b"
)
```

Applied to agents in `validate_agent()` at `:686-693` — it scans the **entire file text** (frontmatter + body), collects matches, and errors with `"framework-neutrality lint: replace brand names ..."`. Lowercase dotted paths like `.claude/skills` are allowed because the pattern is whole-word and case-sensitive on the capitalized brand words (see the skill test `test_lowercase_paths_are_not_banned`, `tests/test_generate.py:968`).

The same pattern is applied to skills at `:283-288`.

### How an agent differs from a skill SKILL.md

| Aspect | Skill (`validate_skill`, `:224-325`) | Agent (`validate_agent`, `:639-694`) |
|---|---|---|
| Frontmatter allowlist | `("name", "description")` only (`:98`) | `name, description, tools, model, sandbox_mode` (`:82-88`) |
| Description prefix | must start with `Use when` (`:252`) | no prefix required |
| Required body sections | `## When to use`, `## Arguments`, `## Workflow`, `## Safety rules`, `## Final report`, in order (`:90-96`, checked `:270-277`) | none — only an H1 open |
| Arguments vocabulary lint | yes (`argument_vocabulary_errors`, `:279-281`) | no |
| Resource dirs | `references/*.md`, `scripts/*.py` allowed (`:130-133`, checked `:290-321`) | agents are flat single `*.md` files only (`validate_agents`, `:701-712`) |
| Neutrality lint | yes (`:283-288`) | yes (`:686-693`) |
| Directory shape | one dir per skill under `templates/skills/<name>/` | one flat `.md` per agent under `templates/agents/` (`:701-708`, "only flat *.md agent sources are shipped") |

### Discovery + collection validation

`agent_names()` (`:613-622`) globs `templates/agents/*.md`, taking `path.stem`, sorted, skipping symlinks. `validate_agents()` (`:697-719`) rejects any subdirectory or non-`.md`/symlink entry under `templates/agents/`, then runs `validate_agent()` on each name and raises a single aggregated `GenerationError`.

## Caveats / Not Found

- There is **no** section-order or governance-content validator for agent bodies. R2/R3/R5/R6 governance invariants (bounded authority, concurrency cap, parent owns report, opening context line) are **not** machine-checked — they are author-discipline only. The only automated gates on an agent body are: H1 open, trailing newline, and the brand-name lint.
- `ALLOWED_AGENT_FRONTMATTER_KEYS` has no field for `delegation` or role wiring — delegation lives in the RuntimeProfile layer (see `registry-delegation.md`), not in agent frontmatter.
</content>
