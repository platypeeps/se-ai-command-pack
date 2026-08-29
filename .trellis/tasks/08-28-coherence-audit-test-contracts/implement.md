# Replace brittle prose pins in se-coherence-audit skill tests with contract assertions — Implementation Plan

## Execution Order

1. **Add the parsing helpers** beside the existing ones in
   `tests/test_skills.py` (after `resource_section()`, ~line 145):
   `markdown_table_column()`, `table_row()`, `bullet_body()`,
   `argument_names()`, `criterion_slugs()`. Each raises `AssertionError` on a missing heading,
   missing table, or empty result. Write these first and confirm the suite is
   still green — they are additive and no test uses them yet.
2. **Rewrite `CoherenceAuditSkillTest`** (`tests/test_skills.py:4124-4300`),
   method by method, in the file's existing order so the diff stays readable:
   - `test_coherence_audit_scope_is_supplied_and_never_widened` — keep the
     `input=`-is-required contract, scope it to the `input=` bullet via
     `bullet_body()`, shorten the workflow pins to `never read outside`,
     `file count`, and the three named emptiness cases.
   - `test_coherence_audit_runs_four_detector_classes` — replace the ordered
     prose pin with: the `classes=` bullet holds the four value tokens, and the
     `##` heading set of `detector-criteria.md` equals the four classes.
   - `test_every_detector_class_states_a_near_miss` — unchanged; structural.
   - **new** `test_every_detector_class_declares_its_criterion_slugs` — assert
     the four criterion-slug sets from the design table.
   - `test_contradiction_and_redundancy_require_two_locations` — keep the
     `at least two` pin; add the finding-schema `locations` row naming
     `contradiction`, `missing-precedence`, and `redundancy`.
   - `test_coherence_audit_classifies_conflicts_against_precedence` — the three
     conflict-class tokens in step 5, plus `missing-precedence` in the schema's
     `class` row.
   - **new** `test_authority_is_the_block_not_the_file` — the two independent
     anchors: `authority` and `block` inside the `contradiction` bullet, and
     `precedence: irrelevant` in the Contradiction worked example.
   - `test_coherence_audit_is_read_only_and_never_widens_scope` — the five short
     safety tokens.
   - `test_findings_need_quotes_locations_and_confidence` — short tokens plus
     `dropped, not reported`.
   - **new** `test_redaction_carveout_agrees_across_skill_and_ledger` — the
     shared three-token helper applied to both files.
   - `test_partial_coverage_is_never_reported_as_complete` — short tokens; add
     the coverage-set assertion from the coverage table.
   - `test_severity_is_scored_by_consequence_not_count` — the four tiers in both
     the schema row and the `## Severity` section; drop the sentence pin.
   - `test_coherence_audit_boundary_is_stated_from_both_sides` — unchanged.
   - `test_coherence_audit_resources_and_final_report_contract` — keep the three
     reference paths and five report field names; **delete** the
     line-break-sensitive resolution pin.
   - **new** `test_resolution_is_a_finding_field_not_a_report_section` —
     `resolution` in the schema field set, and no `## Resolutions` heading or
     `**Resolutions**` report field in either document.
   - **new** `test_argument_surface_is_the_declared_set` — the eight argument
     names, and the four closed value sets. Read each name as the backticked
     head truncated at `=`; `depth`, `sensitivity`, and `format` carry their
     values in that head, the rest in the bullet body.
3. **Run the focused suite** after each group of methods:
   `.venv/bin/python -m unittest discover -s tests -p test_skills.py -k CoherenceAudit`
