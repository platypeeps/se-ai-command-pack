# Design — skill_review internals: one containment predicate, one frontmatter grammar

Covers both PRD requirements. They are unrelated in mechanism and land in the
same file, so they share a branch, a version bump, and a changelog bullet, but
they are designed and validated independently.

## Scope

In scope: `templates/skills/se-review-skills/scripts/skill_review.py` (shipped
payload), one added description guard in `validate_skill`
(`.github/scripts/generate-skill-surfaces.py`, repo-own — see D2's reciprocal
obligation), a new conformance test, `manifest.json` version, `CHANGELOG.md`.

Out of scope: the generator's *parser*, which stays authoritative and unchanged;
the agent frontmatter dialect and the `.gemini/`, `.opencode/`,
`.trellis/agents/`, and `.github/agents/` surfaces — `_frontmatter` cannot reach
any of them, since `_safe_pack_skill_source:614` refuses a basename other than
`SKILL.md`; and any change to what `skill_review.py` reports for a document it
accepts.

---

## D1 — Collapse the two containment predicates

### Observed state

Two helpers with byte-identical bodies and different parameter names:

| Helper | Line | Signature | Call sites |
| --- | --- | --- | --- |
| `_is_relative_to` | 216 | `(path, parent)` | 568, 592, 612, 734, 830, 1251, 1408 |
| `_is_within` | 1648 | `(path, root)` | 1793, 1807, 1810 |

Both are `try: path.relative_to(x) / except ValueError: return False / return True`.
There is no semantic difference to preserve: `relative_to` treats `path == x` as
relative in both, and the one call site that needs strict containment already
spells that out separately — `if candidate == root or not _is_within(candidate, root)`
at 1793.

### Decision

Keep `_is_relative_to`, delete `_is_within`, rewrite its three call sites. Two
reasons for that direction over the reverse: it matches the stdlib spelling
(`Path.is_relative_to`, unavailable on the 3.10 floor, which is why the helper
exists at all), and it has more than twice the call sites, so the diff is
smaller and the surviving name is the one reviewers already know.

### Rejected alternative — one predicate with a `strict=` flag

Folding the `candidate == root` guard into the predicate would change the
verdict at seven call sites that currently permit the root itself, to fix one
that does not want it. A boundary check should stay dumb; the one caller that
wants strictness keeps stating it inline.

### Blast radius

`_is_within` is module-private, is not referenced by `tests/test_skill_review.py`
(grep for the name returns no test hits), and `skill_review.py` has exactly one
tracked copy — the shipped payload — since the `scripts/` wrapper was deleted in
`07-25-audit-repo-tooling-ownership`. The rename is therefore contained to one
file, and the check that proves it is a repo-wide grep for the dead name.

---

## D2 — One authoritative frontmatter grammar

### The two grammars today

- **Generator** (`.github/scripts/generate-skill-surfaces.py:236`) parses with
  `yaml.safe_load` and emits with
  `yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=10000)`.
  That `width=10000` is already an undocumented concession to the shipped
  parser, and the concession is load-bearing. Measured on
  `templates/skills/se-action-inbox/SKILL.md`: re-dumping its real frontmatter at
  `width=40` folds the description across three continuation lines, and the
  shipped parser returns **37 characters where YAML returns 151** — no error, no
  signal, a silently truncated field. The coupling exists; it is just not
  written down and nothing tests it.
- **Shipped** (`skill_review.py:515`) is a hand-rolled line parser. It cannot
  use PyYAML: bundled scripts are stdlib-first
  (`.trellis/spec/backend/directory-structure.md:26-28`), and the pack installs
  into checkouts with no guaranteed third-party dependencies.

### Decision

The generator's grammar is authoritative. `_frontmatter` becomes a **strict
rejecting subset** of it, defined by a conformance relation that a test can
check mechanically:

> For every document `_frontmatter` accepts, its `values` mapping equals
> `yaml.safe_load(raw)` with each scalar normalized through `scalar_text` (D3).
> For every document where that would not hold, `_frontmatter` raises
> `ReviewError`.

The parser never becomes a second opinion about YAML. It either agrees with
PyYAML or it refuses to answer.

### Rejected alternative — make the shipped parser more capable

