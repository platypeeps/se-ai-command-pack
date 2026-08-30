# Implementation plan

1. Thread prior provenance hashes from `install.py` into payload planning and
   application, excluding never-vouched targets.
2. Extend `InstallResult` and the planned-result matcher to represent and
   revalidate a receipt-vouched `updated` destination.
3. Add the non-force, regular-file classification and atomic update path while
   retaining preservation, symlink, force, and backup precedence.
4. Add unit and end-to-end tests for Claude/Codex prior-version updates,
   provenance refresh, user drift, untrusted provenance, and preflight races.
5. Update lifecycle documentation, bump the release version/changelog, and run
   generation if versioned generated surfaces require it.
6. Run focused installer tests, `make check`, `git diff --check`, and the
   Trellis quality review; record evidence before finish-work.

## Risk and rollback points

- The mutation boundary is `install_file()`: never write before ownership and
  destination-state revalidation succeed.
- The full preflight must still stop every selected write when any conflict is
  present.
- Generated files must be refreshed only through `make generate`.
- If compatibility tests expose ambiguity, fail closed to `conflict` rather
  than broadening ownership inference.
