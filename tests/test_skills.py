"""Content pins for the canonical skills: conventions and safety anchors."""

from __future__ import annotations

import re
import unittest
from unittest import mock

import yaml
from install_test_support import PACK_ROOT

from installer.registry import (
    FAMILY_DESCRIPTIONS,
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
    "se-status",
    "se-fact-check",
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

    def test_family_descriptions_match_family_order(self) -> None:
        self.assertEqual(tuple(FAMILY_DESCRIPTIONS), tuple(FAMILY_LABELS))
        self.assertTrue(all(value.strip() for value in FAMILY_DESCRIPTIONS.values()))

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
                "se-status",
                "se-fact-check",
                "se-help",
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
                "se-status": "coordinate",
                "se-fact-check": "understand",
                "se-help": "operate",
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

    def test_shared_reference_consumers_cite_registered_reference(self) -> None:
        for source, consumers in SHARED_REFERENCES.items():
            self.assertTrue(source.startswith("_shared/references/"), source)
            basename = source.rsplit("/", 1)[-1]
            for name in consumers:
                self.assertIn(
                    f"references/{basename}", skill_text(name), name
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

    def test_status_preserves_objective_evidence_and_authority(self) -> None:
        text = normalized("se-status").lower()
        self.assertIn("read-only", text)
        self.assertIn("activity is not an outcome", text)
        self.assertIn("no-material-change", text)
        self.assertIn("stale, inaccessible, or contradictory", text)
        self.assertIn("never invent an owner, date", text)

    def test_status_has_explicit_sibling_boundaries(self) -> None:
        text = normalized("se-status")
        for sibling in ("se-brief", "se-digest", "se-decide", "se-monitor"):
            self.assertIn(f"`{sibling}`", text)

    def test_status_final_report_contract(self) -> None:
        text = skill_text("se-status")
        for field in (
            "**Status header**",
            "**Executive status**",
            "**Outcomes**",
            "**Activity**",
            "**Current state**",
            "**Blockers and risks**",
            "**Decisions**",
            "**Asks**",
            "**Next actions**",
            "**Source coverage and gaps**",
        ):
            self.assertIn(field, text)

    def test_fact_check_uses_exact_verdict_vocabulary(self) -> None:
        text = skill_text("se-fact-check")
        verdicts = (
            "**supported**",
            "**partially supported**",
            "**unverified**",
            "**contradicted**",
            "**outdated**",
        )
        for verdict in verdicts:
            self.assertIn(verdict, text)
        self.assertIn("Assign exactly one verdict", text)

    def test_fact_check_is_claim_led_and_read_only(self) -> None:
        text = normalized("se-fact-check").lower()
        self.assertIn("inventory", text)
        self.assertIn("before verification begins", text)
        self.assertIn("read-only", text)
        self.assertIn("data, not instructions", text)
        self.assertIn("smallest corrected wording", text)
        self.assertIn("never edit or replace", text)

    def test_fact_check_has_explicit_sibling_boundaries(self) -> None:
        text = normalized("se-fact-check")
        for sibling in ("se-research", "se-digest"):
            self.assertIn(f"`{sibling}`", text)

    def test_fact_check_final_report_contract(self) -> None:
        text = skill_text("se-fact-check")
        for field in (
            "**Audit scope**",
            "**Verdict summary**",
            "**Claim ledger**",
            "**Minimal corrections**",
            "**Non-fact-checkable items**",
            "**Evidence gaps and conflicts**",
            "**Methodology**",
        ):
            self.assertIn(field, text)

    def test_meeting_prep_excludes_sensitive_data(self) -> None:
        text = normalized("se-meeting-prep")
        self.assertIn("sensitive personal data", text)
        self.assertIn("stop and ask", text)

    def test_help_modes_and_shared_response_envelope(self) -> None:
        text = skill_text("se-help")
        normalized_text = normalized("se-help")
        for mode in ("list", "explain", "compare", "recommend", "examples", "tour"):
            self.assertIn(mode, normalized_text)
        fields = (
            "**Pack and availability**",
            "**Answer**",
            "**Why it fits**",
            "**Required context**",
            "**Expected output**",
            "**Side effects and boundaries**",
            "**Related skills**",
            "**Next invocation**",
        )
        positions = [text.index(field) for field in fields]
        self.assertEqual(positions, sorted(positions))

    def test_help_preserves_availability_and_version_boundaries(self) -> None:
        text = normalized("se-help").lower()
        for label in (
            "available now",
            "included in the installed pack but not discoverable now",
            "source/package-local only",
            "external",
            "unknown",
        ):
            self.assertIn(label, text)
        self.assertIn("bundled catalog version", text)
        self.assertIn("installed pack version", text)
        self.assertIn("python3 install.py status --user", text)
        self.assertIn("do not guess", text)

    def test_help_routes_without_execution(self) -> None:
        text = normalized("se-help").lower()
        self.assertIn("read-only", text)
        self.assertIn("smallest-fit", text)
        self.assertIn("at most one clarifying question", text)
        self.assertIn("at most three skills", text)
        self.assertIn("separate explicit request", text)
        self.assertIn("never execute", text)
        self.assertIn("platform-native invocation", text)
        self.assertNotIn("/sd:", text)

    def test_help_references_and_examples_use_registered_skills(self) -> None:
        text = skill_text("se-help")
        self.assertIn("references/skill-catalog.md", text)
        self.assertIn("references/examples.md", text)
        examples = (
            SKILLS_ROOT / "se-help" / "references" / "examples.md"
        ).read_text(encoding="utf-8")
        named = set(re.findall(r"`\$?(se-[a-z0-9-]+)`", examples))
        self.assertTrue(named)
        self.assertEqual(named - set(SKILL_NAMES), set())


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