Teaching it flow sequences, nested mappings, and block scalars is a
vendored-YAML project with no consumer: the scan in D3 shows no document in
`_frontmatter`'s reachable scope uses any of them. More surface, same verdicts,
new bug class.

### Rejected alternative — return `dict[str, object]` and match PyYAML exactly

Truer to YAML, but it widens a type used across `skill_review.py` and changes
every consumer's contract (`metadata.get("name") or ...` would start yielding
`True`), for a payload the generator only ever emits booleans into. The
`scalar_text` normalization gets the same conformance guarantee for a
one-function diff, and preserves today's observed output (`true` and `""`,
verified in D3).

---

## D3 — The accepted subset and the rejection set

### Evidence: what the reachable corpus actually contains

`_frontmatter` is reached from `_skill_name` (1059), `_frontmatter_keys_for_sources`
(1316), `_target_matrix` (1362), and `_inventory_record` (1384). Every one of
those paths reaches a file only through discovery or through
`_safe_pack_skill_source`, which refuses anything whose basename is not
`SKILL.md` (`:614`). **The repository corpus is therefore exactly the tracked
`SKILL.md` files — not every manifest `.md` source.** The 122 manifest `.md`
sources contribute nothing beyond them (0 tracked-set additions), and the
non-`SKILL.md` ones among them, including the four `generated/agents/` overlays,
are unreachable by construction.

"Repository corpus" is the precise phrase, and an earlier draft wrongly wrote
"reachable corpus". `_discover_installed` globs `*/SKILL.md` under operator-
supplied runtime roots (`:1029`), `build_inventory` folds those in (`:1588`), and
`_inventory_record` parses whatever comes back (`:1382`) — `tests/test_skill_review.py:1116`
already proves an unowned installed file becomes the canonical path. Those files
exist in no repository and no enumeration can reach them, which is why D5 adds an
installed-root fixture rather than pretending the tracked set is the whole story.

Scanning the repository set with PyYAML:

```
tracked SKILL.md: 180, all carrying frontmatter
non-string values: 14 booleans (generator-emitted disable-model-invocation / user-invocable)
double-quoted values: 29
single-quoted values: 0
backslash anywhere in a frontmatter block: 0
block scalars / flow collections / nested mappings / multi-line values / '#': 0
```

That distinction is load-bearing for D5: agent frontmatter legitimately carries a
list-valued `tools` (`generate-skill-surfaces.py:702`), so binding the agent
dialect to this parser's subset would fail a conformance test on a change that
is correct.

**The divergences below are latent, not live.** Running the conformance relation
against the *current* parser over all 180 documents gives `mismatches: 0`. This
change is preventive: it closes constructs that would silently corrupt if a
future skill, a future generator setting, or a third-party installed skill used
them. The PR must say that rather than imply a live bug was fixed.

That zero-cost property is also what makes "reject" affordable.

### Verified divergences to close

Each row was reproduced against the live parser before being written down:

| Construct | `yaml.safe_load` | `_frontmatter` today | Disposition |
| --- | --- | --- | --- |
| `description: 'a: b''s'` | `"a: b's"` | `'a: bs'` | **Fix** — `ast.literal_eval` applies Python rules; `''` is adjacent-literal concatenation, not a YAML escaped apostrophe |
| `name: se-help # trailing` | `'se-help'` | `'se-help # trailing'` | **Reject** — a polluted `name` becomes a deduplication key and a reported skill identity |
| `tools: [Read, Edit]` | `['Read','Edit']` | `'[Read, Edit]'` | **Reject** |
| `meta:` + indented `inner: 1` | `{'inner': 1}` | `''` | **Reject** |
| `description: \|` + two lines | `'line1\nline2\n'` | `'line1 line2'` | **Reject** |
| `flag: yes` / `on` / `True` | `True` | `'yes'` / `'on'` / `'True'` | **Reject** — YAML 1.1 resolves all of these to a boolean |
| `x: null` / `~` / `Null` | `None` | `'null'` / `'~'` / `'Null'` | **Reject** |
| `n: 010` / `0x1f` / `1.0` / `.inf` | `8` / `31` / `1.0` / `inf` | source text | **Reject** — numeric resolution |
| `d: 2026-08-10` | `datetime.date(...)` | `'2026-08-10'` | **Reject** |
| `disable-model-invocation: true` / `false` | `True` / `False` | `'true'` / `'false'` | **Accept** via `scalar_text` |
| `model:` (empty) | `None` | `''` | **Accept** via `scalar_text` |
| `description: "a\tb"` | `'a\tb'` | `'a\tb'` | Already agrees; still **rejected** (see below) |

