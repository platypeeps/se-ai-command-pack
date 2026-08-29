# Replace brittle prose pins in se-coherence-audit skill tests with contract assertions

## Goal

`CoherenceAuditSkillTest` in `tests/test_skills.py` guards the
`se-coherence-audit` skill by asserting that exact prose sentences appear in
`SKILL.md` and its two references. During PR #278 those literals broke five
separate times while the contract they guard never changed — each break was a
rewording of the same rule, not a regression. The tests cost review rounds and
gave no protection, because a reviewer rewording a sentence had to repin the
literal rather than justify a behavior change.

Replace the prose pins with assertions that fail when the *contract* changes
and pass when only the wording does.

Where a contract has a structural carrier — an argument, a ledger field, a
class, a criterion — that holds without qualification. A few contracts have no
such carrier: the read-only safety rules and the confidence floor are prose and
nothing else. Those keep a minimal token pin, which a voice-inverting rewrite
still breaks. The acceptance criteria below separate the two cases rather than
claiming the stronger property for both, and the bound is recorded in the
research notes.

## Requirements

- Identify every assertion in `CoherenceAuditSkillTest` that pins a full prose
  sentence, and classify each by the contract it is standing in for.
- Replace each with an assertion on the durable surface: the argument set and
  its allowed values, the ledger schema's field names and their cardinality
  rules, the three conflict classes (`resolved-by-precedence`,
  `missing-precedence`, `contradiction`), and the four detector classes.
- Keep the two contracts that most needed guarding and were most fragile:
  1. **Classification** — a conflict is classified by whether an authority
     ordering could settle it, and authority is the block a passage lives in,
     not the file.
  2. **Redaction** — `sensitivity=` may withhold a quote, and a withheld quote
     marks the finding unquotable rather than dropping it. `ledger-format.md`
     and `SKILL.md` must agree on this; a divergence is exactly the defect a
     Copilot thread caught on PR #278.
- Do not weaken coverage: the replacement must still fail if the skill drops an
  argument, a ledger field, a detector class, or either contract above.
- Leave `EXTERNAL_INPUT_SKILLS`, the family map, and the `SKILL_NAMES` ordering
  assertions alone — those pin identifiers, not prose, and did not break.

## Acceptance Criteria

- [x] No assertion in `CoherenceAuditSkillTest` requires a full prose sentence
      to match verbatim, and every contract with a structural carrier is
      asserted against that carrier rather than against prose about it. A
      surviving token pin is permitted only where the research notes name the
      contract and show no structural surface exists for it.
- [x] Rewording a sentence whose contract has a structural carrier — an
      argument, a ledger field, a class, a criterion, a report field — leaves
      the suite green. Contracts with no structural carrier (the read-only
      safety rules, the confidence floor) keep a shortest-token pin, which a
      voice-inverting rewrite still breaks; that bound is deliberate and is
      recorded in the research notes. Demonstrate both halves with worked
      rewordings there.
- [x] Deleting a documented argument, a ledger field, a conflict class, or a
      detector class still fails the suite.
- [x] Dropping the redaction carve-out from either `SKILL.md` or
      `ledger-format.md`, or letting the two disagree, fails the suite.
- [x] `make check` is green.

## Notes

- Related follow-up, out of this repository's scope: the `sd-review` remote
  dispatch forwards the local attempt number as the remote attempt, so an
  attempt above 1 with no prior remote attempt fails the action's
  `request.rerequestOf` precondition and then reports `pending` forever because
  the dispatch is idempotent. Observed on run 33221193956 during PR #278; the
  workaround was a fresh `--attempt-id` at `--attempt 1`. The coordinator lives
  in `platypeeps/sd-ai-command-pack`, not here.
