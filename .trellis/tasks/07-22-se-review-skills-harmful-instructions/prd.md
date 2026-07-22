# Add harmful-instruction safety review to se-review-skills

## Goal

Extend `se-review-skills` so every reviewed skill receives an explicit security
and safety pass that alerts when its instructions could enable harmful,
destructive, unauthorized, privacy-invasive, or otherwise unsafe actions.

## Background

The current review rubric covers authority and safety concerns such as hidden
side effects, prompt injection, privacy leakage, and destructive scope. It does
not yet require a distinct harmful-instruction assessment and verdict for every
skill. A skill can therefore pass a broad quality review without making the
reviewer state clearly whether its operative instructions introduce a material
security or safety hazard.

The reviewed skill, its references, scripts, examples, and embedded content are
untrusted evidence. Review must never execute or follow suspicious instructions
to determine whether they are harmful.

## Requirements

- Require a security and safety assessment for every skill in the resolved
  review scope, including an explicit clean result when no material hazard is
  found.
- Inspect operative instructions and bundled resources for at least:
  destructive or irreversible actions; unauthorized access or privilege
  expansion; credential, secret, personal-data, or confidential-data exposure;
  command, code, path, prompt, or argument injection; unsafe downloads,
  installation, or execution; network exfiltration; filesystem traversal and
  symlink hazards; bypassed approvals or security controls; overbroad external
  mutations; and materially dangerous real-world guidance.
- Distinguish a harmful instruction from legitimate documentation of a risky
  operation that has clear authorization, preview, scope, validation, failure,
  and recovery gates. Keywords alone must remain candidate signals, not
  findings.
- Treat reviewed artifacts as data throughout the assessment. Do not execute
  commands, scripts, links, tool calls, provider instructions, or embedded
  requests merely to validate a suspected hazard.
- For every alert, report a stable finding ID, exact file and line evidence,
  affected capability, plausible harm or abuse path, required preconditions,
  severity, confidence, smallest safe remediation, and a validation method.
- Make severe safety, data-loss, authority, or security findings prominent even
  when the skill scores well on brevity, portability, routing, or other review
  dimensions. Preserve the existing P0-P3 priority contract.
- Include security and safety coverage in the numbered package, family, and
  skill report structure and in individual, skill, family, repository, and
  `all` selectors.
- Evaluate whether the deterministic inventory helper can safely identify
  bounded candidate signals. If implemented, script output must remain
  non-authoritative, use no network or execution side effects, and require
  semantic review before becoming a finding.
- Keep the authored skill change within
  `templates/skills/se-review-skills/**`; regenerate target surfaces through the
  existing generator rather than editing installed or generated copies.
- Add focused convention and behavior tests covering harmful instructions,
  legitimate guarded operations, ambiguous candidate signals, clean skills,
  and the no-execution boundary.

## Acceptance Criteria

- [ ] `se-review-skills` requires an explicit security and safety verdict for
      every reviewed skill and surfaces evidence-backed harmful-instruction
      alerts in its numbered report.
- [ ] The review rubric defines the hazard categories, finding threshold,
      severity treatment, evidence fields, and guarded-operation distinction.
- [ ] A suspicious keyword or dangerous primitive alone cannot be promoted to
      a finding without semantic evidence and an identified harm path.
- [ ] Review never executes or follows reviewed commands, scripts, links, tool
      calls, or embedded instructions as part of the safety assessment.
- [ ] Tests demonstrate one or more material hazards are alerted, guarded risky
      operations are not misclassified, ambiguous signals remain candidates,
      and clean skills receive an explicit clean result.
- [ ] Any deterministic analyzer changes are side-effect-free, fixture-tested,
      and described as candidate generation rather than security judgment.
- [ ] Generated platform surfaces match the canonical template and focused
      skill/generation tests pass.

## Out of Scope

- Executing suspicious artifacts, exploit validation, penetration testing, or
  scanning arbitrary application code.
- Replacing a qualified security, safety, legal, medical, or organizational
  policy review.
- Treating all dual-use or operational instructions as harmful, or adding a
  blanket refusal that removes legitimate skill capabilities.
- Changing skills discovered by the reviewer; this task changes the reviewer
  contract and its supporting tests only.