`scalar_text` is total over the declared value domain: a string maps to itself,
`True`/`False` to `true`/`false`, `None` to `""`. Nothing else is in the domain,
because every other resolved type is rejected above. That is what keeps the
relation a real guarantee instead of a normalization that papers over a type
change.

### Accepted grammar

1. `---\n` opener, `\n---\n` closer — unchanged.
2. One flat mapping. Each entry is `key:` followed by a space or the end of the
   line. `key:value` with no space is **not** an entry — YAML reads the whole
   line as a plain scalar and the document stops being a mapping at all, which
   is the authority's `frontmatter must be a YAML mapping` error.
3. The key is non-empty after stripping and does not repeat an earlier key. It is
   rejected when its **first character** is a YAML indicator, when it is exactly
   `<<`, or when YAML would resolve it to something other than a string
   (`true:`, `010:`, `2026-08-10:` all produce non-string keys).

   **The check is on the opening character only.** An earlier draft said "carries
   no YAML indicator character", which reads as a substring test and would reject
   `disable-model-invocation` — 14 live generated files. Internal `-` and `#` are
   ordinary; `a#b: v` is a valid mapping to PyYAML and stays valid here.

   `<<` needs its own rule because it is not an indicator and not a
   mis-resolution: PyYAML tags it as a merge key and raises `ConstructorError`
   during construction. A parser without a resolver cannot infer that.
4. `value` is one of:
   - **empty** — yields `""`, matching YAML null;
   - a **plain scalar** that is `true` or `false` (yielding `"true"`/`"false"`),
     or that YAML would resolve to a string, and that opens with none of YAML's
     indicator characters and contains no `:` at all;
   - a **single-quoted scalar**, unquoted by replacing `''` with `'` — the whole
     of YAML's single-quote escaping;
   - a **double-quoted scalar containing no backslash**, unquoted by stripping
     the delimiters, which is exactly YAML's result when no escape is present.
5. A blank line is ignored.
6. Surrounding whitespace is trimmed with **ASCII space only** — `strip(" ")`,
   never bare `strip()`. Python treats U+00A0 as whitespace and YAML does not, so
   `description: <NBSP>text` loses a character YAML keeps. The current parser has
   this bug; it is silent, and no corpus document triggers it.

### Rejected constructs, each raising `ReviewError`

- a line inside the block starting with whitespace — nested mapping, sequence
  item, wrapped continuation, or block-scalar content;
- an unquoted value whose **first character** is any YAML indicator — one of
  `-?:,[]{}#&*!|>%@` or a backtick. Testing the first character rather than a
  two-character form like `- ` is deliberate: `k: -` and `k: ?` alone are
  `ScannerError`s too. An earlier draft listed only `|>[{&*!`, and every omission
  is a measured divergence — `- value`, `? value`, `@value`, `%value`, `,value`,
  and a backtick each make PyYAML raise while the line parser returns a string;
- a quoted value that is unterminated or carries trailing content after its
  closing quote;
- a **backslash inside a double-quoted value** (see below);
- an unquoted value containing ` #`;
- an unquoted value containing **any** `:` — not just `: `. YAML raises a
  `ScannerError` for both `value: more` and a trailing `value:`, so accepting
  either would make the subset *wider* than the authority, not narrower;
- a `key:value` line with no space after the mapping colon — see grammar rule 2;
- an unquoted value **or key** that YAML would resolve to something other than a
  string: any spelling of boolean or null except `true`, `false`, and empty;
  anything numeric-looking; anything date-looking. Applying the guard only to
  values was the round-2 gap — `true: v`, `010: v`, and `2026-08-10: v` produce
  `True`, `8`, and a `date` as *keys*;
- an empty key, a quoted key, a key **opening** with a YAML indicator (`&anchor`,
  `!tag`, `*alias`, `? explicit`, `- name`), or the merge key `<<`. `- name` is a
  top-level sequence, which the authority rejects as "frontmatter must be a YAML
  mapping" while the line parser would happily return `{"- name": ...}`;
