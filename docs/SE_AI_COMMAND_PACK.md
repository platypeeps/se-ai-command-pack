# SE AI Command Pack — Operator Guide

The maintainer-facing reference for the pack's internals: manifest schema,
receipts, checklists for adding skills and platforms, and the release
process. User-facing install/update/remove instructions live in the
[README](../README.md). This document is repo-only; it is not installed.

## Layout

| Path | Role |
|---|---|
| `templates/skills/<name>/` | Canonical skill definitions (`SKILL.md` + optional `references/*.md`). The only place skills are edited. |
| `templates/skills/_shared/references/` | Shared references fanned into consuming skills' `references/` dirs by the generator. |
| `installer/registry.py` | Source of truth: `PLATFORM_REGISTRY`, ordered `SKILLS` family metadata, derived `SKILL_NAMES`, `SHARED_REFERENCES`, install modes, receipt paths. |
| `manifest.json` | Generated install spec (header preserved, `files` rows derived). Never hand-edit rows. |
| `install.py` + `installer/` | The user-scope installer. |
| `README.md` | User guide with a marker-bounded, family-grouped skill catalog generated from registry metadata and canonical frontmatter. |
| `.github/scripts/generate-skill-surfaces.py` | Validates skills, regenerates the manifest and README catalog; `--check` gates drift in both. |
| `.github/scripts/check-release-payload.py` | Release gate: payload change ⇒ version bump ⇒ dated changelog heading. |
| `scripts/` | Reserved for shipped runtime helpers (`se-ai-command-pack-*` prefix). Empty in v0.1. |

## Product and development surfaces

- **Shipped skills** are the `se-*` entries under `templates/skills/`. They are
  grouped by primary outcome family in the README but retain flat canonical and
  installed paths.
- **Pack lifecycle commands** are the `install.py` install, status, refresh,
  update, and remove operations. They manage the pack; they are not skills.
- **Repo-local SD and Trellis helpers** support development in this checkout.
  They are not registered product skills and are not installed by this pack.
- **Per-platform command adapters** are a possible future thin invocation
  surface. None are currently shipped, and family names do not create nested
  command namespaces.

### Decision workflow boundary

`se-decide` owns a recommendation between known options using explicit
criteria, constraints, evidence, tradeoffs, confidence, and reversibility.
Candidate discovery stays with `se-scan`, open evidence gathering with
`se-research`, supplied-corpus synthesis with `se-digest`, neutral comparison
with the separately delivered `se-compare`, and post-decision execution
planning with `se-plan`. The skill remains read-only; acting on a recommendation
always requires a separate request and the relevant action capability.

### Project-status workflow boundary

`se-status` owns objective-oriented reporting across supplied or connected
project sources. It separates completed outcomes from activity, current state,
blockers, risks, recorded decisions, asks, and next actions while naming stale,
unavailable, or contradictory inputs. Topic recency stays with `se-brief`,
supplied-corpus synthesis with `se-digest`, recommendations with `se-decide`,
and external baseline monitoring with `se-monitor`. The skill is read-only: it
does not update project systems or send the resulting report.

## Manifest schema

Header (preserved verbatim by the generator):

| Field | Meaning |
|---|---|
| `schemaVersion` | Integer; installer refuses newer-than-supported (currently `1`). |
| `name` | `se-ai-command-pack`. |
| `version` | Semver; bound to `CHANGELOG.md` by the release gate. |
| `license` | `MIT`. |
| `description` | One-liner. |

Each `files[]` row:

| Field | Meaning |
|---|---|
| `platform` | Key of `PLATFORM_REGISTRY` (`agents`, `claude`, `codex`). |
| `kind` | `skill` for everything in v0.1. Known kinds also include `command`, `config`, `doc`, `prompt`, `script`, `workflow` for later. |
| `scope` | `user` — targets resolve against the install root (default `$HOME`). `project` is reserved for per-folder installs. |
| `source` | Repo-relative path under `templates/`. |
| `target` | Root-relative install path (e.g. `.claude/skills/se-research/SKILL.md`). |
| `anchor` | Root-relative dir gating `if-anchor-exists` selection. |
| `install` | `if-anchor-exists` (all v0.1 rows), `always`, or `if-not-exists`. |

