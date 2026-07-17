# Logging Guidelines

> Operational output conventions for this command-line pack.

---

## Overview

The project does not use Python's `logging` module or emit persistent logs.
Commands print deterministic, human-readable plans and summaries. Errors use
stderr through `SystemExit`/`argparse`; normal status and plan output use stdout.

Do not add a logging framework for routine installer output. This is a short-
lived local CLI, and its current plain-text output is part of the tested user
contract.

## Output Categories

- **Status/summary:** installed version, root, source checkout, selected
  platforms, and result counts.
- **Plan:** dry-run actions such as create, preserve, remove, or backup before
  any applying run.
- **Warning/preservation detail:** explain why user-modified or unvouched files
  remain untouched.
- **Error:** concise `error:` text with a nonzero exit status.

There are no debug/info/warn/error log levels. If diagnostic verbosity becomes
necessary, add an explicit CLI contract and tests rather than unconditional
debug printing.

## Format

- Keep output line-oriented and deterministic so tests and humans can scan it.
- Use home-relative or selected-root-relative paths when possible; path display
  helpers in the installer keep output meaningful for user and temporary roots.
- Name the operation and state explicitly, for example `mode: dry-run`,
  `checkout: <version> (refresh available)`, or `would-remove`.
- Send child Git/installer output through the subprocess contract instead of
  inventing a second structured-log format.

## What to Report

- The requested mode and selected install root.
- Planned/applied file outcomes and preservation reasons.
- Version, platform, checkout, and provenance state relevant to lifecycle
  decisions.
- External command failures with enough stderr/stdout to act on them.

Examples live in `installer/management.pack_status()`, the result-reporting
functions in `install.py`, and assertions in `tests/test_install.py` and
`tests/test_management.py`.

## What Not to Report

- Full file contents, skill prompts, or user-modified configuration.
- Environment variables, credentials, tokens, or unrelated home-directory
  paths.
- Python tracebacks for expected CLI failures.
- Noisy per-function tracing or duplicate plan/apply messages that obscure the
  final result.
