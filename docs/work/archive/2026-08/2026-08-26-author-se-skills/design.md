# Design: author the 13 se-* skills

## D1. Family: new `engineer` family, all 13 skills

The existing six families (`understand`/`decide`/`create`/`coordinate`/
`operate`/`improve`) describe knowledge work; stretching them over rust
discipline, gate probes, and rebase hygiene would blur both taxonomies.
Decision: add one family.

- `FAMILY_LABELS["engineer"] = "Engineer"`
- `FAMILY_DESCRIPTIONS["engineer"]` — "Design, build, and review software
  with disciplined engineering workflows." (exact wording tunable at edit
  time; dicts must stay order-matched, `registry.py:629` enforces it.)
- All 13 skills take `family="engineer"`, including the prose pair and
  `se-adr-review`: they exist to serve engineering deliverables, and a single
  family keeps the product line legible in the catalog.

Rejected: mapping onto existing families (semantic stretch, scatters the
line across the catalog); per-skill mixed assignment (arbitrary boundaries,
harder refresh story).

## D2. Runtime profiles

Every skill needs a row in `RUNTIME_PROFILE_ASSIGNMENTS` or the registry
self-check raises. Reuse existing profile constants where the axes match;
introduce no new constant unless an axis combination is missing.

| Skill | Invocation | Context | Model/effort | Profile |
| --- | --- | --- | --- | --- |
| `se-rust-design`, `se-rust-quality`, `se-rust-modules`, `se-rust-async`, `se-typed-holes` | both | inline | deep/high | `INSTRUCTIONAL` |
| `se-rust-review` | both | inline | deep/xhigh | new axes — add constant `ENGINEERING_REVIEW = RuntimeProfile("both", "inline", "deep", "xhigh")` if no existing constant matches at edit time |
| `se-gate-probes` | both | inline | deep/high | `INSTRUCTIONAL` |
| `se-docs-bustest` | both | inline | balanced/medium | `CONVERSATIONAL` |
| `se-rebase-hygiene` | user-only | inline | deep/high | `ARTIFACT_AUTHORING` axes match; renders `disable-model-invocation: true` |
| `se-skill-retro` | user-only | inline | deep/high | same as above |
| `se-prose-lint` | both | inline | balanced/medium | `CONVERSATIONAL` |
| `se-humanizer` | both | inline | deep/high | `INSTRUCTIONAL` |
| `se-adr-review` | both | inline | deep/xhigh | shares `se-rust-review`'s row |

Rationale anchors: review skills get xhigh effort (matching
`PACKAGE_REVIEW`'s posture) but stay `both` because they trigger on diffs;
`se-rebase-hygiene` and `se-skill-retro` are deliberate user actions —
upstream's `disable-model-invocation` intent maps exactly onto `user-only`.

## D3. Canonical body skeleton

Every SKILL.md carries the five required sections (generator-enforced):
`## When to use`, `## Arguments`, `## Workflow`, `## Safety rules`,
`## Final report`. Conventions on top:

- Frontmatter: `name` + trigger-accurate `description` only.
- Voice: this pack's imperative second person; no upstream sentences.
- Arguments: most of these skills take none — state "None." explicitly.
- Safety rules carry the binding conflict findings (parent C5): review-shaped
  skills defer verdict authority to the sd-review lane; `se-rebase-hygiene`
  plans and verifies but never pushes without user approval; prose skills
  state Vale degradation ("Vale absent: report the gap, continue without the
  deterministic pass").
- Routing: only `trellis-check`, `sd-review`, `task.py` surfaces, and sibling
  `se-*` skills by final name. The parent AC4 grep list is the negative test.

## D4. Per-skill content sources

Content is re-derived from the upstream ideas already digested in
[`../08-26-adopt-claude-skills/research/upstream-inventory-2026-08-26.md`](../08-26-adopt-claude-skills/research/upstream-inventory-2026-08-26.md):
write each body from the probe/checklist substance, not from the upstream
file. `se-gate-probes` keeps the 11-probe structure with a block-on-FAIL
table; `se-adr-review` implements the PRD's scope section (MADR completeness,
RFC-2119 drivers, premise-freshness as P1, fixed P1/P2/P3 report);
`se-skill-retro` merges retro + feedback routing (se-* defect -> fix in
`templates/skills/`; sd/Trellis finding -> owning repo task).

## D5. References

No new `_shared` references. Skills that need long checklists inline them —
13 new dirs with per-skill `references/` would be premature; promote to
shared references only when two skills need the same text.

## D6. Ordering and rollback

Author in dependency order so cross-references never dangle within a commit:
(1) registry family + profiles + 13 rows, (2) rust six + typed-holes,
(3) gates three, (4) prose two + skill-retro, (5) adr-review, (6) regenerate.
Each step leaves `--check` green or is reverted as a unit (see implement.md).
