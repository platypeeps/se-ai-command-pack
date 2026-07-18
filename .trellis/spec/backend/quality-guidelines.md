# Quality Guidelines

> Code quality standards for backend development.

---

## Overview

Changes must preserve safe, deterministic installation across supported Python
and operating-system versions. Prefer small modules, explicit data flow,
immutable result records, plan-before-apply operations, and tests at the same
boundary users exercise.

---

## Forbidden Patterns

- Hand-editing generated `manifest.json` rows instead of changing the registry
  or canonical templates and running `make generate`.
- Writing outside the validated install root or following untrusted symlinked
  receipt/destination paths.
- Destructive overwrite/removal without hash or template provenance, except
  when the user explicitly requests `--force`.
- Network/Git mutation during a dry-run.
- Broad exception catches that hide actionable filesystem or subprocess errors.
- Adding a shipped payload change without a manifest version bump and matching
  `CHANGELOG.md` entry.

---

## Required Patterns

- Validate manifest, registry, source, and destination paths before mutation.
- Preview a multi-file lifecycle operation before applying it.
- Use atomic writes for installed files and receipts.
- Keep canonical skill content under `templates/skills/` and pack declarations
  in `installer/registry.py`.
- Preserve compatibility with Python 3.10; use postponed annotations where
  modern typing syntax appears.
- Format for Ruff's 88-character line length and selected `E4`, `E7`, `E9`,
  `F`, `I`, and `B` rules; keep mypy clean for `installer` and `install.py`.

---

## Testing Requirements

- Add focused unittest coverage for every observable behavior change, including
  failure and preservation paths when filesystem state is involved.
- Use temporary install roots; never target the developer's real home directory
  from tests.
- Mock Git/subprocess boundaries when asserting lifecycle sequencing, while
  retaining end-to-end CLI tests for parsing, exit codes, and installed files.
- Run `make check`: generation parity, Ruff, mypy, the unittest suite, and the
  release payload/version gate must all pass.

---

## Code Review Checklist

- Is the change made in the canonical registry/template/module rather than a
  generated or duplicated surface?
- Are all paths constrained to the intended source/install roots?
- Does dry-run avoid mutation, and does apply reuse or revalidate its plan?
- Are user-modified files preserved by default?
- Do errors include actionable context without leaking sensitive contents?
- Do tests cover success, invalid input, conflicts, and compatibility state?
- If payload changed, are `manifest.json`, version, and `CHANGELOG.md` aligned?

---

## Scenario: Pack Lifecycle CLI Changes

### 1. Scope / Trigger

- Trigger: changing `install.py` commands, install receipts, source-checkout
  updates, removal, or retired-skill cleanup.
- Why: these surfaces cross CLI parsing, filesystem state, Git state, generated
  manifests, installed user scopes, and release compatibility.

### 2. Signatures

```text
python3 install.py [install] [--user | --root PATH] [install options]
python3 install.py status [--user | --root PATH]
python3 install.py refresh [--user | --root PATH] [install options]
python3 install.py update [--user | --root PATH] [install options]
python3 install.py remove [--user | --root PATH] [removal options]
python3 install.py --version
```

The bare invocation remains the convenient install form. Lifecycle operations
are positional commands; do not add parallel action flags such as `--remove`.

### 3. Contracts

- `status` reads `.se-ai-command-pack/{manifest,provenance}.json` plus
  `installed-targets.txt` without modifying them.
- `refresh` applies the current checkout through the normal plan-before-apply
  installer path.
- `update` trusts only the provenance-recorded `sourceRoot`, requires the
  expected pack manifest, refuses a dirty checkout, and fast-forwards with
  `git pull --ff-only`.
- After pulling, `update` launches a fresh Python process, runs a dry-run, and
  applies only when that plan succeeds. This prevents old imported modules
  from being mixed with newly pulled files.
- `remove` and retired-target cleanup delete only hash-vouched or
  template-identical files unless the user explicitly passes `--force`.
