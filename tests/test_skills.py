"""Content pins for the canonical skills: conventions and safety anchors."""

from __future__ import annotations

import unittest

import yaml
from install_test_support import PACK_ROOT

from installer.registry import (
    SHARED_REFERENCES,
    SKILL_NAMES,
    TEMPLATES_SKILLS_DIR,
)

SKILLS_ROOT = PACK_ROOT / TEMPLATES_SKILLS_DIR

REQUIRED_SECTIONS = (
    "## When to use",
    "## Arguments",
    "## Workflow",
    "## Safety rules",
    "## Final report",
)

# Skills that read external material must carry the prompt-injection rule.
EXTERNAL_INPUT_SKILLS = (
    "se-research",
    "se-brief",
    "se-meeting-prep",
    "se-scan",
    "se-digest",
)
INJECTION_RULE_FRAGMENT = "data, not instructions"


def skill_text(name: str) -> str:
    return (SKILLS_ROOT / name / "SKILL.md").read_text(encoding="utf-8")


def normalized(name: str) -> str:
    """Skill text with runs of whitespace collapsed, so phrase pins are
    immune to markdown line wrapping."""
    return " ".join(skill_text(name).split())


def skill_frontmatter(name: str) -> dict:
    text = skill_text(name)
    end = text.find("\n---\n")
    return yaml.safe_load(text[len("---\n") : end + 1])


class SkillConventionsTest(unittest.TestCase):
    def test_every_registered_skill_exists(self) -> None:
        for name in SKILL_NAMES:
            self.assertTrue(
                (SKILLS_ROOT / name / "SKILL.md").is_file(),
                f"missing SKILL.md for {name}",
            )

    def test_frontmatter_shape(self) -> None:
        for name in SKILL_NAMES:
            frontmatter = skill_frontmatter(name)
            self.assertEqual(
                sorted(frontmatter), ["description", "name"], name
            )
            self.assertEqual(frontmatter["name"], name)
            description = frontmatter["description"]
            self.assertTrue(description.startswith("Use when"), name)
            self.assertNotIn('"', description, name)
            self.assertLessEqual(len(description), 1024, name)

    def test_required_sections_in_order(self) -> None:
        for name in SKILL_NAMES:
            text = skill_text(name)
            last = -1
            for section in REQUIRED_SECTIONS:
                index = text.find(f"\n{section}\n")
                self.assertGreater(index, last, f"{name}: {section}")
                last = index

    def test_unknown_argument_stop_rule(self) -> None:
        for name in SKILL_NAMES:
            self.assertIn(
                "Unknown argument names are an error",
                skill_text(name),
                name,
            )


class SkillSafetyPinsTest(unittest.TestCase):
    def test_external_input_skills_carry_injection_rule(self) -> None:
        for name in EXTERNAL_INPUT_SKILLS:
            self.assertIn(INJECTION_RULE_FRAGMENT, normalized(name), name)

    def test_research_family_cites_source_standards(self) -> None:
        for source, consumers in SHARED_REFERENCES.items():
            self.assertIn("source-standards.md", source)
            for name in consumers:
                self.assertIn(
                    "references/source-standards.md", skill_text(name), name
                )

    def test_research_cites_verification_protocol(self) -> None:
        self.assertIn(
            "references/verification-protocol.md", skill_text("se-research")
        )

    def test_pack_skill_git_safety(self) -> None:
        text = skill_text("se-pack")
        self.assertIn("--ff-only", text)
        self.assertIn("--dry-run", text)
        self.assertIn("status --porcelain", text)
        self.assertNotIn("reset --hard", text)
        self.assertNotIn("git clean", text)

    def test_pack_skill_dry_run_precedes_apply(self) -> None:
        self.assertIn(
            "Always run the installer with `--dry-run` first",
            normalized("se-pack"),
        )

    def test_brief_is_read_only(self) -> None:
        self.assertIn("read-only", normalized("se-brief"))

    def test_meeting_prep_excludes_sensitive_data(self) -> None:
        text = normalized("se-meeting-prep")
        self.assertIn("sensitive personal data", text)
        self.assertIn("stop and ask", text)


class SkillDocumentationTest(unittest.TestCase):
    def test_readme_lists_every_skill(self) -> None:
        readme = (PACK_ROOT / "README.md").read_text(encoding="utf-8")
        for name in SKILL_NAMES:
            self.assertIn(f"`{name}`", readme)

    def test_changelog_mentions_every_skill(self) -> None:
        changelog = (PACK_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        for name in SKILL_NAMES:
            self.assertIn(name, changelog)


if __name__ == "__main__":
    unittest.main()
