# Status collector reports pack drift as healthy in a consumer repository

## Goal

Stop `sd-status` from presenting an out-of-date installed pack as a healthy
repository, so an operator learns the pack is behind from the ordinary status
report rather than by comparing version strings by hand.

## Problem

`collect_versions` (`scripts/sd-ai-command-pack-status.py:382-415`) decides pack
freshness from a three-way comparison, but in **ordinary local mode** — the
`sd-status` an operator runs inside a consumer repository — one of the three
inputs is always absent. Fleet mode is not affected: it supplies a real target
(`:2443`) and is out of scope here.

The only target source local mode can reach is the repository's own root
manifest, gated on the pack's name (`:393-398`):

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
written once at `:413` and only ever read.

The other input never arrives. `collect_local` declares
`target_pack_version: str | None = None` (`:1926`), and the local-mode call site
(`:2607-2619`) omits the argument entirely. Only the fleet lane supplies it
(`:2443`).

So `target` is `None`, and the state ladder falls through to its neutral rung
(`:399-407`):

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

| Surface | Line | Gate |
| --- | --- | --- |
| Follow-up recommendation | `:1769-1774` | `packState == "different"` |
| Numbered next step | `:1834-1837` | `packState == "different"` |
| Human `Delivery` line | `:2148-2150` | prints `target` only when it is truthy |

```python
if isinstance(versions, dict) and versions.get("packState") == "different":
    add(
        "recommendation",
        "Refresh the installed SD command pack to the source fleet version.",
        "versions.packState",
    )
```

Fleet mode runs the same two gates: `collect_fleet` calls `collect_local`
(`:2431`), which populates `followUps` and `nextSteps` from exactly those
functions (`:2021-2025`). The gates are not the difference — the target is.
Fleet supplies one (`:2443`), so `packState` can actually become `"different"`
there, and fleet additionally compares versions directly for its own rollup
(`item["report"]["versions"]["sdAiCommandPack"] != target`, `:2358-2363`). Local
mode reaches the identical code with nothing to compare against.

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

### The mechanism already exists — it is only wired to the fleet lane

`sd_ai_command_pack_fleet_lib.py` resolves a target version three ways, each
returning `target_version=version` (`:251`, `:268`, `:284`): from an explicitly
requested fleet manifest, from the machine-local fleet profile at
`fleet_profile_path` (`:111-131`, `~/.config/sd-ai-command-pack/config.json`),
or from the runtime pack source checkout. Local status consults none of them.

The profile route is viable but not universal. `fleet_profile_path` resolves
`XDG_CONFIG_HOME` before falling back to `~/.config` (`:119-131`), so the path
is environment-dependent rather than fixed. On the machine where this was
observed, `XDG_CONFIG_HOME` was set, the profile resolved to
`$XDG_CONFIG_HOME/sd-ai-command-pack/config.json`, and it existed — its
`packSource` named the sibling `sd-ai-command-pack` checkout that is at
`0.64.24`. A profile-reading fix would therefore have worked there. Any
disposition must resolve the path through `fleet_profile_path` rather than
assuming `~/.config`.

That cuts both ways. The target was sitting on disk, one documented lookup away,
and local mode still reported healthy — which strengthens the case that this is
an omission rather than a missing capability. But the profile is created only by
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
    `SD status: healthy` carries no claim about pack freshness; and how an
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
- State what a repository with no resolvable target reports. "Healthy with no
  freshness claim" is an acceptable answer; "healthy" alone is the defect.
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
- [ ] The deliverable cites the load-bearing lines by file and line — the
      name-gated source lookup (`:393-398`), the omitted argument at the
      local-mode call site (`:2607-2619`), and the `packState == "different"`
      gate shared by both drift surfaces (`:1769-1774` and `:1834-1837`) — so a
      reader who has not seen this PRD can verify the chain.
- [ ] A reader of the deliverable who has not seen this PRD can determine
      whether `packState: "installed"` on their own repository means *current*
      or *unknown*.
- [ ] The deliverable states the operator procedure for checking drift by hand
      under the chosen disposition, and a run of that procedure on this
      repository reproduces the 2026-08-07 observation: installed `0.64.3`
      against source `0.64.24`, reported `healthy` with no anomaly.
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
  this task's deliverable, and it would change the observation this task
  records.
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
