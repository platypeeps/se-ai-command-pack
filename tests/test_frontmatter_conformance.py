"""Bind the shipped frontmatter parser to the grammar the generator authorizes.

`.github/scripts/generate-skill-surfaces.py` is the authority: it parses skill
frontmatter with `yaml.safe_load` and emits it with `yaml.safe_dump`. The
bundled `skill_review.py` is stdlib-first and cannot ship PyYAML, so it
hand-parses the same block as a strict *rejecting* subset — for every document
it accepts it must return what `yaml.safe_load` returns, and anything outside
the subset must raise instead of being reinterpreted.

Importing PyYAML here is deliberate and dev-only: pinning the shipped parser to
the reference implementation is the whole point of the module.

Six groups, and the split carries meaning. Group 1 passes against the parser
this test was written for *and* against its predecessor — the live corpus
exercises none of the divergences — so it is a regression guard, not evidence
the subset is correct. Groups 2, 3, 5, and 6 are the ones that bite.
"""

from __future__ import annotations

import importlib.util
import itertools
import subprocess
import sys
import unicodedata
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

import yaml
from install_test_support import PACK_ROOT, TempDirTestCase, git_env

from installer.registry import SKILL_NAMES, SKILL_RUNTIME_PROFILES

REVIEW_PATH = (
    PACK_ROOT
    / "templates"
    / "skills"
    / "se-review-skills"
    / "scripts"
    / "skill_review.py"
)
GENERATOR_PATH = PACK_ROOT / ".github" / "scripts" / "generate-skill-surfaces.py"


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


review = _load("skill_review", REVIEW_PATH)
gen = _load("generate_skill_surfaces", GENERATOR_PATH)


def scalar_text(value: object) -> str:
    """Normalize one `yaml.safe_load` scalar the way the subset represents it.

    The subset's value domain is exactly `str`, `bool`, and `None`; every other
    resolution names a construct it refuses, so reaching the final branch means
    the parser accepted something it should have rejected.
    """

    if isinstance(value, str):
        return value
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return ""
    raise AssertionError(f"outside the subset's scalar domain: {value!r}")


def reference(block: str) -> dict[str, str]:
    """What the authority makes of one frontmatter block."""

    loaded = yaml.safe_load(block)
    assert isinstance(loaded, dict), f"not a mapping: {loaded!r}"
    return {key: scalar_text(value) for key, value in loaded.items()}


def split_frontmatter(text: str) -> str:
    """The raw block between the delimiters, sliced as `_frontmatter` slices it."""

    assert text.startswith("---\n")
    end = text.find("\n---\n", 4)
    assert end != -1
    return text[4 : end + 1]


def document(*lines: str) -> str:
    return "---\n" + "".join(f"{line}\n" for line in lines) + "---\nBody.\n"


FIXTURE_SKILL = """---
name: se-fixture
{description_line}
---

# Fixture Skill

Intro paragraph.

## When to use

Text.

## Arguments

Text.

## Workflow

Text.

## Safety rules

Text.

## Final report

Text.
"""


def tracked_skill_documents() -> list[Path]:
    """Every tracked SKILL.md, enumerated from the tree rather than listed.

    Deriving the corpus from `git ls-files` is what keeps the test honest on a
    fresh clone: a hand-written path list keeps passing after a file it names is
    deleted. `-z` matters because a tracked path in this repo contains a space.

    The set is `SKILL.md` and nothing wider. `_safe_pack_skill_source` refuses
    every other basename, so agent overlays are unreachable by this parser and
    binding them here would fail on their legitimate list-valued `tools`.
    """

    result = subprocess.run(
        ["git", "-C", str(PACK_ROOT), "ls-files", "-z", "--", "*SKILL.md"],
        capture_output=True,
        text=True,
        check=True,
        env=git_env(),
    )
    return [
        PACK_ROOT / name
        for name in result.stdout.split("\0")
        if name.endswith("SKILL.md")
    ]


