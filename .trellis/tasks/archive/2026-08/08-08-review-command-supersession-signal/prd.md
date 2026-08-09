# Superseded review commands carry no supersession signal in their peer adapters or frontmatter

## Goal

Make the sd review-command surface tell the truth about itself: if
`sd-review` has superseded `sd-review-local` and `sd-review-pr`, the
superseded commands must say so where a user chooses between them — or the
supersession claim must be withdrawn. Decide the route (upstream proposal
versus recorded acceptance) and record it.

## Disposition decision (2026-08-09)

Route chosen: **upstream proposal**, recorded in `disposition.md` in this task
directory (the single authoritative record for the disposition text, the
proposal, the filing state, and the issue URL). The "accepted as-is" route is
rejected: the catalog notice is invisible at the command-palette choice point,
and its "transitional until 0.62.0" promise expired more than thirty releases
ago (installed pack is 0.64.32), so the existing partial control cannot be
called sufficient. The Requirements below retain both routes as the original
decision frame; this section records the outcome.

## Problem

`.agents/skills/sd-review/SKILL.md:14-16` (vendored, sd-ai-command-pack;
originally verified at v0.64.3, re-verified unchanged at v0.64.32 on
2026-08-09 after the pack refresh) reads:

> This successor is self-contained. Never call, alias, or fall back to
> `sd-review-local`, `sd-review-pr`, a direct Copilot request, or a backend
> command found in configuration or a receipt.

Yet `/sd:review-local` and `/sd:review-pr` remain installed as first-class
peer commands on every surface (21/21 sd command parity across `.claude`,
`.gemini`, `.opencode`, `.github` was verified 2026-08-08), and neither their
command files nor their skill frontmatter/descriptions mention being
superseded. The gap is specifically in the peer adapters: the `sd-help`
catalog (`references/command-catalog.md:40,54`) *does* already label both
"included in installed pack — transitional until 0.62.0; use sd-review" — an
existing partial control — but that notice reaches only users who invoke
`/sd:help`. A user choosing directly from the command palette sees three
unmarked peer review commands.

Adjacent, smaller instances of the same class (document, do not necessarily
fix here), each scoped to the adapter/frontmatter surfaces — the `sd-help`
catalog covers some of them (e.g. its `sd-full-check` row says "use
sd-check"): `sd-full-check`'s own skill and adapter files never name
`sd-check` even though the catalog marks `sd-full-check` transitional in
favor of `sd-check` (succession per the catalog; no capability-subsumption
claim is made — `sd-check` itself treats `sd-full-check` as an independent
legacy surface it refuses to invoke); `sd-create-pr` is a strict prefix of
`sd-ship`; `sd-finish-work` and `sd-housekeeping` are both named as "end of
work" while one invokes the other.

## Constraint: every affected file is vendored

All sd-* skills and command adapters are installed payload from
sd-ai-command-pack, hash-tracked in `.sd-ai-command-pack/provenance.json`.
Hand-editing them locally creates exactly the fork class documented in
`08-07-review-py-local-fork`, and the route for defects in vendored artifacts
is the contract being defined by `08-07-vendored-artifact-upstream-route`.
This task therefore produces a **recorded disposition and an upstream
proposal** (route decided; see Disposition decision above) — not local edits
to vendored files.

## Requirements

- Record a disposition with reasoning, one of:
  - **Upstream (preferred).** Propose to sd-ai-command-pack that
    `sd-review-local` and `sd-review-pr` carry an explicit supersession notice
    in their descriptions/frontmatter (or be removed from the installed
    command surface), so the choice point is self-explaining on every
    platform.
  - **Accepted as-is.** Record why the existing `sd-help` catalog notice
    ("transitional until 0.62.0") is a sufficient control despite not being
    visible at the command-palette choice point.
- Whichever route is chosen, the disposition must reconcile the expired
  transition promise: the catalog says "transitional until 0.62.0" while the
  installed pack is 0.64.32 — the commands outlived their own stated removal
  horizon by more than thirty releases. Accepting the status quo without
  addressing that expiry is not a complete disposition.
- The disposition must quote the `sd-review/SKILL.md` supersession text and
  cite the surfaces where the superseded commands remain installed.
- List the adjacent choice-point ambiguities (full-check/check,
  create-pr/ship, finish-work/housekeeping) in the record as observed, marking
  them explicitly as documented-not-decided unless the upstream proposal
  chooses to cover them.
- No local modification of any file covered by
  `.sd-ai-command-pack/provenance.json`.

## Acceptance Criteria

- [x] `disposition.md` exists in this task directory as the single
      authoritative record, quoting sd-review's supersession text with its
      file path.
- [x] The route chosen is upstream (per the Disposition decision section):
      the proposal text exists in `disposition.md`, names the exact
      files/surfaces to change, and was filed upstream with the issue URL
      recorded — or the concrete blocker that prevented filing is recorded in
      its place.
- [x] `git status` shows no local edits to provenance-tracked sd-* files from
      this task.
- [x] The three adjacent ambiguities are listed in the record with their
      status (deferred / included in proposal).
- [x] The expired "transitional until 0.62.0" promise is explicitly
      reconciled in the disposition (superseded deadline restated, removal
      proposed, or expiry accepted with reason).

## Out of scope

- Implementing the upstream change in sd-ai-command-pack — that repository's
  own task flow owns it.
- The general vendored-defect routing contract
  (`08-07-vendored-artifact-upstream-route`); this task is one instance
  flowing through whatever that contract decides, not a redefinition of it.
- se-* skills — no supersession claims exist there.

## Notes

- Sourced from the 2026-08-08 deep review (UX lane); supersession text
  re-verified directly in `.agents/skills/sd-review/SKILL.md` the same day.
- 2026-08-09: the pack refresh v0.64.3 → v0.64.32 changed none of these
  supersession signals (the refresh did touch some of the files themselves,
  e.g. `sd-review/SKILL.md` and the command catalog, but not the signals at
  issue). Re-verified after the refresh: the `sd-review-local` and
  `sd-review-pr` skill descriptions still carry no supersession notice, the
  `sd-help` catalog rows (40, 43, 54) still say "transitional until 0.62.0",
  and the `sd-full-check` skill still never names `sd-check`. Upstream has had
  thirty-plus releases to retire or mark the transitional commands and has not,
  which strengthens the case for an explicit upstream proposal over waiting.
- 2026-08-09: routing precedent exists — upstream issues 397 and 398 were
  filed against sd-ai-command-pack via the route recorded in
  `08-07-vendored-artifact-upstream-route`'s relay log. This task follows the
  same route: file the proposal as an upstream issue and record the URL in the
  disposition.
- If `08-07-vendored-artifact-upstream-route` lands its contract first, follow
  its recorded route; if this task moves first, note the routing decision it
  made so the contract task can cite a live instance. This filing does not
  add a row to that task's canonical instance table; enrollment and its
  derived-count reconciliation happen per that task's own contract.
- Adversarial review (2026-08-08) narrowed the claim: the supersession signal
  is absent from the peer adapters/frontmatter, not absent everywhere — the
  `sd-help` catalog already carries a transitional notice.
- Lightweight; PRD-only.
