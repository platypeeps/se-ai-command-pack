# Add `se-review-skills`

## Goal

Add a P1 Improve-family skill that reviews any explicitly bounded skill or skill
collection for defects, trigger and workflow overlap, capability-preserving
simplification, metadata quality, and runtime-routing opportunities. Present
evidence-backed improvements that can be selected individually or in explicit
skill-, family-, repository-, or package-wide batches, and route accepted work
to the Trellis repository that owns each skill.

## Background

This package is the first integration target, but not the review boundary. It
currently ships 42 canonical `se-*` skills across six families. Their 5,615
lines are copied unchanged to shared-agent, Claude, and Codex skill roots.
`installer/registry.py` owns family membership, and the generator accepts only
portable `name` and `description` frontmatter in canonical skills.

The requested reviewer is a product skill, not an `sd-*` development command:
this repository owns `templates/skills/se-*`, while `.agents/skills/sd-*` is
installed tooling owned by the separate SD command pack. The public skill name
will be `se-review-skills`, its primary family will be Improve, and this task is
linked to the existing SE skill roadmap. At runtime it may review skills from
this pack, the SD pack, another package, a plugin, or a repository-local skill
tree.

For the two first-party command packs, review and remediation are deliberately
template-only. Installed copies may prove drift, and registries, generators,
manifests, or tests may prove ownership and platform behavior, but those files
are context rather than skill-review targets. An SD or SE finding must resolve
to an allowed upstream template path before it can be selected for a task or
application.

Claude Code supports host-specific skill fields such as `context: fork`,
`agent`, `model`, and `effort`, but those fields are not currently portable
through this package's one-source/three-platform generator. OpenAI's optional
Codex plugin for Claude Code can provide read-only standard or adversarial
review and fresh delegated runs, but it may be unavailable or unauthenticated.

## Requirements

### Review scope and evidence

- Accept one or more explicit `skill=` paths or names and an optional `root=`.
  Support `family=` and `scope=skill|family|repo|package|all` without silently
  broadening an invalid selector. `all` means all discovered skills under the
  resolved boundary, never every skill on the machine.
- When no target is supplied, discover declared skills in the current Git
  repository. If none or multiple unrelated roots are found, stop and request
  an exact `skill=` or `root=` instead of scanning user directories.
- Derive family membership and canonical skill identity from a package
  registry or equivalent declared source of truth. Put skills without declared
  family metadata in `Uncategorized`; do not invent a family from prose.
- Resolve the canonical source separately from installed, generated, vendored,
  plugin, or locally overridden copies. Do not infer ownership from a prefix,
  directory name, or similar content alone.
- Inventory every selected skill before judgment: canonical path, family,
  description, sections, references, line/word size, required contracts,
  platform targets, and validation coverage when observable.
- Separate deterministic observations from reviewer judgment. Every finding
  must cite a file and line or a reproducible command result; unsupported
  suspicions stay in coverage limits, not the improvement list.
- Review these dimensions:
  - correctness, safety, authority, and internal contradictions;
  - trigger, argument, workflow, output, and sibling-boundary overlap;
  - missing capabilities, unclear handoffs, and improvement opportunities;
  - unnecessary repetition, narration, examples, or reference duplication;
  - frontmatter trigger quality and host/runtime metadata opportunities;
  - progressive disclosure, deterministic-helper opportunities, failure paths,
    portability, context cost, and forward-evaluation coverage; and
  - context isolation, subagent decomposition, model/effort routing, and
    optional independent review.

### First-party template boundary

- For `se-ai-command-pack`, review and change only canonical skill templates
  under `templates/skills/**`, including references owned by those template
  directories. Treat `.agents/skills/**`, `.claude/skills/**`,
  `.codex/skills/**`, manifests, documentation catalogs, and installed copies
  as read-only validation evidence, not remediation paths.
