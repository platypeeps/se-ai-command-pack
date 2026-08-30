# Design: Vale prose gate

## D1. Layout

- `.vale.ini` at repo root; committed styles under `.vale/styles/` (kept
  dotted and out of `templates/` so the generator and installer never treat
  them as product surfaces).
- `StylesPath = .vale/styles`; one custom style package `se`.
- Scope via `.vale.ini` glob sections: `templates/skills/**/*.md` and root
  `*.md` (README, CONTRIBUTING, top-level docs). Everything else —
  `.claude/`, `.opencode/`, `.gemini/`, `.codex/`, `.trellis/`, generated
  trees, `docs/` subtrees that vendor external text — excluded by not being
  matched.

## D2. Initial `se` style inventory (modest, tunable)

- `se/AiTells.yml` — substitution/existence rules for ai-tell vocabulary
  (delve, crucial, leverage-class fillers, "it's important to note").
- `se/Weasel.yml` — hedging and weasel words (very, quite, simply, just...)
  at `suggestion` level initially.
- `se/Contractions.yml` or tone rules only if the tuning pass shows the
  corpus needs them — do not pre-author rules with zero corpus hits.
- RFC-2119 carve-out: rules never flag MUST/SHOULD/MAY tokens; where a rule
  would (capitalization checks), scope the regex to exclude them. In-file
  suppression comments require written justification at the suppression site.

## D3. Severity and promotion ladder

1. Land config + styles; `make prose-lint` target runs
   `vale --config .vale.ini <scoped paths>`; documented as advisory.
2. Tuning pass over the current corpus: fix or suppress every finding;
   record the count at promotion time in the task.
3. Promote: add `prose-lint` to `make check` and the CI workflow. Error-level
   rules gate; suggestion-level stay visible but non-fatal
   (`--minAlertLevel=error` in the gating invocation).

## D4. CI availability

CI installs Vale explicitly (pinned version, same major as local 3.18);
`make prose-lint` fails fast with "vale not installed; see docs" when the
binary is absent rather than silently passing. The fleet-side `se-prose-lint`
skill (sibling task) treats absence as graceful degradation — the hard
requirement lives only in this repo's CI.

## D5. Falsification check

Seed a scratch file with a known ai-tell sentence; `make prose-lint` must
exit nonzero on it and zero after removal (task AC2). This is the gate's own
bus test — a config that matches nothing passes forever.
