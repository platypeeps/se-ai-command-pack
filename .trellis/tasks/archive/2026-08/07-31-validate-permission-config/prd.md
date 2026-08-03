# Validate permission config files across every settings tier

## Goal

A permission-config defect is found by a check rather than by an unattended routine
stalling on a prompt nobody is there to answer. Walk every settings file a routine's
grants can live in and report four structural defects — defects about the *files*, not
about which grants ought to be in them.

## Requirements

- Walk every settings file a routine's grants can live in: `.claude/settings.json` and
  `.claude/settings.local.json` in each project, plus the two under `~/.claude/`.
- Report defect 1, **does not parse**: the file and the decoder's own error line. A file
  that fails here contributes *zero* rules, so every downstream rule review is
  meaningless until it is fixed.
- Report defect 2, **orphaned mirror**: a backup or mirror whose live target no longer
  exists, so it records grants that are active nowhere.
- Report defect 3, **empty rule set in a file a routine depends on** — reported separately
  from "does not parse", because the two have different causes and the same symptom.
- Report defect 4, **a routine whose invocation form cannot match any rule present**,
  reusing the existing `audit-approval-rules` comparison rather than re-implementing it.
- Judging *which* grants ought to be present is deliberately out of scope.

## Acceptance Criteria

- [ ] Every settings tier listed above is walked, and the set walked is reported (a tier
      that does not exist is named as absent, never omitted silently).
- [ ] A file that fails `json.load` is reported with the decoder's error line.
- [ ] A mirror whose live target is missing is reported as orphaned.
- [ ] A file that parses to zero rules is reported under its own defect class, distinct
      from a parse failure.
- [ ] An invocation form that matches no rule present is reported, via the existing
      `audit-approval-rules` comparison.
- [ ] A clean result prints the count of files checked, so zero defects is
      distinguishable from zero files walked.

## Notes

Filed by `llm-wiki-accept` from `SKILL-PROPOSALS.md` in `sdelmas-llm-wiki`, accepted
2026-07-31 by Sven.

**Evidence.** Four instances across two harvest batches. This batch: a missing comma from
concurrent edits disabling every rule in `.claude/settings.json`, and
`~/.claude/settings.local.json` deleted while a maintained mirror still described its
grants (*ORPHANED BACKUP*) with `~/.claude/settings.json` carrying zero rules — a routine
due to run the next morning had no grants at all. The 2026-07-28 batch: `Write(path)`
rules accepted by the loader and never consulted, and one-shot literal rules that can
never match twice. Different defects, one file, none visible from reading the rules.

**Why a skill and not a note.** All four are mechanical: `json.load`, an
`os.path.exists`, a length check, a string comparison. None requires judgement, and the
judgement that *does* exist — which grants ought to be there — is deliberately out of
scope. A note would have to be read by someone who already suspects the file, which is
exactly the person who does not exist at 21:30.

**Cost of getting it wrong.** Cheap over-reporting: a false "this mirror is orphaned"
costs one `ls`. Expensive under-reporting, and silently so — an unattended routine with no
usable grants does not error, it stalls on a prompt nobody answers, and the run looks
identical to a night with nothing to do. That is the failure this vault has now recorded
four separate times.
