# Audit ledger
Cross-session memory of sd-audit-repo findings for platypeeps/se-ai-command-pack; managed by sd-audit-repo.

## A-001 — Trellis gitignore rule defeats SD-pack re-includes, leaving .claude dogfood surface untracked while receipts claim it
- status: fixed
- severity: P2 · effort: S · confidence: Plausible
- dimension: architecture
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - .gitignore:27 — Trellis rule `.claude/` ignores the directory, defeating the managed re-includes at lines 92–95.
  - .sd-ai-command-pack/installed-targets.txt:1 — receipt claims 21 .claude/* targets; git ls-files .claude → 0.
  - scripts/sd-ai-command-pack-install-audit.py:489 — pack's own audit flags the mismatch on a fresh clone.
- why: Dogfood state irreproducible for the primary platform; receipts claim files a fresh clone lacks.
- fix: Pick one owner: narrow .gitignore:27 so re-includes work, or stop claiming .claude in receipts.
- notes: 2026-08-15 reconciled at 564d4a2 — `git ls-files .claude` returns 107;
  the re-includes work.

## A-002 — Shipped skill payload AST-parses installer/registry.py, making an internal module an unversioned cross-repo contract
- status: fixed
- severity: P2 · effort: M · confidence: Plausible
- dimension: architecture
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - templates/skills/se-review-skills/scripts/skill_review.py:325 — _parse_registry AST-parses the pack checkout's internal module.
  - templates/skills/se-review-skills/scripts/skill_review.py:341 — hard-codes both repos' layouts plus sibling internals (:403).
- why: Registry/layout refactors silently break already-installed copies (fleet version skew).
- fix: Export a versioned machine-readable registry snapshot; have skill_review.py consume it.
- notes: 2026-08-15 reconciled at 564d4a2 — `_parse_registry` is still live in
  skill_review.py. Removal is owned by blocked task
  08-04-audit-registry-snapshot-ast-removal, which waits on the SD pack
  shipping a snapshot producer.
- notes: 2026-08-16 reconciled at 74ad2f6 — FIXED. `_parse_registry` and every `ast.parse`
  call are gone from skill_review.py (grep returns 0); the consumer resolves the
  registry from `generated/registry-snapshot.json` alone. Landed as
  platypeeps/se-ai-command-pack#239 (`36e3450`, release 0.70.0) once the SD pack
  began shipping a snapshot producer. The prescribed fix -- "export a versioned
  machine-readable registry snapshot; have skill_review.py consume it" -- is
  what shipped.

## A-003 — Generated catalog lives inside the declared source-of-truth tree
- status: fixed
- severity: P3 · effort: S · confidence: Plausible
- dimension: architecture
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - .github/scripts/generate-skill-surfaces.py:52 — HELP_CATALOG_PATH points into templates/skills/_shared/references/.
  - templates/skills/_shared/references/skill-catalog.md:1 — do-not-edit banner committed under templates/.
- why: Source/generated boundary inverted for one file; hand edits get clobbered by make generate.
- fix: Emit under generated/ (repoint manifest row) or document the exception where the boundary is declared.
- notes: 2026-08-15 reconciled at 564d4a2 — HELP_CATALOG_SOURCE now resolves
  under the generated references dir.

## A-004 — Repo-own tooling interleaved with vendored SD-pack and Trellis files
- status: fixed
- severity: P3 · effort: M · confidence: Plausible
- dimension: architecture
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - scripts/se-ai-command-pack-skill-review.py:1 — 17 of 19 scripts/ files are SD-pack-installed; only 2 repo-own.
  - Makefile:14 — build pipeline lives in .github/scripts beside installed prompts and Trellis files.
  - CONTRIBUTING.md:1 — no editable-source vs vendored distinction documented.
- why: Contributors cannot tell source from installed product; local edits to vendored files get clobbered.
- fix: One home for repo-own tooling; list vendored do-not-edit path families in CONTRIBUTING.md.
- notes: 2026-08-15 reconciled at 564d4a2 — CONTRIBUTING.md:17 documents the
  repo-own vs vendored split; its "all 26 files" count matches `ls scripts/`.

## A-005 — Parallel sd:* and trellis:* entry points for the same workflows with divergent routing guidance
- status: open
- severity: P3 · effort: S · confidence: Plausible
- dimension: architecture
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - AGENTS.md:13 — routing block names only /trellis:finish-work, /trellis:continue.
  - .agents/skills/sd-finish-work/SKILL.md:11 — sd wrapper overrides the trellis journal step.
- why: Agents following AGENTS.md bypass the SD pack's recording/gating steps; session records diverge by entry point.
- fix: Make one entry point canonical per platform (amend routing doc or suppress the shadowed surface).
- notes: 2026-08-15 reconciled at 564d4a2 — partially addressed:
  AGENTS.md:30-36 adds a canonical /sd:* block, but :13 still names only
  /trellis:*. The two upstream halves are owned by blocked task
  08-10-upstream-entrypoint-routing-mechanisms.
- notes: 2026-08-16 reconciled at 74ad2f6 — still open, unchanged since the last
  pass: AGENTS.md:13 still names only `/trellis:*`, while :34-37 carries the
  canonical `/sd:*` block. Deliverable 1 of the owning task was relayed upstream
  as platypeeps/sd-ai-command-pack#486 on 2026-08-16, so its blocker is now upstream triage rather than
  per-PR approval. Deliverable 2 (mindfold-ai/Trellis) is unrelayed.

## A-006 — Same skill-argument names carry conflicting meanings and vocabularies across 53 skills
- status: fixed
- severity: P2 · effort: M · confidence: Plausible
- dimension: design
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - templates/skills/se-research/SKILL.md:37 — sources=N is a count; ~20 siblings use sources= for locator lists.
  - templates/skills/se-monitor/SKILL.md:46 — one verbosity axis spelled length=/detail=/depth=/format= across 40+ skills.
  - tests/test_skills.py:144 — unknown-argument stop rule turns cross-skill transfer into hard errors.
- why: The key=value surface is the pack's primary UI; identical concepts differ per skill and one name changes type.
- fix: Pack-wide argument vocabulary enforced in generator validation; rename sources=N → min_sources=.
- notes: 2026-08-15 reconciled at 564d4a2 — `sources=` is now `min_sources=`;
  tests/test_skills.py:190 enforces argument-vocabulary conformance.

## A-007 — SHARED_REFERENCES fan-out is a hand-maintained opt-in list with no citation-closure validation
- status: fixed
- severity: P2 · effort: S · confidence: Plausible
- dimension: design
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - installer/registry.py:292 — source-standards.md consumers enumerate 50 of 53 skills individually.
  - .github/scripts/generate-skill-surfaces.py:326 — validate_skills never checks citation closure.
  - tests/test_skills.py:365 — only the forward direction enforced; reverse closure holds by discipline.
- why: A forgotten registry append ships a skill citing a references/ file that never installs; no gate fails.
- fix: Fail validate_skills on unregistered citations, or invert to an opt-out exclusion set.
- notes: 2026-08-15 reconciled at 564d4a2 — generate-skill-surfaces.py:454-456
  validates reverse citation closure.

## A-008 — --platform promise not honored for always/if-not-exists manifest rows
- status: open
- severity: P3 · effort: S · confidence: Plausible
- dimension: design
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - install.py — `--platform` help promises platform-only install.
  - installer/fileops.py:145 — ALWAYS_INSTALL/IF_NOT_EXISTS rows are selected before the platform_filter check at :152 (latent: all rows are if-anchor-exists).
- why: First static row added through the preserved generator seam ignores --platform unnoticed.
- fix: Apply platform filter before the install-mode shortcut, or amend the help text.
- notes: 2026-08-15 reconciled at 564d4a2 — installer/fileops.py:145 still
  selects ALWAYS_INSTALL/IF_NOT_EXISTS rows and continues before the platform
  check at :152. Unchanged.
- notes: 2026-08-16 reconciled at 74ad2f6 — still open. Line drift only:
  fileops.py:137 -> :145, with the platform filter at :152. The ordering that
  makes the finding true is unchanged.

## A-009 — skill_review.py defines the same path-containment predicate twice under two names
- status: fixed
- severity: P3 · effort: S · confidence: Plausible
- dimension: design
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - templates/skills/se-review-skills/scripts/skill_review.py:211 — _is_relative_to.
  - templates/skills/se-review-skills/scripts/skill_review.py:1545 — _is_within, byte-identical; both load-bearing (:509, :1690).
- why: Two names for one concept in a security-sensitive module invite divergence.
- fix: Keep one helper for all call sites.
- notes: 2026-08-15 reconciled at 564d4a2 — the duplicate _is_within is gone;
  only _is_relative_to remains.

## A-010 — Two divergent frontmatter grammars parse the same SKILL.md artifacts
- status: fixed
- severity: P3 · effort: M · confidence: Plausible
- dimension: design
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - .github/scripts/generate-skill-surfaces.py:161 — YAML grammar gates what ships.
  - templates/skills/se-review-skills/scripts/skill_review.py:412 — hand-rolled parser applied to the same files on consumer machines.
- why: Parallel grammars can classify metadata differently from what the generator validated.
- fix: Declare YAML authoritative; shipped parser becomes a rejecting strict subset with a conformance test.
- notes: 2026-08-15 reconciled at 564d4a2 — two parsers remain by design, but
  tests/test_frontmatter_conformance.py now binds them (skill_review.py:522).

## A-011 — default_file_mode mutates process umask as a hidden side effect
- status: fixed
- severity: P3 · effort: S · confidence: Plausible
- dimension: design
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - installer/fileops.py:68 — query-named helper executes os.umask(0)/restore per installed file (called from :106).
- why: Thread-hostile: a concurrent open during the window could create 0666/0777 files.
- fix: Read umask once into a module constant, or document the mutation.
- notes: 2026-08-15 reconciled at 564d4a2 — installer/fileops.py:67-77 captures
  _PROCESS_UMASK once at import.

## A-012 — Stale-lock recovery race can let two work-loop runs acquire the same exclusive lock
- status: fixed
- severity: P2 · effort: M · confidence: Plausible
- dimension: correctness
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - scripts/sd-ai-command-pack-work-loop.py:937 — stale judgment → unlink by path → recreate, no identity re-check at unlink time.
  - scripts/sd-ai-command-pack-work-loop.py:1011 — same pattern for the terminal lock.
  - .agents/skills/sd-work-backlog/SKILL.md:108 — shipped skill instructs --recover-stale-lock, making concurrent recovery realistic.
- why: The slower unlink removes the winner's fresh lock; both processes run autonomous sessions until the next heartbeat check.
- fix: Identity-verified delete (rename+content check or st_ino compare) before recreate; upstream fix in pack source.
- notes: tracked upstream in sd-ai-command-pack task 07-25-fix-work-loop-lock-race (2026-07-25); SE-side task retired.
- notes: 2026-08-15 reconciled at 564d4a2 — work-loop.py:1071 verifies identity
  before unlinking a stale lock.

## A-013 — install.py update runs network git with no timeout — only unbounded subprocess path in the pack
- status: fixed
- severity: P3 · effort: S · confidence: Plausible
- dimension: correctness
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - installer/management.py:110 — _run_git without timeout; fetch/pull at :164/:190.
  - scripts/sd_ai_command_pack_lib.py:10 — every other wrapper bounds subprocesses (60s/20s).
- why: A stalled network hangs install.py update forever; inconsistency invites inherited hangs.
- fix: timeout=60 + convert TimeoutExpired to the clean error message.
- notes: 2026-08-15 reconciled at 564d4a2 — installer/management.py:397 passes
  timeout=GIT_TIMEOUT_SECONDS.

## A-014 — create-release-tag.py crashes with a raw traceback on git timeout or missing git
- status: fixed
- severity: P3 · effort: S · confidence: Plausible
- dimension: correctness
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - .github/scripts/create-release-tag.py:21 — nothing catches TimeoutExpired/FileNotFoundError (used with --push in tests.yml:95).
  - .github/scripts/check-release-payload.py:47 — sibling script shows the clean GateError pattern.
- why: Transient stall during tagging fails CI with a stack trace instead of the documented error contract.
- fix: Mirror check-release-payload.py's exception handling.
- notes: 2026-08-15 reconciled at 564d4a2 — create-release-tag.py:34,36 catch
  FileNotFoundError and TimeoutExpired.

## A-015 — Housekeeping review-thread pagination loop is unbounded on a repeating GraphQL cursor
- status: fixed
- severity: P3 · effort: S · confidence: Plausible
- dimension: correctness
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - scripts/sd-ai-command-pack-housekeeping.sh:529 — while hasNextPage with no page cap.
  - scripts/sd-ai-command-pack-housekeeping.sh:554 — only the empty-cursor case guarded.
- why: One pagination glitch turns auto-merge gating into an infinite network loop.
- fix: Cap pages or break on repeated endCursor; treat overflow as inspection failure (skip auto-merge); upstream fix.
- notes: tracked upstream in sd-ai-command-pack task 07-25-harden-toolchain-failure-paths (2026-07-25); SE-side task retired.
- notes: 2026-08-15 reconciled at 564d4a2 — the shell `while hasNextPage` loop
  is gone from housekeeping.sh; paging moved to review.py, which delegates to
  `gh --paginate` and caps accumulation at :1322.

## A-016 — work-loop atomic_write_json failure path double-closes a descriptor already closed by fdopen
- status: open
- severity: P3 · effort: S · confidence: Plausible
- dimension: correctness
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - scripts/sd-ai-command-pack-work-loop.py:570 — except-cleanup closes an fd fdopen already owned/closed (e.g. failed os.replace at :564).
  - templates/skills/se-review-skills/scripts/skill_review.py:1738 — correct descriptor=-1 handoff exists in-repo.
- why: In threaded embeddings the stale close can shut an unrelated reused fd.
- fix: Adopt the skill_review.py ownership handoff; upstream fix.
- notes: tracked upstream in sd-ai-command-pack task 07-25-harden-toolchain-failure-paths (2026-07-25); SE-side task retired.
- notes: 2026-08-15 reconciled at 564d4a2 — work-loop.py:717 still closes a
  descriptor os.fdopen owned at :705. The wrapping `except OSError` hides EBADF
  but does not prevent closing a reused descriptor; masking is not fixing.
- notes: 2026-08-16 reconciled at 74ad2f6 — NOT VERIFIABLE HERE, relayed as
  platypeeps/sd-ai-command-pack#487. The cited files were vendored pack content and left this
  repository at `b7dd320` (thin conversion); `scripts/` is now enforced-empty by
  `ScriptsDirectoryStaysEmptyTest` and no repo-own successor exists under
  `.github/scripts/`. This is not evidence that the descriptor double-close was fixed -- only that
  this repository can no longer see it. The upstream issue states plainly that
  its evidence is from 2026-08-15 and unverified against that repository's
  current main. Status stays `open` rather than a relayed-* value because the
  managing skill's vocabulary is `open|fixed|regressed`
  (sd-audit-repo/SKILL.md:228); an invented status would put this file out of
  contract with the tool that rewrites it.

## A-017 — install.py update runs git and executes install.py from an unverified receipt-recorded path
- status: fixed
- severity: P2 · effort: S · confidence: Plausible
- dimension: security
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - installer/management.py:96 — source_root from provenance.json sourceRoot, no integrity protection.
  - installer/management.py:190 — git pull on that path, then executes its install.py (:192, :209).
  - install.py:324 — update dispatches before manifest load/validation.
- why: One writable JSON file under the install root escalates to arbitrary code execution on next update; pull also runs the checkout's git hooks/config.
- fix: Require sourceRoot == running checkout unless explicitly confirmed; refuse non-owned/non-git paths.
- notes: 2026-08-15 reconciled at 564d4a2 — installer/management.py:294 gates
  the recorded source path before any git or exec, labelled "audit A-017,
  hardened by A-017/1".

## A-018 — Toolchain resolver points Python bytecode and uv tool dirs at shared, non-user-scoped /tmp paths
- status: fixed
- severity: P2 · effort: S · confidence: Plausible
- dimension: security
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - scripts/sd-ai-command-pack-toolchain.sh:392 — PYTHONPYCACHEPREFIX/UV_CACHE_DIR/UV_TOOL_DIR/RUFF_CACHE_DIR at ${TMPDIR:-/tmp}/sd-ai-command-pack-* unqualified.
  - scripts/sd-ai-command-pack-shell-lib.sh:165 — sibling helper UID-qualifies the same pattern; update_repomix:12 too.
  - docs/SD_AI_COMMAND_PACK.md:1290 — unqualified pattern documented fleet-wide.
- why: Another local user can pre-create the fixed /tmp paths and have planted bytecode/tools executed under this user's identity.
- fix: UID-qualify the fallback, create 0700, fail on foreign ownership; upstream fix + doc update.
- notes: tracked upstream in sd-ai-command-pack task 07-25-user-scope-toolchain-caches (2026-07-25); SE-side task retired.
- notes: 2026-08-15 reconciled at 564d4a2 — the variables moved to
  sd_ai_command_pack_lib.py:118-124 and the cache root is UID-qualified at
  :333.

## A-019 — --backup copies follow symlinks and drop the source file's permission bits
- status: fixed
- severity: P3 · effort: S · confidence: Plausible
- dimension: security
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - installer/fileops.py:409 — shutil.copyfile follows symlinks; .bak gets umask-default mode.
  - installer/fileops.py:181 — check-then-use window at the .bak path.
- why: A 0600 file gets a 0644 .bak; a symlink planted in the window redirects the write outside the install root (not reachable today).
- fix: O_CREAT|O_EXCL|O_NOFOLLOW backup open; copy into the descriptor; preserve source mode.
- notes: 2026-08-15 reconciled at 564d4a2 — installer/fileops.py:406 opens the
  backup exclusively and streams via copyfileobj instead of shutil.copyfile.

## A-020 — No coverage measurement or floor in any gate
- status: fixed
- severity: P2 · effort: M · confidence: Plausible
- dimension: testing
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - Makefile:24 — bare unittest discover.
  - .github/workflows/tests.yml:32 — no coverage step/threshold in any lane; requirements-dev.txt:3 has no coverage tool.
- why: Untested branches in installer/scripts merge green silently under heavy autonomous development.
- fix: coverage.py with a floor scoped to installer/, install.py, .github/scripts; fail CI below it.
- notes: 2026-08-15 reconciled at 564d4a2 — Makefile:106 runs `coverage
  report --fail-under=80`.

## A-021 — Subprocess git tests inherit the developer's global git config
- status: fixed
- severity: P3 · effort: S · confidence: Plausible
- dimension: testing
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - tests/test_release_gate.py:17 — git() helper with no env scrubbing; commits and pushes in tests.
  - tests/test_skill_review.py:904 — raw git init with inherited user config; no isolation anywhere in tests/.
- why: make test fails or runs user hooks under common git configs (gpgsign, hooksPath) while CI stays green.
- fix: GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_SYSTEM=/dev/null (or HOME=temp) in the git helpers.
- notes: 2026-08-15 reconciled at 564d4a2 — tests/test_release_gate.py passes
  env=git_env() at every git call site.

## A-022 — `update` is the only installer lifecycle command with no real end-to-end test
- status: fixed
- severity: P3 · effort: M · confidence: Plausible
- dimension: testing
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - tests/test_management.py:108 — update tests assert only mock call sequences.
  - installer/management.py:146 — real flow mutates the user checkout and re-execs install.py; install/remove have subprocess e2e, update none.
- why: Regressions in real git interplay or the re-exec handshake pass CI.
- fix: One e2e: temp clone + bare origin one commit ahead → run update → assert pull + refresh.
- notes: 2026-08-15 reconciled at 564d4a2 — tests/test_update_e2e.py provides
  the missing end-to-end coverage.

## A-023 — generated/skills/ payload surface undocumented; manifest schema and CONTRIBUTING payload definition stale
- status: fixed
- severity: P2 · effort: S · confidence: Plausible
- dimension: documentation
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - docs/SE_AI_COMMAND_PACK.md:848 — schema says source is "under templates/" — false for 52 generated/ rows (manifest.json:39).
  - README.md:430 — regenerated-surfaces list omits generated/; Layout table has no generated/ row.
  - CONTRIBUTING.md:14 — payload definition omits generated/** though the gate enforces it since a267be0.
- why: 52 shipped payload files and the runtime-overlay mechanism are invisible in maintainer docs; the schema reference is wrong.
- fix: Add layout row; correct schema row, surface lists, payload definition; extend never-hand-edit rule.
- notes: merged from documentation + release-hygiene reviewers.
- notes: 2026-08-15 reconciled at 564d4a2 — CONTRIBUTING.md and README.md both
  document the generated/ surface.

## A-024 — Contributor docs omit the `make setup` prerequisite; documented flow fails on a fresh clone
- status: fixed
- severity: P2 · effort: S · confidence: Plausible
- dimension: documentation
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - README.md:440 — maintaining steps start at make generate; CONTRIBUTING never mentions make setup.
  - .github/scripts/generate-skill-surfaces.py:22 — fresh clone → ModuleNotFoundError: yaml; Makefile:2 falls back to system python3.
- why: The first documented contributor command crashes without the never-mentioned setup target.
- fix: Add step 0 "make setup" to README + CONTRIBUTING.
- notes: 2026-08-15 reconciled at 564d4a2 — `make setup` is documented in
  README.md and CONTRIBUTING.md.

## A-025 — Committed 1 MB generated repomix map: ~45% of history weight, freshness by manual chore only
- status: fixed
- severity: P2 · effort: M · confidence: Plausible
- dimension: bloat
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - docs/repomix-map.md:1 — 983.7 KB generated file; 114 blobs, 23.06 MiB compressed of 51 MB .git; 50/475 commits touch it.
  - .trellis/spec/backend/quality-guidelines.md:1130 — spec mandates regenerate+commit with no --check gate (tests assert scope only).
  - scripts/sd-ai-command-pack-install-audit.py:246 — tooling treats the map as optional context.
- why: One regenerable artifact dominates clone cost, grows ~1 MB per regeneration, and drifts silently when the manual step is skipped.
- fix: Gitignore + generate on demand (preferred) or add a --check drift gate; update quality-guidelines + README.
- notes: merged from bloat + improvements reviewers.
- notes: 2026-08-15 reconciled at 564d4a2 — docs/repomix-map.md is no longer
  tracked; .gitignore cites this policy and the map is produced on demand.

## A-026 — Unreferenced repo-root wrapper scripts/se-ai-command-pack-skill-review.py is dead code
- status: fixed
- severity: P3 · effort: S · confidence: Plausible
- dimension: bloat
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - scripts/se-ai-command-pack-skill-review.py:9 — runpy forwarder; only references are an archived task and the generated map.
- why: Dead entry point nothing installs, tests, or documents; drifts silently.
- fix: Delete, or document + test if repo-root invocation is wanted.
- notes: 2026-08-15 reconciled at 564d4a2 —
  scripts/se-ai-command-pack-skill-review.py is deleted.

## A-027 — Fleet status collects each consumer repo serially
- status: fixed
- severity: P2 · effort: M · confidence: Plausible
- dimension: performance
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - scripts/sd-ai-command-pack-status.py:1547 — collect_fleet iterates consumers, no concurrency.
  - scripts/sd-ai-command-pack-status.py:967 — 2+ serial gh calls per repo, 20s timeout each (:23); ~12 git subprocesses per repo.
- why: 10–20 repo fleet takes 15–40s; degraded network stacks 20s timeouts serially.
- fix: ThreadPoolExecutor over consumers, output in registry order; upstream fix.
- notes: tracked upstream in sd-ai-command-pack task 07-25-parallelize-fleet-status (2026-07-25); SE-side task retired.
- notes: 2026-08-15 reconciled at 564d4a2 — status.py:3284 collects the fleet
  through a ThreadPoolExecutor.

## A-028 — review-learnings fetches Copilot comments with one gh GraphQL subprocess per PR (N+1)
- status: fixed
- severity: P2 · effort: M · confidence: Plausible
- dimension: performance
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - scripts/sd-ai-command-pack-review-learnings.py:1174 — per-PR gh api graphql spawn.
  - .agents/skills/sd-review-learnings/SKILL.md:39 — documented --github-days 2 --update at measured cadence → ~30–45 serial spawns per run.
- why: Dozens of serial network subprocesses per run, growing toward secondary-rate-limit territory.
- fix: Alias-batched GraphQL (15–25 PRs per query); upstream fix.
- notes: primary route: absorbed by sd-ai-command-pack 07-25-generalize-review-learnings-across-reviewers; tactical task 07-25-batch-review-learnings-github filed upstream (2026-07-25); SE-side task retired.
- notes: 2026-08-15 reconciled at 564d4a2 — review-learnings.py:1951 uses an
  aliased-batch query, batching 20 PRs per request.

## A-029 — review-preflight recomputes changed-path and base-ref discovery per check
- status: open
- severity: P3 · effort: S · confidence: Plausible
- dimension: performance
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - scripts/sd-ai-command-pack-review-preflight.mjs:2040 — unmemoized discovery called at :485, :598, :935, :1281 (+ base-ref at :1113, :1889, :2000).
  - scripts/sd-ai-command-pack-review-preflight.mjs:15 — per-run memoization is the established pattern for other caches.
- why: ~14–24 redundant git spawns per run recomputing identical results.
- fix: Per-run module caches reset in runReviewPreflight(); upstream fix.
- notes: tracked upstream in sd-ai-command-pack task 07-25-reduce-review-tooling-spawns (2026-07-25); SE-side task retired.
- notes: 2026-08-15 reconciled at 564d4a2 — no memoization of changed-path or
  base-ref discovery in review-preflight.mjs; readTextCache at :21 is a
  different cache. The file was restructured, so the original line numbers no
  longer resolve.
- notes: 2026-08-16 reconciled at 74ad2f6 — NOT VERIFIABLE HERE, relayed as
  platypeeps/sd-ai-command-pack#488. The cited files were vendored pack content and left this
  repository at `b7dd320` (thin conversion); `scripts/` is now enforced-empty by
  `ScriptsDirectoryStaysEmptyTest` and no repo-own successor exists under
  `.github/scripts/`. This is not evidence that the unmemoized discovery was fixed -- only that
  this repository can no longer see it. The upstream issue states plainly that
  its evidence is from 2026-08-15 and unverified against that repository's
  current main. Status stays `open` rather than a relayed-* value because the
  managing skill's vocabulary is `open|fixed|regressed`
  (sd-audit-repo/SKILL.md:228); an invented status would put this file out of
  contract with the tool that rewrites it.

## A-030 — review-scope classifier forks a grep plus subshells per changed file
- status: open
- severity: P3 · effort: S · confidence: Plausible
- dimension: performance
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - scripts/sd-ai-command-pack-review-scope.sh:127 — per-file grep -Fxq + ~3 subshells (:259–273).
  - scripts/sd-ai-command-pack-full-check.sh:466 — run twice per full check; 378-target refresh diffs pay ~1.5–3s each pass.
- why: Routine rollout branches pay seconds of fork overhead for a one-process membership test.
- fix: Associative array or single grep -Fxf pass; upstream fix.
- notes: tracked upstream in sd-ai-command-pack task 07-25-reduce-review-tooling-spawns (2026-07-25); SE-side task retired.
- notes: 2026-08-15 reconciled at 564d4a2 — review-scope.sh:127 still runs
  `grep -Fxq` per path, called per changed file from :373.
- notes: 2026-08-16 reconciled at 74ad2f6 — NOT VERIFIABLE HERE, relayed as
  platypeeps/sd-ai-command-pack#489. The cited files were vendored pack content and left this
  repository at `b7dd320` (thin conversion); `scripts/` is now enforced-empty by
  `ScriptsDirectoryStaysEmptyTest` and no repo-own successor exists under
  `.github/scripts/`. This is not evidence that the per-file grep fork was fixed -- only that
  this repository can no longer see it. The upstream issue states plainly that
  its evidence is from 2026-08-15 and unverified against that repository's
  current main. Status stays `open` rather than a relayed-* value because the
  managing skill's vocabulary is `open|fixed|regressed`
  (sd-audit-repo/SKILL.md:228); an invented status would put this file out of
  contract with the tool that rewrites it.

## A-031 — No dependency-update or CVE-audit path; dogfooded sd-update-deps workflow is inert
- status: fixed
- severity: P2 · effort: S · confidence: Plausible
- dimension: dependencies
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - requirements-dev.txt:3 — exact pins committed once, never moved; no audit tooling repo-wide.
  - .agents/skills/sd-update-deps/SKILL.md:14 — workflow triages bot PRs only; no dependabot/renovate config exists.
- why: Pins age silently, CVEs unseen, and the pack's own update workflow can never fire here.
- fix: .github/dependabot.yml for pip + npm; optionally a scheduled pip-audit lane.
- notes: 2026-08-15 reconciled at 564d4a2 — .github/dependabot.yml exists and
  drives the update path.

## A-032 — .opencode/package.json declares an unused, floating @opencode-ai/plugin with no lockfile
- status: open
- severity: P3 · effort: S · confidence: Plausible
- dimension: dependencies
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - .opencode/package.json:3 — "^1.14.39", no lockfile; all .opencode JS imports only node builtins.
  - .gitignore:52 — node_modules ignored, so OpenCode auto-installs fresh floating 1.x per machine.
- why: Unpinned npm fetch on every machine for a package nothing imports.
- fix: Remove; or pin exact + commit lockfile if kept for editor types.
- notes: 2026-08-15 reconciled at 564d4a2 — .opencode/package.json:3 still
  declares the floating dependency; `git log` on that path shows only the
  original add. The local disposition recorded in task
  08-10-upstream-relay-opencode-plugin-dep was the decision to relay upstream,
  not an edit to the package file.
- notes: 2026-08-16 reconciled at 74ad2f6 — still open, unchanged:
  .opencode/package.json still declares `@opencode-ai/plugin: ^1.14.39` with no
  lockfile. Owned by the parked task 08-10-upstream-relay-opencode-plugin-dep,
  which targets mindfold-ai/Trellis and was deliberately not relayed.

## A-033 — requirements-dev.txt pins only top-level packages; transitives float unpinned and unhashed
- status: fixed
- severity: P3 · effort: S · confidence: Plausible
- dimension: dependencies
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - requirements-dev.txt:5 — 3 pins; 5 unpinned transitives via mypy (local freeze).
  - .github/workflows/tests.yml:43 — plain pip install across 3.10/3.13 matrix; no hashes.
- why: Bad transitive release breaks CI non-reproducibly; no integrity hashes. Dev-only blast radius.
- fix: Fully pinned (hash-locked) compiled requirements for CI and make setup.
- notes: 2026-08-15 reconciled at 564d4a2 — requirements-dev.lock is committed
  fully pinned, hashed and wheel-only; `make lock-check` guards drift.

## A-034 — repomix refresh executes npx --yes with unlocked transitives and install scripts enabled
- status: open
- severity: P3 · effort: S · confidence: Plausible
- dimension: dependencies
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - .github/scripts/update-repomix:27 — `exec npx --yes "repomix@${repomix_version}"`; transitives fresh, lifecycle scripts on.
  - .github/scripts/update-repomix:25 — `export NPM_CONFIG_IGNORE_SCRIPTS=true` disables lifecycle scripts for the unattended fetch, so that half of the original finding is mitigated.
- why: Maintainer machines run a freshly resolved unlocked npm tree with scripts enabled.
- fix: --ignore-scripts, or committed package-lock + npm ci, or record risk as accepted.
- notes: 2026-08-15 reconciled at 564d4a2 — half addressed. The script moved to
  .github/scripts/update-repomix, which sets NPM_CONFIG_IGNORE_SCRIPTS=true at
  :26, closing the lifecycle-script half. `npx --yes repomix@1.16.1` at :27
  still resolves transitives fresh with no lockfile, so the unlocked-transitive
  half stands.
- notes: 2026-08-16 reconciled at 74ad2f6 — still open, and the path
  MOVED: `scripts/update_repomix:24` -> `.github/scripts/update-repomix:27`,
  the repo-own tooling home. Checking only whether the old path exists would
  have retired a live finding -- `scripts/` is empty since `b7dd320`, so a
  path-existence test reports "gone" for a file that simply relocated.
- notes: 2026-08-16 correction — the entry above misread the script. Line 24 is
  a comment, but line 25 is `export NPM_CONFIG_IGNORE_SCRIPTS=true`, which
  *disables* lifecycle scripts rather than merely documenting the risk. The
  original finding's "lifecycle scripts on" half is therefore already fixed.
  What remains: `npx --yes` pins only the top-level (`repomix@1.16.1`) and
  resolves transitives fresh with no lockfile, so the residual exposure is
  unpinned transitive resolution on a maintainer machine. Severity is lower
  than the original P3/S text implies. Recorded as a correction rather than a
  silent edit because the mistaken reading shipped in #242.

## A-035 — Local release-payload gate goes vacuous once changes are committed
- status: fixed
- severity: P2 · effort: S · confidence: Plausible
- dimension: tooling
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - Makefile:32 — release-check runs check-release-payload.py with no --base (default HEAD = uncommitted only, per its help at :176).
  - .github/workflows/tests.yml:60 — CI checks the full PR range local runs skip; vendored full-check version gate self-skips on manifest-name mismatch (full-check.sh:595).
- why: Committed payload change without a bump passes make check green and fails only at PR CI.
- fix: Pass --base origin/main (or merge-base) when resolvable, else HEAD.
- notes: 2026-08-15 reconciled at 564d4a2 — Makefile:163 passes `--base auto`,
  so the local gate is no longer vacuous.

## A-036 — Shipped payload Python (skill_review.py) sits outside every ruff/mypy gate; tools find real defects
- status: fixed
- severity: P2 · effort: S · confidence: Plausible
- dimension: tooling
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - Makefile:27 — lint scope excludes templates/…/skill_review.py (1952 lines, only shipped executable); tests.yml:44–45 mirrors.
  - templates/skills/se-review-skills/scripts/skill_review.py:297 — ruff B905; mypy errors at :673 and :268.
- why: The one Python file that runs on consumer machines is the least-guarded Python surface in the repo.
- fix: Add path to ruff+mypy in Makefile and tests.yml; fix the three findings.
- notes: merged from tooling + improvements reviewers.
- notes: 2026-08-15 reconciled at 564d4a2 — Makefile:7-8 list skill_review.py
  in both LINT_PATHS and MYPY_PATHS.

## A-037 — Release-payload gate is PR-only while auto-tag-release fires on any push to main
- status: fixed
- severity: P3 · effort: S · confidence: Plausible
- dimension: tooling
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - .github/workflows/tests.yml:48 — gate if: pull_request; auto-tag-release (:88) needs [unittest, lint] only.
  - .github/scripts/create-release-tag.py:57 — existing tag left in place; consumers pull main HEAD (installer/management.py:190).
- why: Direct push (if permitted) or same-version concurrent merges ship payload whose version no longer identifies content; latent today.
- fix: Run the gate on push (base = last release tag) before auto-tag; and/or require up-to-date branches / document branch protection.
- notes: merged from tooling + consumer-impact reviewers.
- notes: 2026-08-15 reconciled at 564d4a2 — tests.yml:89 runs the gate on
  pull_request and on push to refs/heads/main.

## A-038 — No pip caching in any of the five CI jobs
- status: fixed
- severity: P3 · effort: S · confidence: Plausible
- dimension: tooling
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - .github/workflows/tests.yml:28 — setup-python steps (:28, :40, :55) without cache: pip.
- why: Five cold installs per PR run at heavy cadence — wasted runner minutes.
- fix: cache: pip + cache-dependency-path: requirements-dev.txt on each step.
- notes: 2026-08-15 reconciled at 564d4a2 — tests.yml:37,62,77 set `cache:
  pip`.

## A-039 — No concurrency group — superseded PR runs execute to completion
- status: fixed
- severity: P3 · effort: S · confidence: Plausible
- dimension: tooling
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - .github/workflows/tests.yml:1 — no concurrency: block.
- why: Rapid successive pushes leave stale 5-job pipelines running, delaying current results.
- fix: concurrency group on workflow+ref, cancel-in-progress for PRs.
- notes: 2026-08-15 reconciled at 564d4a2 — tests.yml:13 declares a concurrency
  group cancelling superseded PR runs.

## A-040 — Release payload gate omits install.py/installer/; installer behavior can ship without bump or changelog
- status: fixed
- severity: P2 · effort: S · confidence: Plausible
- dimension: release-hygiene
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - .github/scripts/check-release-payload.py:27 — PAYLOAD_PREFIXES = templates/, generated/, manifest.json only.
  - CHANGELOG.md:3 — 0.64.0 entry documents installer behavior — treated as release-worthy by convention.
- why: Installer flags/receipts/exit codes are declared consumer contract; a silent fix ships under an already-tagged version.
- fix: Add install.py + installer/ to PAYLOAD_PREFIXES (registry-metadata carve-out); update CONTRIBUTING.
- notes: 2026-08-15 reconciled at 564d4a2 — check-release-payload.py:42,48
  include installer/ and install.py as payload.

## A-041 — Changelog version 0.53.0 has no git tag; multi-bump PRs leave intermediate releases unfetchable
- status: open
- severity: P3 · effort: S · confidence: Plausible
- dimension: release-hygiene
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - CHANGELOG.md — 0.53.0 heading has no corresponding git tag; 90 tags vs 91 changelog versions, and 0.53.0 is the only one missing.
  - manifest.json history — PR #89 bumped twice in one branch; auto-tag tags only merged HEAD.
- why: Tags-match-changelog broken; gate checks only the top heading so recurrence is unguarded.
- fix: Gate base→head to exactly one version step, or collapse intra-PR bumps; document the policy.
- notes: 2026-08-15 reconciled at 564d4a2 — 89 tags against 90 changelog
  headings; 0.53.0 is still untagged.
- notes: 2026-08-16 reconciled at 74ad2f6 — still open. The gap is
  still exactly one and still 0.53.0; the counts moved 65/66 -> 90/91 as
  releases accumulated, including v0.70.0 which tagged correctly. So the
  multi-bump-in-one-branch shape has not recurred since, but the historical
  hole is unrepaired.

## A-042 — No documented bump policy: perpetual 0.x with no minor-vs-patch rule or breaking-change signal
- status: fixed
- severity: P3 · effort: S · confidence: Plausible
- dimension: release-hygiene
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - docs/SE_AI_COMMAND_PACK.md:837 — "Semver; bound to CHANGELOG.md" is the only scheme statement.
  - CHANGELOG.md:129 — 0.50.0 removes public behavior indistinguishably from feature minors.
- why: Fleet consumers must read every entry to spot removals; bump choice is undocumented convention.
- fix: Document bump rules + Removed/Breaking convention in CONTRIBUTING.md, or state 1.0 criteria.
- notes: 2026-08-15 reconciled at 564d4a2 — docs/SE_AI_COMMAND_PACK.md:1088
  points at the CONTRIBUTING.md patch-versus-minor policy.

## A-043 — 42 hand-copied per-skill shared-reference tests instead of the registry-driven form beside them
- status: fixed
- severity: P2 · effort: M · confidence: Plausible
- dimension: improvements
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - tests/test_generate.py:218 — ~790-line block of identical per-skill methods (42 copies).
  - tests/test_generate.py:174 — generic registry-driven precedent already exists in-file.
- why: Every skill addition (highest-frequency operation) pays a manual copy; forgotten copies are silently uncovered.
- fix: Snapshot dict + one subTest-driven test over SKILL_NAMES; retire per-skill methods.
- notes: 2026-08-15 reconciled at 564d4a2 — tests/test_generate.py:445,630
  iterate gen.SHARED_REFERENCES instead of hand-copied per-skill methods.

## A-044 — README promises $CODEX_HOME support the installer never implements
- status: fixed
- severity: P2 · effort: S · confidence: Plausible
- dimension: consumer-impact
- first-seen: 2026-07-25 @ 4067caa
- last-seen: 2026-07-25 @ 4067caa
- evidence:
  - README.md:360 — codex row claims "(honors `$CODEX_HOME`)".
  - installer/registry.py:61 — hard-coded .codex/skills; zero environ reads in install.py/installer/.
  - docs/SE_AI_COMMAND_PACK.md:927 — operator guide states "No environment variables are read in v0.1."
- why: Relocated-CODEX_HOME consumers get skills where Codex never reads them; the pack's two docs contradict each other.
- fix: Implement CODEX_HOME resolution (with test), or delete the README claim and document the --root/symlink workaround.
- notes: merged — found independently by architecture, documentation, improvements, and consumer-impact reviewers.
- notes: 2026-08-15 reconciled at 564d4a2 — README.md:164 states ~/.codex is
  read regardless of $CODEX_HOME.
