# Implement — Dependency bot config (A-031)

Branch `audit/dependabot-config` off `main`.

## Ordered checklist

1. **Add `.github/dependabot.yml`** (per design D3):
   ```yaml
   version: 2
   updates:
     - package-ecosystem: "pip"
       directory: "/"
       schedule:
         interval: "weekly"
       open-pull-requests-limit: 5
       commit-message:
         prefix: "chore(deps)"
   ```

2. **Validate the config offline — strict** (design D4). Assert every planned
   field/value and reject unknown top-level keys; a subset check would pass a
   config that dropped the two optional fields. Write no committed test; run
   inline:
   ```bash
   bash scripts/sd-ai-command-pack-toolchain.sh run-python -- - <<'PY'
   import yaml
   d = yaml.safe_load(open(".github/dependabot.yml"))
   assert set(d) == {"version", "updates"}, f"unexpected top-level keys: {set(d)}"
   assert d["version"] == 2, d["version"]
   ups = d["updates"]
   assert isinstance(ups, list) and len(ups) == 1, "expected exactly one update entry"
   pip = ups[0]
   assert set(pip) == {
       "package-ecosystem", "directory", "schedule",
       "open-pull-requests-limit", "commit-message",
   }, f"unexpected keys in pip entry: {set(pip)}"
   assert pip["package-ecosystem"] == "pip", pip.get("package-ecosystem")
   assert pip["directory"] == "/", pip.get("directory")
   assert pip["schedule"]["interval"] == "weekly", pip.get("schedule")
   assert pip["open-pull-requests-limit"] == 5, pip.get("open-pull-requests-limit")
   assert pip["commit-message"]["prefix"] == "chore(deps)", pip.get("commit-message")
   print("dependabot.yml strict field check OK")
   PY
   ```
   Expected decisive line: `dependabot.yml strict field check OK`.
   Note: this offline check is the pre-merge gate. GitHub reads/validates
   `dependabot.yml` only from the default branch, so its authoritative
   validation is a post-merge signal (see "Post-archive handoff" below /
   design D6), not a PR gate and not acceptance evidence.

3. **Document in `CONTRIBUTING.md`** (design D5/D6) — add a "Dependency
   updates" section: Dependabot opens weekly pip PRs against
   `requirements-dev.txt`; triage with `sd-update-deps` (classify, merge the
   safe class under the housekeeping gate, park the rest). Record: npm coverage
   deferred (root has no deps; `.opencode` unused + removal-pending A-032);
   no scheduled pip-audit lane (considered, deferred); and the enablement model
   — committing `dependabot.yml` to the default branch enables version updates
   on this non-fork repo (no separate repo toggle), with org-level Dependabot
   disablement the only possible blocker.

   Do not add a manual `.obsidian-kb` step: KB mirroring of CONTRIBUTING.md is a
   routine local-only side effect owned by the ship lifecycle (sd-create-pr's
   update-spec stage refreshes it before `sd-check` runs; housekeeping refreshes
   post-finish). It is out of this task's committed scope (design "Scope").

4. **Mark PRD acceptance boxes at finalization** (pre-archive). Both ACs are
   satisfiable before merge/archive, which is required by the completion
   contract (all ACs true before `task.py archive`; merge is post-archive):
   - AC1 = valid `.github/dependabot.yml` committed and passing the step-2
     strict field check, plus the enablement model documented in CONTRIBUTING.
   - AC2 = sd-update-deps triage path documented in CONTRIBUTING.
   Add a short acceptance-evidence note citing the strict-check output line and
   the CONTRIBUTING section. Do **not** condition an AC box on any post-merge
   observation.

## Post-archive handoff (not an acceptance criterion)

After `sd-housekeeping` merges the PR to `main`, confirm GitHub registered the
config — Insights → Dependency graph → Dependabot tab lists it with no parse
errors, and/or a `dependabot[bot]` pip PR appears
(`gh pr list --repo platypeeps/se-ai-command-pack --author 'app/dependabot'`).
Record the observed state during follow-ups. If Dependabot reports a real config
error or an org policy suppresses updates, capture that **observed** blocker as a
follow-up Trellis task (design D6). This verification runs after archive and does
not gate task completion.

## Validation commands

- `make check` — full gate (test/lint/release-check). Config-and-docs-only
  change; expect green, coverage floor unaffected.
- The inline strict field check in step 2.
- KB currency (`knowledge.obsidian-kb`) is checked by `sd-check` inside the ship
  review stage after update-spec refreshes it; no manual `--check` step here.

## Named falsifiable check (pre-work)

`make check` exits 0 AND the step-2 strict check prints
`dependabot.yml strict field check OK`. Any nonzero exit or failed assert =
failure. (Post-merge Dependabot pickup is a post-archive handoff, not part of
this pre-archive check — it cannot be observed offline.)

## Review gates

- Planning-adversarial-review before `task.py start` (project rule).
- sd-ship Stage 2 (sd-check + gito + Copilot) at PR time.

## Rollback

Delete `.github/dependabot.yml` and the CONTRIBUTING section; revert PRD boxes.
No code or payload touched, so nothing downstream depends on this.