- Retiring a skill requires removing it from `SKILL_NAMES`, deleting its
  canonical template, regenerating `manifest.json`, and registering every
  previously shipped target in `RETIRED_TARGETS`.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| Install root is missing | Exit nonzero with `install root not found`. |
| Status receipts are absent or invalid | Report not installed and return 1. |
| Recorded source checkout is missing or is the wrong pack | Exit before Git or filesystem writes. |
| Source checkout is dirty | Exit before fetch, pull, or refresh. |
| Fast-forward pull fails | Exit with the Git failure; never merge or rebase. |
| Refreshed dry-run fails | Do not run the applying refresh. |
| Retired target is hash-vouched | Remove it during normal refresh. |
| Retired target drifted | Preserve and report it unless `--force` is explicit. |

### 5. Good/Base/Bad Cases

- Good: `python3 install.py update --user` fast-forwards a clean recorded
  checkout, previews the new payload, and reapplies from a fresh process.
- Base: `python3 install.py --user` remains an idempotent install/refresh.
- Bad: implementing lifecycle behavior in a skill prompt, accepting both a
  positional command and an action flag, continuing in the pre-pull Python
  process, or deleting retired files without provenance vouching.

### 6. Tests Required

- CLI tests assert each positional command dispatches correctly and obsolete
  action flags are rejected.
- Status tests assert installed version, source checkout, platform grouping,
  and the not-installed return code.
- Update tests assert dirty-checkout refusal, `--ff-only`, dry-run-before-apply,
  and two fresh-process invocations for planning and application.
- Retirement tests inject a prior provenance hash and assert normal refresh
  removes the vouched old target while existing drift-preservation tests stay
  green.
- Run `make check` to cover unit tests, Ruff, mypy, generated manifest parity,
  and the release payload/version gate.

### 7. Wrong vs Correct

#### Wrong

```text
python3 install.py --remove
```

This duplicates the positional command model and creates a second parser path.

#### Correct

```text
python3 install.py remove --user --dry-run
python3 install.py remove --user
```

One command surface owns removal, with an explicit preview before application.

## Scenario: Repomix Repository Map Refresh

### 1. Scope / Trigger

- Trigger: adding or changing the checked-in repository map, its Repomix
  configuration, or its refresh command.

### 2. Signatures

```text
make repomix
bash scripts/update_repomix
```

### 3. Contracts

- `repomix.config.json` owns the input exclusions and writes compressed,
  parsable Markdown to `docs/repomix-map.md`.
- `scripts/update_repomix` runs the pinned Repomix version through `npx`
  without adding Node dependencies to this Python project.
- The generated map excludes itself, local knowledge copies and receipts,
  Trellis task/session state, and copied agent-platform surfaces.

### 4. Validation & Error Matrix

| Condition | Required behavior |
|---|---|
| `npx` is unavailable | Exit nonzero with an actionable requirement message. |
| Repomix installation or generation fails | Propagate the nonzero exit; do not report a refreshed map. |
| Repomix detects suspicious content | Treat the generation as failed and inspect before committing. |
| Configuration changes | Regenerate and commit `docs/repomix-map.md` in the same change. |

### 5. Good/Base/Bad Cases

- Good: `make repomix` uses the pinned version and replaces the tracked map.
- Base: rerunning the command without source changes produces no map diff.
- Bad: running an unpinned global or latest Repomix version and committing an
  output whose behavior cannot be reproduced from the repository.

### 6. Tests Required

- Run `make repomix` and require a successful Repomix security scan.
- Run `git diff --check` and verify `docs/repomix-map.md` is the configured
  output and does not include itself.
- Run `make check` so repository-map tooling changes do not regress the Python
  pack, generated surfaces, or release gate.

### 7. Wrong vs Correct

#### Wrong

```text
npx repomix@latest
```

#### Correct

```text
make repomix
```

The repository-owned command pins the tool and applies the curated exclusions.
