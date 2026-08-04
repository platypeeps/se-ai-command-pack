# Implement: Add `agent` artifact kind to installer and generator

Execution plan for the design in `design.md`. Complex task — do not `task.py start` until
this and `design.md` are reviewed.

## Non-blocking note — A-002 (decoupled, verified 2026-08-03)

`07-25-audit-registry-snapshot-contract` (A-002) is **not** a precondition. Verified: the
shipped consumer parser `skill_review.py:286` reads only `PLATFORM_REGISTRY` dict keys, not
`PlatformInfo` field values, so adding an optional `agents_dir` field is invisible to it —
no misparse, no incompatibility. There is no versioned snapshot pinning the field shape
(that is A-002's own deliverable). Proceed without waiting on A-002.

## Ordered checklist

1. **Registry** (`installer/registry.py`)
   - [ ] Add optional `agents_dir: str | None = None` to `PlatformInfo`.
   - [ ] Set `claude.agents_dir=".claude/agents"`, `codex.agents_dir=".codex/agents"`,
         leave `agents` (Amp) at `None`.
   - [ ] No consumer-parser change needed for this field (see A-002 note); if
         `07-25-audit-registry-snapshot-contract` later introduces a snapshot schema,
         include `agents_dir` in it then.

2. **Canonical source** (`templates/agents/`)
   - [ ] Create `templates/agents/se-smoke.md` — neutral MD + frontmatter
         (`name`, `description`, optional `tools`, `model`); body is a minimal system prompt.
         Throwaway smoke agent (OQ1 resolved); keep minimal, mark for removal when
         `07-25-worker-agents` ships the first real role.

3. **Generator** (`.github/scripts/generate-skill-surfaces.py`)
   - [ ] Replace the hardcoded `if platform == "claude" and relative == "SKILL.md"` branch
         (line ~524) with a per-`(platform, kind)` renderer lookup; skill-row output must be
         byte-identical (assert via existing `test_generate`).
   - [ ] Add `build_agent_rows()`: for each `templates/agents/*.md`, for each platform whose
         `agents_dir` is not `None`, emit a `kind: agent`, `scope: user`,
         `install: if-anchor-exists` row sourced from the generated overlay.
   - [ ] Add `render_claude_agent()` (near-passthrough MD → `generated/agents/claude/<name>.md`)
         and `render_codex_agent()` (TOML → `generated/agents/codex/<name>.toml`, correct
         escaping, body as `developer_instructions`).
   - [ ] Extend the case-folded duplicate-target guard to the merged skill+agent row set.
   - [ ] Absorb the `GENERATED_SHARED_REFERENCES` catalog special-case into the same hook
         (A-003 coordination) rather than leaving a parallel exception.

4. **Manifest** (`installer/manifest.py`)
   - [ ] Add `"agent"` to `KNOWN_MANIFEST_KINDS`. No new row-shape rules — agent rows pass
         the existing `validate_manifest` scope/install/path checks.

5. **Generate + payload discipline**
   - [ ] `make generate` → new `generated/agents/**` + manifest rows.
   - [ ] Bump `manifest.json` version; add a dated `## <version> - YYYY-MM-DD` CHANGELOG entry.
   - [ ] Update maintainer docs (`docs/SE_AI_COMMAND_PACK.md`, CONTRIBUTING) for the new kind.

6. **Tests**
   - [ ] `tests/test_generate.py`: renderer outputs (Claude MD dialect, Codex TOML escaping);
         `--check` detects agent drift.
   - [ ] `tests/test_install.py`: install/status/remove/update round-trip for agent rows on
         `claude` and `codex`; **assert zero agent rows target `.config/agents/**` (Amp, D5)**.
   - [ ] `tests/test_skills.py`: registry `PlatformInfo.agents_dir` present; any golden
         fixtures updated.

## Validation commands

```bash
.venv/bin/python -m unittest discover -s tests -p "test_generate.py"
.venv/bin/python -m unittest discover -s tests -p "test_install.py"
.venv/bin/python -m unittest discover -s tests -p "test_skills.py"
.venv/bin/python .github/scripts/generate-skill-surfaces.py --check   # drift gate, exit 0
PYTHON=.venv/bin/python make test                                      # full suite
# behavioral round-trip against a throwaway root:
python3 install.py install --root <tmp> --platform claude --platform codex
python3 install.py status  --root <tmp>
python3 install.py remove  --root <tmp>
```

Acceptance: agent round-trip works on claude+codex, Amp gets none (test-asserted), `--check`
catches drift, full suite green, version bumped + changelog dated.

## Risky files / rollback points

- `generate-skill-surfaces.py build_rows()` — the renderer-hook refactor must not change any
  existing skill row; `test_generate` golden comparison is the tripwire.
- `installer/registry.py PlatformInfo` — adding optional `agents_dir` is consumer-safe
  (parser reads only `PLATFORM_REGISTRY` keys; see A-002 note).
- Rollback: delete `templates/agents/**` + regenerate; agent rows vanish; `remove`/`update`
  prune installed files via provenance. No migration.
