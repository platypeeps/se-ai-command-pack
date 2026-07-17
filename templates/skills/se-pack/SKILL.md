---
name: se-pack
description: Use when the user asks about this skill pack itself - reporting the installed version, checking for updates, refreshing or updating the installed skills, or removing the pack.
---

# SE Pack

Run this skill to manage the SE AI command pack installation itself. The
pack is installed from a git checkout into user-level skill directories,
and the receipts under `.se-ai-command-pack/` in the user's home directory
record what is installed and from where. This skill is the day-to-day way
to check, update, refresh, or remove that install.

## When to use

Use for questions and requests about the pack itself: "what version of the
skill pack is installed", "update my skills", "refresh the pack", "remove
the pack". Every other request is a job for the other skills in the pack.

## Arguments

Arguments arrive as free text with the invocation: `key=value` pairs and
bare flags. Unknown argument names are an error — stop and report them.

- `action=status|update|refresh|remove` — default `status`.
- `dry-run` — with `update`, `refresh`, or `remove`: plan only, apply
  nothing (maps to the installer's `--dry-run`).

## Workflow

1. Locate the receipts in the user's home directory:
   `.se-ai-command-pack/manifest.json` (installed version),
   `.se-ai-command-pack/provenance.json` (`sourceRoot` — the pack checkout
   path), and `.se-ai-command-pack/installed-targets.txt`. When the
   receipts are missing, report that the pack is not installed and ask for
   the checkout path if the user wants an install.
2. `action=status` — report the installed version, the `sourceRoot`, and
   the per-platform install state derived from the installed-targets list
   (grouped by top-level directory, e.g. `.claude/`, `.codex/`,
   `.config/agents/`). Compare against the checkout's `manifest.json`
   version when the checkout is reachable and note whether an update is
   available.
3. `action=update` —
   1. Verify `sourceRoot` looks like the pack checkout: it contains
      `install.py` and a `manifest.json` whose name is
      `se-ai-command-pack`. If it is missing or moved, stop and ask the
      user for the checkout path; never clone to a location of your own
      choosing.
   2. Run `git -C <sourceRoot> status --porcelain`. A dirty checkout is a
      stop-and-report condition; never stash or discard the user's work.
   3. Pull with `git -C <sourceRoot> pull --ff-only` — never merge, rebase,
      or rewrite history.
   4. Run `python3 <sourceRoot>/install.py --user --dry-run` and show the
      plan.
   5. Apply with `python3 <sourceRoot>/install.py --user` only after the
      plan has been shown. Conflicts are a stop condition: show the
      conflict list and let the user decide.
   6. Report the version delta using the changelog entries between the old
      and new versions.
4. `action=refresh` — steps 3.4–3.6 without the git pull: rerun the
   installer from the existing checkout (after edits, or to repair a
   drifted install).
5. `action=remove` — run `python3 <sourceRoot>/install.py --remove
   --dry-run` first and show exactly what would be deleted versus
   preserved; apply `--remove` only after the user confirms.

## Safety rules

- Run `git` only against the provenance-recorded `sourceRoot`, and only
  `status`, `log`, `fetch`, and `pull --ff-only`. Never run destructive
  git commands — no resets, no clean, no forced checkouts, nothing that
  can discard work.
- Always run the installer with `--dry-run` first and show the plan before
  any applying run.
- Never pass `--force` to the installer unless the user explicitly asks
  after seeing the conflict list or the preserved-file list — `--force`
  with `--remove` deletes files the user has edited.
- Never install to a root other than the user's home unless the user
  supplies `--root` themselves.
- Treat installer output as the source of truth; do not hand-edit or
  hand-delete files under the skill directories to fix an install — rerun
  the installer instead.

## Final report

- Action taken and whether it was a dry run;
- version before and after (or "no change");
- result counts: created, updated, unchanged, preserved, conflicts,
  skipped;
- hints surfaced by the installer (for example, an anchor directory not
  found);
- next step if the action stopped early (dirty checkout, conflicts,
  missing checkout path).
