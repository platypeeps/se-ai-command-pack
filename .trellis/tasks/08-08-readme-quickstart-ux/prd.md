# README buries the product and never names the post-install entry point

## Goal

Make the first screen of the README answer the three questions a new user
actually has — what is this, how do I install it, what do I type afterwards —
and make the install command's output end in a summary instead of a 553-line
file wall.

## Problem

Measured 2026-08-08 against README.md at 34,834 bytes:

- **84.5% of the file precedes `## Install`** (heading at README.md:386;
  29,431 bytes before it). There is no table of contents and no quick-start
  above the fold.
- **The catalog is printed twice, inconsistently.** A generated, marker-bounded
  table covers all 54 skills (README.md:31-115); hand-written prose then
  re-describes 34 of them (README.md:117-360). The other 20 get a table row
  only, so the prose section reads as an arbitrary subset rather than a tier.
- **Nothing tells the user what to do after install succeeds.** The headings go
  Skills → What gets installed where → Install → Update → Remove → How it
  works → Maintaining. All 54 skills are natural-language-triggered by design
  (command surfaces are a stated v0.1 non-goal, README.md:512), so discovery
  rests entirely on `se-help` — which the README names only as a catalog row
  (README.md:90) and in two maintainer-section mentions (README.md:463, 482),
  never as the starting point.
- **No minimum Python version is declared anywhere user-facing.** CI tests
  3.10 and 3.13 (`tests.yml:20-28`) and CONTRIBUTING.md:28-31 mentions the
  matrix in a coverage context, but no user-facing document states a floor a
  person installing the pack can rely on.
- **A cloner sees 21 `/sd:*` commands the README never explains.** The
  dogfooded sd-ai-command-pack surface is documented only in
  CONTRIBUTING.md:91-97; README's three `sd-` mentions (README.md:21, 319,
  513) are lineage and non-goals, not an explanation.
- **Install output is a wall.** `install.py:289-290` prints one status line
  per manifest payload row (553), plus receipt-retirement lines (556 total
  observed under `--all --dry-run`); `_print_install_summary` emits no
  aggregate count or completion line, and `--dry-run` produces the same wall.

## Requirements

- Restructure the README so that, within roughly the first screen: a
  one-paragraph description, the install command, the stated Python floor, and
  "after installing, ask your agent for `se-help`" (or equivalent phrasing) all
  appear. A table of contents or equivalent navigation for the rest.
- Resolve the double catalog: either delete the 34-skill prose subset in
  favour of the generated table, or make the prose section a deliberate,
  labelled tier with stated membership criteria. Do not leave an unlabelled
  arbitrary subset.
- Add one short section (or paragraph) explaining the dogfooded `sd-*` and
  `trellis-*` surfaces a cloner will see, linking to CONTRIBUTING for detail.
- Make `install.py` print an aggregate summary (per-platform file counts and a
  completion line). Per-file lines may remain under a verbose flag or for
  conflicts only — the default success path should be readable at a glance.
- Respect the generator: the catalog table and any marker-bounded region are
  owned by `.github/scripts/generate-skill-surfaces.py`. Structural README
  changes around those markers must keep `generate-skill-surfaces.py --check`
  green, and changes to generated content go through the generator, never by
  hand (CONTRIBUTING.md:9-14).

## Acceptance Criteria

- [ ] `## Install` content (or a quick-start equivalent) begins within the
      first ~60 lines of README.md.
- [ ] `se-help` is named as the post-install entry point in the quick-start
      path, not only in the catalog table.
- [ ] Exactly one catalog listing exists, or the second is a labelled tier
      with stated criteria; verified by reading the file, not the diff.
- [ ] A minimum Python version appears in the README install section,
      consistent with the CI matrix (3.10 is the lowest tested).
- [ ] The README explains why `/sd:*` commands appear in a fresh clone.
- [ ] `python3 install.py --user` on a machine with anchors present ends with
      an aggregate summary line; the 553-per-file wall is no longer the
      default success output.
- [ ] `make check` passes, including `generate-skill-surfaces.py --check` and
      the README wording contract in `tests/test_installer_docs.py`.

## Out of scope

- Adding command surfaces for se-* skills (stated non-goal, README.md:512).
- Changing what gets installed, the manifest, or the registry.
- CHANGELOG format or cadence.
- docs/ restructuring (operator guides, troubleshooting) — worth doing, not
  this task.

## Notes

- Sourced from the 2026-08-08 deep review (UX lane). Byte and line figures
  measured against the tree at commit 01976aa; re-measure before relying on
  exact offsets, since any README edit shifts them.
- `tests/test_installer_docs.py` pins some README wording — expect to update
  it in the same change.
- Lightweight; PRD-only.
