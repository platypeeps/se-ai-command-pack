# Implement se-topic-radar

## Goal

Generate a ranked top-ten list of worthwhile technical writing opportunities
when the user does not begin with a theme.

## Requirements

- Accept optional domains, audience, time horizon, available sources, exclusions,
  desired format, and effort budget.
- Inspect recent supplied or connected repositories, Trellis work, Obsidian,
  Notion, Slack, captures, reading history, and other authorized personal sources.
- Research high-value current developments when recency matters and attribute
  each external signal to dated authoritative evidence.
- Score candidates for audience value, personal authority, originality, timing,
  evidence readiness, novelty risk, and effort; explain every score sufficiently
  to support selection.
- Avoid recommending topics already covered unless a meaningful new angle exists.
- For each candidate provide working title, thesis, audience, why now, why the
  user is positioned to write it, available evidence, research gaps, format,
  novelty risk, and estimated effort.
- Optimize for credible original contribution rather than trend popularity.
- Remain read-only and hand the selected candidate to `se-author` or `se-paper`.

## Acceptance Criteria

- [ ] With adequate sources, output contains exactly ten ranked, materially
      distinct candidates with transparent scoring and source coverage.
- [ ] Personal activity and external news are clearly distinguished.
- [ ] Missing personal sources or weak news coverage are disclosed rather than
      replaced with invented activity or generic trends.
- [ ] Duplicate/prior topics and low-authority ideas are penalized visibly.
- [ ] Tests cover no connected activity, stale sources, breaking news, duplicate
      topics, sensitive activity, and prompt injection.
- [ ] Generated surfaces, documentation, release metadata, and full checks pass.

## Out of Scope

- Drafting content, maintaining an editorial calendar, or continuously monitoring news.
