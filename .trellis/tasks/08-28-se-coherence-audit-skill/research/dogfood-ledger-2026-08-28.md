# se-coherence-audit dry run — this repository (2026-08-28)

Acceptance A6. Invocation: `input=AGENTS.md,.claude/rules/`

## Audit contract

- Resolved file set: **2 files, 5,237 bytes** (from 2 supplied paths)
- Exclusions: none
- Detector classes run: contradiction, vagueness, bandaid, redundancy (all four)
- Precedence: **declared in the corpus, partially** — `AGENTS.md:44-48` declares
  that the repo-own routing block overrides Trellis-emitted next actions, and
  enumerates three sources it governs
- Depth: `deep` — the run lists its near-misses and dropped candidates
  individually, which is what `deep` adds
- Severity floor: `low`, set by the default `min_severity=`; `depth=` sets no
  floor of its own
- Sensitivity: `standard` — the corpus is agent-instruction text with no
  secret-shaped or customer material, so nothing was redacted or withheld
- Output shape: `ledger`
- Overall confidence: medium — the corpus is small, so the run exercises the
  detectors rather than establishing that the repository is coherent

## Coverage

| Set | Files |
|---|---|
| read in full | `AGENTS.md` (88 lines), `.claude/rules/sd-planning-adversarial-review.md` (11 lines) |
| sampled | none |
| skipped | none |

**Fully audited within the supplied boundary.** Both supplied paths resolved
and were read end to end. The audit covers agent-instruction text only; no other
corpus was read. An earlier draft of acceptance A6 also named a root
agent-instruction file that this repository does not have; that criterion was
corrected rather than satisfied with a substitute.

## Findings ledger

```
M-1  missing-precedence  high  confidence: medium
  criterion: exclusive-trigger
  precedence: declared at AGENTS.md:44-48 but reaching neither side
  AGENTS.md:13
    "If a Trellis command is available on your platform (e.g.
     `/trellis:finish-work`, `/trellis:continue`), prefer it over manual steps."
  AGENTS.md:35
    "- `finish-work` — canonical `/sd:finish-work`; bypassed by resolving
     `trellis-finish-work` directly"
  why: the same trigger — needing to finish work — routes to `/trellis:finish-work`
       by one passage and away from it by the other, which calls that route a
       bypass rather than an alternative. Classified `missing-precedence` rather
       than `contradiction`: the clause at AGENTS.md:44-48 declares an ordering
       but does not cover both sides, because it enumerates "the session hooks,
       the `.trellis/workflow.md` phase flows, and the Trellis CLI itself" and
       omits the vendored Trellis block of AGENTS.md, which is where line 13
       lives. No declared ordering reaches these two passages, so the absent
       precedence is the finding. Confidence is medium, not high, because a
       reader may extend that clause by analogy — but the corpus does not say so.
  resolution: add the vendored `AGENTS.md` Trellis block to the enumeration at
       AGENTS.md:44-48, so the precedence covers the file it is written in.
```

```
R-1  redundancy  low  confidence: high
  criterion: overlapping-authority
  AGENTS.md:29
    "The SD command pack wraps four Trellis workflows. For each, the `sd:*`
     wrapper is the canonical entry point in this repository."
  AGENTS.md:57
    "The SD AI Command Pack wraps several Trellis workflows. Where a wrapper
     exists, it is the canonical entry point"
  why: two managed blocks in one file each define which entry points are
       canonical for wrapped workflows, and neither declares a relationship to
       the other. They are owned by different writers — the first is repo-own,
       the second is replaced on the next pack install — so they drift
       independently, and a reader asking "which entry point is canonical" gets
       two answers with no rule for which governs. Severity is `low`, not
       higher: the two copies agree today, so the harm is drift risk with no
       present-tense wrong outcome — the severity model's own `low` case.
  resolution: have the repo-own block state its relationship to the pack block
       (which one governs when they differ), since only the repo-own block can
       be edited here.
```

## Observations

**Near-misses dropped** (`depth=deep`):

- `AGENTS.md:44-48` — "Those files are vendored and cannot be corrected from
  this repository" reads as a workaround, but records its root cause and names
  the external constraint. Dropped by the **bandaid** near-miss "a workaround
  for a named external defect". Task `08-10-upstream-entrypoint-routing-mechanisms`
  tracks the upstream fix.
- `AGENTS.md:76-78` — "list the installed skills rather than relying on a list
  written down somewhere" sits above a written-down list at `AGENTS.md:34-37`.
  Dropped by the **contradiction** near-miss "two rules whose scopes are stated
  and do not overlap": the list at 34-37 states its own pinning at `AGENTS.md:50-51`
  (`tests/test_agent_routing.py` derives the four workflows at run time), which
  is the property the warning is about.
- `.claude/rules/sd-planning-adversarial-review.md:9` — "Apply that contract once
  per coherent planning edit batch" leaves "coherent planning edit batch"
  undefined. Held below `confidence: medium` and therefore **not reported**: a
  reader can approximate the boundary, and the criterion `undefined-gate`
  requires that they cannot.

## Limits

- 99 lines of corpus is enough to exercise all four detectors and both drop
  rules, but not enough to claim the repository's instruction surface is
  coherent. The rest of `.trellis/spec/` and `docs/` were not supplied and were
  not read.
- Both findings are in `AGENTS.md`. That is where the corpus's directives are,
  not evidence that other files are clean.

## Verification of A6

- Every reported finding carries at least one `path:line` and verbatim quoted
  text: **yes** (M-1: 2 locations; R-1: 2 locations). R-1 quotes the two
  authority-claiming sentences rather than the block headings above them: a
  heading names a section, it is not the rule that overlaps.
- Every reported pairing manually confirmed against both quoted passages:
  **yes** — M-1's two quotes were re-read at `AGENTS.md:13` and `AGENTS.md:35`
  and the precedence clause at `AGENTS.md:44-48` was read in full before
  classifying. Zero fabricated pairs. The run reported no `contradiction`: the
  one conflict it found is classified `missing-precedence`, because no declared
  ordering reaches both of its sides.
