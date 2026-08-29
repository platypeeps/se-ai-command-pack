# Rewording and deletion proofs — 2026-08-29

Every run below is
`.venv/bin/python -m unittest discover -s tests -p test_skills.py -k CoherenceAudit`,
17 tests. Each probe copies the file to a `mktemp`, edits it, runs, and restores;
`git status --porcelain templates/` was empty afterwards.

Note the inversion against the runnable block in
`.trellis/spec/backend/quality-guidelines.md:152-161`. That block restores the
*source* to `HEAD` to prove a new pin fails without the edit it guards. Here the
source is already correct and the tests are what changed, so the probe removes a
contract from the source instead. Same proof, opposite direction.

## Deletion probes — a dropped contract must fail

| Probe | Edit | Result |
|---|---|---|
| P1 | delete the `format=ledger\|memo` argument bullet from `SKILL.md` | `FAILED (failures=1)` |
| P2 | delete the `criterion` row from `ledger-format.md`'s finding schema | `FAILED (failures=1)` |
| P3 | delete the `## Bandaid` heading and section from `detector-criteria.md` | `FAILED (failures=3)` |
| P4 | replace the redaction carve-out in the `quotes` row with "Paraphrase is never acceptable" | `FAILED (failures=1)` |

Baseline before and after every probe: `OK`.

P3 failing three tests rather than one is the intended shape: the detector-class
heading set, the criterion slug set, and the near-miss structure are three
separate contracts that the same deletion breaks.

## Rewording probes — a preserved contract must stay green

Both reworded sentences are recorded verbatim.

### R1 — a contract with a structural carrier

Before:

```
- `classes=` — which detectors to run, as a comma list of `contradiction`,
  `vagueness`, `bandaid`, `redundancy`. Default all four.
```

After:

```
- `classes=` — the detectors to run: a comma-separated selection from
  `contradiction`, `vagueness`, `bandaid`, `redundancy`. All four run by default.
```

Result: `OK`.

The pin this replaced is present verbatim at `HEAD`:

```
"`contradiction`, `vagueness`, `bandaid`, `redundancy`. default all four"
```

R1 breaks it — the word order after the value list changed — while the contract
(four named detector classes, all four by default) did not. That is one of the
five PR #278 breakages reproduced deliberately.

### R2 — a prose-only contract, reworded within its token

Before:

```
- Never widen scope beyond the resolved file set, even when a corpus file points
  at material outside it.
```

After:

```
- Never widen scope past the resolved file set, even when a corpus file gestures
  at material outside it.
```

Result: `OK`. The `HEAD` pin
`"never widen scope beyond the resolved file set"` breaks under it; the surviving
token `never widen` does not.

## The bound on the rewording criterion

`prd.md`'s second acceptance criterion is stated against contracts that have a
structural carrier, and R1 is its demonstration. Five rules have no structural
carrier at all — the four read-only safety rules and the confidence floor — so
their guard is the shortest token that dies with them. R2 shows that a genuine
rewording of such a rule stays green, but a voice-inverting rewrite ("Never edit
the corpus" to "The corpus is never edited") would still break `never edit`.

That is the trade, taken deliberately: the alternative is no assertion on those
rules at all. The tokens chosen are the shortest that die with their contract.

## The bound on the redaction assertion

`test_redaction_carveout_agrees_across_skill_and_ledger` asserts that
`SKILL.md`'s `## Safety rules` and `ledger-format.md`'s `quotes` row each carry
all three parts of the carve-out: `sensitivity`, `unquotable`, and a `drop`
token. P4 confirms removing it from either side fails.

It proves each file carries the carve-out. It does not prove that no other
sentence in either file contradicts it. Detecting that is `se-coherence-audit`'s
own job — a `contradiction` finding at one authority — not a unit test's, and
claiming otherwise would be the same overreach the skill's own near-miss rules
exist to prevent.