- For `sd-ai-command-pack`, review and change only files under `templates/**`.
  Treat `templates/.agents/skills/**` and `templates/.commands/**` as the
  primary authored skill and neutral command sources. Platform adapter
  templates such as `templates/.claude/**`, `templates/.gemini/**`, and
  `templates/.github/**` may be inspected for target correctness, but normally
  inherit changes through the package's generation workflow rather than
  receiving a hand-maintained duplicate fix.
- Classify every observed file as `authored-template`,
  `generated-template-adapter`, `installed-copy`, or `local-override`. Findings
  about installed or generated copies must map to an authored template before
  they become selectable skill remediation. If no template change can address
  the issue, report it as an out-of-scope packaging/tooling limitation instead
  of broadening the skill review.
- Reject `task=` or `apply=` selections for SD or SE findings whose proposed
  affected paths escape the corresponding template allowlist. Do not edit a
  consumer installation to repair upstream content.
- Other repositories continue to use their declared canonical skill source;
  do not impose the SD or SE directory convention on them.

### Capability-preserving brevity

- Establish a capability ledger for each skill before suggesting deletion or
  compression. At minimum preserve its trigger, inputs, output contract,
  authority and mutation boundary, safety gates, verification, failure states,
  sibling boundaries, and required platform compatibility.
- Treat "as short as possible" as the shortest version that preserves every
  accepted capability and safety contract, not as a line-count target.
- Prefer removing duplicated explanation and moving conditional detail into a
  directly linked reference over weakening an operative rule.
- Identify workflow steps that can move into a deterministic script: repeated
  parsing, normalization, validation, transformation, hashing, path resolution,
  inventory, schema checks, or stable command orchestration. For each candidate,
  define inputs, outputs, errors, side effects, portability, dependencies,
  idempotence, dry-run needs, and tests.
- Keep semantic judgment, user dialogue, approvals, evidence interpretation,
  authority decisions, and unbounded external actions in the skill. Do not
  replace a clear one-off instruction with a script whose maintenance or runtime
  dependency costs exceed its reliability or context savings.
- Report estimated lines or words saved, the capability-preservation argument,
  and the regression risk for every brevity finding.
- Do not recommend compressing text that tests intentionally pin unless the
  proposal includes the corresponding behavior-preserving test update.

### Metadata and runtime routing

- Audit the portable top-of-file metadata first: exact name, concise trigger
  description, invocation intent, and ambiguity with neighboring skills.
- Distinguish frontmatter from host UI metadata. When a Codex-compatible
  `agents/openai.yaml` is applicable, evaluate its display name, short
  description, and default prompt; do not misrepresent those fields as YAML
  frontmatter or require them on hosts that do not consume them.
- For each skill, recommend one context mode with rationale:
  `inline`, `forked`, or `fresh-session`. Distinguish a host forked subagent
  from a new independent session; never use the terms interchangeably.
- For each skill, recommend a portable model profile (`inherit`, `fast`,
  `balanced`, or `deep`) plus reasoning effort and rationale. Name an exact
  model only when the current host exposes it and the recommendation is scoped
  to that host; unavailable model names must not enter canonical skill text.
- Keep canonical `name` and `description` portable. Host-specific fields such
  as context, agent, model, effort, invocation controls, paths, or tool grants
  may be applied only through a validated per-platform overlay mechanism.
  Until that mechanism exists, report them as recommendations rather than
  inserting unsupported keys into canonical frontmatter.
- Evaluate target-tool behavior through a capability matrix derived from the
  owning package's declared platform registry and generated template contracts.
  The matrix must distinguish portable skill content, host frontmatter,
  command/argument syntax, UI metadata, context isolation, model selection,
  tool grants, and validation support. Unknown support stays `unknown`; it is
  not inferred from another host.
- Preserve one portable authored body wherever possible. Recommend a generated
  target adapter or metadata overlay only when host syntax or semantics require
  it; never recommend separately hand-maintained Claude, Codex, Gemini, or
  other full skill bodies.