- **any Unicode category `Cc` control character other than the line break**,
  anywhere inside the block. This subsumes the tab case (`name \t: x` is a
  `ScannerError` the line parser would silently strip away) and closes NUL and
  friends, which make PyYAML's reader raise `special characters are not allowed`
  while a line parser sails through;
- a duplicate key;
- a non-blank line with no `:`.

The current parser silently `continue`s on the whitespace and missing-colon
cases. That silence is what let the wrapped-`description` hazard sit behind
`width=10000` undocumented.

Measured cost of the round-2 additions across the 180-file repository corpus:
unquoted values containing any `:` — **0**; `key:value` lines with no space after
the colon — **0**; keys resolving to a non-string — **0**.

### The grammar was proven a subset before it was implemented

This specification was prototyped and fuzzed against PyYAML rather than reasoned
about: the Cartesian product of 13 key shapes and 39 value shapes, 468 documents,
plus a sweep of every `Cc` control character and the Unicode separators.

```
cases=468 accepted=72 rejected=396
DIVERGENCES=0
CONTROL-CHAR DIVERGENCES=0
```

Neither run was clean on the first attempt, and every failure became a rule
above: the NBSP stripping bug (rule 6), the control-character hole, and the
merge-key case. None was reachable by reading the code — the strip bug in
particular is inherited from the current parser and invisible until something
compares against PyYAML character by character. The widened corpus is what
proved `disable-model-invocation` and `a#b` stay accepted while `<<`, `k: -`, and
`k: ?` are refused. D5 group 6 keeps the fuzz so the property survives
implementation.

### Why reject backslashes instead of implementing YAML's escapes

YAML's double-quoted escape set is not Python's: `\/`, `\e`, `\N`, `\_`, `\L`,
and `\P` are valid in YAML and wrong or invalid in Python, and Python passes
unknown escapes through where YAML errors. Hand-rolling that table in a shipped
stdlib-only script is a new bug class with no consumer — **no frontmatter block
in the reachable corpus contains a backslash at all**. Refusing the construct is
smaller, provably conformant, and costs nothing today. Double-quoted values
without a backslash stay accepted, which matters: 29 of them are live.

### The tool's own self-description must move with the grammar

`skill_review.py:1635` publishes, in every inventory payload's
`coverage.limits`, the sentence *"Metadata parsing is intentionally limited to
top-level scalar fields."* That is the caveat the tool gives operators about
this exact parser. After the change the statement is incomplete in the direction
that matters: parsing is not merely limited, it now refuses what it cannot
represent. The string is updated with the rest.

It is safe to change: it appears nowhere else in the repository, and
`tests/test_skill_review.py:429` pins only a fixture value (`"fixture limit"`),
not this text. It is still payload — a `limits` entry feeds the
`snapshotId` hash — so it belongs in the same commit as the parser, not in a
follow-up.

### Rejected constructs that are not real

An earlier draft also rejected "a second `---` document boundary inside the
block". It is unreachable: `text.find("\n---\n", 4)` makes the first such line
the closer by construction, so nothing inside the block can be one.

### Reciprocal obligation on the generator

The authoritative side must not emit outside the subset. Today's guards get
close but **do not** get there, and an earlier draft of this design wrongly
claimed they did.

`width=10000` prevents wrapping, and `validate_skill`
(`generate-skill-surfaces.py:277-292`) refuses a canonical `description` that is
empty, contains a double quote, spans more than one LF-separated line, or
exceeds the length cap. It permits tabs, CR, NEL (U+0085), and U+2028/U+2029.
`safe_dump` then produces, measured:

| Description contains | Emitted as | Under the subset |
| --- | --- | --- |
| tab | `description: "Use when alpha\tomega"` | **rejected** — backslash in a double-quoted value |
| CR | `description: "alpha\romega"` | **rejected** — same |
| NEL / U+2028 | single-quoted with a real line break, folded onto a continuation line | **rejected** — indented line |
| NBSP | plain `description: alpha\xa0omega` | accepted |

So a canonical description containing a tab passes `make generate` and produces
an overlay the review tool then refuses to read. That is not a subset violation
the shipped parser should absorb — it is a hole in the authority's own
validation.

