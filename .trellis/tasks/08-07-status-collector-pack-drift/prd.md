# Status collector emits no pack-freshness signal in a consumer repository

## Goal

Stop `sd-status` from reporting on an out-of-date installed pack without any
freshness signal, so an operator learns the pack is behind from the ordinary
status report rather than by comparing version strings by hand.

The defect is the **silence**, not the verdict. `SD status: healthy` is not a
claim about pack freshness and `SD status: attention` is not a denial of one —
both are computed from anomalies, working-tree state, and sync state
(`render_local`, `:2095-2100`), none of which consults the pack. Wherever this
task is restated, state the missing signal; do not describe the defect as
"reporting healthy".

## Problem

> **Line citations in this PRD are pinned to installed pack `0.64.3`** —
> `scripts/sd-ai-command-pack-status.py` at 2631 lines and
> `scripts/sd_ai_command_pack_fleet_lib.py` at 803 lines, every anchor below
> re-verified against those files on 2026-08-07. Both files are
> `install: "always"` (see *Constraint: the collector is vendored*), so a pack
> refresh overwrites them and the line numbers **may** move — how much differs
> per file, which is why the rule below is stated per citation rather than as a
> blanket claim. Checked 2026-08-07 against source `0.64.25`:
>
> - `sd-ai-command-pack-status.py` **moved** — 2631 lines installed against 2705
>   in source; at the source's `:393` is blank, `:1769` is `)`, and `:2607` is a
>   `print` call. Every status citation below is therefore stale on `0.64.25`.
> - `sd_ai_command_pack_fleet_lib.py` is **byte-for-byte identical** between the
>   two versions (`diff -q` reports no difference), so `:111-131`, `:251`,
>   `:268`, and `:284` still resolve. That is a property of this version pair,
>   not a guarantee — the file is equally overwritable on the next refresh.
>
> Each citation therefore also names its enclosing symbol.
> **Re-locate by symbol, not by line, on any version other than `0.64.3`, and
> re-verify rather than assuming a citation did or did not survive.**
>
> | Symbol | File | Role |
> | --- | --- | --- |
> | `collect_versions` | status | computes `packState`, `sourcePack`, `targetPack` |
> | `collect_local` | status | local report; declares `target_pack_version` default |
> | `main` | status | local-mode `collect_local(` call site |
> | `collect_follow_ups` | status | drift recommendation |
> | `next_steps` | status | drift numbered step |
> | `render_local` | status | human `Delivery` line |
> | `collect_fleet` | status | fleet lane; supplies `target_pack_version` |
> | `fleet_next_steps` | status | fleet rollup version compare |
> | `fleet_profile_path` | fleet lib | machine profile path resolution |
> | `resolve_fleet_configuration` | fleet lib | the three `target_version=version` returns |

`collect_versions` (`scripts/sd-ai-command-pack-status.py:382-415`) decides pack
freshness from a three-way comparison, but in **ordinary local mode** — the
`sd-status` an operator runs inside a consumer repository — one of the three
inputs is always absent. Fleet mode is not affected: it supplies a real target
(`:2443`, in `collect_fleet`) and is out of scope here.

The only target source local mode can reach is the repository's own root
manifest, gated on the pack's name (`:393-398`, in `collect_versions`):

```python
source_manifest = read_json_object(repo / "manifest.json")
source_pack = None
if source_manifest and source_manifest.get("name") == "sd-ai-command-pack":
```

That gate is satisfied only inside the `sd-ai-command-pack` source checkout. A
consumer repository either has no root `manifest.json` or — as here — has its
own: this repository's is named `se-ai-command-pack` at version `0.67.1`, which
is its own pack version and has nothing to do with the installed SD pack.
Either way `source_pack` stays `None`.

There is no second chance at it. `sd-status` exposes no flag that supplies a
target version in local mode, and `packState` is produced nowhere else — it is
written once at `:413` (`collect_versions`) and only ever read.

The other input never arrives. `collect_local` declares
`target_pack_version: str | None = None` (`:1926`, in `collect_local`), and the
local-mode call site (`:2607-2619`, in `main`) omits the argument entirely. Only
the fleet lane supplies it (`:2443`, in `collect_fleet`).

