# Handle root Obsidian KB symlinks safely Design

## Overview

The KB helper currently uses following checks such as `Path.exists()` and then
creates/copies below `.obsidian-kb`. When that root is a symlink, refresh can
silently operate in an external vault while Git reports the link as untracked.
Make root-path classification an invariant owned before every mode dispatch.

## Proposal

Add a small non-following root classifier using `lstat`/`is_symlink` semantics.
Return `absent`, `directory`, or `conflict`; regular files, dangling symlinks,
absolute symlinks, and relative links that escape or alias the repo are all
conflicts. Do not resolve or traverse a conflicting root.

Run the classifier before `--if-present` decides to skip and before dry-run,
check, or refresh discovers sources or touches the KB. Reuse one diagnostic and
exit contract so each mode agrees. Preserve existing handling for tool-owned
legacy links found *inside* a verified real directory.

## Safety And Compatibility

- Never unlink, rename, copy into, or inspect through a conflicting root link.
- Do not print the external target unless an existing diagnostic contract
  requires it; the link path and recovery steps are sufficient.
- An absent root remains a no-op only for `--if-present`; ordinary refresh may
  create the ignored directory as today.
- A real directory keeps current copy, pruning, dashboard, and overview behavior.

## Validation

Use temporary repositories and external sentinel directories. Assert sentinel
bytes and directory entries are unchanged after every mode, including failure.
Cover dangling and relative-escaping links, then retain ordinary absent and
real-directory regression cases. Run the focused KB-helper tests and `make check`.