**Decision: close it on the authoritative side.** `validate_skill` gains a guard
refusing control characters and Unicode line/paragraph separators in a
description, alongside the double-quote and single-line guards it already has.
The generator is repo-own tooling, so this adds no payload surface; it makes the
reciprocal obligation enforced rather than accidental, which is exactly the
"generator-side counterpart" the PRD anticipated. Measured cost: **0 of 180**
tracked `SKILL.md` files carry a control character, separator, or non-ASCII
space in any frontmatter value, so no existing skill needs an edit.

`validate_agent` deliberately does not get the same guard. Agent frontmatter is
never read by `_frontmatter` (`_safe_pack_skill_source:614`), so no subset
obligation reaches it, and adding a constraint there would restrict a dialect
this task has no contract with.

The `: `-in-an-unquoted-value rejection deserves the same check, since prose
descriptions use colons constantly: **0 of 180** unquoted values contain one.
They cannot — YAML raises a `ScannerError` there, which is why the 29
double-quoted values exist in the first place.

D5 group 4 then tests the *property* rather than today's snapshot: for each
hostile-but-currently-legal description, either the generator refuses it or the
shipped parser accepts its overlay and agrees. Rendering only the overlays that
exist today would have missed this entirely.

---

## D4 — Error surface

Reuse `ReviewError`, matching the existing style at 517 and 520, with the
document label, the 1-based line number within the frontmatter block, and the
construct name:

```
templates/skills/se-foo/SKILL.md:3: unsupported frontmatter construct: flow sequence
```

Fatal, not a recorded finding. Two reasons: `_frontmatter`'s existing failures
(`missing frontmatter opening`) are already fatal, and no *intermediate* call
site catches `ReviewError` — the only handlers are the `raise` re-raise at
`:1739`/`:1852` and `main` at `:2000`/`:2028`, which turns it into a message and
exit code 2, so the operator gets a controlled failure rather than a traceback
or a partial verdict. A non-fatal path would be new machinery. Second, a
partially-parsed frontmatter feeds a deduplication key and a skill identity,
where a wrong answer is worse than no answer. This is the same judgment the
`07-25-audit-repo-tooling-ownership` post-mortem reached: a degraded verdict is
a regression wearing a fix's clothing.

Cost, stated plainly: an installed third-party `SKILL.md` using richer YAML now
aborts a scan that previously produced a wrong row for it. The message names the
file and line so the operator can narrow scope.

---

## D5 — The shared conformance test

New `tests/test_frontmatter_conformance.py`. Dev-only `import yaml` is
legitimate here — PyYAML is in `requirements-dev.lock` and the generator already
imports it; the point of the test is precisely to bind the shipped parser to the
reference implementation it may not ship.

Six groups. The split matters because the first group **passes today** — the
corpus exercises none of the divergences — so it proves absence of regression,
not presence of the fix. Groups 2, 3, 5, and 6 bite on the parser rewrite.

1. **Corpus regression guard.** Enumerate `**/SKILL.md` from `git ls-files -z` —
   never a hand-written list, and **never the wider manifest `.md` set**, which
   includes agent overlays this parser cannot reach and whose list-valued `tools`
   the subset rightly forbids. For every document assert `_frontmatter(...)[0] ==
   {k: scalar_text(v) for k, v in yaml.safe_load(raw).items()}` and that the key
   tuple equals the YAML key order. This enumerating shape is the convention
   `07-25-audit-test-hermeticity` extracted from the PR #206 incident: derive
   from the tracked tree so the test runs identically on a fresh clone. Guard
   against vacuity by asserting the enumeration is non-empty and actually covers
   the interesting shapes — at least one boolean value and at least one
   double-quoted value, both of which the corpus has today (14 and 29).
2. **Agreement table.** Synthetic documents inside the accepted subset where the
   old and new parsers differ: `'a: b''s'`, a double-quoted value containing a
   colon, an empty value, `true`/`false`. Each asserts equality with
   `yaml.safe_load` under `scalar_text`. This group fails against the current
   `ast.literal_eval` implementation, which is what makes it a bite proof.
3. **Rejection table.** One case per D3 rejection bullet, asserting `ReviewError`
   and that the message names the construct and the line.