class CorpusRegressionTests(unittest.TestCase):
    """Group 1 — every tracked SKILL.md parses identically under both grammars."""

    def test_tracked_skill_documents_agree_with_pyyaml(self) -> None:
        documents = tracked_skill_documents()
        booleans = 0
        double_quoted = 0
        without_frontmatter: list[str] = []

        for path in documents:
            label = path.relative_to(PACK_ROOT).as_posix()
            with self.subTest(document=label):
                text = path.read_text(encoding="utf-8")
                if not text.startswith("---\n"):
                    # Counted and reported, never silently skipped: a document
                    # that stops carrying frontmatter has to surface somewhere.
                    without_frontmatter.append(label)
                    continue
                block = split_frontmatter(text)
                loaded = yaml.safe_load(block)
                self.assertIsInstance(loaded, dict)
                values, _, keys = review._frontmatter(text, label)
                self.assertEqual(values, reference(block))
                self.assertEqual(list(keys), list(loaded))
                booleans += sum(
                    1 for value in loaded.values() if isinstance(value, bool)
                )
                double_quoted += sum(
                    1 for line in block.splitlines() if ': "' in line
                )

        self.assertEqual(without_frontmatter, [])
        # Vacuity guards. An enumeration that quietly matched nothing would
        # otherwise pass this group forever. Today: 180 documents, 14 boolean
        # values, 29 double-quoted values.
        self.assertGreaterEqual(len(documents), 150)
        self.assertGreaterEqual(booleans, 1)
        self.assertGreaterEqual(double_quoted, 1)


class AgreementTableTests(unittest.TestCase):
    """Group 2 — documents inside the subset where the old parser diverged."""

    CASES = (
        ("single-quoted escape", "description: 'a: b''s'"),
        ("double-quoted colon", "description: \"a: b\""),
        ("empty value", "description:"),
        ("boolean true", "disable-model-invocation: true"),
        ("boolean false", "disable-model-invocation: false"),
        ("single-quoted hash", "description: 'a # b'"),
        ("plain apostrophe", "description: Use when it's needed"),
        ("unicode", "description: Use when é appears"),
    )

    def test_accepted_documents_match_pyyaml(self) -> None:
        for name, line in self.CASES:
            with self.subTest(case=name):
                text = document("name: se-fixture", line)
                values, _, _ = review._frontmatter(text, "fixture")
                self.assertEqual(values, reference(split_frontmatter(text)))

    def test_key_order_is_preserved(self) -> None:
        text = document("description: Use when order matters", "name: se-fixture")
        _, _, keys = review._frontmatter(text, "fixture")
        self.assertEqual(keys, ("description", "name"))


