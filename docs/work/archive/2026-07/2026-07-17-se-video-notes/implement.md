# Implement se-video-notes Implementation Plan

## Execution Order

1. Add synthetic metadata/transcript fixtures and failing coverage/timestamp tests.
2. Implement single-video full/partial transcript notes with provenance separation.
3. Add metadata-only fallback, compare mode, claim handoffs, and portable capture output.
4. Register under Understand, fan in source standards, add safety/docs/release, regenerate.
5. Run focused/full checks and inspect generated payloads.

## Validation Plan

- Unit/generator tests; `make generate`; `make check`; `git diff --check`.
- Manual full/partial/absent captions, offset mismatch, auto-caption error,
  long transcript, compare mode, and injected description.

## Documentation And Spec Updates

Document coverage states, timestamp fidelity, source-versus-analysis labels,
and capture/fact-check/knowledge-persistence handoffs.

## Review Notes

Trace every timestamp/quote to transcript data and confirm missing captions never
produce guessed content.

## Follow-Ups

Transcription/downloading and channel mutations remain separate integrations.
