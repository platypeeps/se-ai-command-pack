"""Content pins for the canonical skills: conventions and safety anchors."""

from __future__ import annotations

import unittest
from unittest import mock

import yaml
from install_test_support import PACK_ROOT

from installer.registry import (
    FAMILY_LABELS,
    SHARED_REFERENCES,
    SKILL_NAMES,
    SKILLS,
    TEMPLATES_SKILLS_DIR,
    SkillInfo,
    validate_registry,
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
    "se-decide",
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


class SkillFamilyRegistryTest(unittest.TestCase):
    def test_family_labels_have_stable_outcome_order(self) -> None:
        self.assertEqual(
            list(FAMILY_LABELS.items()),
            [
                ("understand", "Understand"),
                ("decide", "Decide"),
                ("create", "Create"),
                ("coordinate", "Coordinate"),
                ("operate", "Operate"),
                ("improve", "Improve"),
            ],
        )

    def test_skill_names_are_derived_without_reordering(self) -> None:
        self.assertEqual(SKILL_NAMES, tuple(skill.name for skill in SKILLS))
        self.assertEqual(
            SKILL_NAMES,
            (
                "se-research",
                "se-brief",
                "se-meeting-prep",
                "se-scan",
                "se-digest",
                "se-decide",
            ),
        )
        self.assertEqual(
            {skill.name: skill.family for skill in SKILLS},
            {
                "se-research": "understand",
                "se-brief": "coordinate",
                "se-meeting-prep": "coordinate",
                "se-scan": "understand",
                "se-digest": "understand",
                "se-decide": "decide",
            },
        )

    def assert_invalid_skills(
        self, skills: tuple[SkillInfo, ...], fragment: str
    ) -> None:
        names = tuple(skill.name for skill in skills)
        with (
            mock.patch("installer.registry.SKILLS", skills),
            mock.patch("installer.registry.SKILL_NAMES", names),
            mock.patch("installer.registry.SHARED_REFERENCES", {}),
            self.assertRaises(RuntimeError) as caught,
        ):
            validate_registry()
        self.assertIn(fragment, str(caught.exception))

    def test_registry_rejects_unknown_family(self) -> None:
        self.assert_invalid_skills(
            (SkillInfo("se-test", "unknown"),), "unknown family"
        )

    def test_registry_rejects_empty_name_and_family(self) -> None:
        self.assert_invalid_skills((SkillInfo("", "understand"),), "empty name")
        self.assert_invalid_skills((SkillInfo("se-test", ""),), "empty family")

    def test_registry_rejects_duplicate_skill_membership(self) -> None:
        self.assert_invalid_skills(
            (
                SkillInfo("se-test", "understand"),
                SkillInfo("se-test", "decide"),
            ),
            "duplicate skill name",
        )

    def test_registry_preserves_prefix_validation(self) -> None:
        self.assert_invalid_skills(
            (SkillInfo("test", "understand"),), "missing se- prefix"
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

    def test_brief_is_read_only(self) -> None:
        self.assertIn("read-only", normalized("se-brief"))

    def test_decide_preserves_uncertainty_and_never_acts(self) -> None:
        text = normalized("se-decide").lower()
        self.assertIn("read-only", text)
        self.assertIn("unknown remains unknown", text)
        self.assertIn("do not invent weights, scores, or numeric precision", text)
        self.assertIn("strongest counterargument", text)
        self.assertIn("conditions would change the recommendation", text)

    def test_decide_has_explicit_sibling_boundaries(self) -> None:
        text = normalized("se-decide")
        for sibling in (
            "se-scan",
            "se-research",
            "se-digest",
            "se-compare",
            "se-plan",
        ):
            self.assertIn(f"`{sibling}`", text)

    def test_decide_final_report_contract(self) -> None:
        text = skill_text("se-decide")
        for field in (
            "**Decision**",
            "**Option comparison**",
            "**Tradeoffs**",
            "**Confidence**",
            "**Reversibility**",
            "**Missing evidence**",
            "**Next action**",
        ):
            self.assertIn(field, text)

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