class RejectionTableTests(unittest.TestCase):
    """Group 3 — one case per rejection the grammar owes, with its message."""

    CASES = (
        ("indented line", "indented line", ("name: a", "  child: b")),
        ("no colon", "line without a mapping colon", ("name",)),
        ("no space after colon", "mapping colon without a following space", ("name:a",)),
        ("empty key", "empty key", (": value",)),
        ("flow sequence", "value opening with a YAML indicator", ("tools: [Read]",)),
        ("flow mapping", "value opening with a YAML indicator", ("tools: {a: b}",)),
        ("block literal", "value opening with a YAML indicator", ("description: |",)),
        ("block folded", "value opening with a YAML indicator", ("description: >",)),
        ("anchor value", "value opening with a YAML indicator", ("name: &anchor",)),
        ("alias value", "value opening with a YAML indicator", ("name: *anchor",)),
        ("bare dash", "value opening with a YAML indicator", ("name: -",)),
        ("bare question", "value opening with a YAML indicator", ("name: ?",)),
        ("at sign", "value opening with a YAML indicator", ("name: @reserved",)),
        ("percent", "value opening with a YAML indicator", ("name: %reserved",)),
        ("backtick", "value opening with a YAML indicator", ("name: `reserved",)),
        ("comma", "value opening with a YAML indicator", ("name: ,leading",)),
        ("hash value", "value opening with a YAML indicator", ("name: #comment",)),
        ("trailing colon", "colon in a plain scalar", ("name: value:",)),
        ("interior colon", "colon in a plain scalar", ("name: a: b",)),
        ("plain comment", "comment in a plain scalar", ("name: value # c",)),
        ("yaml 1.1 yes", "value that YAML resolves to a non-string", ("name: yes",)),
        ("yaml 1.1 off", "value that YAML resolves to a non-string", ("name: off",)),
        ("null tilde", "value that YAML resolves to a non-string", ("name: ~",)),
        ("null word", "value that YAML resolves to a non-string", ("name: null",)),
        ("octal", "value that YAML resolves to a non-string", ("name: 010",)),
        ("float", "value that YAML resolves to a non-string", ("name: 1.0",)),
        ("date", "value that YAML resolves to a non-string", ("name: 2026-08-10",)),
        ("quoted key", "key opening with a YAML indicator", ("'name': a",)),
        ("anchored key", "key opening with a YAML indicator", ("&k name: a",)),
        ("sequence key", "key opening with a YAML indicator", ("- name: a",)),
        ("boolean key", "key that YAML resolves to a non-string", ("true: a",)),
        ("octal key", "key that YAML resolves to a non-string", ("010: a",)),
        ("date key", "key that YAML resolves to a non-string", ("2026-08-10: a",)),
        ("merge key", "key that YAML resolves to a non-string", ("<<: a",)),
        ("duplicate key", "duplicate key", ("name: a", "name: b")),
        ("unterminated single", "unterminated quoted scalar", ("name: 'a",)),
        ("unterminated double", "unterminated quoted scalar", ('name: "a',)),
        ("trailing content", "content after a closing quote", ("name: 'a' junk",)),
        (
            "double-quoted escape",
            "escape sequence in a double-quoted scalar",
            ('name: "a\\tb"',),
        ),
    )

    def test_each_rejection_names_its_construct_and_line(self) -> None:
        for name, construct, lines in self.CASES:
            with self.subTest(case=name):
                text = document(*lines)
                with self.assertRaises(review.ReviewError) as caught:
                    review._frontmatter(text, "fixture")
                message = str(caught.exception)
                self.assertIn(construct, message)
                self.assertTrue(
                    message.startswith(f"fixture:{len(lines)}:"),
                    f"{message!r} must name line {len(lines)}",
                )

    def test_control_characters_are_rejected(self) -> None:
        for code in (0x00, 0x09, 0x0D, 0x1B, 0x7F):
            with self.subTest(code=hex(code)):
                text = document(f"description: a{chr(code)}b")
                with self.assertRaises(review.ReviewError) as caught:
                    review._frontmatter(text, "fixture")
                self.assertIn("control character", str(caught.exception))

    def test_control_character_names_its_own_line(self) -> None:
        """The character is invisible; the line number is the whole diagnostic."""

        text = document("name: se-fixture", "description: a\tb")
        with self.assertRaises(review.ReviewError) as caught:
            review._frontmatter(text, "fixture")
        self.assertTrue(
            str(caught.exception).startswith("fixture:2:"), str(caught.exception)
        )

    def test_missing_delimiters_are_rejected(self) -> None:
        with self.assertRaises(review.ReviewError):
            review._frontmatter("name: a\n---\nBody.\n", "fixture")
        with self.assertRaises(review.ReviewError):
            review._frontmatter("---\nname: a\nBody.\n", "fixture")

    def test_no_break_space_survives_the_trim(self) -> None:
        """`strip()` would eat U+00A0; YAML keeps it. `strip(" ")` must too."""

        text = document("description: \u00a0kept")
        values, _, _ = review._frontmatter(text, "fixture")
        self.assertEqual(values, reference(split_frontmatter(text)))
        self.assertEqual(values["description"], "\u00a0kept")