So `target` is `None`, and the state ladder falls through to its neutral rung
(`:399-407`, in `collect_versions`):

```python
target = target_pack_version or source_pack
if installed_pack is None:
    pack_state = "not-installed"
elif target is None:
    pack_state = "installed"
```

`"installed"` is not "current" — but nothing downstream says so. Three separate
surfaces would report drift, and every one of them is gated on the state local
mode cannot reach:

| Surface | Line (`0.64.3`) | Symbol | Gate |
| --- | --- | --- | --- |
| Follow-up recommendation | `:1769-1774` | `collect_follow_ups` | `packState == "different"` |
| Numbered next step | `:1834-1837` | `next_steps` | `packState == "different"` |
| Human `Delivery` line | `:2148-2150` | `render_local` | prints `target` only when it is truthy |

```python
if isinstance(versions, dict) and versions.get("packState") == "different":
    add(
        "recommendation",
        "Refresh the installed SD command pack to the source fleet version.",
        "versions.packState",
    )
```

Fleet mode runs the same two gates: `collect_fleet` calls `collect_local`
(`:2431`, in `collect_fleet`), which populates `followUps` and `nextSteps` from
exactly those functions (`:2021-2025`, in `collect_local`). The gates are not the
difference — the target is. Fleet supplies one (`:2443`), so `packState` can
actually become `"different"` there, and fleet additionally compares versions
directly for its own rollup
(`item["report"]["versions"]["sdAiCommandPack"] != target`, `:2358-2363`, in
`fleet_next_steps`). Local mode reaches the identical code with nothing to
compare against.

### Observed

This repository on 2026-08-07: installed pack `0.64.3`, sibling source checkout
`../sd-ai-command-pack` at `0.64.24`. `sd-status --no-network` reported:

```
SD status: healthy
- SD pack: 0.64.3 (installed)
...
==> Anomalies
none
```

with `"packState": "installed"`, `"sourcePack": null`, `"targetPack": null`. No
anomaly, no follow-up, no recommendation. The report is not wrong about any
fact it states; it simply cannot state the one that mattered.

Two things in that record are circumstantial rather than load-bearing.

The source version is a **snapshot, not a fixture**. Re-checked later the same
day, the sibling checkout was at `0.64.25` while the installed pack was still
`0.64.3` — the source moves independently of this task.

`SD status: healthy` is **not part of the defect**. `render_local` sets
`attention` when there are anomalies *or* the tree is dirty *or* the branch is
unsynchronized (`:2095-2100`, in `render_local`), none of which involves the
pack. The run above said `healthy` because the tree was clean at that moment; the
same run on a dirty branch says `attention` with the pack defect equally present
and equally unreported. The defect is the *silence* — `packState: "installed"`,
`targetPack: null`, no anomaly, no follow-up, no recommendation — not the verdict
printed above it.

What reproduces is therefore the shape: installed strictly behind source, and no
pack-freshness signal emitted. Criteria below are written against that, not
against the version pair or the verdict.

### The mechanism already exists — it is only wired to the fleet lane

`sd_ai_command_pack_fleet_lib.py` resolves a target version three ways, each
returning `target_version=version` (`:251`, `:268`, `:284`, all in
`resolve_fleet_configuration`): from an explicitly
requested fleet manifest, from the machine-local fleet profile at
`fleet_profile_path` (`:111-131`, `~/.config/sd-ai-command-pack/config.json`),
or from the runtime pack source checkout. Local status consults none of them.

The profile route is viable but not universal. `fleet_profile_path` resolves
`XDG_CONFIG_HOME` before falling back to `~/.config` (`:119-131`), so the path
is environment-dependent rather than fixed. On the machine where this was
observed, `XDG_CONFIG_HOME` was set, the profile resolved to
`$XDG_CONFIG_HOME/sd-ai-command-pack/config.json`, and it existed — its
`packSource` named the sibling `sd-ai-command-pack` checkout, which was at
`0.64.24` when observed and has advanced since. A profile-reading fix would
therefore have worked there, and what makes it work is that the checkout is
ahead of the installed pack at all — not the particular version it held. Any
disposition must resolve the path through `fleet_profile_path` rather than
assuming `~/.config`.