- For the SD pack, account for its registry-driven target adapters and validate
  platform-specific command syntax and behavioral parity from templates. For
  the SE pack, recognize that the current supported targets are shared-agent,
  Claude, and Codex, and that all consume the same canonical body. Treat Gemini
  installation support or a new overlay generator as a separate package
  capability, not an implied skill edit.
- Evaluate whether the reviewer itself should use isolated context. The
  default design is a fresh or forked read-only analysis pass for package-wide
  review, with inline orchestration for selection and application.
- For each skill, recommend `delegation=none|optional|required` and bounded
  roles only when the work can be split into self-contained artifacts. Prefer
  subagents for parallel independent inventories, family reviews, adversarial
  validation, or target-specific checks; keep approval loops, tightly coupled
  edits, and small tasks inline.
- Pair every delegated role with a portable model profile and effort level:
  use `fast` for deterministic discovery and low-risk classification,
  `balanced` for ordinary review or implementation, and `deep` for ambiguous,
  safety-sensitive, cross-skill, or adversarial synthesis. Exact model names
  remain verified host overrides.
- Delegation must remain bounded: pass the minimum source scope and explicit
  output contract, preserve the caller's mutation authority, cap fan-out, avoid
  recursive delegation, and make the parent agent verify, deduplicate, and
  reconcile all returned findings. Independent validation must receive raw
  artifacts rather than the primary reviewer's conclusions.

### Optional Codex peer review

- When running inside Claude Code, detect whether the official Codex plugin is
  already installed, callable, authenticated, and suitable for the selected
  review stage. Never install, enable, authenticate, or reconfigure it.
- Use its read-only review or adversarial-review path only when there is a
  concrete diff or bounded artifact to review. Use a fresh delegated run only
  when independence is valuable and the operation remains read-only.
- Treat plugin output as evidence to verify, not authority. Deduplicate it with
  the primary review and record provider, model/profile when observable, and
  coverage. Continue with a native independent pass when the plugin is absent
  or unsuitable.
- Keep canonical instructions capability-based and framework-neutral; route
  host-specific invocation through a platform overlay or optional reference.

### Report and selection contract

- Return one stable, hierarchical numbered list grouped by owning repository or
  package when more than one is present, then declared family order, then
  skill. Assign each finding an immutable selector for the current review
  snapshot, such as `2.4.3`.
- Put package-wide or cross-family findings in a short leading section. Assign
  each overlap to one primary skill and cross-reference the peer skill instead
  of duplicating the finding under both.
- Each finding must include category, priority, effort, evidence, issue or
  opportunity, proposed change, capability impact, expected reduction when
  applicable, and validation needed.
- End every skill and family group with explicit batch selectors and end the
  report with repository/package and complete-scope selectors:
  - `apply=skill:<skill-name>` — do all accepted findings for one skill;
  - `apply=family:<family-name>` — do all accepted findings for one family;
  - `apply=repo:<repo-id>` — do all accepted findings owned by one repository;
  - `apply=all` — do all accepted findings in the bounded report; and
  - `apply=<finding-id,...>` — apply only named findings.
- Accept the same selector forms under `task=` to create or reconcile Trellis
  tasks without starting implementation. Every `apply=` selection performs the
  same task reconciliation first.
- A report with no findings must say so and still report coverage and limits.

### Ownership and Trellis task routing

- Reconcile selected findings with active and archived Trellis tasks before
  creating anything. Reuse an accurate open task, flag a stale task for review,
  and create a new task only for untracked accepted work.
- Group selected findings into at most one new task per affected skill and
  review snapshot. Keep finding IDs, evidence, proposed changes, capability
  risks, validation, and peer-skill dependencies in that task's PRD seed.
