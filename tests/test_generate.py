"""Tests for the skill-surface generator: validation, regen, drift check."""

from __future__ import annotations

import importlib.util
import json
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest import mock

from install_test_support import PACK_ROOT, TempDirTestCase

GENERATOR_PATH = PACK_ROOT / ".github" / "scripts" / "generate-skill-surfaces.py"

spec = importlib.util.spec_from_file_location(
    "generate_skill_surfaces", GENERATOR_PATH
)
assert spec is not None and spec.loader is not None
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

VALID_SKILL = """---
name: {name}
description: Use when testing the generator fixture behavior end to end.
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


class RealRepoGeneratorTest(unittest.TestCase):
    def test_canonical_skills_validate(self) -> None:
        gen.validate_skills()

    def test_manifest_matches_generated(self) -> None:
        committed = (PACK_ROOT / "manifest.json").read_text(encoding="utf-8")
        self.assertEqual(committed, gen.regenerated_manifest_text())

    def test_manifest_description_matches_bootstrap_default(self) -> None:
        committed = json.loads(
            (PACK_ROOT / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            committed["description"],
            gen.DEFAULT_MANIFEST_HEADER["description"],
        )

    def test_readme_catalog_matches_generated(self) -> None:
        committed = (PACK_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertEqual(committed, gen.regenerated_readme_text())

    def test_help_catalog_matches_generated(self) -> None:
        committed = gen.HELP_CATALOG_PATH.read_text(encoding="utf-8")
        self.assertEqual(committed, gen.regenerated_help_catalog_text())

    def test_help_catalog_uses_version_family_order_and_frontmatter(self) -> None:
        rendered = gen.regenerated_help_catalog_text()
        manifest = json.loads((PACK_ROOT / "manifest.json").read_text("utf-8"))
        self.assertIn(f"Bundled pack version: `{manifest['version']}`", rendered)
        headings = [f"## {label}" for label in gen.FAMILY_LABELS.values()]
        for earlier, later in zip(headings, headings[1:], strict=False):
            self.assertLess(rendered.index(earlier), rendered.index(later))
        for family, description in gen.FAMILY_DESCRIPTIONS.items():
            self.assertIn(gen.FAMILY_LABELS[family], rendered)
            self.assertIn(description, rendered)
        self.assertIn(
            "Use when the user asks for deep, multi-source research",
            rendered,
        )
        self.assertIn("`se-help`", rendered)

    def test_readme_catalog_uses_family_order_and_frontmatter(self) -> None:
        rendered = gen.regenerated_readme_text()
        self.assertLess(rendered.index("### Understand"), rendered.index("### Decide"))
        self.assertLess(rendered.index("### Decide"), rendered.index("### Coordinate"))
        self.assertNotIn("### Create", rendered)
        self.assertIn("### Operate", rendered)
        self.assertNotIn("### Improve", rendered)
        self.assertIn(
            "Use when the user asks for deep, multi-source research",
            rendered,
        )
        self.assertIn(
            "Use when the user wants a defensible recommendation",
            rendered,
        )
        self.assertIn(
            "Use when the user wants an objective-oriented project status",
            rendered,
        )
        self.assertIn(
            "Use when the user supplies claims or a draft",
            rendered,
        )
        self.assertLess(rendered.index("`se-meeting-prep`"), rendered.index("`se-status`"))

    def test_check_mode_passes(self) -> None:
        self.assertEqual(gen.main(["--check"]), 0)

    def test_rows_cover_every_skill_and_platform(self) -> None:
        manifest = json.loads((PACK_ROOT / "manifest.json").read_text("utf-8"))
        rows = manifest["files"]
        for name in gen.SKILL_NAMES:
            for platform, info in gen.PLATFORM_REGISTRY.items():
                target = f"{info.skills_dir}/{name}/SKILL.md"
                matches = [row for row in rows if row["target"] == target]
                self.assertEqual(
                    len(matches), 1, f"expected one row for {target}"
                )
                self.assertEqual(matches[0]["platform"], platform)
                self.assertEqual(matches[0]["scope"], "user")
                self.assertEqual(matches[0]["anchor"], info.anchor)

    def test_shared_reference_fanned_into_consumers(self) -> None:
        manifest = json.loads((PACK_ROOT / "manifest.json").read_text("utf-8"))
        targets = {row["target"] for row in manifest["files"]}
        for source, consumers in gen.SHARED_REFERENCES.items():
            basename = Path(source).name
            for consumer in consumers:
                for info in gen.PLATFORM_REGISTRY.values():
                    self.assertIn(
                        f"{info.skills_dir}/{consumer}/references/{basename}",
                        targets,
                    )

    def test_help_catalog_reference_fans_into_help_only(self) -> None:
        source = "_shared/references/skill-catalog.md"
        self.assertEqual(gen.SHARED_REFERENCES[source], ("se-help",))
        manifest = json.loads((PACK_ROOT / "manifest.json").read_text("utf-8"))
        rows = manifest["files"]
        for platform, info in gen.PLATFORM_REGISTRY.items():
            target = f"{info.skills_dir}/se-help/references/skill-catalog.md"
            matches = [row for row in rows if row["target"] == target]
            self.assertEqual(len(matches), 1, (platform, target))
            self.assertEqual(
                matches[0]["source"],
                "templates/skills/_shared/references/skill-catalog.md",
            )

    def test_fact_check_installs_all_cited_shared_references(self) -> None:
        expected_sources = {
            "_shared/references/source-standards.md",
            "_shared/references/verification-protocol.md",
        }
        actual_sources = {
            source
            for source, consumers in gen.SHARED_REFERENCES.items()
            if "se-fact-check" in consumers
        }
        self.assertEqual(actual_sources, expected_sources)

    def test_verification_protocol_preserves_research_targets(self) -> None:
        source = "_shared/references/verification-protocol.md"
        self.assertEqual(
            gen.SHARED_REFERENCES[source],
            ("se-research", "se-fact-check"),
        )
        manifest = json.loads((PACK_ROOT / "manifest.json").read_text("utf-8"))
        rows = manifest["files"]
        for platform, info in gen.PLATFORM_REGISTRY.items():
            for consumer in ("se-research", "se-fact-check"):
                target = (
                    f"{info.skills_dir}/{consumer}/references/"
                    "verification-protocol.md"
                )
                matches = [row for row in rows if row["target"] == target]
                self.assertEqual(len(matches), 1, (platform, consumer))
                self.assertEqual(
                    matches[0]["source"],
                    "templates/skills/_shared/references/"
                    "verification-protocol.md",
                )


class SandboxGeneratorTest(TempDirTestCase):
    """Generator behavior against a synthetic skills tree."""

    def setUp(self) -> None:
        super().setUp()
        self.skills_root = self.base / "templates" / "skills"
        self.skills_root.mkdir(parents=True)
        self.manifest_path = self.base / "manifest.json"
        self.readme_path = self.base / "README.md"
        self.help_catalog_path = self.base / "skill-catalog.md"
        self.readme_path.write_text(
            "# Fixture\n\n## Skills\n\n"
            "<!-- SE_SKILL_CATALOG:START -->\n"
            "old catalog\n"
            "<!-- SE_SKILL_CATALOG:END -->\n\n"
            "Tail.\n",
            encoding="utf-8",
        )
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(
            mock.patch.object(gen, "SKILLS_ROOT", self.skills_root)
        )
        stack.enter_context(
            mock.patch.object(gen, "MANIFEST_PATH", self.manifest_path)
        )
        stack.enter_context(
            mock.patch.object(gen, "README_PATH", self.readme_path)
        )
        stack.enter_context(
            mock.patch.object(gen, "HELP_CATALOG_PATH", self.help_catalog_path)
        )
        stack.enter_context(
            mock.patch.object(
                gen,
                "FAMILY_LABELS",
                {"understand": "Understand", "decide": "Decide"},
            )
        )
        stack.enter_context(
            mock.patch.object(
                gen,
                "FAMILY_DESCRIPTIONS",
                {
                    "understand": "Understand fixture outcomes.",
                    "decide": "Decide fixture outcomes.",
                },
            )
        )
        stack.enter_context(
            mock.patch.object(
                gen,
                "SKILLS",
                (gen.SkillInfo(name="se-test", family="understand"),),
            )
        )
        stack.enter_context(
            mock.patch.object(gen, "SKILL_NAMES", ("se-test",))
        )
        stack.enter_context(mock.patch.object(gen, "SHARED_REFERENCES", {}))

    def write_skill(self, name: str = "se-test", text: str | None = None) -> Path:
        skill_dir = self.skills_root / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            text if text is not None else VALID_SKILL.format(name=name),
            encoding="utf-8",
        )
        return skill_md

    def assert_validation_error(self, fragment: str) -> None:
        with self.assertRaises(gen.GenerationError) as caught:
            gen.validate_skills()
        self.assertIn(fragment, str(caught.exception))

    def test_valid_fixture_passes(self) -> None:
        self.write_skill()
        gen.validate_skills()

    def test_missing_skill_dir(self) -> None:
        self.assert_validation_error("has no directory")

    def test_unregistered_skill_dir(self) -> None:
        self.write_skill()
        self.write_skill("se-rogue")
        self.assert_validation_error("not registered")

    def test_missing_frontmatter(self) -> None:
        self.write_skill(text="# No frontmatter\n")
        self.assert_validation_error("missing YAML frontmatter")

    def test_name_mismatch(self) -> None:
        self.write_skill(text=VALID_SKILL.format(name="se-other"))
        self.assert_validation_error("must equal the skill directory name")

    def test_description_prefix(self) -> None:
        text = VALID_SKILL.format(name="se-test").replace(
            "Use when testing", "For testing"
        )
        self.write_skill(text=text)
        self.assert_validation_error("must start with 'Use when'")

    def test_description_double_quotes(self) -> None:
        text = VALID_SKILL.format(name="se-test").replace(
            "end to end.", 'end to "end".'
        )
        self.write_skill(text=text)
        self.assert_validation_error("double quotes")

    def test_extra_frontmatter_key(self) -> None:
        text = VALID_SKILL.format(name="se-test").replace(
            "---\n\n# Fixture",
            "allowed-tools: all\n---\n\n# Fixture",
        )
        self.write_skill(text=text)
        self.assert_validation_error("not allowed")

    def test_missing_section(self) -> None:
        text = VALID_SKILL.format(name="se-test").replace(
            "## Safety rules\n\nText.\n\n", ""
        )
        self.write_skill(text=text)
        self.assert_validation_error("missing required section '## Safety rules'")

    def test_out_of_order_sections(self) -> None:
        text = VALID_SKILL.format(name="se-test")
        text = text.replace("## When to use", "## TEMP")
        text = text.replace("## Final report", "## When to use")
        text = text.replace("## TEMP", "## Final report")
        self.write_skill(text=text)
        self.assert_validation_error("out of order")

    def test_banned_phrase(self) -> None:
        text = VALID_SKILL.format(name="se-test").replace(
            "Intro paragraph.", "Ask Claude to do it."
        )
        self.write_skill(text=text)
        self.assert_validation_error("framework-neutrality")

    def test_lowercase_paths_are_not_banned(self) -> None:
        text = VALID_SKILL.format(name="se-test").replace(
            "Intro paragraph.", "Skills install under `.claude/skills/`."
        )
        self.write_skill(text=text)
        gen.validate_skills()

    def test_unexpected_file_in_skill_dir(self) -> None:
        self.write_skill()
        (self.skills_root / "se-test" / "notes.txt").write_text(
            "x", encoding="utf-8"
        )
        self.assert_validation_error("unexpected file")

    def test_missing_shared_reference(self) -> None:
        self.write_skill()
        with mock.patch.object(
            gen,
            "SHARED_REFERENCES",
            {"_shared/references/source-standards.md": ("se-test",)},
        ):
            self.assert_validation_error("missing shared reference")

    def test_shared_reference_collision(self) -> None:
        self.write_skill()
        shared = self.skills_root / "_shared" / "references"
        shared.mkdir(parents=True)
        (shared / "source-standards.md").write_text("bar\n", encoding="utf-8")
        own = self.skills_root / "se-test" / "references"
        own.mkdir()
        (own / "source-standards.md").write_text("own\n", encoding="utf-8")
        with mock.patch.object(
            gen,
            "SHARED_REFERENCES",
            {"_shared/references/source-standards.md": ("se-test",)},
        ):
            self.assert_validation_error("collides with the shared reference")

    def test_unregistered_shared_file(self) -> None:
        self.write_skill()
        shared = self.skills_root / "_shared" / "references"
        shared.mkdir(parents=True)
        (shared / "orphan.md").write_text("x\n", encoding="utf-8")
        self.assert_validation_error("not registered in")

    def test_bootstrap_writes_manifest(self) -> None:
        self.write_skill()
        self.assertEqual(gen.main([]), 0)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "se-ai-command-pack")
        targets = {row["target"] for row in manifest["files"]}
        for info in gen.PLATFORM_REGISTRY.values():
            self.assertIn(f"{info.skills_dir}/se-test/SKILL.md", targets)
        self.assertIn("### Understand", self.readme_path.read_text(encoding="utf-8"))
        self.assertIn(
            "Bundled pack version: `0.1.0`",
            self.help_catalog_path.read_text(encoding="utf-8"),
        )

    def test_catalog_groups_skills_and_escapes_pipes(self) -> None:
        first = VALID_SKILL.format(name="se-test").replace(
            "end to end.", "end | to end."
        )
        self.write_skill(text=first)
        self.write_skill(name="se-second")
        with (
            mock.patch.object(
                gen,
                "SKILLS",
                (
                    gen.SkillInfo(name="se-test", family="understand"),
                    gen.SkillInfo(name="se-second", family="decide"),
                ),
            ),
            mock.patch.object(gen, "SKILL_NAMES", ("se-test", "se-second")),
        ):
            rendered = gen.regenerated_readme_text()
        self.assertLess(rendered.index("### Understand"), rendered.index("### Decide"))
        self.assertIn("end \\| to end.", rendered)

    def test_help_catalog_groups_all_families_and_escapes_pipes(self) -> None:
        first = VALID_SKILL.format(name="se-test").replace(
            "end to end.", "end | to end."
        )
        self.write_skill(text=first)
        rendered = gen.regenerated_help_catalog_text()
        self.assertLess(rendered.index("## Understand"), rendered.index("## Decide"))
        self.assertIn("Understand fixture outcomes.", rendered)
        self.assertIn("No bundled skills in this release.", rendered)
        self.assertIn("end \\| to end.", rendered)

    def test_catalog_requires_exactly_one_marker_pair(self) -> None:
        self.write_skill()
        for text in (
            "# Missing markers\n",
            "<!-- SE_SKILL_CATALOG:START -->\n"
            "<!-- SE_SKILL_CATALOG:START -->\n"
            "<!-- SE_SKILL_CATALOG:END -->\n",
        ):
            self.readme_path.write_text(text, encoding="utf-8")
            with self.assertRaises(gen.GenerationError) as caught:
                gen.regenerated_readme_text()
            self.assertIn("catalog markers", str(caught.exception))

    def test_missing_readme_fails_cleanly_before_manifest_write(self) -> None:
        self.write_skill()
        self.readme_path.unlink()
        self.assertEqual(gen.main([]), 1)
        self.assertFalse(self.manifest_path.exists())

    def test_validation_failure_writes_neither_surface(self) -> None:
        self.write_skill()
        self.readme_path.write_text("# Missing markers\n", encoding="utf-8")
        self.assertEqual(gen.main([]), 1)
        self.assertFalse(self.manifest_path.exists())

    def test_readme_write_failure_keeps_manifest_unchanged(self) -> None:
        self.write_skill()
        committed_readme = self.readme_path.read_text(encoding="utf-8")
        calls: list[Path] = []

        def fail_readme(path: Path, content: str) -> None:
            calls.append(path)
            raise SystemExit(f"error: cannot write {path}: read-only fixture")

        with mock.patch.object(gen, "atomic_write_text", side_effect=fail_readme):
            self.assertEqual(gen.main([]), 1)
        self.assertEqual(calls, [self.readme_path])
        self.assertEqual(
            self.readme_path.read_text(encoding="utf-8"), committed_readme
        )
        self.assertFalse(self.manifest_path.exists())

    def test_manifest_write_failure_rolls_back_readme(self) -> None:
        self.write_skill()
        committed_readme = self.readme_path.read_text(encoding="utf-8")
        atomic_write_text = gen.atomic_write_text

        def fail_manifest(path: Path, content: str) -> None:
            if path == self.manifest_path:
                raise SystemExit(f"error: cannot write {path}: read-only fixture")
            atomic_write_text(path, content)

        with mock.patch.object(gen, "atomic_write_text", side_effect=fail_manifest):
            self.assertEqual(gen.main([]), 1)
        self.assertEqual(
            self.readme_path.read_text(encoding="utf-8"), committed_readme
        )
        self.assertFalse(self.help_catalog_path.exists())
        self.assertFalse(self.manifest_path.exists())

    def test_help_catalog_write_failure_rolls_back_readme(self) -> None:
        self.write_skill()
        committed_readme = self.readme_path.read_text(encoding="utf-8")
        atomic_write_text = gen.atomic_write_text

        def fail_help_catalog(path: Path, content: str) -> None:
            if path == self.help_catalog_path:
                raise SystemExit(f"error: cannot write {path}: read-only fixture")
            atomic_write_text(path, content)

        with mock.patch.object(
            gen, "atomic_write_text", side_effect=fail_help_catalog
        ):
            self.assertEqual(gen.main([]), 1)
        self.assertEqual(
            self.readme_path.read_text(encoding="utf-8"), committed_readme
        )
        self.assertFalse(self.help_catalog_path.exists())
        self.assertFalse(self.manifest_path.exists())

    def test_check_detects_drift(self) -> None:
        self.write_skill()
        self.assertEqual(gen.main([]), 0)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        manifest["files"] = []
        self.manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        self.assertEqual(gen.main(["--check"]), 1)

    def test_check_detects_readme_catalog_drift(self) -> None:
        self.write_skill()
        self.assertEqual(gen.main([]), 0)
        committed = self.readme_path.read_text(encoding="utf-8")
        self.readme_path.write_text(
            committed.replace("### Understand", "### Drifted"),
            encoding="utf-8",
        )
        self.assertEqual(gen.main(["--check"]), 1)

    def test_check_detects_help_catalog_drift(self) -> None:
        self.write_skill()
        self.assertEqual(gen.main([]), 0)
        committed = self.help_catalog_path.read_text(encoding="utf-8")
        self.help_catalog_path.write_text(
            committed.replace("## Understand", "## Drifted"),
            encoding="utf-8",
        )
        self.assertEqual(gen.main(["--check"]), 1)

    def test_header_and_static_rows_preserved(self) -> None:
        self.write_skill()
        self.manifest_path.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "name": "se-ai-command-pack",
                    "version": "3.2.1",
                    "license": "MIT",
                    "description": "Custom description.",
                    "files": [
                        {
                            "platform": "claude",
                            "kind": "script",
                            "scope": "user",
                            "source": "scripts/se-ai-command-pack-helper.py",
                            "target": ".claude/helper.py",
                            "anchor": ".claude",
                            "install": "if-anchor-exists",
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self.assertEqual(gen.main([]), 0)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "3.2.1")
        self.assertEqual(manifest["description"], "Custom description.")
        self.assertEqual(
            manifest["files"][0]["source"],
            "scripts/se-ai-command-pack-helper.py",
        )
        derived = [row for row in manifest["files"] if gen.is_derived_row(row)]
        self.assertGreater(len(derived), 0)

    def test_unknown_header_field_rejected(self) -> None:
        self.write_skill()
        self.manifest_path.write_text(
            json.dumps({"schemaVersion": 1, "requiresTrellis": True, "files": []})
            + "\n",
            encoding="utf-8",
        )
        with self.assertRaises(gen.GenerationError) as caught:
            gen.regenerated_manifest_text()
        self.assertIn("unknown header fields", str(caught.exception))

    def test_generation_error_exits_nonzero(self) -> None:
        # No skill dir written: validate_skills fails inside main.
        self.assertEqual(gen.main([]), 1)


if __name__ == "__main__":
    unittest.main()
