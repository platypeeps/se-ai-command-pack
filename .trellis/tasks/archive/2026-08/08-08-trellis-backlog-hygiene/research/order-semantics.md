# Ranker order semantics (evidence, 2026-08-09)

`scripts/sd-ai-command-pack-work-loop.py` (rank subcommand) applies
deterministic tie-breakers with the priority band **before** the `order`
signal — confirmed by reading the comparator (v-installed copy, rank
tie-breakers near line 874) and by adversarial review round 1 of this
task's PRD. Consequences for the quality-guidelines.md write-set:

- `order` is meaningful only within one priority band; a flat number line
  spanning P2 and P3 writers cannot serialize them against each other.
- The documented landing sequence must therefore be band-aware: P2 writers
  by order, then P3 writers by order (see the task `record.md`).
- Unique order values across the whole write-set remain useful for human
  readers, but they are documentation hygiene, not ranker semantics.