- Create remediation tasks in planning state without activating them
  (`task.py create --no-start` or the destination's equivalent). Reviewing
  another repository must never replace the operator's current Trellis task.
- Determine ownership from verifiable provenance in this order: canonical
  source path inside a Git checkout; installed pack provenance and vouched
  target mapping; manifest package identity plus verified source checkout and
  remote; then an explicit user-supplied owner repository. Never route from a
  skill prefix alone.
- Route canonical `sd-ai-command-pack` skills to Trellis tasks in the verified
  `platypeeps/sd-ai-command-pack` upstream checkout.
- Route canonical `se-ai-command-pack` skills to Trellis tasks in the verified
  `platypeeps/se-ai-command-pack` upstream checkout. Trellis work is represented
  by tasks; there is no separate Trellis skill-planning artifact.
- Route every other skill to a Trellis task in the enclosing repository that
  owns its canonical source. Verify the Git root and local
  `.trellis/scripts/task.py` before creating the task.
- When a reviewed installed or vendored copy has drifted, split ownership:
  reproduce canonical defects upstream before routing them there, and route
  local overrides or integration-only defects to the local repository.
- For an overlap spanning repositories, create or reuse one task per repository
  only when each repository must change; cross-reference the shared review
  snapshot and dependency rather than pretending the repositories share one
  atomic task.
- Before task creation, preview task title, priority, destination repository,
  parent decision, and selected finding IDs. An explicit task/apply selector
  authorizes only those additive Trellis files in the displayed destinations.
- If the required upstream checkout is unavailable, its remote identity is
  wrong, the worktree is ambiguously dirty, or a generic owner lacks Trellis,
  do not clone, bootstrap, or write elsewhere. Return a paste-ready task
  proposal and the exact blocker.
- Derive task priority from the highest selected finding, preserve existing
  parent/child conventions when clearly applicable, and never attach a generic
  remediation task to this package's roadmap merely because this reviewer ran.

### Safe application

- Default to read-only review. Never modify skills merely because findings
  were generated.
- Require an explicit `apply=` selector from the user. Before editing, show the
  exact findings and files selected, confirm the review snapshot still matches
  the current source, and reject stale or ambiguous selectors.
- Create or reconcile the required Trellis task in the owning repository before
  implementation. Cross-repository selections create the tasks and return
  handoffs; they do not edit several repositories in one implicit batch.
- Apply the smallest coherent batch. Preserve unrelated work and stop before a
  product, safety, dependency, or platform tradeoff not already accepted by
  the selector.
- For SD and SE batches, enforce the template allowlist both before task
  creation and immediately before editing. Generated consumer surfaces may be
  regenerated for verification, but the reviewer must not select or directly
  repair them as source files.
- After each skill batch, rerun deterministic skill validation and focused
  tests. After a family or package batch, run generation drift checks, focused
  skill tests, isolated install checks, and the repository's full quality gate.
- Report partial application explicitly. Do not continue to the next skill or
  family after a failed validation without user direction.
- Do not stage, commit, push, publish, install skills, or change global host
  configuration unless separately requested.

### Boundaries

- Complement `se-help`: the new skill reviews skill definitions and routing;
  it does not help end users choose a skill for an ordinary knowledge task.
- Complement `sd-audit-repo`: the new skill is skill-package-specific and does
  not produce the repository-wide audit ledger or audit arbitrary source code.
- Complement `sd-review-local`: optional providers may inform findings, but the
  new skill owns skill-aware inventory, capability preservation, grouping, and
  selection.
- Do not claim that word count, token count, or pairwise similarity alone proves
  bloat, overlap, or correctness.

## Acceptance Criteria

- [ ] `se-review-skills` is registered in the Improve family and installed to
      every supported platform without changing flat skill paths.
- [ ] Review supports arbitrary skill paths plus one skill, one family, one
      repository/package, and all skills inside an explicit boundary; invalid
      selectors never broaden scope.
- [ ] Findings cover issues, overlap, improvement opportunities, brevity,
      metadata, progressive disclosure, deterministic helpers, failure paths,
      portability, context cost, forward evaluation, context isolation,
      delegation, and model/effort routing with file/line or command evidence.
- [ ] Every brevity proposal includes a capability ledger, estimated reduction,
      regression risk, and validation plan; safety or authority contracts cannot
      disappear merely to reduce size.
- [ ] Every script-extraction proposal identifies the deterministic boundary,
      stable input/output/error contract, portability and dependency impact,
      side effects, idempotence or dry-run behavior, focused tests, and the
      judgment or approval steps that must remain in the skill.
- [ ] Output is hierarchically numbered, grouped by family then skill, dedupes
      cross-skill findings, and exposes individual, skill, family, repository,
      and all-scope apply selectors.
- [ ] Accepted SD-pack findings create or reuse Trellis tasks only in the
      verified SD upstream; accepted SE-pack findings do the same in the SE
      upstream; other findings use the canonical source's local Trellis repo.
- [ ] SD and SE task seeds and apply previews contain only allowed upstream
      template paths. Installed copies are read-only evidence, and a finding
      that cannot map to a template is reported as out-of-scope packaging work.
- [ ] SE review targets only `templates/skills/**`; SD review targets only
      `templates/**` and distinguishes authored neutral sources from generated
      target adapters.
- [ ] Drifted copies split upstream-reproducible findings from local integration
      findings, and ambiguous/missing ownership yields no task mutation.
- [ ] Task creation is deduplicated by skill and review snapshot, previews the
      destination and priority, preserves existing tasks, and returns a
      paste-ready proposal when the destination cannot be safely written.
- [ ] Cross-repository task creation leaves the current active Trellis task
      unchanged and never starts implementation implicitly.
- [ ] Review mode is read-only; apply mode requires explicit selection, rejects
      stale snapshots, previews scope, validates each batch, and stops safely on
      partial failure.
- [ ] Portable metadata remains limited to supported canonical fields unless a
      tested per-platform overlay is implemented; unsupported host keys never
      leak into other platforms.
- [ ] A target capability matrix prevents Claude-only, Codex-only, Gemini-only,
      or other host semantics from being presented as portable. The reviewer
      prefers one shared body and recommends generated adapters or overlays only
      where required by a verified host contract.
- [ ] Every skill receives a bounded delegation recommendation with role-level
      model profiles; subagents are used only for independently testable work,
      inherit no broader authority, avoid recursive fan-out, and return results
      that the parent verifies and reconciles.
- [ ] Host UI metadata such as `agents/openai.yaml` is audited separately from
      `SKILL.md` frontmatter and is generated only for platforms that support it.
- [ ] Claude Code can use the official Codex plugin as an optional, read-only
      peer reviewer when already available; absence or failure has a documented
      native fallback and never blocks baseline review.
- [ ] Tests pin sibling boundaries with `se-help`, `sd-audit-repo`, and
      `sd-review-local`, plus self-review, no-findings, stale-report, plugin
      unavailable, and partial-application cases.
- [ ] Generated surfaces, versioning, isolated install targets, and the full
      repository quality gate pass.

## Out of Scope

- Bulk-remediating all existing skills in the same PR that introduces the
  reviewer.
- Unbounded discovery across a user's home directory or every installed host.
- Cloning an upstream repository, bootstrapping Trellis, or repairing a dirty
  destination checkout as a side effect of review.
- Auto-installing or authenticating reviewer plugins or changing user-level
  model configuration.
- Choosing models solely by brand or hardcoding a model that a host may not
  expose.
- Replacing deterministic generation, convention tests, `se-help`, or formal
  repository audits.
- Reviewing or remediating SD/SE registry, installer, generator, manifest,
  documentation, test, or consumer-installation files as though they were skill
  templates. A tooling limitation discovered while reviewing a skill is
  reported separately and is not silently added to a skill batch.
- Publishing, committing, or opening a PR from the review/apply workflow.
