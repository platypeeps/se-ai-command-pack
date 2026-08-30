# Inspiration: claude-skills

The pack's Engineer family and Rust agent trio were re-authored from ideas in
an external skills library. Nothing was copied: every shipped file is written
in this pack's conventions, routes only to lanes this pack ships, and carries
this pack's license posture. This file records where the ideas came from, what
was deliberately changed, what was declined and why, and how to harvest more.

## Pinned sources

| Source | Pin | Nature |
| --- | --- | --- |
| `Shearerbeard/claude-skills` | `0e4fb48ed69d665fd1307a51cb126af915c6502b` | Public upstream, active. 22 skills at the pin. |
| `opencode-cfg` | `b37c6ec` | Private local checkout, no remote. Design source for the agent trio only; its configuration holds private infrastructure identifiers and must never gain a public remote. |

Neither is a dependency. There is no submodule, no vendored copy, and no CI
job that fetches either one.

The two pins do different jobs. The upstream pin is a harvest cursor: anyone
can clone that repository and diff it, so the ritual below can be run by
someone who was not here. The `opencode-cfg` pin is provenance only. It names
the revision the agent trio was designed against on one machine, and nobody
else can fetch it — so it records where an idea came from and never feeds the
harvest. The ritual below covers the upstream source alone; changes on the
private side reach this pack as an ordinary Trellis task, described in the
task rather than diffed from a pin.

## Inspiration map

| Shipped surface | Upstream source | What changed deliberately |
| --- | --- | --- |
| `se-rust-design` | `rust-design` | Rewritten in pack voice; routing points at sibling `se-*` skills and the `sd-review` lane. |
| `se-rust-quality` | `rust-quality` | Same; toolchain mandates that contradict this repo were dropped. |
| `se-rust-modules` | `rust-modules` | Same. |
| `se-rust-async` | `rust-async` | Same. |
| `se-rust-review` | `rust-review` | Reframed as a local lens: it never owns a review verdict, which stays with the `sd-review` lane. |
| `se-typed-holes` | `typed-holes` | Names the pack's own agent trio as optional executors. |
| `se-gate-probes` | `gate-probes` | Routing table rewritten end to end. Upstream routed commit-message writing to a skill this pack declined; no such route exists here. The "review this diff" claim was removed — probes report, the review lane decides. |
| `se-docs-bustest` | `docs-bustest` | Rewritten in pack voice. |
| `se-rebase-hygiene` | `rebase-hygiene` | User-invoked only. Rewritten so the skill plans and verifies while the user approves the push — this repository forbids unapproved force pushes. |
| `se-skill-retro` | `skill-retro` + `process-feedback` | Two upstream skills merged. Upstream wrote findings to a marketplace feedback directory that does not exist here; findings now route to the repository that owns the surface. |
| `se-prose-lint` | `prose-lint` | Upstream assumed personal style files that never shipped. This version drives the pack's own Vale gate and degrades gracefully where Vale is absent. |
| `se-humanizer` | `humanizer` | Substance re-derived; no upstream text and no license header carried over. Same graceful-degradation clause. |
| `se-adr-review` | `adr-review` | Narrowed to the review process only, per an explicit product decision. It never authors or templates a record. |
| `se-rust-write`, `se-rust-fill`, `se-rust-reviewer` | `opencode-cfg` agent roster | Foreign model pins dropped (they inherit the session model). The deny-by-default posture survives as prose plus tool grants, never as copied permission data. |
| Planning thinking guide (`docs/spec/guides/planning-thinking-guide.md`) | `plan-discipline` | Folded rather than shipped as a skill: it competed with the Trellis planning workflow. Trellis still owns when planning starts; the upstream trigger and gate ladder were dropped. |
| Prism required checks `fail-loud`, `single-traversal-projection`, `comment-intent` | `python-review`, `python-quality` | Folded into the existing local review provider. The click, pytest, and uv mandates were dropped: this repository uses argparse and unittest. |

## Declined, with reasons

Recorded so a later harvest does not re-litigate settled decisions.

| Upstream | Reason |
| --- | --- |
| `mermaid` | Depends on a viewer from the author's personal dotfiles; it arrives broken. |
| `git-commit` | Forbids the commit trailers this user's convention mandates, and demands per-commit approval that standing workflow authority waives. |
| `codex-cli`, `opencode-cli`, `collaborating-with-antigravity` | Route reviews to external CLIs. The `sd-review` lane forbids direct reviewer fallbacks and no review-tooling document binds lanes. Revisit only after such a document exists. |
| `plan-discipline` as a skill | Competes with Trellis planning. Folded instead (see the map). |
| `python-quality`, `python-review` as skills | Toolchain mandates contradict this repository. Folded instead. |
| `codebase-design`, `prose-corpus`, `vale-lsp`, `haskell-lsp` | Not skills, or not shipped upstream. |
| Agents `frontier-reviewer`, `prose-write`, `python-write`, `python-reviewer` | Deferred. Review agents compete with the `sd-review` lane; revisit on a demonstrated gap. |

## Harvest ritual

On demand, or roughly quarterly. The ritual produces Trellis tasks or nothing
at all — it never edits `templates/` directly.

1. Fetch the upstream checkout and list what moved since the pin:

   ```bash
   git -C <upstream checkout> fetch origin
   git -C <upstream checkout> log --stat 0e4fb48ed69d665fd1307a51cb126af915c6502b..origin/HEAD
   ```

2. Read the new and changed skills. Judge each against three questions: is
   this a new idea worth a task, does it change a skill this pack already
   re-authored, or is it nothing of note?
3. Check the declined table before proposing anything from it. A declined
   entry reopens only when its stated reason no longer holds, and the harvest
   report must say which reason changed.
4. Write a harvest report naming what was reviewed, what was found, and what
   became a task.
5. Advance the pin in this file **in the same commit as the report**. A pin
   that moves without a report loses the record of what was skipped.
