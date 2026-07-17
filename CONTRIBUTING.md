# Contributing

## Workflow

1. Branch from `main`; open a PR for every change.
2. Edit canonical skills under `templates/skills/`, never the generated
   `manifest.json` rows by hand.
3. Run `make generate` after any skill or registry change so the manifest
   stays in sync (`make release-check` verifies this).
4. Run `make check` (tests, lint, release gates) before requesting review.

## Release discipline

Any change to the shipped payload (`templates/**` or `manifest.json`) must:

- bump `version` in `manifest.json`, and
- add a matching top heading to `CHANGELOG.md` in the form
  `## <version> - YYYY-MM-DD`.

CI enforces this via the release payload gate. Merges to `main` are tagged
`v<version>` automatically when the version changes.

## Dogfooding

`make sync` installs the pack into your own home directory (`install.py
--user`) so the skills you are editing are the skills you use.
