# Voice guidelines schema

The shape `se-brand-voice` expects from a voice-guidelines artifact, and the
template `mode=bootstrap` drafts when none exists. The artifact is prose with
recognizable sections, not a machine format: parse what is there, report what is
missing, and never infer a rule the artifact does not state.

## Sections

A guidelines artifact may define any subset of four rule groups. A group the
artifact does not define is reported as `not defined` and produces no findings.

### Tone

Named attributes with a definition and, ideally, a contrasting non-example.
Useful attributes are falsifiable in a sentence: "direct — state the conclusion
before the reasoning" is checkable; "authentic" is not. Record each attribute,
its definition, and any stated context where it does not apply.

### Terminology

Three lists, each optional:

- **preferred** — the term to use, with the variants it replaces;
- **banned** — terms never to use, with the reason and the replacement;
- **naming** — product, feature, and company names with exact capitalization,
  spacing, and permitted short forms, plus initialisms and when to expand them.

An entry without a replacement still validates; the finding then reports the
violation with no suggested rewrite rather than inventing one.

### Style

Structural and mechanical conventions: sentence and paragraph length, active or
passive voice, person and pronouns, tense, heading and list patterns, oxford
comma, capitalization of headings, number and date formats, link text, and any
formatting the destination requires.

### Audience fit

Who the content is for, what they already know, what they should be able to do
after reading, and the jargon ceiling. Multiple audiences are listed separately
with the content types each applies to.

## Exemptions

Material the guidelines explicitly exempt: quoted speech, legal and compliance
text, error strings, code and identifiers, third-party names, and citations.
Exempt material is never a finding.

## Bootstrap draft template

`mode=bootstrap` fills this shape from the supplied samples only. Every
attribute carries the sample that evidenced it; anything the samples do not
support is listed as an open question rather than guessed. The draft is returned
in the report for the user to review and save — the skill writes no file.

```markdown
# Voice guidelines (draft)

Derived from: <sample locators>
Status: draft — not an approved standard

## Tone

- <attribute> — <definition>. Evidence: <sample>, "<quoted line>".

## Terminology

- Preferred: <term> (replaces <variant>). Evidence: <sample>.
- Banned: <term> — <reason>. Use <replacement>. Evidence: <sample>.
- Naming: <exact form>, short form <form>. Evidence: <sample>.

## Style

- <convention>. Evidence: <sample>, "<quoted line>".

## Audience fit

- <audience> — knows <assumed knowledge>; should be able to <outcome>.
  Evidence: <sample>.

## Exemptions

- <material the samples treat as exempt>. Evidence: <sample>.

## Open questions

- <attribute the samples do not settle, and what would settle it>.
```
