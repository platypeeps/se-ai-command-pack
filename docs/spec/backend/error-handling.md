# Error Handling

> How CLI and installer failures are represented and propagated.

---

## Overview

Expected user-facing failures abort with `SystemExit` and an actionable message
prefixed with `error:`. Helpers validate inputs before mutation, catch narrow
operating-system or decoding failures to add context, and suppress exception
chaining when the lower-level traceback would not help a CLI user.

## Error Types

- Use `SystemExit("error: ...")` for invalid manifests, unsafe paths, missing
  install state, filesystem failures, and refused lifecycle operations.
- Use `argparse` errors for invalid command-line syntax so usage and a nonzero
  exit status remain conventional.
- Use `RuntimeError` for programmer/configuration invariants evaluated during
  module initialization, as in `installer.registry.validate_registry()`.
- Return integer status codes when non-success is an expected query result.
  `installer.management.pack_status()` prints “not installed” and returns `1`.
- Do not add custom exception classes unless callers need to distinguish and
  recover from multiple domain failure types.

## Error Handling Patterns

Catch the narrow exception at the boundary that can add useful path or command
context:

```python
try:
    return path.read_text(encoding="utf-8")
except FileNotFoundError:
    raise SystemExit(f"error: manifest not found: {path}") from None
except UnicodeDecodeError as error:
    raise SystemExit(f"error: manifest is not valid UTF-8: {path} ({error})") from None
```

Subprocess wrappers must preserve the relevant stderr/stdout and command:
`installer.management._run_git()` reports `git <args> failed: <detail>`.
Never continue to an applying step after validation, dry-run, or subprocess
planning fails.

Filesystem mutations must be sequenced after path validation and planning.
`installer/fileops.atomic_write_bytes()` also cleans up its temporary file in a
`finally` block.

## CLI Error Responses

This project has no HTTP API. CLI failures write a concise `error:` message to
stderr and exit nonzero; dry-run/status output goes to stdout. Tests should
assert the return code and a stable, user-actionable fragment rather than an
entire platform-dependent error string.

## Examples

- `installer/manifest.py` converts JSON, UTF-8, schema, and path failures into
  contextual `SystemExit` messages.
- `installer/fileops.py` refuses non-file destinations and reports write,
  backup, and removal failures with the affected path.
- `tests/test_install_core.py` and `tests/test_management.py` assert both
  failure behavior and message fragments.

## Common Mistakes

- Catching `Exception` and hiding programming errors.
- Dropping subprocess stderr, which removes the actionable Git failure.
- Printing an error and returning success.
- Mutating files before all safety checks and dry-run planning have passed.
- Exposing tracebacks for routine invalid user input.
