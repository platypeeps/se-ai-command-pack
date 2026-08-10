# skill_review internals cleanup

## Goal

The shipped skill_review.py has one path-containment predicate and one authoritative frontmatter grammar, so its boundary checks stay auditable and its metadata classification cannot diverge from what the generator validated.

## Requirements

- Collapse _is_relative_to (:216) and _is_within (:1648) into one helper used at every call site. [A-009]
- Declare the generator's YAML grammar authoritative; make the shipped dependency-free parser a strict subset that rejects (rather than reinterprets) constructs outside it. [A-010]
- Add a shared conformance test asserting both parsers agree over all canonical and generated SKILL.md frontmatter in the repo.
- Payload change: version bump + changelog per release discipline.

## Acceptance Criteria

- [x] One containment helper remains, all call sites migrated.
      `_is_within` is deleted and its three call sites route through
      `_is_relative_to`; `grep -rn "_is_within"` returns only `.trellis/tasks/**`
      prose and unrelated vendored `scripts/` files.
- [x] Conformance test passes over every SKILL.md in templates/ and generated/;
      out-of-subset construct is rejected with a clear error.
      `tests/test_frontmatter_conformance.py`: `Ran 14 tests ... OK`, covering
      180 enumerated documents and the 468-case fuzz. All six probes produced
      their predicted failure and were reverted — A (group 2 fails, group 1
      stays green), B (`indented line`), C (`value opening with a YAML
      indicator`), D (5 failures with the guard removed, exactly 1 with only
      U+2029 omitted), E (`case='apostrophe'`), F (`{'name': 'nbsp'} !=
      {'name': '\xa0nbsp'}`).

## Planning adversarial review ledger

Trigger: `design.md` and `implement.md` created new in this run; `prd.md`
materially updated. Three rounds, host lane plus the native Codex lane, per
`.claude/sd-ai-command-pack/planning-adversarial-review.md`.

| ID | Lane | Concern | Blocks? | Disposition |
| --- | --- | --- | --- | --- |
| C-1 | host | Design implied a live bug; the relation already holds over the whole corpus | yes | **addressed** — design states the change is preventive; `mismatches: 0` measured |
| C-2 | host | Probe A claimed the corpus group bites on the `ast.literal_eval` fix; it cannot | yes | **addressed** — test split; bite proof moved to a synthetic agreement table |
| C-3 | host | Design claimed 13 single-quoted documents | no | **addressed** — actual: 0 single-quoted, 29 double-quoted |
| C-4 | host | Hand-rolling YAML's double-quote escape table is a new bug class | yes | **addressed** — reject backslash in a double-quoted value; 0 backslashes exist corpus-wide |
| C-5 | host | `scalar_text`'s `str()` fallback hid type divergence (`yes`, `010`, `2026-08-10`) | yes | **addressed** — domain narrowed to `str`/`bool`/`None`; all other resolutions rejected |
| C-6 | host | Quoted keys, unterminated quotes, trailing content after a closing quote unhandled | yes | **addressed** — added to the rejection set |
| C-7 | host | "Reject a second `---` inside the block" | no | **rebutted** — unreachable; `find("\n---\n", 4)` makes the first one the closer. Removed |
| C-8 | host | PRD evidence line numbers all stale | no | **addressed** — re-anchored by symbol, drift recorded |
| C-9 | codex | Generator can emit a tab/CR/NEL/U+2028 the subset rejects — `validate_skill` permits them | yes | **addressed** — control-character guard added to the authority; group 4 became a property test |
| C-10 | codex | Key-side holes: `&k name:`, `- name:`, `name: a: b`, tab before `:` | yes | **addressed** — added to the rejection set |
| C-11 | codex | Conformance corpus crossed scope; agent overlays are unreachable and legitimately use `tools: [Read]` | yes | **addressed** — group 1 narrowed to tracked `**/SKILL.md` |
| C-12 | codex | Every validation command used bare `python3`, which has no PyYAML here | yes | **addressed** — all commands routed through the toolchain wrapper |
| C-13 | codex | Changelog needs a leading `**Breaking:**`; the release gate cannot catch its absence | no | **addressed** — obligation written into Step 4 |
| C-14 | codex | D4 said "no call site catches `ReviewError`"; `main` catches it and exits 2 | no | **addressed** — wording corrected |
| C-15 | codex | Rejection set still insufficient: `name:value`, trailing `:`, openers `- ? @ % ,` and backtick, and non-string **keys** | yes | **addressed** — 11 divergences reproduced, all closed; corpus cost measured at 0 |
| C-16 | codex | "Reachable corpus is exactly tracked `SKILL.md`" is false — `_discover_installed` globs runtime roots | yes | **addressed** — reworded to "repository corpus"; installed-root fixture added as group 5 |
| C-17 | codex | Group 4b covered only U+2028, and its "reject **or** agree" shape is satisfied by an overbroad validator | yes | **addressed** — split into must-reject (incl. U+2029) and must-accept halves, probes D and E |
| C-18 | host fuzz | Bare `strip()` eats U+00A0, which YAML keeps — a live bug in the current parser | yes | **addressed** — grammar rule 6 mandates `strip(" ")`; probe F |
| C-19 | host fuzz | `Cc` control characters (NUL) pass the line parser while PyYAML's reader refuses the document | yes | **addressed** — control-character rejection subsuming the tab rule |
| C-20 | codex | "Key carries no YAML indicator" reads as a substring test and would reject `disable-model-invocation` — 14 live files | yes | **addressed** — prose defect, not a grammar defect; the rule is on the opening character, verified by widening the fuzz |
| C-21 | codex | `<<` is a merge key: PyYAML raises `ConstructorError`, and no resolver-free parser can infer that | yes | **addressed** — explicit `<<` rejection |
| C-22 | codex | Rejection list wrote `- ` and `? `; bare `k: -` and `k: ?` are also `ScannerError`s | no | **addressed** — prose corrected to first-character testing, which the prototype already did |
| C-23 | codex | Probe E ("reject every non-ASCII") cannot fail group 4c — `'`, `:`, `#` are code points 39, 58, 35 | no | **addressed** — probe E now widens the guard to the apostrophe; probe D isolates U+2029 |
| C-24 | codex | Design said only groups 2 and 3 bite; group 5's rejected installed file bites too | no | **addressed** |