That cuts both ways. The target was sitting on disk, one documented lookup away,
and local mode still emitted no freshness signal — which strengthens the case
that this is an omission rather than a missing capability. But the profile is created only by
`install.py TARGET --configure-fleet`, so it is absent on any machine that has
not run it, and the disposition still has to say what a repository with no
profile reports.

## Constraint: the collector is vendored

`.sd-ai-command-pack/manifest.json` records the collector at `files[30]`:

```json
{
  "platform": "shared",
  "kind": "script",
  "source": "templates/scripts/sd-ai-command-pack-status.py",
  "target": "scripts/sd-ai-command-pack-status.py",
  "install": "always"
}
```

`install: "always"` means every pack refresh overwrites it, so a local edit is
reverted rather than kept. `scripts/sd_ai_command_pack_fleet_lib.py` is
installed from the same pack. A behaviour change to either is an **upstream**
pull request against `sd-ai-command-pack` and needs explicit approval for that
pull request, which the autonomous run-level authority excludes. Only this
repository's `.trellis/spec/` guidance is editable locally.

This is the self-referential case: the defect that hides vendored pack drift
lives in a vendored file.

## Requirements

- Decide and record a disposition:
  - **Upstream.** Propose that local mode resolve a target version and that the
    report distinguish "no target available" from "up to date". State which
    sources are consulted and in what order.
  - **Local-only.** Document in `.trellis/spec/backend/quality-guidelines.md`
    that `packState: "installed"` means *unknown*, not *current*; that
    the `SD status` verdict carries no claim about pack freshness in either
    direction, `healthy` or `attention`; and how an
    operator checks drift by hand.
- The local documentation lands on **both** routes. On the upstream route it is
  the interim record while the proposal is pending, and it must land first and
  not depend on the upstream change merging — the same rule
  `08-06-watch-coordinator-infra-classification` already states for its own
  upstream option. The routes differ in whether an upstream proposal is also
  made, not in whether anything is written down here.
- Whichever route is chosen, name the target sources considered and why each
  was accepted or rejected. At minimum: the machine fleet profile, a sibling
  source checkout discovered by path convention, and the GitHub release list.
  A source that requires network access must degrade under `--no-network`
  rather than fail or silently report `current`.
- State what a repository with no resolvable target reports. An explicit "target
  unknown, freshness not checked" is an acceptable answer; emitting nothing about
  freshness at all is the defect. Do not phrase this requirement in terms of the
  `SD status` verdict — a report that says "no target resolved" is satisfactory
  whether the verdict reads `healthy` or `attention`, and one that says nothing
  is unsatisfactory in either case.
- Do not make the absence of a target an error. `sd-status` is advisory and
  exits zero on a dirty or stale report; a missing target must not change that.
- Do not weaken the collector's read-only character. It must not fetch, install,
  refresh the pack, or create the fleet profile in order to learn a version.
- Do not edit `scripts/sd-ai-command-pack-status.py` or
  `scripts/sd_ai_command_pack_fleet_lib.py` in this repository. Both are
  `install: "always"` and the edit would be reverted by the next refresh.

## Acceptance Criteria

Every criterion below is checked against **the deliverable**, not against this
PRD. The deliverable is the guidance section in
`.trellis/spec/backend/quality-guidelines.md`, which lands on either route, plus
the upstream pull-request description when the upstream route is taken. A
criterion satisfied only by text in this `prd.md` is not satisfied.

- [ ] The disposition is recorded in the deliverable with its reasoning,
      including whether upstream approval was sought.
- [ ] The deliverable cites the load-bearing code — the name-gated source lookup
      (`collect_versions`, `:393-398`), the omitted argument at the local-mode
      call site (`main`, `:2607-2619`), and the `packState == "different"` gate
      shared by both drift surfaces (`collect_follow_ups`, `:1769-1774`, and
      `next_steps`, `:1834-1837`) — so a reader who has not seen this PRD can
      verify the chain.
- [ ] Every citation in the deliverable names its enclosing symbol and states the
      pack version its line numbers were taken from. Both cited files are
      `install: "always"`, so a bare line number may stop resolving at any
      refresh — whether it does is per file and not predictable from the version
      numbers, which is why the symbol is required regardless. Verified by
      re-locating each cited symbol in the currently installed collector, not by
      trusting the line numbers.