4. **Run the deletion probes** (step 3 of the design's validation) and record
   each result.
5. **Run both rewording probes** — one structural-carrier sentence, one
   prose-only safety sentence reworded within its token — and record each
   reworded sentence verbatim. Both expected green.
6. **Write the research notes** at
   `research/rewording-proof-2026-08-29.md` (`mkdir -p` the directory; the task
   has none yet), holding both worked rewordings, the four deletion probes with
   their observed output line, the stated bound of the redaction assertion, and
   the structural-carrier bound on the rewording criterion.
7. **`make check`**, then commit.

## Validation Plan

Focused, during the rewrite:

```bash
.venv/bin/python -m unittest discover -s tests -p test_skills.py \
  -k CoherenceAudit -k MarkdownContractHelper
```

The helper class is part of the focused lane, not an afterthought: the contract
assertions are only as good as the parse under them, so a run that exercises the
assertions without the parsers validates half the change.

Deletion probe, once per target (expect `FAILED` then `OK`):

```bash
FILE=<the file the probe edits>
TMP="$(mktemp)"
cp "$FILE" "$TMP"
# apply the deletion to "$FILE"
.venv/bin/python -m unittest discover -s tests -p test_skills.py -k CoherenceAudit   # expect FAILED
cp "$TMP" "$FILE" && rm -f "$TMP"
.venv/bin/python -m unittest discover -s tests -p test_skills.py -k CoherenceAudit   # expect OK
```

Note the inversion against
`.trellis/spec/backend/quality-guidelines.md:152-161`: that block restores the
*source* to `HEAD` to prove a new pin fails without the edit. Here the source is
already correct and the test is what changed, so the probe removes a contract
from the source instead. Same proof, opposite direction; the research notes say
so explicitly.

Broad gate, before the commit and again before the push:

```bash
make check
```

Per `.trellis/spec/backend/quality-guidelines.md`, `make check` runs before the
commit and again before the push — three commits on the `se-coherence-audit`
branch were pushed red for skipping exactly this.

## Documentation And Spec Updates

- The prose-contract section already states the rule this task applies, so
  nothing in it becomes wrong. It did gain the convention the probes earned:
  "assert the set, not a member", the parser-must-raise rule, and the probe
  inversion this task used, added under
  `### Prose contracts: prove the pin can fail` during the update-spec step.
  Both of the review findings against that paragraph — that `assertEqual`
  already catches an empty parse — are folded into its final wording.
- No release payload files change, so no version bump and no `make generate`.
  `make check`'s `release-check` lane confirms this rather than assuming it.

## Review Notes

- The set assertions are deliberately strict: adding an argument, a ledger
  field, or a detector class fails the suite until the test is updated. That is
  the contract being guarded, and the failure message names the unexpected
  member.
- The redaction assertion proves both files carry the carve-out's three parts.
  It does not prove no other sentence contradicts them — stated as a bound in
  the research notes rather than left implied.
- Every surviving prose token was chosen to be the shortest that dies with its
  contract. Per the spec's rule, `grep` each new token against the unedited file
  first; a token that is already present elsewhere in the target section is the
  wrong token.
- The diff is one test class plus five helpers. If it grows past that, scope
  has slipped.
- Converting a prose pin drops any second contract its sentence carried. Two
  were lost this way and restored in review round 2 — `classes=`'s default and
  `input=`'s accepted forms. Before replacing a pin, list what it asserts.

## Rollback Points

1. After step 1 (helpers only) — additive, suite green, safe to stop.
2. After step 2 — the class is rewritten and green, before any probe edits.
3. Each probe restores its file from a `mktemp` copy immediately; a probe that
   is interrupted leaves a dirty tree, so `git status` before the commit is part
   of step 7, and `git checkout -- <file>` is the recovery.

## Follow-Ups

- Out of repository scope, already recorded in `prd.md`: the `sd-review` remote
  dispatch forwards the local attempt number as the remote attempt, so an
  attempt above 1 with no prior remote attempt fails the action's
  `request.rerequestOf` precondition and then reports `pending` forever. Filed
  upstream during PR #278's session; the coordinator lives in
  `platypeeps/sd-ai-command-pack`.
- Other skill test classes in `tests/test_skills.py` likely carry the same
  prose-pin shape. Not in this PR — a separate audit task if the pattern proves
  out here.