4. **Generator reciprocity, as a property.** Three halves, and the split matters.
   (a) Render each Claude overlay through `render_claude_skill` and assert the
   shipped parser accepts it and agrees — so shrinking `width` or adding a
   list-valued overlay field fails here. Half (a) alone only ever tests today's
   snapshot, which is how the tab hole survived the first draft.
   (b) **Must reject**: a description containing any Unicode category `Cc`
   control character, U+2028, **or U+2029**, asserted against `validate_skill`.
   U+2029 is not decoration — PyYAML emits it as a real folded continuation line,
   so an implementation that guards only U+2028 would pass a one-case test and
   still generate an overlay the subset refuses.
   (c) **Must accept and round-trip**: a description containing an apostrophe, a
   colon-space, or a `#`. Without this half, an "either the validator rejects it
   or the parser agrees" assertion is satisfied by a validator that refuses
   everything — the round-2 draft had exactly that hole.
5. **Installed-root integration.** A temporary runtime root containing
   `external/SKILL.md`, passed through the installed-discovery path that
   `_discover_installed` (`:1029`) and `build_inventory` (`:1588`) actually use.
   One accepted file must produce a record; one carrying a rejected construct
   must raise with the file named. No enumeration can reach a real operator's
   installed skills, so this fixture is what covers them.
6. **Product fuzz.** Port the planning prototype's generator: over the Cartesian
   product of the key and value shapes, assert that every document
   `_frontmatter` accepts equals `yaml.safe_load` under `scalar_text`, and that
   every document it rejects would also have failed or diverged under PyYAML.
   Add the control-character and separator sweep. This is the group that found
   the NBSP and NUL holes during planning; keeping it means a later
   "simplification" of the parser cannot quietly reintroduce them.

---

## D6 — Release discipline

`skill_review.py` is an installed target, so the payload gate demands a manifest
version bump and a matching `CHANGELOG.md` heading. Per
`CONTRIBUTING.md:127-135`, "a change in what an existing surface refuses or
requires" is a **minor**: `0.68.3` → `0.69.0`, one changelog entry covering both
requirements, with the new rejections stated explicitly since they are what a
consumer can trip over.

The bullet leads with `**Breaking:**` per `CONTRIBUTING.md:137`. Input a consumer's
`SKILL.md` could previously carry is now refused, which is the definition the
document uses. The release gate checks only the heading format, so nothing
enforces this marker — it is a policy obligation the plan has to carry.

D1 alone would have been a patch. The bump follows D2.

---

## Risks and rollback

| Risk | Mitigation |
| --- | --- |
| A reachable document outside the subset breaks a real scan | The corpus scan above found none; the conformance test re-derives the corpus on every run rather than trusting this snapshot |
| Third-party installed skills with richer YAML now abort | Accepted and documented in D4 and the changelog; the error names file and line |
| `scalar_text` hides a genuine type change | Its domain is only `str`/`bool`/`None`; every other resolved YAML type is rejected outright, and D5 group 1 asserts the corpus stays inside that domain |
| The rewrite silently changes an accepted document's parse | D5 group 1 is exactly that regression test, over all 180 live documents including the 29 double-quoted values the unquoting rewrite touches |
| The corpus scan is a snapshot that ages | D5 group 1 re-derives it from `git ls-files` on every run; the numbers in this design are evidence for the decision, never an input to the test |
| Runtime-discovered installed skill roots are outside any corpus a test can enumerate | Inherent and accepted: `_walk_skill_files` reaches `SKILL.md` files that exist on an operator's machine and in no repository. The conformance test binds the grammar; D4's fatal, file-and-line-naming error is what handles the rest |

Rollback is `git revert` of one commit: no data migration, no generated-surface
change beyond the version, and no consumer contract other than the stricter
refusal.

## Evidence

- `templates/skills/se-review-skills/scripts/skill_review.py:216` `_is_relative_to`, `:1648` `_is_within`, `:515` `_frontmatter`, `:1793`/`:1807`/`:1810` the three `_is_within` call sites.
- `.github/scripts/generate-skill-surfaces.py:236` `parse_frontmatter`, `:541` the `safe_dump` call and its `width=10000`.
- `.trellis/spec/backend/directory-structure.md:26-28` — shipped scripts are stdlib-first.
- `CONTRIBUTING.md:127-135` — minor versus patch.
- Divergence table and corpus counts: reproduced against the live parser and the
  tracked tree during planning, not quoted from the audit report.