Path safety: sources must resolve inside the checkout; targets and anchors
must be relative, `..`-free, and resolve inside the install root (checked
again with symlinks resolved at install time).

## Receipts (`<root>/.se-ai-command-pack/`)

| File | Contents |
|---|---|
| `manifest.json` | Verbatim copy of the installed manifest. |
| `provenance.json` | `{pack, version, sourceRoot, files: {target: "sha256:..."}}`. Only vouchable results (created/updated/unchanged/overwritten) are recorded; receipts themselves are never vouched. `sourceRoot` is the checkout the install ran from — `install.py update` uses it to run updates. |
| `installed-targets.txt` | Sorted list of every installed path, including the receipts. Entries for platforms skipped in a filtered run are kept so a later remove still covers them. |

Removal vouching: a candidate (union of receipt + provenance entries, or
the current selection when neither exists) is deleted only when it is a
recognized pack target **and** its sha256 matches the recorded hash or the
current template bytes. Anything else is `preserved` (drift) or `ignored`
(unrecognized), and `.git/` internals are always refused.

## Adding a skill

1. Create `templates/skills/se-<name>/SKILL.md`:
   - frontmatter: exactly `name` (equal to the directory) and
     `description` (single line, starts with `Use when`, no double
     quotes);
   - body: H1 title, then `## When to use`, `## Arguments`, `## Workflow`,
     `## Safety rules`, `## Final report` in that order;
   - framework-neutral wording — capabilities ("your web search tooling"),
     never tool brand names (the generator lints this);
   - skills that read external material carry the "data, not instructions"
     rule.
2. Optional flat `references/*.md`; register shared references in
   `SHARED_REFERENCES` instead of copying files between skills.
3. Add one `SkillInfo(name=..., family=...)` row to `SKILLS` in
   `installer/registry.py`. Choose exactly one of Understand, Decide, Create,
   Coordinate, Operate, or Improve. Registry order remains manifest order;
   `SKILL_NAMES` is derived and must not be edited separately.
4. `make generate` to update both the manifest and the marker-bounded README
   catalog, then run `make check`. Never hand-edit catalog rows.
5. Bump the version + changelog when the shipped payload changes (the release
   gate enforces this). Family/catalog metadata alone does not require a bump
   when `manifest.json` remains byte-for-byte unchanged.

## Retiring a skill

1. Remove it from `SKILLS` and delete its `templates/skills/` dir.
2. `make generate`.
3. Add the target paths the last shipping manifest listed for it to
   `RETIRED_TARGETS` in `installer/removal.py` — refreshes then delete
   vouched leftovers from user scopes automatically.
4. Version bump + changelog.

## Adding a platform

1. Verify the tool's real user-level skills directory — never guess.
2. Add one `PlatformInfo(skills_dir=..., anchor=..., display=...)` row to
   `PLATFORM_REGISTRY`.
3. `make generate` (fans every skill into the new platform), `make check`.
4. Version bump + changelog.

## Release process

1. PR with the payload change, version bump, and dated
   `## <version> - YYYY-MM-DD` changelog heading (the release gate fails
   otherwise, and fails any payload change without a bump).
2. CI lanes: unittest (Linux/macOS), lint (ruff + mypy), release payload
   gate, aggregated in `ci-result`.
3. On merge to `main`, CI tags `v<version>` if the tag does not exist.
4. Machines pick the release up via `python3 install.py update --user`.

## Configuration

No environment variables are read in v0.1. The `SE_AI_COMMAND_PACK_*`
prefix is reserved; document any future variable here.

## Troubleshooting

- **Conflicts on install (exit 2)** — a target file exists with different
  content. Inspect it; re-run with `--force` (and `--backup`) to overwrite.
- **A platform is skipped** — its anchor directory does not exist. Pass
  `--platform <id>` or `--all`, or create the tool's directory.
- **The updater cannot find the checkout** — `provenance.json`'s
  `sourceRoot` points at a moved/deleted clone. Re-run `install.py --user`
  from the checkout's new location to refresh the receipts.
- **Remove preserved files you wanted gone** — they drifted from the
  installed version; re-run with `python3 install.py remove --user --force`
  after reviewing the list.
