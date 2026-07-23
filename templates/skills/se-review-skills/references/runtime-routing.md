# Runtime and Agent Routing

Keep one portable authored skill body. Treat exact host fields, model names,
agent mechanisms, and UI metadata as target-specific capabilities that must be
verified at runtime or generated through a tested overlay.

Host behavior in this reference was last verified on 2026-07-21 against the
official Claude Code skill documentation and the official OpenAI Codex plugin
README. Reverify mutable fields and command names before proposing an overlay.

## Recommendation record

Return this for every reviewed skill:

```text
invocation: automatic | user-only | both
context: inline | forked | fresh-session
delegation: none | optional | required
roles: [name, bounded input, artifact, model-profile, effort]
model-profile: inherit | fast | balanced | deep
effort: low | medium | high | xhigh
host-override: optional verified field/value
rationale: one evidence-backed sentence
```

`forked` means a host-managed isolated subagent that returns to the caller.
`fresh-session` means an independent run without inherited conclusions. They
are not interchangeable.

## Context selection

- Use `inline` for approvals, incremental evidence gathering, user dialogue,
  or tightly coupled edits.
- Use `forked` for bounded read-only inventory, one family review, one target
  parity check, or another self-contained artifact returned to the caller.
- Use `fresh-session` for independent validation, package-wide adversarial
  review, or tests where inherited conclusions would bias the result.
- Context isolation is not automatically better. Include its cost, lost context,
  and merge burden in the recommendation.

## Session inspection routing

Keep conversation discovery, invocation confirmation, privacy minimization,
version provenance, and causal classification inline with the parent reviewer.
They depend on the current project boundary and user authority, and separating
them can leak private context or turn an incidental match into a false finding.

Use only an already available project-scoped session reader. `trellis mem` is
one suitable example when the repository already provides it; never install,
enable, authenticate, or reconfigure a history provider for the review. Do not
substitute a global session search, plugin-cache crawl, or raw home-directory
scan. Provider absence or incomplete indexing is a coverage limit, not a reason
to broaden discovery.

Never pass raw sessions to a subagent. When an independent validator needs to
test a session-derived claim, give it only the current canonical skill artifact,
the user-shaped request, and a minimized evidence record with redacted behavior,
outcome, provenance, and causal hypothesis. The parent retains session locators,
verifies the evidence, and owns the final classification.

Claude Code documents that `context: fork` runs the skill in a subagent without
the current conversation history, so use it only for task-shaped instructions
whose bounded prompt is self-sufficient. Its current skill frontmatter also
supports host-specific model, effort, agent, invocation, path, and shell
controls; do not assume those fields are portable.

## Subagent decomposition

Delegate only an independently verifiable unit. Useful roles include:

- inventory one repository or declared family;
- compare one sibling cluster for overlap;
- validate one target adapter against the neutral template;
- challenge a proposed deletion against the capability ledger; or
- forward-test one raw skill artifact and user request.

Give each role the smallest complete source set, explicit exclusions, authority
boundary, expected artifact, and stop condition. Cap concurrency to the host and
task budget, prohibit recursive spawning, and keep task creation or edits with
the parent unless separately authorized. The parent verifies evidence,
deduplicates overlaps, resolves conflicts, and owns the final report.

For independent validation, pass raw skill artifacts and the user-shaped
request, but never raw sessions. Do not pass suspected defects, expected
findings, intended fixes, or the primary reviewer's conclusion unless the
validation is explicitly testing that claim.

## Model profiles

- `inherit` — approval-heavy or context-dependent orchestration where changing
  models adds no clear value.
- `fast` — deterministic discovery, metadata extraction, classification, and
  low-risk parity checks with a strict output schema.
- `balanced` — ordinary semantic review, bounded implementation, and synthesis.
- `deep` — ambiguous cross-skill ownership, safety or authority analysis,
  deletion risk, adversarial review, and multi-repository synthesis.

Use the lowest profile that preserves quality. Exact model identifiers are
host overrides only after availability is observed. Never put an assumed model
name in portable canonical frontmatter.

## First-party target contracts

### SE package

The current registry targets shared agent directories, Claude Code, and Codex.
They share one authored canonical `templates/skills/**` body. The pack applies
reviewed invocation, fork, model, and effort choices through generated Claude
frontmatter overlays; the review inventory maps those generated installed
bytes back to the authored canonical source. Codex `agents/openai.yaml` remains
a recommendation because it is UI metadata rather than a model or context
execution control. Shared-agent and Codex skills retain portable frontmatter.
Gemini and OpenCode agent adapters are separate package work because neither is
an SE installation target and both express model and isolation choices through
agent definitions rather than skill frontmatter.

### SD package

Review only `templates/**`. Treat `templates/.agents/skills/**` and
`templates/.commands/**` as authored neutral sources. Treat generated Claude,
Gemini, GitHub, and other adapter templates as target-validation surfaces whose
behavior normally changes through the neutral template and generator. Validate
argument, command-format, and body parity; Gemini TOML is not equivalent to a
Markdown command file.

## Optional Codex peer review in Claude Code

When Claude Code already exposes the official Codex plugin and it is callable,
authenticated, and suitable, use its read-only review or adversarial-review
path for a concrete diff or bounded artifact. A fresh delegated run is useful
when independence matters. Never install, enable, authenticate, or configure
the plugin. Treat its output as evidence to verify and fall back to a native
isolated pass when unavailable.

Record provider, observed model or portable profile, scope, and coverage. The
optional peer review never blocks the baseline workflow.

## Verification sources

- Claude Code skills: https://code.claude.com/docs/en/slash-commands
- Claude Code subagents: https://code.claude.com/docs/en/sub-agents
- OpenAI Codex plugin for Claude Code:
  https://github.com/openai/codex-plugin-cc/blob/main/README.md