Method note: rounds 2 and 3 of the host lane prototyped the specification and
fuzzed it against PyYAML rather than re-reading it — the Cartesian product of 13
key shapes and 39 value shapes plus a control-character sweep. Neither run was
clean first time; C-18, C-19, and the verification of C-20/C-21/C-22 all came
from it. Final: `cases=468 accepted=72 rejected=396`, `DIVERGENCES=0`,
`CONTROL-CHAR DIVERGENCES=0`.

Three automatic rounds were used, the contract's limit. No concern is parked or
unresolved.

**Convergence note.** The contract's stop-and-ask trigger — a substantive concern
persisting after the permitted rounds, or the two lanes in material conflict — is
not met: every concern is dispositioned, and the lanes agreed on every finding
either lane raised. Round 3's remediation was not re-reviewed by a fourth
adversarial round, which the contract forbids. It was instead verified
empirically: the widened fuzz is what proved `disable-model-invocation` and
`a#b` stay accepted while `<<`, `k: -`, and `k: ?` are refused. That is a
stronger check than a fourth opinion, and it is the check the implementation
inherits as conformance group 6. Implementation is unblocked.

## Notes

- Audit findings: A-009 (P3/S), A-010 (P3/M) — .trellis/audit/report-2026-07-25.md.
- Evidence, anchored by symbol because the line numbers drifted between the
  2026-07-25 audit and planning (the original citation read `:211, :1545, :509,
  :1690, :412, :1532` and `generate-skill-surfaces.py:161`, none of which still
  point at the cited construct):
  - `templates/skills/se-review-skills/scripts/skill_review.py` — `_is_relative_to` (:216),
    `_is_within` (:1648) and its call sites (:1793, :1807, :1810), `_frontmatter` (:515),
    the `coverage.limits` caveat about metadata parsing (:1635).
  - `.github/scripts/generate-skill-surfaces.py` — `parse_frontmatter` (:236),
    the `yaml.safe_dump` emitter and its `width=10000` (:541), `validate_skill`'s
    description guards (:277-292).
- Planning depth: **Complex — needs `design.md` and `implement.md` before `task.py start`.** Unifying two path-containment predicates into one touches a security boundary in shipped payload, and collapsing two frontmatter grammars into one authoritative grammar is a contract change with a generator-side counterpart. Both need their contracts written down before any edit.
