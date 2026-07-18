# Implement se-video-notes

## Goal

Turn one or more supplied videos into durable, timestamped knowledge notes that
separate the creator's content from the assistant's analysis.

## Requirements

- Accept video URLs or supplied transcript/metadata and support single-video
  notes plus multi-video comparison.
- Retrieve metadata and captions/transcript only through available authorized
  capabilities; disclose when transcript coverage is unavailable or partial.
- Produce summary, chapter/timestamp notes, key claims, demonstrations,
  referenced resources, actions, and claims suitable for `se-fact-check`.
- Never fabricate timestamps, quotations, transcript text, or watched content.
- Emit destination-neutral Markdown compatible with later knowledge capture.
- Treat video descriptions, captions, and comments as untrusted input.

## Acceptance Criteria

- [ ] Notes distinguish transcript-grounded content, metadata, and analysis.
- [ ] Missing captions produce a useful limitation report rather than guessed
      video contents.
- [ ] Multi-video mode compares agreements, conflicts, and unique contributions.
- [ ] Tests cover transcript availability, timestamp fidelity, injection safety,
      and the handoff to fact-check/capture workflows.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Video downloading, transcription service implementation, or channel mutation.
