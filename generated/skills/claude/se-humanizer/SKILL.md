---
name: se-humanizer
description: Use when text should read as if a person wrote it — the user says humanize, de-AI, naturalize, sounds robotic, or reads like AI, or prose written on the user's behalf is about to be committed or sent — removing hedging, filler, throat-clearing, formulaic transitions, and generated-text vocabulary while restoring specificity and a human cadence.
model: opus
effort: high
---

# SE Humanizer

Rewrite prose so it stops sounding generated. Strip the tells — hedging,
filler, throat-clearing, formulaic transitions, inflated vocabulary — and
put back what generated text rounds off: specific detail, varied rhythm, a
voice that belongs to someone. Meaning survives intact; only the delivery
changes.

## When to use

Use on prose the user calls AI-sounding, on findings handed over by
`se-prose-lint`, and as the final pass before committing or sending text
written on the user's behalf: docs, README sections, commit and PR text,
release notes, posts, and drafts.

Do not use for:

- the deterministic finding pass itself — that is `se-prose-lint`;
- a full correctness-and-citations editorial review — that is
  `se-technical-editor`;
- conformance to a stated house or brand voice — that is `se-brand-voice`;
- ordinary conversational replies, unless the user asks for tone or style
  work.

## Arguments

None. The text arrives as free text or a file locator; a writing sample for
voice matching may accompany it.

This skill takes no `key=value` arguments.
Unknown argument names are an error — stop and report them before starting.

## Workflow

1. Take the deterministic findings first. When `se-prose-lint` results
   accompany the request, take its disposition per finding rather than
   rewriting on the alert alone: a `fix` is a hard constraint addressed in
   the rewrite, a `suppress` is a judgement already made that the rewrite
   preserves, and a `promote` is a rule question for the repository, not a
   span to edit. Rewriting a suppressed span silently overturns the call
   that suppressed it.
   When none were provided and Vale is available, run it for the same
   constraint set. Where Vale is absent, state the gap in one plain
   sentence and continue — a missing gate never blocks the rewrite.
2. Calibrate voice before touching a sentence. With a writing sample,
   match its sentence-length mix, register, punctuation habits, and
   transition style rather than substituting a house default. Without one,
   write plainly: varied rhythm, concrete words, no manufactured
   personality — and for technical or reference prose, neutral and plain
   is the correct human voice.
3. Sweep the pattern families and mark every hit:
   - **inflated significance** — claims that something `marks a pivotal
     moment` or `reflects broader trends`; cut the ceremony, keep the fact;
   - **promotional puffery** — `vibrant`, `renowned`, `nestled`-class
     language where a plain description belongs;
   - **participle padding** — trailing `-ing` clauses (`highlighting...`,
     `showcasing...`) that fake depth; end the sentence instead;
   - **vague authority** — `experts argue`, `observers note`; name the
     source or drop the claim;
   - **copula avoidance** — `serves as`, `boasts`, `features` where `is`
     and `has` are honest;
   - **formula rhythms** — negative parallelism (`not just X, it's Y`),
     rule-of-three stacking, false `from X to Y` ranges, aphorism
     templates, staccato runs of clipped fragments for drama;
   - **synonym cycling** — the same subject renamed every sentence; repeat
     the plain word;
   - **tell vocabulary** — the post-2023 cluster (`delve`, `crucial`,
     `landscape`, `tapestry`, `testament`, `underscore`); replace with the
     word a person would use;
   - **filler and hedging** — `in order to`, `it is important to note`,
     stacked qualifiers (`could potentially possibly`); say the thing once;
   - **conversation residue** — signposting (`let's dive in`), sycophancy,
     chat closers (`I hope this helps`), knowledge-cutoff disclaimers;
   - **generic endings** — upbeat conclusions that promise a bright future
     instead of stating what happens next.
4. Judge in clusters, not isolated hits. One em dash, one short sentence,
   or one formal word proves nothing; a pile-up is the confession. Preserve
   the signals of a real writer — hard-to-fabricate specifics, mixed
   feelings, genuine asides, uneven sentence lengths — and leave clean
   human prose alone rather than sanding it featureless.
5. Rewrite the marked spans. Keep the core message, sharpen vague claims
   into specific ones only when the source material supports the
   specificity, and read the result aloud in your head for cadence.
6. Run the adversarial closing pass: ask what still reads as generated in
   the rewrite, fix exactly those remnants, and deliver the final version.
   When invoked by another skill as a chained final pass, return the
   reduced contract instead of the full report below: the revised text and
   a one-line status, nothing more.

## Safety rules

- Meaning, citations, numbers, and technical claims survive the rewrite
  unchanged. Never invent a specific detail to make prose feel human.
- Never post, send, or commit the result on the user's behalf; deliver the
  rewrite and stop.
- Where Vale is absent, degrade gracefully — report the gap and continue.
  Never fail a session over a missing deterministic gate.
- Do not over-edit. Text with isolated tells and strong human signals is
  left alone, and that restraint is reported, not hidden.
- Never score or assert whether a human or a model wrote the text; this
  skill fixes prose, it does not run authorship detection.
- Normative vocabulary is off limits: `MUST`, `SHOULD`, `MAY` and their
  negations in specs and decision records stay exactly as written.

## Final report

This is the direct-invocation report. A chained final pass returns the
reduced contract from step 6 instead, and never both.

- **Rewrite** — the revised text, or the locator of the edited file;
- **What changed** — the pattern families that fired, with a representative
  before/after pair per family rather than an exhaustive ledger;
- **Deterministic pass** — findings consumed from `se-prose-lint` or a
  direct run, or the stated Vale gap;
- **Voice calibration** — sample-matched or default, and what the sample
  dictated;
- **Left alone** — spans deliberately untouched and the human signals that
  earned the restraint; and
- **Residual risk** — anything that may still read as generated and why it
  was kept.
