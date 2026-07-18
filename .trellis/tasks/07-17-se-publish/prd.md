# Implement se-publish

## Goal

Transform an approved source artifact into a destination-appropriate draft while
preserving meaning, evidence, audience intent, and traceability.

## Requirements

- Require source artifact, audience, destination format, objective, and tone;
  make inferred choices visible.
- Support drafts for Slack canvas/message, Notion page, internal memo,
  announcement, briefing, and YouTube outline through capability-neutral output.
- Preserve load-bearing claims and citations; label omissions and adaptations.
- Never publish or send without an explicit destination write request and preview.
- Avoid duplicating `se-digest`: publish adapts an accepted artifact rather than
  discovering the synthesis itself.
- Provide channel-specific length, structure, and accessibility checks.

## Acceptance Criteria

- [ ] The draft identifies source, audience, objective, and material adaptations.
- [ ] Unsupported promotional claims cannot be introduced during transformation.
- [ ] Output supports preview and later connector-specific publication.
- [ ] Tests cover citation retention, tight length limits, sensitive content,
      destination mismatch, and read-only behavior.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Direct sending, social-media management, or image/video production.