class GeneratorReciprocityTests(TempDirTestCase):
    """Group 4 — what the authority emits, the subset must be able to read."""

    def test_every_rendered_claude_overlay_parses_and_agrees(self) -> None:
        """4a — the shipped snapshot round-trips through both grammars."""

        for name in SKILL_NAMES:
            with self.subTest(skill=name):
                canonical = (gen.SKILLS_ROOT / name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                rendered = gen.render_claude_skill(
                    name, canonical, SKILL_RUNTIME_PROFILES[name]
                )
                block = split_frontmatter(rendered)
                values, _, keys = review._frontmatter(rendered, f"generated/{name}")
                self.assertEqual(values, reference(block))
                self.assertEqual(list(keys), list(yaml.safe_load(block)))

    def _fixture_root(self, description_line: str) -> Path:
        root = self.base / "skills"
        skill = root / "se-fixture" / "SKILL.md"
        skill.parent.mkdir(parents=True, exist_ok=True)
        skill.write_text(
            FIXTURE_SKILL.format(description_line=description_line), encoding="utf-8"
        )
        return root

    def _validate(self, description_line: str) -> list[str]:
        root = self._fixture_root(description_line)
        with mock.patch.object(gen, "SKILLS_ROOT", root):
            errors, _ = gen.validate_skill("se-fixture")
        return errors

    def test_unrenderable_descriptions_are_refused(self) -> None:
        """4b - must reject.

        `yaml.safe_dump` escapes a control character into a double-quoted scalar
        and folds U+2028/U+2029 onto a real continuation line. Both land outside
        the subset, so the authority has to refuse them before emitting. U+2029
        is not decoration: a guard covering only U+2028 passes a one-case test
        and still generates an overlay the shipped parser cannot read.

        The fixtures are double-quoted with YAML escapes, which is how such a
        character reaches a description in practice. A raw one would be stopped
        a step earlier by PyYAML's own reader, and stopping it there would prove
        nothing about this guard.
        """

        for label, escape in (
            ("tab", "\\t"),
            ("nul", "\\0"),
            ("escape", "\\e"),
            ("line separator", "\\u2028"),
            ("paragraph separator", "\\u2029"),
        ):
            with self.subTest(character=label):
                line = f'description: "Use when alpha{escape}omega"'
                errors = self._validate(line)
                self.assertTrue(
                    any("must not contain" in error for error in errors),
                    f"{label} was accepted: {errors}",
                )

    def test_ordinary_punctuation_still_round_trips(self) -> None:
        """4c - must accept.

        Without this half, "either the validator rejects it or the parser
        agrees" is satisfied by a validator that refuses everything.
        """

        for label, line, expected in (
            ("apostrophe", "description: Use when it's time", "Use when it's time"),
            (
                "colon space",
                "description: 'Use when alpha: omega applies'",
                "Use when alpha: omega applies",
            ),
            (
                "hash",
                "description: 'Use when tag #1 applies'",
                "Use when tag #1 applies",
            ),
            (
                "unicode",
                "description: Use when \u00e9 appears",
                "Use when \u00e9 appears",
            ),
        ):
            with self.subTest(case=label):
                self.assertEqual(self._validate(line), [])
                root = self._fixture_root(line)
                canonical = (root / "se-fixture" / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                rendered = gen.render_claude_skill(
                    "se-fixture", canonical, SKILL_RUNTIME_PROFILES[SKILL_NAMES[0]]
                )
                values, _, _ = review._frontmatter(rendered, "fixture")
                self.assertEqual(values, reference(split_frontmatter(rendered)))
                self.assertEqual(values["description"], expected)


class InstalledRootTests(TempDirTestCase):
    """Group 5 — the operator's installed skills, which no enumeration reaches.

    `_discover_installed` globs runtime roots outside any repository, so a
    tracked-tree corpus is structurally blind to them. This fixture is the only
    coverage they get.
    """

    SECTIONS = "\n".join(f"{section}\n\nText.\n" for section in gen.REQUIRED_SECTIONS)

    def _installed_root(self, lines: tuple[str, ...]) -> Path:
        root = self.base / "runtime" / "skills"
        skill = root / "external" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text(document(*lines) + self.SECTIONS, encoding="utf-8")
        return root

    def _pack_root(self) -> Path:
        root = self.base / "pack"
        skill = root / "templates" / "skills" / "se-test" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text(
            document(
                "name: se-test",
                "description: Use when the fixture pack needs a skill.",
            )
            + self.SECTIONS,
            encoding="utf-8",
        )
        return root

    def _inventory(self, installed_root: Path) -> dict[str, Any]:
        return review.build_inventory(
            self._pack_root(),
            [],
            None,
            "package",
            root_was_explicit=True,
            installed_mode="auto",
            installed_roots=[installed_root],
        )

    def test_accepted_installed_skill_produces_a_record(self) -> None:
        root = self._installed_root(
            ("name: external", "description: Use when an installed skill is reviewed.")
        )
        payload = self._inventory(root)
        names = {skill["name"] for skill in payload["skills"]}
        self.assertIn("external", names)

    def test_rejected_installed_skill_names_the_file(self) -> None:
        root = self._installed_root(("name: external", "tools: [Read]"))
        with self.assertRaises(review.ReviewError) as caught:
            self._inventory(root)
        message = str(caught.exception)
        self.assertIn("SKILL.md", message)
        self.assertIn("value opening with a YAML indicator", message)


class ProductFuzzTests(unittest.TestCase):
    """Group 6 — the Cartesian sweep that found the NBSP and NUL holes.

    A later "simplification" of the parser cannot quietly reintroduce them while
    this group runs: every accepted document must equal `yaml.safe_load` under
    `scalar_text`, and every rejected one must be a document PyYAML would itself
    have failed or resolved differently.
    """

    KEYS = (
        "name",
        "description",
        "disable-model-invocation",
        "a#b",
        "<<",
        "true",
        "010",
        "2026-08-10",
        "a b",
        "&k n",
        "- n",
        "n ",
        "",
    )
    VALUES = (
        "",
        "plain",
        "true",
        "false",
        "yes",
        "null",
        "~",
        "010",
        "1.0",
        "2026-08-10",
        "'quoted'",
        "'it''s'",
        "'a: b'",
        '"dq"',
        '"a: b"',
        '"a\\tb"',
        "'unterminated",
        '"unterminated',
        "'a' junk",
        "[a, b]",
        "{a: b}",
        "|",
        ">",
        "- seq",
        "? ex",
        "@at",
        "%pct",
        ",comma",
        "`tick",
        "#hash",
        "has # hash",
        "trailing:",
        "mid: dle",
        "para graph",
        "éaccent",
        "\u00a0nbsp",
    )
    # The planning prototype's baseline. A run that accepts materially more or
    # fewer means the parser drifted from the design, not that the fuzz is
    # wrong — reconcile against design.md before touching these numbers.
    EXPECTED_CASES = 468
    EXPECTED_ACCEPTED = 72

    @staticmethod
    def _line(key: str, value: str) -> str:
        if not value:
            return f"{key}:"
        if value.startswith(" "):
            return f"{key}:{value}"
        return f"{key}: {value}"

    def test_accepted_documents_never_diverge_from_pyyaml(self) -> None:
        accepted = 0
        cases = 0
        for key, value in itertools.product(self.KEYS, self.VALUES):
            cases += 1
            line = self._line(key, value)
            text = document(line)
            with self.subTest(line=line):
                try:
                    values, _, _ = review._frontmatter(text, "fuzz")
                except review.ReviewError:
                    continue
                accepted += 1
                self.assertEqual(values, reference(line + "\n"))

        self.assertEqual(cases, self.EXPECTED_CASES)
        self.assertEqual(accepted, self.EXPECTED_ACCEPTED)

    def test_control_and_separator_sweep(self) -> None:
        swept = 0
        for code in (*range(0x00, 0x20), 0x7F, 0x85, 0x2028, 0x2029):
            character = chr(code)
            if unicodedata.category(character) not in {"Cc", "Zl", "Zp", "Cf"}:
                continue
            swept += 1
            text = document(f"description: plain{character}text")
            with self.subTest(code=hex(code)):
                try:
                    values, _, _ = review._frontmatter(text, "fuzz")
                except review.ReviewError:
                    continue
                # Anything the parser still accepts must survive the authority
                # unchanged; a control character that reaches here would not.
                self.assertEqual(
                    values, reference(f"description: plain{character}text\n")
                )
        self.assertGreaterEqual(swept, 33)