- [ ] A reader of the deliverable who has not seen this PRD can determine
      whether `packState: "installed"` on their own repository means *current*
      or *unknown*.
- [ ] The deliverable states the operator procedure for checking drift by hand
      under the chosen disposition, and a run of that procedure on this
      repository reproduces the defect *shape*: with an installed version
      strictly behind the resolvable source version, `sd-status` emits **no
      pack-freshness signal at all** — `packState: "installed"`, `targetPack:
      null`, `sourcePack: null`, and no anomaly, follow-up, or recommendation
      naming pack drift.

      Do **not** write the criterion against the top-line `SD status: healthy`.
      That verdict is not a pack-freshness claim: `render_local` sets `attention`
      when there are anomalies **or** the working tree is dirty **or** the branch
      is unsynchronized (`:2095-2100`, in `render_local`), so an ordinary
      mid-branch run reports `attention` with the pack defect fully present. The
      original 2026-08-07 observation showed `healthy` only because the tree
      happened to be clean at that moment. The pack-freshness fields are the
      invariant; the verdict is not.

      Do not pin the criterion to a version pair either — the source checkout
      advances on its own, and it moved from `0.64.24` to `0.64.25` within a day
      of the original observation.
- [ ] If the installed pack has reached parity with the source before the
      deliverable is written, say so plainly rather than implying a live run: at
      parity the shape **cannot** be reproduced by running `sd-status`, because
      `packState` legitimately becomes `current` once a target resolves — and in
      a consumer repository with no target it stays `installed` whether or not
      drift exists, which is the defect itself. The criterion is then satisfied
      by citing the recorded observation together with a re-derivation of the
      code path showing the target is still unresolvable in local mode. Naming
      historical version strings is not a reproduction and must not be presented
      as one.
- [ ] Every target source considered is accounted for: each accepted one with
      the reason it was accepted and its position in the lookup order, each
      rejected one with its rejection reason. Absence from the list is not a
      rejection.
- [ ] The deliverable states that a repository with no resolvable target still
      exits zero and is not reported as an error, and names what it does report
      instead.
- [ ] The deliverable states that learning a version must not fetch, install,
      refresh the pack, or create the fleet profile, and the disposition it
      records satisfies that constraint.
- [ ] The `--no-network` behaviour of any network-dependent source is stated
      explicitly and does not report `current` when it could not check.
- [ ] No file installed by `.sd-ai-command-pack/manifest.json` is modified in
      this repository. Verified by checking each changed path against that
      manifest's `target` values, not by reading the diff.

## Out of scope

- Refreshing this repository's installed pack. That is an operator action, not
  this task's deliverable. It does not block the task: the citations above carry
  their symbols and their pinned version, and the reproduction criterion is
  written against the defect shape rather than a version pair, so a refresh
  changes which numbers the record shows and not whether the record is
  verifiable.
- Fleet-mode reporting, which already resolves a target and already surfaces
  `packState: "different"`.
- Any change to `install.py`, `--configure-fleet`, or the fleet profile format.
- Detecting per-file drift against `provenance.json` hashes. That is a
  different question from version drift and has its own cost.

## Notes

- A member of the vendored-artifact pattern, and the instance that motivated
  writing the pattern down. Membership is recorded as a row in the canonical
  table in `08-07-vendored-artifact-upstream-route/prd.md`; no ordinal is kept
  here, because a count maintained in several PRDs at once drifts the moment one
  is added.
- Found on 2026-08-07 while checking why an installed pack well behind the
  source checkout produced no status signal. The version gap is verified from
  `.sd-ai-command-pack/provenance.json` and `../sd-ai-command-pack/manifest.json`.
  `gh release list --repo platypeeps/sd-ai-command-pack` returned no output on
  that check, so the published release count is unverified and the GitHub
  release lane must be treated as an unproven target source until it is.
- Planning depth: PRD-only if the local-only route is chosen. The upstream route
  adds source precedence, network degradation, and a report-shape change, and
  needs both a `design.md` and an `implement.md` before `task.py start`.
