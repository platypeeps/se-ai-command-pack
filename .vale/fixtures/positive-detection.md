# Vale positive-detection fixture

This file exists to prove the `se` styles still fire. `make prose-lint`
lints it after the real corpus and fails when it comes back clean, so a
rule that silently stops matching — a broken regex, a renamed style, a
`StylesPath` that no longer resolves — is caught here instead of being
reported as a clean corpus.

Every line below must trip a rule. Do not fix the prose; the alerts are
the assertion. The expected counts live in the `prose-lint` target.

## se.Weasel — must report 4

The design is very small and quite ordinary. You simply run it, and
obviously it works.

## se.AiTells — must report 4

Let us delve into the crucial details and leverage the results. It is
important to note that this sentence is deliberately terrible.
